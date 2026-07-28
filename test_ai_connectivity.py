import os
import httpx
from dotenv import load_dotenv

# Load .env
load_dotenv('/mnt/c/Users/lenov/AppData/burhanuddin work/Aperion-Search/.env')

providers = [
    {"name": "Groq", "url": "https://api.groq.com/openai/v1/models", "key": os.getenv("AI_GROQ_API_KEY")},
    {"name": "OpenRouter", "url": "https://openrouter.ai/api/v1/models", "key": os.getenv("AI_OPENROUTER_API_KEY")},
    {"name": "Gemini", "url": "https://generativelanguage.googleapis.com/v1beta/models", "key": os.getenv("AI_GEMINI_API_KEY")},
    {"name": "Sambanova", "url": "https://api.sambanova.ai/v1/models", "key": os.getenv("AI_SAMBANOVA_API_KEY")},
    {"name": "Mistral", "url": "https://api.mistral.ai/v1/models", "key": os.getenv("AI_MISTRAL_API_KEY")},
    {"name": "OpenAI", "url": "https://api.openai.com/v1/models", "key": os.getenv("AI_OPENAI_API_KEY")},
]

print("Testing AI provider connectivity...\n")

for provider in providers:
    print(f"Testing {provider['name']}...")
    try:
        with httpx.Client(timeout=10.0) as client:
            if provider['name'] == "Gemini":
                # Gemini needs API key in URL
                url = f"{provider['url']}?key={provider['key']}"
            else:
                url = provider['url']
                headers = {}
                if provider['key']:
                    headers['Authorization'] = f'Bearer {provider['key']}'
            
            response = client.get(url, headers=headers if provider['key'] and provider['name'] != 'Gemini' else None)
            print(f"  ✓ {provider['name']}: Status {response.status_code}")
    except Exception as e:
        print(f"  ✗ {provider['name']}: {e}")

print("\nDone.")
