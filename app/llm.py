"""Minimal Ollama helper — calls the local LLM."""

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"  # change if you pulled a different model


def ask_ollama(system_prompt: str, conversation_history: list) -> str:
    """Send a prompt with conversation history to Ollama and return the response text.
    
    conversation_history is a list of dicts with 'role' and 'content' keys.
    """
    messages = [
        {"role": "system", "content": system_prompt}
    ] + conversation_history
    
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]