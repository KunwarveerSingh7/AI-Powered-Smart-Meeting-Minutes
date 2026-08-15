

"""
ai_service.py
Handles all communication with the locally-hosted Ollama / Llama 3 model.

Key design decisions:
  - temperature=0.1  →  factual extraction, minimal creativity
  - Explicit "DO NOT invent" rules in the system prompt
  - _parse_response() enforces null fields independently of the model
  - manager_review_required=True on any item with a missing assignee or deadline
  - Falls back to Mistral if Llama 3 is unavailable
"""

import json
import re

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_URL      = "http://localhost:11434/api/generate"
PRIMARY_MODEL   = "llama3"
FALLBACK_MODEL  = "mistral"
TIMEOUT_SECONDS = 120

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a meeting minutes analyst. Extract structured information \
from the meeting text provided.

STRICT RULES — follow every rule exactly:
1. DO NOT invent, guess or infer deadlines, dates, names or any other detail \
that is not explicitly written in the meeting text.
2. If a deadline is not stated word-for-word, set "deadline" to null.
3. If an assignee is not named explicitly, set "assignee" to null.
4. If a priority is not mentioned, set "priority" to "medium".
5. Return ONLY a valid JSON object. No explanation. No markdown fences. \
No extra text before or after the JSON.

REQUIRED OUTPUT FORMAT (use exactly these keys):
{
  "summary": "2 to 4 sentence factual summary of what was discussed and decided.",
  "decisions": [
    "Decision text exactly as stated in the meeting."
  ],
  "action_items": [
    {
      "task": "Clear description of the task.",
      "assignee": "Full name as written in the text, or null",
      "deadline": "YYYY-MM-DD if a date was stated, otherwise null",
      "priority": "high, medium, or low",
      "notes": "Any extra context about this task, or null"
    }
  ],
  "flags": [
    "Any ambiguity, missing information or item needing manager attention."
  ]
}"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyse_meeting(meeting_text: str, model: str = PRIMARY_MODEL) -> dict:
    """
    Send extracted meeting text to Ollama and return a structured dict.

    The returned dict always contains:
        summary        str
        decisions      list[str]
        action_items   list[dict]  — each item has manager_review_required added
        flags          list[str]

    Raises RuntimeError if Ollama is unreachable on both models.
    Raises ValueError if the model returns non-JSON output.
    """
    prompt = f"{SYSTEM_PROMPT}\n\nMEETING TEXT:\n{meeting_text}\n\nJSON:"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": 2048,
        },
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        raw = response.json().get("response", "")
        return _parse_response(raw)

    except requests.exceptions.ConnectionError:
        if model != FALLBACK_MODEL:
            # Primary model not available — try Mistral
            return analyse_meeting(meeting_text, model=FALLBACK_MODEL)
        raise RuntimeError(
            "Ollama is not running. Start it with: ollama serve"
        )

    except requests.exceptions.Timeout:
        raise RuntimeError(
            f"Ollama timed out after {TIMEOUT_SECONDS}s. "
            "Try a smaller model (e.g. mistral) or increase TIMEOUT_SECONDS."
        )


def check_ollama_running() -> bool:
    """Return True if Ollama is reachable on localhost:11434."""
    try:
        r = requests.get("http://localhost:11434", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def list_models() -> list[str]:
    """Return the names of all models currently pulled in Ollama."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_response(raw_text: str) -> dict:
    """
    Extract, validate and normalise the JSON from the model's raw output.

    Steps:
      1. Strip any markdown fences the model may have added.
      2. Find the first {...} block.
      3. Parse as JSON.
      4. Enforce required keys with safe defaults.
      5. Add manager_review_required to every action item.
    """
    # Strip markdown fences (```json ... ``` or ``` ... ```)
    cleaned = re.sub(r"```(?:json)?", "", raw_text).strip()

    # Find the outermost JSON object
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(
            "The AI model returned non-JSON output. "
            f"Raw response was:\n{raw_text[:500]}"
        )

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON parsing failed: {exc}. "
            f"Raw text:\n{match.group()[:500]}"
        ) from exc

    # Ensure required top-level keys exist
    data.setdefault("summary", "No summary was extracted.")
    data.setdefault("decisions", [])
    data.setdefault("action_items", [])
    data.setdefault("flags", [])

    # Normalise and annotate each action item
    normalised_items = []
    for item in data["action_items"]:
        item.setdefault("task", "Unnamed task")
        item.setdefault("assignee", None)
        item.setdefault("deadline", None)
        item.setdefault("priority", "medium")
        item.setdefault("notes", None)

        # Null strings → Python None
        if isinstance(item["assignee"], str) and item["assignee"].lower() in ("null", "none", ""):
            item["assignee"] = None
        if isinstance(item["deadline"], str) and item["deadline"].lower() in ("null", "none", ""):
            item["deadline"] = None

        # Validate priority value
        if item["priority"] not in ("high", "medium", "low"):
            item["priority"] = "medium"

        # Flag for manager review if any key field is missing
        item["manager_review_required"] = (
            item["assignee"] is None or item["deadline"] is None
        )

        # Add a flag entry so it surfaces in the manager dashboard
        if item["manager_review_required"]:
            missing = []
            if item["assignee"] is None:
                missing.append("assignee")
            if item["deadline"] is None:
                missing.append("deadline")
            flag_msg = (
                f"Task '{item['task'][:60]}' is missing: "
                + ", ".join(missing)
                + " — manager review required."
            )
            if flag_msg not in data["flags"]:
                data["flags"].append(flag_msg)

        normalised_items.append(item)

    data["action_items"] = normalised_items
    return data
