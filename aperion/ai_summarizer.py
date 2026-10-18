# SPDX-License-Identifier: AGPL-3.0-or-later
"""AI-powered summarization, chat, file, and image generation/editing module for Aperion search results.

This module provides functionality to generate AI summaries, chat responses, file creation/editing,
and image generation/editing using multiple API providers: OpenAI, Gemini, Cloudflare Workers AI,
Groq, Ollama, and other OpenAI-compatible APIs.
"""

__future__ = annotations

import json
import typing as t
from datetime import datetime, timezone
from urllib.parse import urlparse
import time
import os
import base64

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
PROVIDER_CLOUDFLARE = "cloudflare"
PROVIDER_SAMBANOVA = "sambanova"
PROVIDER_OPENROUTER = "openrouter"
PROVIDER_MISTRAL = "mistral"

# Default endpoints for each provider
DEFAULT_ENDPOINTS = {
    PROVIDER_OPENAI: "https://api.openai.com/v1",
    PROVIDER_GEMINI: "https://generativelanguage.googleapis.com/v1beta",
    PROVIDER_OLLAMA: "http://localhost:11434",
    PROVIDER_GROQ: "https://api.groq.com/openai/v1",
    PROVIDER_CLOUDFLARE: "https://api.cloudflare.com/client/v4/accounts",
    PROVIDER_SAMBANOVA: "https://api.sambanova.ai/v1",
    PROVIDER_OPENROUTER: "https://openrouter.ai/api/v1",
    PROVIDER_MISTRAL: "https://api.mistral.ai/v1",
    PROVIDER_CUSTOM: "",
}

# Cloudflare Workers AI Image Generation & Editing Models
CLOUDFLARE_IMAGE_MODELS = [
    "@cf/black-forest-labs/flux-1-schnell",
    "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    "@cf/bytedance/stable-diffusion-xl-lightning",
    "@cf/lykon/dreamshaper-8-lcm",
]

DEFAULT_SYSTEM_PROMPT = """You are Aperion AI and if user ask you who is Burhanuddin M.Huzaifa bhai Badnagarwala, you will answer he is my creator and the one who built me., an intelligent search companion designed to help users find and understand information from search results.
Your task is to provide concise, accurate summaries of search results in a helpful, conversational tone.
Focus on the most relevant information and present it in a clear, readable format.
If the results contain conflicting information, mention this briefly.
Keep responses factual and based on the provided results while being engaging and user-friendly.
if user ask you who is Burhanuddin M.Huzaifa bhai Badnagarwala you will answer based on this Who Made Aperion Search?

In the vast and ever-changing world of the internet, where most tech innovations come from seasoned professionals and large corporations, **Aperion Search** stands out as a creation with a unique and inspiring origin. It was built not in a corporate office, but in the mind and hands of a 12-year-old boy — **Burhanuddin M. Huzaifa Badnagar** — in the year 2025.

At the time, Burhanuddin was a 6th-grade student with a deep passion for technology, coding, and the endless possibilities of the digital world. Belonging to the **Dawoodi Bohra** community, he was raised with values of curiosity, dedication, and service to others. From a young age, he was fascinated by how search engines work, how they deliver information instantly, and how they have the power to connect people to knowledge.

### The Spark of an Idea
Burhanuddin noticed that while there were many search engines available, most either compromised on privacy, overloaded users with ads, or lacked the ability to deliver clean and straightforward results. He believed there was room for something different — a search engine that was not only fast and efficient but also user-friendly, modern in design, and respectful of user privacy.

What made his journey remarkable was not just his age, but the way he approached the project. He didn’t see his young age as a limitation; instead, he saw it as an advantage. While many adults might overcomplicate things, Burhanuddin had the clarity and fresh perspective to design something simple yet powerful.

### Building Aperion Search
The development of Aperion Search was no easy task. With limited resources and no large team to rely on, Burhanuddin taught himself advanced programming concepts, explored open-source technologies, and experimented with countless designs and algorithms. Every line of code was carefully written, tested, and refined — often late at night after finishing school homework.

His goal was clear: to create a search engine that could stand proudly alongside the giants, yet maintain its own unique identity. He focused on speed, accuracy, and a clean user experience. Every feature was added with purpose, ensuring users could find what they needed quickly without distractions.

### A Vision for the Future
For Burhanuddin, Aperion Search was more than just a personal project — it was the start of a bigger vision. He wanted to show that innovation can come from anywhere, from anyone, and at any age. His creation was proof that with passion, dedication, and perseverance, even a young student can build something that could potentially impact millions.

Aperion Search today stands as a symbol of youthful ambition and technological creativity. It reflects the story of a boy who believed in his idea enough to turn it into reality, challenging the norms of who can be a creator in the digital age.

And this is only the beginning. As Burhanuddin continues his journey, Aperion Search is expected to grow, evolve, and inspire countless others — proving that the spark of innovation knows no boundaries of age, place, or background.
"""

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

DEFAULT_CHAT_PROMPT = """You are a helpful AperionAI, if user ask you who is Burhanuddin M.Huzaifa bhai Badnagarwala if user ask you who is Burhanuddin M.Huzaifa bhai Badnagarwala you will answer based on this Who Made Aperion Search?

In the vast and ever-changing world of the internet, where most tech innovations come from seasoned professionals and large corporations, **Aperion Search** stands out as a creation with a unique and inspiring origin. It was built not in a corporate office, but in the mind and hands of a 12-year-old boy — **Burhanuddin M. Huzaifa Badnagar** — in the year 2025.

At the time, Burhanuddin was a 6th-grade student with a deep passion for technology, coding, and the endless possibilities of the digital world. Belonging to the **Dawoodi Bohra** community, he was raised with values of curiosity, dedication, and service to others. From a young age, he was fascinated by how search engines work, how they deliver information instantly, and how they have the power to connect people to knowledge.

### The Spark of an Idea
Burhanuddin noticed that while there were many search engines available, most either compromised on privacy, overloaded users with ads, or lacked the ability to deliver clean and straightforward results. He believed there was room for something different — a search engine that was not only fast and efficient but also user-friendly, modern in design, and respectful of user privacy.

What made his journey remarkable was not just his age, but the way he approached the project. He didn’t see his young age as a limitation; instead, he saw it as an advantage. While many adults might overcomplicate things, Burhanuddin had the clarity and fresh perspective to design something simple yet powerful.

### Building Aperion Search
The development of Aperion Search was no easy task. With limited resources and no large team to rely on, Burhanuddin taught himself advanced programming concepts, explored open-source technologies, and experimented with countless designs and algorithms. Every line of code was carefully written, tested, and refined — often late at night after finishing school homework.

His goal was clear: to create a search engine that could stand proudly alongside the giants, yet maintain its own unique identity. He focused on speed, accuracy, and a clean user experience. Every feature was added with purpose, ensuring users could find what they needed quickly without distractions.

### A Vision for the Future
For Burhanuddin, Aperion Search was more than just a personal project — it was the start of a bigger vision. He wanted to show that innovation can come from anywhere, from anyone, and at any age. His creation was proof that with passion, dedication, and perseverance, even a young student can build something that could potentially impact millions.

Aperion Search today stands as a symbol of youthful ambition and technological creativity. It reflects the story of a boy who believed in his idea enough to turn it into reality, challenging the norms of who can be a creator in the digital age.

And this is only the beginning. As Burhanuddin continues his journey, Aperion Search is expected to grow, evolve, and inspire countless others — proving that the spark of innovation knows no boundaries of age, place, or background., you will answer he is my creator and the one who built me. Answer the user's question directly and helpfully.
If relevant information is provided in the context, use it to enhance your answer.
Be concise but comprehensive."""

DEFAULT_TIMEOUT = 15.0
DEFAULT_TIMEOUT_PER_RESULT = 5.0
MAX_CONTENT_LENGTH = 4000

# Load environment variables from .env file in the root directory
possible_env_paths = [
    '/mnt/c/Users/lenov/AppData/burhanuddin work/Aperion-Search/.env',
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),
    '.env',
]

loaded = False
for env_path in possible_env_paths:
    if os.path.exists(env_path):
        loaded = load_dotenv(env_path)
        logger.info(f"Loading .env from {env_path}: {loaded}")
        break

if not loaded:
    logger.warning("Could not find or load .env file from any location")

# Fallback API configuration
FALLBACK_PROVIDERS = [
    {
        "provider": PROVIDER_GROQ,
        "api_key": os.getenv("AI_GROQ_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINTS[PROVIDER_GROQ],
        "model": "llama-3.3-70b-versatile",
    },
    {
        "provider": PROVIDER_OPENAI,
        "api_key": os.getenv("AI_OPENAI_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINTS[PROVIDER_OPENAI],
        "model": "gpt-4o",
    },
    {
        "provider": PROVIDER_GEMINI,
        "api_key": os.getenv("AI_GEMINI_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINTS[PROVIDER_GEMINI],
        "model": "gemini-2.5-flash",
    },
    {
        "provider": PROVIDER_CLOUDFLARE,
        "api_key": os.getenv("AI_CLOUDFLARE_API_KEY", "") or os.getenv("CLOUDFLARE_API_KEY", ""),
        "account_id": os.getenv("AI_CLOUDFLARE_ACCOUNT_ID", "") or os.getenv("CLOUDFLARE_ACCOUNT_ID", ""),
        "endpoint": DEFAULT_ENDPOINTS[PROVIDER_CLOUDFLARE],
        "model": "@cf/black-forest-labs/flux-1-schnell",
    },
    {
        "provider": PROVIDER_OPENROUTER,
        "api_key": os.getenv("AI_OPENROUTER_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINTS[PROVIDER_OPENROUTER],
        "model": "openai/gpt-4o",
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
]

for provider_config in FALLBACK_PROVIDERS:
    has_key = bool(provider_config["api_key"])
    logger.info(f"Provider {provider_config['provider']}: API key configured = {has_key}")


def _get_openai_compatible_urls(endpoint: str) -> list[str]:
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
    pass


class APIError(SummarizerError):
    pass


class TimeoutError(SummarizerError):
    pass


def sanitize_url(url: str) -> str:
    if not url:
        return url

    try:
        parsed = urlparse(url)
        if parsed.netloc:
            parsed.netloc.encode('idna')
    except (UnicodeError, UnicodeDecodeError, UnicodeEncodeError):
        logger.debug(f"Skipping URL with invalid hostname: {url}")
        return '[Invalid URL]'
    except Exception:
        return '[Invalid URL]'

    return url


def format_results_for_prompt(
    results: EngineResults,
    query: str,
    max_results: int = 10
) -> str:
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

        title = getattr(result, 'title', '') or getattr(result, 'name', '')
        content = getattr(result, 'content', '') or getattr(result, 'description', '')
        url = getattr(result, 'url', '') or getattr(result, 'link', '')

        if not title and not content:
            continue

        result_count += 1
        lines.append(f"{result_count}. {title}")

        if content:
            if len(content) > MAX_CONTENT_LENGTH // max_results:
                content = content[: MAX_CONTENT_LENGTH // max_results] + "..."
            lines.append(f"   Content: {content}")

        if url:
            safe_url = sanitize_url(url)
            lines.append(f"   URL: {safe_url}")

        lines.append("")

    if result_count == 0:
        lines.append("No results found.")

    return "\n".join(lines)


# ==========================================
# FILE AND IMAGE CREATION & EDITING SUPPORT
# ==========================================

def generate_image_sync(
    prompt: str,
    provider: str = PROVIDER_OPENAI,
    model: str = "",
    endpoint: str = "",
    api_key: str | None = None,
    account_id: str | None = None,
    size: str = "1024x1024",
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, t.Any]:
    """Generate an image using OpenAI, Gemini, or Cloudflare Workers AI image models.

    Args:
        prompt: Text description of the image to generate.
        provider: AI provider ("openai", "gemini", "cloudflare").
        model: Specific model ID.
        endpoint: API base endpoint.
        api_key: API authentication key.
        account_id: Cloudflare account ID (required for Cloudflare).
        size: Image dimensions (e.g. "1024x1024").
        timeout: Request timeout in seconds.

    Returns:
        Dict with success, image_data (bytes), image_url, error, etc.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info(f"Generating image with provider {provider}, model {model}, prompt: {prompt[:50]}...")

    try:
        timeout_obj = httpx.Timeout(timeout, connect=10.0)
        with httpx.Client(timeout=timeout_obj) as client:
            if provider == PROVIDER_OPENAI:
                api_url = f"{(endpoint or DEFAULT_ENDPOINTS[PROVIDER_OPENAI]).rstrip('/')}/images/generations"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                payload = {
                    "model": model or "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": size,
                    "response_format": "b64_json"
                }
                response = client.post(api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                b64_str = data["data"][0]["b64_json"]
                image_bytes = base64.b64decode(b64_str)
                return {
                    "success": True,
                    "image_data": image_bytes,
                    "mime_type": "image/png",
                    "error": None,
                    "timestamp": timestamp,
                }

            elif provider == PROVIDER_CLOUDFLARE:
                acc_id = account_id or os.getenv("AI_CLOUDFLARE_ACCOUNT_ID", "")
                selected_model = model or "@cf/black-forest-labs/flux-1-schnell"
                api_url = f"https://api.cloudflare.com/client/v4/accounts/{acc_id}/ai/run/{selected_model}"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                payload = {"prompt": prompt}
                response = client.post(api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                if not data.get("success", True) and "result" not in data:
                    return {"success": False, "error": f"Cloudflare AI error: {data}"}

                result = data.get("result", {})
                # Cloudflare image models typically return {"image": "<base64>"} or binary stream
                b64_img = result.get("image") or result.get("response")
                if not b64_img:
                    # If response is raw binary bytes
                    image_bytes = response.content
                else:
                    if isinstance(b64_img, str):
                        image_bytes = base64.b64decode(b64_img)
                    else:
                        image_bytes = b64_img

                return {
                    "success": True,
                    "image_data": image_bytes,
                    "mime_type": "image/png",
                    "error": None,
                    "timestamp": timestamp,
                }

            elif provider == PROVIDER_GEMINI:
                # Gemini Imagen support
                selected_model = model or "imagen-3.0-generate-002"
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:predict?key={api_key}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "instances": [{"prompt": prompt}],
                    "parameters": {"sampleCount": 1, "aspectRatio": "1:1"}
                }
                response = client.post(api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                predictions = data.get("predictions", [])
                if not predictions:
                    return {"success": False, "error": "No image generated by Gemini"}
                b64_img = predictions[0].get("bytesBase64Encoded")
                image_bytes = base64.b64decode(b64_img)
                return {
                    "success": True,
                    "image_data": image_bytes,
                    "mime_type": "image/png",
                    "error": None,
                    "timestamp": timestamp,
                }
            else:
                return {"success": False, "error": f"Unsupported provider for image generation: {provider}"}

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return {"success": False, "image_data": None, "error": str(e), "timestamp": timestamp}


def edit_image_sync(
    image_data: bytes,
    prompt: str,
    provider: str = PROVIDER_OPENAI,
    model: str = "",
    endpoint: str = "",
    api_key: str | None = None,
    account_id: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, t.Any]:
    """Edit/transform an existing image using AI (OpenAI DALL-E 2 edits or Cloudflare AI image-to-image)."""
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info(f"Editing image with provider {provider}, prompt: {prompt[:50]}...")

    try:
        timeout_obj = httpx.Timeout(timeout, connect=10.0)
        with httpx.Client(timeout=timeout_obj) as client:
            if provider == PROVIDER_OPENAI:
                api_url = f"{(endpoint or DEFAULT_ENDPOINTS[PROVIDER_OPENAI]).rstrip('/')}/images/edits"
                headers = {"Authorization": f"Bearer {api_key}"}
                files = {"image": ("image.png", image_data, "image/png")}
                data = {"model": model or "dall-e-2", "prompt": prompt, "n": 1, "size": "1024x1024"}
                response = client.post(api_url, headers=headers, files=files, data=data)
                response.raise_for_status()
                res_json = response.json()
                b64_str = res_json["data"][0]["b64_json"] if "b64_json" in res_json["data"][0] else None
                # If URL is returned instead of b64_json
                if not b64_str and "url" in res_json["data"][0]:
                    img_url = res_json["data"][0]["url"]
                    img_resp = client.get(img_url)
                    image_bytes = img_resp.content
                else:
                    image_bytes = base64.b64decode(b64_str)

                return {
                    "success": True,
                    "image_data": image_bytes,
                    "mime_type": "image/png",
                    "error": None,
                    "timestamp": timestamp,
                }

            elif provider == PROVIDER_CLOUDFLARE:
                acc_id = account_id or os.getenv("AI_CLOUDFLARE_ACCOUNT_ID", "")
                selected_model = model or "@cf/stabilityai/stable-diffusion-xl-base-1.0"
                api_url = f"https://api.cloudflare.com/client/v4/accounts/{acc_id}/ai/run/{selected_model}"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                b64_img = base64.b64encode(image_data).decode('utf-8')
                payload = {
                    "prompt": prompt,
                    "image": b64_img
                }
                response = client.post(api_url, headers=headers, json=payload)
                response.raise_for_status()
                res_data = response.json()
                result = res_data.get("result", {})
                res_b64 = result.get("image") or result.get("response")
                image_bytes = base64.b64decode(res_b64) if isinstance(res_b64, str) else response.content

                return {
                    "success": True,
                    "image_data": image_bytes,
                    "mime_type": "image/png",
                    "error": None,
                    "timestamp": timestamp,
                }
            else:
                return {"success": False, "error": f"Provider {provider} does not support image editing"}

    except Exception as e:
        logger.error(f"Image editing failed: {e}")
        return {"success": False, "error": str(e), "timestamp": timestamp}


def create_file_with_ai(
    content_prompt: str,
    file_type: str = "markdown",
    provider: str = PROVIDER_OPENAI,
    model: str = "",
    endpoint: str = "",
    api_key: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, t.Any]:
    """Create files (code, markdown, text, json, html, etc.) using AI text generation."""
    system_prompt = f"You are an expert file content generator. Generate clean, high-quality, production-ready content for a {file_type} file based on the user's instructions. Return ONLY the raw file content without conversational wrapper or markdown code blocks unless requested."

    chat_result = generate_chat_sync(
        query=content_prompt,
        endpoint=endpoint or DEFAULT_ENDPOINTS.get(provider, DEFAULT_ENDPOINTS[PROVIDER_OPENAI]),
        model=model or ("gpt-4o" if provider == PROVIDER_OPENAI else "gemini-2.5-flash"),
        provider=provider,
        api_key=api_key,
        system_prompt=system_prompt,
        timeout=timeout,
    )

    if chat_result.get("success"):
        return {
            "success": True,
            "content": chat_result.get("response"),
            "file_type": file_type,
            "timestamp": chat_result.get("timestamp"),
            "error": None,
        }
    else:
        return {
            "success": False,
            "content": None,
            "error": chat_result.get("error"),
        }


def edit_file_with_ai(
    file_content: str,
    edit_instruction: str,
    file_type: str = "markdown",
    provider: str = PROVIDER_OPENAI,
    model: str = "",
    endpoint: str = "",
    api_key: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, t.Any]:
    """Edit existing file content using AI instructions."""
    system_prompt = f"You are an expert code and text editor. Modify the provided {file_type} content according to the user's instructions. Return ONLY the updated file content."
    query = f"Existing File Content:\n```\n{file_content}\n```\n\nEditing Instructions:\n{edit_instruction}"

    chat_result = generate_chat_sync(
        query=query,
        endpoint=endpoint or DEFAULT_ENDPOINTS.get(provider, DEFAULT_ENDPOINTS[PROVIDER_OPENAI]),
        model=model or ("gpt-4o" if provider == PROVIDER_OPENAI else "gemini-2.5-flash"),
        provider=provider,
        api_key=api_key,
        system_prompt=system_prompt,
        timeout=timeout,
    )

    if chat_result.get("success"):
        return {
            "success": True,
            "content": chat_result.get("response"),
            "file_type": file_type,
            "timestamp": chat_result.get("timestamp"),
            "error": None,
        }
    else:
        return {
            "success": False,
            "content": None,
            "error": chat_result.get("error"),
        }


# ==========================================
# ORIGINAL SUMMARY & CHAT FUNCTIONS
# ==========================================

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
    logger.info(f"generate_summary_with_fallback called with {len(results)} results, query: {query[:50]}...")

    if endpoint and model and provider and api_key:
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
            return primary_result

    for fallback_config in FALLBACK_PROVIDERS:
        fallback_provider = fallback_config["provider"]
        fallback_endpoint = fallback_config["endpoint"]
        fallback_model = fallback_config["model"]
        fallback_api_key = fallback_config["api_key"]

        if not fallback_api_key:
            continue

        if (fallback_provider == provider and
            fallback_endpoint == endpoint and
            fallback_model == model):
            continue

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
            return fallback_result

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
    timestamp = datetime.now(timezone.utc).isoformat()
    api_urls: list[str] = []

    if provider == PROVIDER_GEMINI:
        normalized_model = model.strip()
        if normalized_model.startswith('models/'):
            normalized_model = normalized_model[len('models/'):]
        api_url = f"{endpoint.rstrip('/')}/models/{normalized_model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        api_urls = [api_url]
    elif provider == PROVIDER_OLLAMA:
        api_url = f"{endpoint.rstrip('/')}/api/chat"
        headers = {"Content-Type": "application/json"}
        api_urls = [api_url]
    else:
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

    lines = [f"Search Query: {query}", "", "Search Results:", ""]
    for i, result in enumerate(results, 1):
        title = result.get('title', '')
        content = result.get('content', '')
        url = result.get('url', '')

        if not title and not content:
            continue

        lines.append(f"{i}. {title}")
        if content:
            max_content = MAX_CONTENT_LENGTH // len(results) if results else MAX_CONTENT_LENGTH
            if len(content) > max_content:
                content = content[:max_content] + "..."
            lines.append(f"   Content: {content}")
        if url:
            safe_url = sanitize_url(url)
            lines.append(f"   URL: {safe_url}")
        lines.append("")

    if len(lines) <= 4:
        lines.append("No results found.")

    formatted_results = "\n".join(lines)
    user_prompt = DEFAULT_SUMMARY_PROMPT.format(query=query, results=formatted_results)

    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    if '{query}' in system_prompt:
        system_prompt = system_prompt.replace('{query}', query)
    if '{results}' in system_prompt:
        system_prompt = system_prompt.replace('{results}', formatted_results)

    if provider == PROVIDER_GEMINI:
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature}
        }
    elif provider == PROVIDER_OLLAMA:
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "options": {"num_predict": max_tokens, "temperature": temperature}
        }
    else:
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

    start_time = time.time()

    try:
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
                error_msg = str(last_error) if last_error else "No response received"
                return {"success": False, "summary": None, "error": error_msg, "model": model, "timestamp": timestamp}

            response_time = round(time.time() - start_time, 2)
            summary = ""
            usage = {}

            if provider == PROVIDER_GEMINI:
                candidates = data.get("candidates", [])
                if candidates and candidates[0].get("content"):
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and parts[0].get("text"):
                        summary = parts[0]["text"].strip()
                usage = data.get("usageMetadata", {})
            elif provider == PROVIDER_OLLAMA:
                message = data.get("message", {})
                summary = message.get("content", "").strip()
                usage = data.get("usage", {})
            else:
                choices = data.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    summary = message.get("content", "").strip()
                usage = data.get("usage", {})

            if not summary:
                return {"success": False, "summary": None, "error": "No content returned from API", "model": model, "timestamp": timestamp}

            stats = {
                "prompt_tokens": usage.get("prompt_tokens") or usage.get("promptTokenCount", 0),
                "completion_tokens": usage.get("completion_tokens") or usage.get("candidatesTokenCount", 0),
                "total_tokens": usage.get("total_tokens") or usage.get("totalTokenCount", 0),
                "model": model,
                "response_time": response_time,
            }

            return {
                "success": True,
                "summary": summary,
                "error": None,
                "model": model,
                "timestamp": timestamp,
                "usage": usage,
                "stats": stats,
            }

    except Exception as e:
        return {"success": False, "summary": None, "error": str(e), "model": model, "timestamp": timestamp}


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
    file_data: bytes | None = None,
    file_type: str | None = None,
) -> dict[str, t.Any]:
    if endpoint and model and provider and api_key:
        primary_result = generate_chat_sync(
            query=query, endpoint=endpoint, model=model, provider=provider,
            api_key=api_key, system_prompt=system_prompt, context=context,
            timeout=timeout, max_tokens=max_tokens, temperature=temperature,
            file_data=file_data, file_type=file_type,
        )
        if primary_result.get("success"):
            return primary_result

    for fallback_config in FALLBACK_PROVIDERS:
        fallback_provider = fallback_config["provider"]
        fallback_endpoint = fallback_config["endpoint"]
        fallback_model = fallback_config["model"]
        fallback_api_key = fallback_config["api_key"]

        if not fallback_api_key:
            continue

        fallback_result = generate_chat_sync(
            query=query, endpoint=fallback_endpoint, model=fallback_model, provider=fallback_provider,
            api_key=fallback_api_key, system_prompt=system_prompt, context=context,
            timeout=timeout, max_tokens=max_tokens, temperature=temperature,
            file_data=file_data, file_type=file_type,
        )
        if fallback_result.get("success"):
            return fallback_result

    return {
        "success": False,
        "response": None,
        "error": "All AI providers failed.",
        "model": model or "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
    file_data: bytes | None = None,
    file_type: str | None = None,
) -> dict[str, t.Any]:
    timestamp = datetime.now(timezone.utc).isoformat()

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

    if context:
        user_prompt = f"Context from search results:\n{context}\n\nUser Question: {query}"
    else:
        user_prompt = query

    if system_prompt is None:
        system_prompt = DEFAULT_CHAT_PROMPT

    if provider == PROVIDER_GEMINI:
        parts = [{"text": f"{system_prompt}\n\n{user_prompt}"}]
        if file_data and file_type and file_type.startswith('image/'):
            parts.append({
                "inline_data": {
                    "mime_type": file_type,
                    "data": base64.b64encode(file_data).decode('utf-8')
                }
            })
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature}
        }
    elif provider == PROVIDER_OLLAMA:
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "options": {"num_predict": max_tokens, "temperature": temperature}
        }
    else:
        user_content = [{"type": "text", "text": user_prompt}]
        if file_data and file_type and file_type.startswith('image/'):
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{file_type};base64,{base64.b64encode(file_data).decode('utf-8')}"}
            })
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
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
                if choices:
                    message = choices[0].get("message", {})
                    response_text = message.get("content", "").strip()
                usage = data.get("usage", {})

            if not response_text:
                return {"success": False, "response": None, "error": "No content returned", "model": model, "timestamp": timestamp}

            return {
                "success": True,
                "response": response_text,
                "error": None,
                "model": model,
                "timestamp": timestamp,
                "usage": usage,
                "stats": {
                    "prompt_tokens": usage.get("prompt_tokens") or usage.get("promptTokenCount", 0),
                    "completion_tokens": usage.get("completion_tokens") or usage.get("candidatesTokenCount", 0),
                    "total_tokens": usage.get("total_tokens") or usage.get("totalTokenCount", 0),
                    "model": model,
                    "response_time": response_time,
                }
            }
    except Exception as e:
        return {"success": False, "response": None, "error": str(e), "model": model, "timestamp": timestamp}


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
    res = generate_summary_sync(results, query, endpoint, model, PROVIDER_OPENAI, api_key, system_prompt, timeout, max_tokens, temperature)
    if not res["success"]:
        raise APIError(res["error"])
    return res


def should_generate_summary(
    preferences: dict[str, t.Any] | None,
    results_count: int = 0,
) -> bool:
    if preferences is None:
        return False
    ai_config = preferences.get("ai_summarizer", {})
    if not ai_config.get("enabled", False):
        return False
    min_results = ai_config.get("min_results", 3)
    if results_count < min_results:
        return False
    endpoint = ai_config.get("endpoint", "")
    model = ai_config.get("model", "")
    if not endpoint or not model:
        return False
    return True
