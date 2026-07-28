import os
from dotenv import load_dotenv

# Try loading from WSL path
load_dotenv('/mnt/c/Users/lenov/AppData/burhanuddin work/Aperion-Search/.env')

print("Testing API key loading:")
print(f"Groq key: {bool(os.getenv('AI_GROQ_API_KEY'))}")
print(f"OpenRouter key: {bool(os.getenv('AI_OPENROUTER_API_KEY'))}")
print(f"Gemini key: {bool(os.getenv('AI_GEMINI_API_KEY'))}")
print(f"Sambanova key: {bool(os.getenv('AI_SAMBANOVA_API_KEY'))}")
print(f"Mistral key: {bool(os.getenv('AI_MISTRAL_API_KEY'))}")
print(f"OpenAI key: {bool(os.getenv('AI_OPENAI_API_KEY'))}")
