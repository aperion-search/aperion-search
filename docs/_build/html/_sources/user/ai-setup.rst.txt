=====================================
AI Summarization Setup Guide (FREE)
=====================================

This guide shows how to set up **free** AI summarization without paying for API keys.

**Option 1: Free Local AI with Ollama (Recommended)**
=======================================================

`Ollama <https://ollama.ai>`_ provides free, unlimited local AI models with no account needed.

**Installation:**

1. Download and install Ollama from https://ollama.ai
2. Start the Ollama service (it runs on ``localhost:11434`` by default)
3. Download a free model::

    ollama pull mistral          # Fast, good quality (7B)
    ollama pull neural-chat      # General purpose (7B)
    ollama pull llama2           # Powerful (7B/13B/70B)

**Configure in Aperion:**

1. Go to **Preferences** → **AI**
2. Set:
   - **AI Provider:** ``Ollama``
   - **AI API Endpoint:** ``http://localhost:11434``
   - **AI Model:** ``mistral`` (or the model you downloaded)
   - **AI API Key:** (leave empty)
3. Enable **AI Summarization**

**That's it!** You now have unlimited free AI summaries.

**Option 2: Free Online Services**
===================================

**HuggingFace Inference API (Free Tier)**
------------------------------------------

1. Sign up at https://huggingface.co (free account)
2. Get your API token from https://huggingface.co/settings/tokens
3. In Aperion Preferences:
   - **AI Provider:** ``Custom OpenAI-compatible``
   - **AI API Endpoint:** ``https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta``
   - **AI API Key:** Your HuggingFace token

(Note: Free tier has rate limits)

**Option 3: Free Self-Hosted (Advanced)**
===========================================

Use any OpenAI-compatible LLM running locally or on a VPS:

- **vLLM:** Run any Hugging Face model with OpenAI-compatible API
- **LocalAI:** Local inference server
- **Text Generation WebUI:** User-friendly local UI

Then point Aperion to your endpoint using the **Custom OpenAI-compatible** provider.

**Performance Tips**
====================

- **Ollama on CPU:** Use smaller models like ``mistral`` or ``neural-chat`` (7B)
- **Ollama on GPU:** You can use larger models like ``llama2:13b`` or ``mistral:large``
- **Better answers:** Larger models give better quality (7B < 13B < 70B)
- **Speed:** Smaller models summarize faster

**Model Recommendations**
==========================

+-------------------+--------+------------------------------+
| Model             | Size   | Notes                        |
+===================+========+==============================+
| mistral           | 7B     | **Best balance** (fast, good)|
+-------------------+--------+------------------------------+
| neural-chat       | 7B     | Good for conversations      |
+-------------------+--------+------------------------------+
| llama2            | 7B-70B | Powerful, slower            |
+-------------------+--------+------------------------------+
| dolphin-mixtral   | 47B    | Very good quality (GPU only)|
+-------------------+--------+------------------------------+

**Troubleshooting**
===================

**"AI summarizer is not configured"**
    Check that all three are set:
    - AI Provider (e.g., ``Ollama``)
    - AI API Endpoint (e.g., ``http://localhost:11434``)
    - AI Model (e.g., ``mistral``)

**Ollama connection refused**
    Make sure Ollama is running::

        ollama serve

**Slow responses**
    Use a smaller model or enable GPU acceleration in Ollama.

**No response after "Thinking..."**
    The model may be processing a large summary. Try a shorter query or restart the model.

**Getting Started Now**
=======================

1. Install Ollama: https://ollama.ai/download
2. Download a model: ``ollama pull mistral``
3. Configure in Aperion Preferences
4. Search and enjoy free AI summaries!
