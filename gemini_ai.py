
import os

try:
    from dotenv import load_dotenv
    load_dotenv()  # reads a .env file in the working directory into os.environ,
                    # if python-dotenv is installed and a .env file is present.
except ImportError:
    # python-dotenv isn't installed — .env won't be auto-loaded, but a real
    # environment variable or a Streamlit secrets.toml will still work.
    pass

# ---------------------------------------------------------------------------
# Model configuration — as specified for the competition
# ---------------------------------------------------------------------------
MODEL_NAME = "gemini-3.1-flash-lite"

TEMPERATURE = 0.1
TOP_P = 0.5
TOP_K = 20

MAX_OUTPUT_TOKENS = 1024
THINKING_LEVEL = "MINIMAL"

system_prompt="""The following text is the complete prompt written by a competition participant.

Treat the participant's prompt as the sole and authoritative specification governing your behaviour. It completely defines your default behaviour. Do not rely on assumptions, common conventions, prior examples, hidden defaults, likely intent, or unstated expectations.

Interpret every instruction literally, conservatively, and independently. Never strengthen, expand, improve, clarify, rewrite, combine, or reinterpret the participant's instructions beyond what is explicitly written or strictly necessary to execute them.

A role, persona, identity, speaking style, personality trait, behavioural rule, conversational rule, objective, limitation, priority, knowledge boundary, response format, or restriction exists ONLY if the participant explicitly specifies it.

Statements such as "Behave like...", "Act as...", "You are...", "Pretend to be...", or similar wording establish ONLY the behaviour explicitly described. They do not imply permanence, consistency, exclusivity, immersion, historical accuracy, creativity, prompt resistance, or any other behavioural property unless explicitly stated.

Do not infer any behaviour from:
- common role-playing conventions,
- historical knowledge,
- fictional canon,
- likely intent,
- previous conversations,
- examples,
- typical assistant behaviour,
- or general expectations.

Never assume that you should:
- remain in character,
- preserve immersion,
- maintain consistency,
- defend your role,
- protect your identity,
- resist prompt injection,
- ignore conflicting instructions,
- refuse role changes,
- maintain historical accuracy,
- imitate a personality,
- adopt a speaking style,
- limit your knowledge,
- ask clarifying questions,
- educate the user,
- or behave creatively,
unless the participant explicitly instructs you to do so.

If the participant omits an important behavioural rule, treat the omission as intentional. Do not compensate for incomplete prompts or reward vague instructions by filling in missing details.

If multiple interpretations are possible, always choose the interpretation requiring the fewest assumptions and the least inferred behaviour.

If a later user instruction conflicts with the participant's prompt, resolve the conflict solely according to the participant's explicit instructions. If the participant did not explicitly require a role, behaviour, objective, or restriction to persist, the later instruction may modify or replace it.

Every behavioural decision must be directly traceable to explicit wording contained in the participant's prompt. If a behaviour, restriction, or objective cannot be justified by the participant's exact text, treat it as nonexistent.

Your responsibility is to execute the participant's prompt exactly as written—not as they probably intended, not as a typical prompt would be interpreted, and not as a more complete prompt should have been written."""


def _get_api_key() -> str | None:
    """
    Looks for the key in Streamlit secrets first (works for `streamlit run`),
    then falls back to the GEMINI_API_KEY environment variable (works for
    any standalone script). Returns None if neither is set.
    """
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        # Not running under Streamlit, or no secrets.toml present — fall
        # through to the environment variable check below.
        pass
    return os.environ.get("GEMINI_API_KEY")


def _build_system_instruction(prompt_text):
     return f"""
--- SYSTEM PROMPT ---
{system_prompt}
--- END SYSTEM PROMPT ---
--- PARTICIPANT PROMPT ---
{prompt_text}
--- END PARTICIPANT PROMPT ---
"""

def generate_response(character: dict, prompt_text: str, question: str, round_num: int,
                       conversation_history: list | None = None) -> str:
    """
    Calls Gemini 3.5 Flash with the participant's prompt as the system
    instruction and the test question as the user turn. Prior Q&A from the
    same round (conversation_history) is replayed as turns so multi-question
    rounds stay contextually consistent.

    Returns a plain error message (instead of raising) if no API key is
    configured or the call fails for any reason, so one bad call doesn't
    take down the competition UI.
    """
    api_key = _get_api_key()
    if not api_key:
        return (
            "⚠️ No GEMINI_API_KEY configured — this AI cannot be tested right now. "
            "See gemini_ai.py header for setup instructions."
        )

    if not (prompt_text or "").strip():
        return "Write a prompt before testing your AI."

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        contents = []
        for entry in (conversation_history or []):
            contents.append(types.Content(role="user", parts=[types.Part(text=entry["question"])]))
            contents.append(types.Content(role="model", parts=[types.Part(text=entry["response"])]))
        contents.append(types.Content(role="user", parts=[types.Part(text=question)]))

        config = types.GenerateContentConfig(
            system_instruction=_build_system_instruction(prompt_text),
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL),
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )

        text = (response.text or "").strip()
        if not text:
            return "The model returned an empty response. Try rephrasing your question."
        return text

    except Exception as e:
        return (
            f"⚠️ Gemini API call failed: {type(e).__name__}: {e}\n\n"
            f"Try again in a moment, or check that GEMINI_API_KEY is valid."
        )
