# SPDX-License-Identifier: AGPL-3.0-or-later
"""AI-powered summarization module for Aperion search results.

This module provides functionality to generate AI summaries of search results
using multiple API providers: OpenAI, Gemini, Ollama, and other OpenAI-compatible APIs.
"""

from __future__ import annotations

import json
import typing as t
from datetime import datetime, timezone
from urllib.parse import urlparse
import time
import os

import httpx
from dotenv import load_dotenv

from aperion import logger

logger = logger.getChild('ai_summarizer')

if t.TYPE_CHECKING:
    from aperion.result_types import EngineResults

# API Provider Constants
PROVIDER_OPENAI = "openai"
PROVIDER_GEMINI = "gemini"
PROVIDER_OLLAMA = "ollama"
PROVIDER_CUSTOM = "custom"
PROVIDER_GROQ = "groq"
PROVIDER_SAMBANOVA = "sambanova"
PROVIDER_OPENROUTER = "openrouter"
PROVIDER_MISTRAL = "mistral"

# Default endpoints for each provider
DEFAULT_ENDPOINTS = {
    PROVIDER_OPENAI: "https://api.openai.com/v1",
    PROVIDER_GEMINI: "https://generativelanguage.googleapis.com/v1beta",
    PROVIDER_OLLAMA: "http://localhost:11434",
    PROVIDER_CUSTOM: "",
    PROVIDER_GROQ: "https://api.groq.com/openai/v1",
    PROVIDER_SAMBANOVA: "https://api.sambanova.ai/v1",
    PROVIDER_OPENROUTER: "https://openrouter.ai/api/v1",
    PROVIDER_MISTRAL: "https://api.mistral.ai/v1",
}

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that summarizes search results.
Your task is to provide a concise, accurate summary of the provided search results.
Focus on the most relevant information and present it in a clear, readable format.
If the results contain conflicting information, mention this briefly.
Keep the summary factual and based on the provided results."""

DEFAULT_SUMMARY_PROMPT = """Search Query: {query}

Search Results:
{results}

Please provide a concise, well-structured summary of these search results that directly answers the query.

IMPORTANT: Your response must be:
- Between 50 and 300 words
- Complete sentences (never cut off mid-sentence)
- Well-structured with clear beginning and end

Format your response using Markdown:
- Use **bold** for emphasis on key points
- Use bullet points (-) for lists
- Use numbered lists (1., 2., etc.) for steps or ranked items
- Add paragraph breaks between different topics
- Use proper formatting to make it easy to read

Focus on the most relevant and reliable information."""

DEFAULT_CHAT_PROMPT = """You are a helpful AI assistant. Answer the user's question directly and helpfully.
If relevant information is provided in the context, use it to enhance your answer.
Be concise but comprehensive."""

DEFAULT_TIMEOUT = 15.0
DEFAULT_TIMEOUT_PER_RESULT = 5.0
MAX_CONTENT_LENGTH = 4000

# Load environment variables from .env file in the root directory
# Try multiple possible locations for .env file
possible_env_paths = [
    '/mnt/c/Users/lenov/AppData/burhanuddin work/Aperion-Search/.env',  # WSL path (priority)
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),  # Relative to aperion dir
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),  # Project root
    '.env',  # Current directory
]

loaded = False
for env_path in possible_env_paths:
    if os.path.exists(env_path):
        loaded = load_dotenv(env_path)
        logger.info(f"Loading .env from {env_path}: {loaded}")
        break

if not loaded:
    logger.warning("Could not find or load .env file from any location")

# Fallback API configuration - these are used when primary provider fails
# API keys are read from environment variables
# Ordered by priority (most credits/free tier first)
FALLBACK_PROVIDERS = [
    {
        "provider": PROVIDER_GROQ,
        "api_key": os.getenv("AI_GROQ_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINTS[PROVIDER_GROQ],
        "model": "llama-3.3-70b-versatile",
    },
    {
        "provider": PROVIDER_OPENROUTER,
        "api_key": os.getenv("AI_OPENROUTER_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINTS[PROVIDER_OPENROUTER],
        "model": "openai/gpt-4o",
    },
    {
        "provider": PROVIDER_GEMINI,
        "api_key": os.getenv("AI_GEMINI_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINTS[PROVIDER_GEMINI],
        "model": "gemini-2.5-flash",
    },
    {
        "provider": PROVIDER_SAMBANOVA,
        "api_key": os.getenv("AI_SAMBANOVA_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINTS[PROVIDER_SAMBANOVA],
        "model": "Meta-Llama-3.1-70B-Instruct",
    },
    {
        "provider": PROVIDER_MISTRAL,
        "api_key": os.getenv("AI_MISTRAL_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINTS[PROVIDER_MISTRAL],
        "model": "mistral-large-latest",
    },
    {
        "provider": PROVIDER_OPENAI,
        "api_key": os.getenv("AI_OPENAI_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINTS[PROVIDER_OPENAI],
        "model": "gpt-4o",
    },
]

# Log which providers have API keys configured
for provider_config in FALLBACK_PROVIDERS:
    has_key = bool(provider_config["api_key"])
    logger.info(f"Provider {provider_config['provider']}: API key configured = {has_key}")


def _get_openai_compatible_urls(endpoint: str) -> list[str]:
    """Return candidate API URLs for OpenAI-compatible endpoints.

    Some providers expose the chat endpoint at /v1/chat/completions while others
    expect /chat/completions directly. This helper tries the most common forms.
    """
    if not endpoint:
        return []

    cleaned_endpoint = endpoint.rstrip('/')
    if not cleaned_endpoint:
        return []

    if cleaned_endpoint.endswith('/chat/completions'):
        return [cleaned_endpoint]

    candidates = []
    if cleaned_endpoint.endswith('/v1'):
        candidates.append(f"{cleaned_endpoint}/chat/completions")
    else:
        candidates.append(f"{cleaned_endpoint}/v1/chat/completions")
        candidates.append(f"{cleaned_endpoint}/chat/completions")
        candidates.append(f"{cleaned_endpoint}/api/chat/completions")

    return list(dict.fromkeys(candidates))


class SummarizerError(Exception):
    """Base exception for summarizer errors."""
    pass


class APIError(SummarizerError):
    """Exception raised when the API returns an error."""
    pass


class TimeoutError(SummarizerError):
    """Exception raised when the request times out."""
    pass


def sanitize_url(url: str) -> str:
    """Sanitize URL to handle invalid IDNA hostnames gracefully.

    Args:
        url: The URL to sanitize

    Returns:
        The original URL if valid, or '[Invalid URL]' if the URL
        has invalid characters that would cause IDNA encoding errors.
    """
    if not url:
        return url

    try:
        parsed = urlparse(url)
        if parsed.netloc:
            # Test if hostname is valid IDNA - this will raise UnicodeError
            # for invalid characters like '›' (U+203A) or other special chars
            parsed.netloc.encode('idna')
    except (UnicodeError, UnicodeDecodeError, UnicodeEncodeError):
        logger.debug(f"Skipping URL with invalid hostname: {url}")
        return '[Invalid URL]'
    except Exception:
        # Catch any other parsing errors
        return '[Invalid URL]'

    return url


def format_results_for_prompt(
    results: EngineResults,
    query: str,
    max_results: int = 10
) -> str:
    """Format search results into a prompt suitable for AI summarization.

    Args:
        results: The search results to format
        query: The original search query
        max_results: Maximum number of results to include in the prompt

    Returns:
        A formatted string containing the search results
    """
    lines = [
        f"Search Query: {query}",
        "",
        "Search Results:",
        "",
    ]

    result_count = 0
    for result in results:
        if result_count >= max_results:
            break

        # Extract title and content from result
        title = getattr(result, 'title', '') or getattr(result, 'name', '')
        content = getattr(result, 'content', '') or getattr(result, 'description', '')
        url = getattr(result, 'url', '') or getattr(result, 'link', '')

        if not title and not content:
            continue

        result_count += 1
        lines.append(f"{result_count}. {title}")

        if content:
            # Truncate content if too long
            if len(content) > MAX_CONTENT_LENGTH // max_results:
                content = content[: MAX_CONTENT_LENGTH // max_results] + "..."
            lines.append(f"   Content: {content}")

        if url:
            # Sanitize URL to handle invalid IDNA hostnames
            safe_url = sanitize_url(url)
            lines.append(f"   URL: {safe_url}")

        lines.append("")

    if result_count == 0:
        lines.append("No results found.")

    return "\n".join(lines)


async def fetch_available_models(
    endpoint: str,
    provider: str = PROVIDER_OPENAI,
    api_key: str | None = None,
    timeout: float = 10,
) -> list[str]:
    """Fetch available models from the API endpoint based on provider.

    Args:
        endpoint: The base URL of the API endpoint
        provider: The API provider (openai, gemini, ollama, custom)
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds (default: 10)

    Returns:
        List of model IDs, or empty list on error
    """
    headers: dict[str, str] = {}
    
    # Provider-specific endpoint and header configuration
    if provider == PROVIDER_GEMINI:
        # Gemini uses different endpoint structure
        url = f"{endpoint.rstrip('/')}/models?key={api_key}"
    elif provider == PROVIDER_OLLAMA:
        # Ollama uses /api/tags
        url = f"{endpoint.rstrip('/')}/api/tags"
    elif provider in (PROVIDER_GROQ, PROVIDER_SAMBANOVA, PROVIDER_OPENROUTER, PROVIDER_MISTRAL):
        # These are OpenAI-compatible
        url = f"{endpoint.rstrip('/')}/v1/models"
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
    else:
        # OpenAI and custom use /v1/models
        url = f"{endpoint.rstrip('/')}/v1/models"
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            models = []
            
            if provider == PROVIDER_GEMINI:
                # Gemini response format: { "models": [{ "name": "models/..." }] }
                for model in data.get("models", []):
                    model_name = model.get("name", "")
                    if model_name:
                        models.append(model_name)
            elif provider == PROVIDER_OLLAMA:
                # Ollama response format: { "models": [{ "name": "model:tag" }] }
                for model in data.get("models", []):
                    model_name = model.get("name", "")
                    if model_name:
                        models.append(model_name)
            else:
                # OpenAI-compatible format: { "data": [{ "id": "model-name" }] }
                    model_id = model.get("id", "")
                    if model_id:
                        models.append(model_id)
            
            logger.debug(f"Fetched {len(models)} models from {provider} at {endpoint}")
            return models

    except Exception as e:
        logger.warning(f"Error fetching models from {provider} at {endpoint}: {e}")
        return []


def generate_summary_with_fallback(
    results: list[dict],
    query: str,
    endpoint: str = "",
    model: str = "",
    provider: str = "",
    api_key: str | None = None,
    system_prompt: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_tokens: int = 500,
    temperature: float = 0.7,
) -> dict[str, t.Any]:
    """Generate AI summary with fallback to multiple providers.

    Tries the primary provider first if configured, then falls back to configured backup providers
    if the primary fails. If no primary is configured, uses fallback providers directly.
    Returns the first successful result.

    Args:
        results: List of search result dicts with 'title', 'content', 'url' keys
        query: The original search query
        endpoint: The base URL of the API endpoint (optional, uses fallback if empty)
        model: The model ID to use for summarization (optional, uses fallback if empty)
        provider: The API provider (optional, uses fallback if empty)
        api_key: Optional API key for authentication
        system_prompt: Optional custom system prompt
        timeout: Request timeout in seconds
        max_tokens: Maximum tokens in the response
        temperature: Temperature for generation (0.0 to 1.0)

    Returns:
        A dictionary with success, summary, error, model, timestamp, usage, stats
    """
    logger.info(f"generate_summary_with_fallback called with {len(results)} results, query: {query[:50]}...")
    logger.info(f"Primary config - endpoint: {endpoint}, model: {model}, provider: {provider}, has_api_key: {bool(api_key)}")
    
    # If primary provider is configured, try it first
    if endpoint and model and provider and api_key:
        logger.info(f"Attempting primary provider: {provider}")
        primary_result = generate_summary_sync(
            results=results,
            query=query,
            endpoint=endpoint,
            model=model,
            provider=provider,
            api_key=api_key,
            system_prompt=system_prompt,
            timeout=timeout,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        if primary_result.get("success"):
            logger.info(f"Successfully generated summary using primary provider {provider}")
            return primary_result

        logger.warning(f"Primary provider {provider} failed: {primary_result.get('error', 'Unknown error')}")

    # Try fallback providers in priority order
    for fallback_config in FALLBACK_PROVIDERS:
        fallback_provider = fallback_config["provider"]
        fallback_endpoint = fallback_config["endpoint"]
        fallback_model = fallback_config["model"]
        fallback_api_key = fallback_config["api_key"]

        # Skip if no API key is configured for this provider
        if not fallback_api_key:
            logger.debug(f"Skipping {fallback_provider} - no API key configured")
            continue

        # Skip if this is the same as the failed primary provider
        if (fallback_provider == provider and 
            fallback_endpoint == endpoint and 
            fallback_model == model):
            continue

        logger.info(f"Attempting fallback provider: {fallback_provider}")
        fallback_result = generate_summary_sync(
            results=results,
            query=query,
            endpoint=fallback_endpoint,
            model=fallback_model,
            provider=fallback_provider,
            api_key=fallback_api_key,
            system_prompt=system_prompt,
            timeout=timeout,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        if fallback_result.get("success"):
            logger.info(f"Successfully generated summary using fallback provider {fallback_provider}")
            return fallback_result

        logger.warning(f"Fallback provider {fallback_provider} failed: {fallback_result.get('error', 'Unknown error')}")

    # All providers failed
    logger.error("All AI providers failed to generate summary")
    return {
        "success": False,
        "summary": None,
        "error": "All AI providers failed. Please check your API keys in the .env file.",
        "model": model if model else "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "usage": None,
        "stats": None,
    }


def generate_summary_sync(
    results: list[dict],
    query: str,
    endpoint: str,
    model: str,
    provider: str = PROVIDER_OPENAI,
    api_key: str | None = None,
    system_prompt: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_tokens: int = 500,
    temperature: float = 0.7,
) -> dict[str, t.Any]:
    """Generate AI summary synchronously (blocking call).

    Args:
        results: List of search result dicts with 'title', 'content', 'url' keys
        query: The original search query
        endpoint: The base URL of the API endpoint
        model: The model ID to use for summarization
        provider: The API provider (openai, gemini, ollama, custom)
        api_key: Optional API key for authentication
        system_prompt: Optional custom system prompt
        timeout: Request timeout in seconds
        max_tokens: Maximum tokens in the response
        temperature: Temperature for generation (0.0 to 1.0)

    Returns:
        A dictionary with success, summary, error, model, timestamp, usage, stats
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    api_urls: list[str] = []

    # Provider-specific endpoint and payload configuration
    if provider == PROVIDER_GEMINI:
        # Gemini API format
        normalized_model = model.strip()
        if normalized_model.startswith('models/'):
            normalized_model = normalized_model[len('models/'):]
        api_url = f"{endpoint.rstrip('/')}/models/{normalized_model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        api_urls = [api_url]
    elif provider == PROVIDER_OLLAMA:
        # Ollama API format
        api_url = f"{endpoint.rstrip('/')}/api/chat"
        headers = {"Content-Type": "application/json"}
        api_urls = [api_url]
    else:
        # OpenAI and custom format
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        api_urls = _get_openai_compatible_urls(endpoint)
        if not api_urls:
            return {
                "success": False,
                "summary": None,
                "error": "AI endpoint is not configured",
                "model": model,
                "timestamp": timestamp,
                "usage": None,
                "stats": None,
            }

    # Format results into prompt text
    lines = [f"Search Query: {query}", "", "Search Results:", ""]
    for i, result in enumerate(results, 1):
        title = result.get('title', '')
        content = result.get('content', '')
        url = result.get('url', '')

        if not title and not content:
            continue

        lines.append(f"{i}. {title}")
        if content:
            # Truncate content if too long
            max_content = MAX_CONTENT_LENGTH // len(results) if results else MAX_CONTENT_LENGTH
            if len(content) > max_content:
                content = content[:max_content] + "..."
            lines.append(f"   Content: {content}")
        if url:
            # Sanitize URL to handle invalid IDNA hostnames
            safe_url = sanitize_url(url)
            lines.append(f"   URL: {safe_url}")
        lines.append("")

    if len(lines) <= 4:  # Only header lines, no results
        lines.append("No results found.")

    formatted_results = "\n".join(lines)

    # Build the user prompt
    user_prompt = DEFAULT_SUMMARY_PROMPT.format(
        query=query,
        results=formatted_results
    )

    # Use default system prompt if none provided
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    
    if '{query}' in system_prompt:
        system_prompt = system_prompt.replace('{query}', query)
    if '{results}' in system_prompt:
        system_prompt = system_prompt.replace('{results}', formatted_results)

    # Provider-specific payload construction
    if provider == PROVIDER_GEMINI:
        # Gemini API format
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            }
        }
    elif provider == PROVIDER_OLLAMA:
        # Ollama API format
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            }
        }
    else:
        # OpenAI and custom format
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

    start_time = time.time()

    try:
        # Use sync client instead of async - create explicit timeout object
        timeout_obj = httpx.Timeout(timeout, connect=10.0)
        with httpx.Client(timeout=timeout_obj) as client:
            data = None
            last_error: Exception | None = None
            for api_url in ([api_url] if provider in {PROVIDER_GEMINI, PROVIDER_OLLAMA} else api_urls):
                try:
                    response = client.post(api_url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    break
                except httpx.HTTPStatusError as e:
                    last_error = e
                    if e.response.status_code not in (404, 405) or api_url == api_urls[-1]:
                        break
                except httpx.RequestError as e:
                    last_error = e
                    break

            if data is None:
                if isinstance(last_error, httpx.HTTPStatusError):
                    error_msg = f"API returned error: {last_error.response.status_code}"
                    try:
                        error_data = last_error.response.json()
                        if "error" in error_data:
                            error_msg = f"{error_msg} - {error_data['error'].get('message', '')}"
                    except Exception:
                        pass
                    logger.warning(error_msg)
                    return {
                        "success": False,
                        "summary": None,
                        "error": error_msg,
                        "model": model,
                        "timestamp": timestamp,
                        "usage": None,
                        "stats": None,
                    }
                if isinstance(last_error, httpx.TimeoutException):
                    logger.warning("Timeout generating summary")
                    return {
                        "success": False,
                        "summary": None,
                        "error": f"Request timed out after {timeout}s",
                        "model": model,
                        "timestamp": timestamp,
                        "usage": None,
                        "stats": None,
                    }
                if isinstance(last_error, httpx.RequestError):
                    logger.warning(f"Request error generating summary: {last_error}")
                    return {
                        "success": False,
                        "summary": None,
                        "error": f"Request failed: {last_error}",
                        "model": model,
                        "timestamp": timestamp,
                        "usage": None,
                        "stats": None,
                    }
                logger.warning("No response received from API")
                return {
                    "success": False,
                    "summary": None,
                    "error": "No response received from API",
                    "model": model,
                    "timestamp": timestamp,
                    "usage": None,
                    "stats": None,
                }

            # Calculate response time
            response_time = round(time.time() - start_time, 2)

            # Provider-specific response parsing
            summary = ""
            usage = {}
            
            if provider == PROVIDER_GEMINI:
                # Gemini response format
                candidates = data.get("candidates", [])
                if candidates and candidates[0].get("content"):
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and parts[0].get("text"):
                        summary = parts[0]["text"].strip()
                usage = data.get("usageMetadata", {})
            elif provider == PROVIDER_OLLAMA:
                # Ollama response format
                message = data.get("message", {})
                summary = message.get("content", "").strip()
                usage = data.get("usage", {})
            else:
                # OpenAI-compatible format
                choices = data.get("choices", [])
                if not choices:
                    logger.warning("No choices in API response")
                    return {
                        "success": False,
                        "summary": None,
                        "error": "No completion returned from API",
                        "model": model,
                        "timestamp": timestamp,
                        "usage": None,
                        "stats": None,
                    }
                message = choices[0].get("message", {})
                summary = message.get("content", "").strip()
                usage = data.get("usage", {})

            if not summary:
                logger.warning("No summary content in API response")
                return {
                    "success": False,
                    "summary": None,
                    "error": "No content returned from API",
                    "model": model,
                    "timestamp": timestamp,
                    "usage": None,
                    "stats": None,
                }

            # Extract usage stats (provider-specific)
            if provider == PROVIDER_GEMINI:
                stats = {
                    "prompt_tokens": usage.get("promptTokenCount", 0),
                    "completion_tokens": usage.get("candidatesTokenCount", 0),
                    "total_tokens": usage.get("totalTokenCount", 0),
                    "model": model,
                    "response_time": response_time,
                }
            elif provider == PROVIDER_OLLAMA:
                stats = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                    "model": model,
                    "response_time": response_time,
                }
            else:
                stats = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                    "model": model,
                    "response_time": response_time,
                }

            logger.debug(f"Generated summary using {provider} model {model}")

            return {
                "success": True,
                "summary": summary,
                "error": None,
                "model": model,
                "timestamp": timestamp,
                "usage": usage,
                "stats": stats,
            }

    except httpx.TimeoutException:
        logger.warning("Timeout generating summary")
        return {
            "success": False,
            "summary": None,
            "error": f"Request timed out after {timeout}s",
            "model": model,
            "timestamp": timestamp,
            "usage": None,
            "stats": None,
        }

    except httpx.HTTPStatusError as e:
        error_msg = f"API returned error: {e.response.status_code}"
        try:
            error_data = e.response.json()
            if isinstance(error_data, dict):
                if "error" in error_data:
                    if isinstance(error_data["error"], dict):
                        message = error_data["error"].get("message", "")
                        if message:
                            error_msg = f"{error_msg} - {message}"
                    else:
                        error_msg = f"{error_msg} - {error_data['error']}"
                elif "message" in error_data:
                    error_msg = f"{error_msg} - {error_data['message']}"
        except Exception:
            response_text = getattr(e.response, "text", "")
            if response_text:
                error_msg = f"{error_msg} - {response_text[:500]}"
        logger.warning(error_msg)
        hint = ""
        if provider == PROVIDER_GEMINI:
            hint = " Try Gemini endpoint https://generativelanguage.googleapis.com/v1beta with a valid API key and model like gemini-1.5-flash."
        elif provider == PROVIDER_OLLAMA:
            hint = " Try Ollama endpoint http://localhost:11434 with a downloaded model such as llama3.2."
        elif provider == PROVIDER_GROQ:
            hint = " Try Groq endpoint https://api.groq.com/openai/v1 with a valid API key and model like llama-3.3-70b-versatile."
        elif provider == PROVIDER_SAMBANOVA:
            hint = " Try Sambanova endpoint https://api.sambanova.ai/v1 with a valid API key and model like Meta-Llama-3.1-70B-Instruct."
        elif provider == PROVIDER_OPENROUTER:
            hint = " Try OpenRouter endpoint https://openrouter.ai/api/v1 with a valid API key and model like openai/gpt-4o."
        elif provider == PROVIDER_MISTRAL:
            hint = " Try Mistral endpoint https://api.mistral.ai/v1 with a valid API key and model like mistral-large-latest."
        else:
            hint = " Check your OpenAI-compatible endpoint, API key, and model in Preferences > AI Summarization."
        return {
            "success": False,
            "summary": None,
            "error": f"{error_msg}{hint}",
            "model": model,
            "timestamp": timestamp,
            "usage": None,
            "stats": None,
        }

    except httpx.RequestError as e:
        logger.warning(f"Request error generating summary: {e}")
        return {
            "success": False,
            "summary": None,
            "error": f"Request failed: {e}",
            "model": model,
            "timestamp": timestamp,
            "usage": None,
            "stats": None,
        }

    except Exception as e:
        # Catch any unexpected errors (e.g., from URL processing, etc.)
        logger.error(f"Unexpected error generating summary: {e}")
        return {
            "success": False,
            "summary": None,
            "error": f"Unexpected error: {e}",
            "model": model,
            "timestamp": timestamp,
            "usage": None,
            "stats": None,
        }


def generate_chat_with_fallback(
    query: str,
    endpoint: str = "",
    model: str = "",
    provider: str = "",
    api_key: str | None = None,
    system_prompt: str | None = None,
    context: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_tokens: int = 1000,
    temperature: float = 0.7,
) -> dict[str, t.Any]:
    """Generate AI chat response with fallback to multiple providers.

    Tries the primary provider first if configured, then falls back to configured backup providers
    if the primary fails. If no primary is configured, uses fallback providers directly.
    Returns the first successful result.

    Args:
        query: The user's query/question
        endpoint: The base URL of the API endpoint (optional, uses fallback if empty)
        model: The model ID to use (optional, uses fallback if empty)
        provider: The API provider (optional, uses fallback if empty)
        api_key: Optional API key for authentication
        system_prompt: Optional custom system prompt
        context: Optional context from search results
        timeout: Request timeout in seconds
        max_tokens: Maximum tokens in the response
        temperature: Temperature for generation (0.0 to 1.0)

    Returns:
        A dictionary with success, response, error, model, timestamp, usage, stats
    """
    # If primary provider is configured, try it first
    if endpoint and model and provider and api_key:
        logger.debug(f"Attempting primary provider for chat: {provider}")
        primary_result = generate_chat_sync(
            query=query,
            endpoint=endpoint,
            model=model,
            provider=provider,
            api_key=api_key,
            system_prompt=system_prompt,
            context=context,
            timeout=timeout,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        if primary_result.get("success"):
            logger.info(f"Successfully generated chat response using primary provider {provider}")
            return primary_result

        logger.warning(f"Primary provider {provider} failed for chat: {primary_result.get('error', 'Unknown error')}")

    # Try fallback providers in priority order
    for fallback_config in FALLBACK_PROVIDERS:
        fallback_provider = fallback_config["provider"]
        fallback_endpoint = fallback_config["endpoint"]
        fallback_model = fallback_config["model"]
        fallback_api_key = fallback_config["api_key"]

        # Skip if no API key is configured for this provider
        if not fallback_api_key:
            logger.debug(f"Skipping {fallback_provider} - no API key configured")
            continue

        # Skip if this is the same as the failed primary provider
        if (fallback_provider == provider and 
            fallback_endpoint == endpoint and 
            fallback_model == model):
            continue

        logger.debug(f"Attempting fallback provider for chat: {fallback_provider}")
        fallback_result = generate_chat_sync(
            query=query,
            endpoint=fallback_endpoint,
            model=fallback_model,
            provider=fallback_provider,
            api_key=fallback_api_key,
            system_prompt=system_prompt,
            context=context,
            timeout=timeout,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        if fallback_result.get("success"):
            logger.info(f"Successfully generated chat response using fallback provider {fallback_provider}")
            return fallback_result

        logger.warning(f"Fallback provider {fallback_provider} failed for chat: {fallback_result.get('error', 'Unknown error')}")

    # All providers failed
    logger.error("All AI providers failed to generate chat response")
    return {
        "success": False,
        "response": None,
        "error": "All AI providers failed. Please check your API keys in the .env file.",
        "model": model if model else "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "usage": None,
        "stats": None,
    }


def generate_chat_sync(
    query: str,
    endpoint: str,
    model: str,
    provider: str = PROVIDER_OPENAI,
    api_key: str | None = None,
    system_prompt: str | None = None,
    context: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_tokens: int = 1000,
    temperature: float = 0.7,
) -> dict[str, t.Any]:
    """Generate AI chat response synchronously (blocking call).

    Args:
        query: The user's query/question
        endpoint: The base URL of the API endpoint
        model: The model ID to use
        provider: The API provider (openai, gemini, ollama, custom)
        api_key: Optional API key for authentication
        system_prompt: Optional custom system prompt
        context: Optional context from search results
        timeout: Request timeout in seconds
        max_tokens: Maximum tokens in the response
        temperature: Temperature for generation (0.0 to 1.0)

    Returns:
        A dictionary with success, response, error, model, timestamp, usage, stats
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # Provider-specific endpoint and payload configuration
    if provider == PROVIDER_GEMINI:
        api_url = f"{endpoint.rstrip('/')}/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
    elif provider == PROVIDER_OLLAMA:
        api_url = f"{endpoint.rstrip('/')}/api/chat"
        headers = {"Content-Type": "application/json"}
    else:
        endpoint = endpoint.rstrip('/')
        if not endpoint.endswith('/v1'):
            endpoint = f"{endpoint}/v1"
        api_url = f"{endpoint}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

    # Build the user prompt
    if context:
        user_prompt = f"Context from search results:\n{context}\n\nUser Question: {query}"
    else:
        user_prompt = query

    # Use default system prompt if none provided
    if system_prompt is None:
        system_prompt = DEFAULT_CHAT_PROMPT

    # Provider-specific payload construction
    if provider == PROVIDER_GEMINI:
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            }
        }
    elif provider == PROVIDER_OLLAMA:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            }
        }
    else:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

    start_time = time.time()

    try:
        timeout_obj = httpx.Timeout(timeout, connect=10.0)
        with httpx.Client(timeout=timeout_obj) as client:
            response = client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            response_time = round(time.time() - start_time, 2)

            # Provider-specific response parsing
            response_text = ""
            usage = {}
            
            if provider == PROVIDER_GEMINI:
                candidates = data.get("candidates", [])
                if candidates and candidates[0].get("content"):
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and parts[0].get("text"):
                        response_text = parts[0]["text"].strip()
                usage = data.get("usageMetadata", {})
            elif provider == PROVIDER_OLLAMA:
                message = data.get("message", {})
                response_text = message.get("content", "").strip()
                usage = data.get("usage", {})
            else:
                choices = data.get("choices", [])
                if not choices:
                    return {
                        "success": False,
                        "response": None,
                        "error": "No completion returned from API",
                        "model": model,
                        "timestamp": timestamp,
                        "usage": None,
                        "stats": None,
                    }
                message = choices[0].get("message", {})
                response_text = message.get("content", "").strip()
                usage = data.get("usage", {})

            if not response_text:
                return {
                    "success": False,
                    "response": None,
                    "error": "No content returned from API",
                    "model": model,
                    "timestamp": timestamp,
                    "usage": None,
                    "stats": None,
                }

            # Extract usage stats
            if provider == PROVIDER_GEMINI:
                stats = {
                    "prompt_tokens": usage.get("promptTokenCount", 0),
                    "completion_tokens": usage.get("candidatesTokenCount", 0),
                    "total_tokens": usage.get("totalTokenCount", 0),
                    "model": model,
                    "response_time": response_time,
                }
            elif provider == PROVIDER_OLLAMA:
                stats = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                    "model": model,
                    "response_time": response_time,
                }
            else:
                stats = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                    "model": model,
                    "response_time": response_time,
                }

            logger.debug(f"Generated chat response using {provider} model {model}")

            return {
                "success": True,
                "response": response_text,
                "error": None,
                "model": model,
                "timestamp": timestamp,
                "usage": usage,
                "stats": stats,
            }

    except httpx.TimeoutException:
        logger.warning("Timeout generating chat response")
        return {
            "success": False,
            "response": None,
            "error": f"Request timed out after {timeout}s",
            "model": model,
            "timestamp": timestamp,
            "usage": None,
            "stats": None,
        }

    except httpx.HTTPStatusError as e:
        error_msg = f"API returned error: {e.response.status_code}"
        try:
            error_data = e.response.json()
            if "error" in error_data:
                error_msg = f"{error_msg} - {error_data['error'].get('message', '')}"
        except Exception:
            pass
        logger.warning(error_msg)
        return {
            "success": False,
            "response": None,
            "error": error_msg,
            "model": model,
            "timestamp": timestamp,
            "usage": None,
            "stats": None,
        }

    except httpx.RequestError as e:
        logger.warning(f"Request error generating chat response: {e}")
        return {
            "success": False,
            "response": None,
            "error": f"Request failed: {e}",
            "model": model,
            "timestamp": timestamp,
            "usage": None,
            "stats": None,
        }

    except Exception as e:
        logger.error(f"Unexpected error generating chat response: {e}")
        return {
            "success": False,
            "response": None,
            "error": f"Unexpected error: {e}",
            "model": model,
            "timestamp": timestamp,
            "usage": None,
            "stats": None,
        }


async def generate_summary(
    results: EngineResults,
    query: str,
    endpoint: str,
    model: str,
    api_key: str | None = None,
    system_prompt: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_tokens: int = 500,
    temperature: float = 0.7,
) -> dict[str, t.Any]:
    """Generate an AI summary of search results.

    Args:
        results: The search results to summarize
        query: The original search query
        endpoint: The base URL of the API endpoint (e.g., "https://api.openai.com/v1")
        model: The model ID to use for summarization
        api_key: Optional API key for authentication
        system_prompt: Optional custom system prompt (uses default if not provided)
        timeout: Request timeout in seconds
        max_tokens: Maximum tokens in the response
        temperature: Temperature for generation (0.0 to 1.0)

    Returns:
        A dictionary containing:
        - success: Boolean indicating success
        - summary: The generated summary (if successful)
        - error: Error message (if failed)
        - model: The model used
        - timestamp: ISO format timestamp
        - usage: Token usage information (if available)

    Raises:
        APIError: If the API returns an error response
        TimeoutError: If the request times out
    """
    # Ensure endpoint has /v1 suffix for OpenAI-compatible APIs
    endpoint = endpoint.rstrip('/')
    if not endpoint.endswith('/v1'):
        endpoint = f"{endpoint}/v1"
    url = f"{endpoint}/chat/completions"

    headers: dict[str, str] = {
        "Content-Type": "application/json",
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Format results for the prompt
    formatted_results = format_results_for_prompt(results, query)

    # Build the user prompt
    user_prompt = DEFAULT_SUMMARY_PROMPT.format(
        query=query,
        results=formatted_results
    )

    # Use default system prompt if none provided
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract summary from response
            choices = data.get("choices", [])
            if not choices:
                logger.warning("No choices in API response")
                return {
                    "success": False,
                    "summary": None,
                    "error": "No completion returned from API",
                    "model": model,
                    "timestamp": timestamp,
                    "usage": None,
                }

            message = choices[0].get("message", {})
            summary = message.get("content", "").strip()

            logger.debug(f"Generated summary using model {model}")

            return {
                "success": True,
                "summary": summary,
                "error": None,
                "model": model,
                "timestamp": timestamp,
                "usage": data.get("usage"),
            }

    except httpx.TimeoutException as e:
        logger.warning(f"Timeout generating summary: {e}")
        raise TimeoutError(f"Request timed out after {timeout}s") from e

    except httpx.HTTPStatusError as e:
        error_msg = f"API returned error: {e.response.status_code}"
        try:
            error_data = e.response.json()
            if "error" in error_data:
                error_msg = f"{error_msg} - {error_data['error'].get('message', '')}"
        except Exception:
            pass
        logger.warning(error_msg)
        raise APIError(error_msg) from e

    except httpx.RequestError as e:
        logger.warning(f"Request error generating summary: {e}")
        raise APIError(f"Request failed: {e}") from e


async def stream_generate_summary(
    results: EngineResults,
    query: str,
    endpoint: str,
    model: str,
    api_key: str | None = None,
    system_prompt: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_tokens: int = 500,
    temperature: float = 0.7,
) -> t.AsyncGenerator[str, None]:
    """Stream an AI summary of search results.

    Args:
        results: The search results to summarize
        query: The original search query
        endpoint: The base URL of the API endpoint (e.g., "https://api.openai.com/v1")
        model: The model ID to use for summarization
        api_key: Optional API key for authentication
        system_prompt: Optional custom system prompt (uses default if not provided)
        timeout: Request timeout in seconds
        max_tokens: Maximum tokens in the response
        temperature: Temperature for generation (0.0 to 1.0)

    Yields:
        Chunks of the generated summary as they arrive from the API

    Raises:
        APIError: If the API returns an error response
        TimeoutError: If the request times out
    """
    # Ensure endpoint has /v1 suffix for OpenAI-compatible APIs
    endpoint = endpoint.rstrip('/')
    if not endpoint.endswith('/v1'):
        endpoint = f"{endpoint}/v1"
    url = f"{endpoint}/chat/completions"

    headers: dict[str, str] = {
        "Content-Type": "application/json",
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Format results for the prompt
    formatted_results = format_results_for_prompt(results, query)

    # Build the user prompt
    user_prompt = DEFAULT_SUMMARY_PROMPT.format(
        query=query,
        results=formatted_results
    )

    # Use default system prompt if none provided
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,  # Enable streaming
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue

                    # OpenAI streaming format: data: {"choices": [{"delta": {"content": "text"}}]}
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix

                        if data == "[DONE]":
                            break

                        try:
                            chunk_data = json.loads(data)
                            choices = chunk_data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse streaming chunk: {data}")
                            continue

    except httpx.TimeoutException as e:
        logger.warning(f"Timeout generating summary: {e}")
        raise TimeoutError(f"Request timed out after {timeout}s") from e

    except httpx.HTTPStatusError as e:
        error_msg = f"API returned error: {e.response.status_code}"
        try:
            error_data = e.response.json()
            if "error" in error_data:
                error_msg = f"{error_msg} - {error_data['error'].get('message', '')}"
        except Exception:
            pass
        logger.warning(error_msg)
        raise APIError(error_msg) from e

    except httpx.RequestError as e:
        logger.warning(f"Request error generating summary: {e}")
        raise APIError(f"Request failed: {e}") from e


def should_generate_summary(
    preferences: dict[str, t.Any] | None,
    results_count: int = 0,
) -> bool:
    """Check if an AI summary should be generated based on user preferences.

    Args:
        preferences: User preferences dictionary containing AI summarization settings.
            Expected structure:
            {
                "ai_summarizer": {
                    "enabled": bool,
                    "min_results": int,
                    "endpoint": str,
                    "model": str
                }
            }
        results_count: Number of search results available

    Returns:
        True if a summary should be generated, False otherwise
    """
    if preferences is None:
        return False

    ai_config = preferences.get("ai_summarizer", {})

    # Check if AI summarization is enabled
    if not ai_config.get("enabled", False):
        return False

    # Check if we have enough results to summarize
    min_results = ai_config.get("min_results", 3)
    if results_count < min_results:
        return False

    # Check if endpoint and model are configured
    endpoint = ai_config.get("endpoint", "")
    model = ai_config.get("model", "")
    if not endpoint or not model:
        logger.debug("AI summarization enabled but endpoint or model not configured")
        return False

    return True

