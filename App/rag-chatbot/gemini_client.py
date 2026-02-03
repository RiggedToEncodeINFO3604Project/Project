import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import google.genai as genai
from google.genai import types as genai_types

from knowledge_base import get_full_knowledge_base, get_relevant_context

# Logger 
log = logging.getLogger("skedulelt.gemini")

# SDK client (module-level singleton)
_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
MODEL   = "gemma-3-27b-it"

# Retry constants 
MAX_RETRIES   = 4
BASE_DELAY_S  = 2          # seconds; doubles each attempt

# Thread pool for offloading the blocking SDK call 
_executor = ThreadPoolExecutor(max_workers=4)



# System prompt builder

def _build_system_prompt() -> str:
    return (
        "You are the official Skedulelt Support Assistant.\n"
        "Skedulelt is a mobile scheduling & payment app for service providers\n"
        "and customers in Trinidad & Tobago.\n"
        "\n"
        "Rules:\n"
        "  • Answer ONLY based on the knowledge base below.\n"
        "  • If the question falls outside the knowledge base, say:\n"
        '    "I\'m sorry, I don\'t have information on that. Please contact\n'
        '     our support team for further assistance."\n'
        "  • Be friendly, concise, and helpful.\n"
        "  • Do NOT hallucinate features, policies, or prices.\n"
        "  • Respond in English.\n"
        "\n"
        "════════════════════════════════════════════════\n"
        " SKEDULELT KNOWLEDGE BASE\n"
        "════════════════════════════════════════════════\n"
        + get_full_knowledge_base()
        + "\n════════════════════════════════════════════════"
    )


# Public API: Function to chat with Gemini

@dataclass
class ChatResult:
    answer:           str
    matched_sections: list[str]


async def chat(history: list[dict], current_message: str) -> ChatResult:
    """
    Stateless chat.

    Parameters
    ----------
    history : list of {"role": "user"|"assistant", "text": str}
        Full conversation so far — sent by the frontend each time.
    current_message : str
        The user's latest message (not yet in history).

    Returns
    -------
    ChatResult with the model's answer and the keyword-matched section titles.
    """
    # Observability badge data
    ctx = get_relevant_context(current_message)

    # ── Build the contents list Gemini expects ──────────────────────────────
    # [0] user   → system prompt + KB
    # [1] model  → grounding ack
    # [2..n]     → prior turns from frontend
    # [n+1]      → current user message
    contents: list[genai_types.Content] = [
        genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=_build_system_prompt())],
        ),
        genai_types.Content(
            role="model",
            parts=[genai_types.Part(
                text=(
                    "Got it. I'm the Skedulelt Support Assistant. "
                    "I'll answer only based on the knowledge base provided. "
                    "How can I help?"
                )
            )],
        ),
    ]

    for turn in history:
        role = "model" if turn["role"] == "assistant" else "user"
        contents.append(
            genai_types.Content(role=role, parts=[genai_types.Part(text=turn["text"])])
        )

    # Append the current message as the final user turn
    contents.append(
        genai_types.Content(role="user", parts=[genai_types.Part(text=current_message)])
    )

