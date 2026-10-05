# utils.py — Helper functions for the AI Math Tutor
#
# This file has one job: talk to the Gemini API.
# app.py calls functions from here — it never touches the API directly.
#
# WHY SEPARATE?
#   If Google changes the Gemini API tomorrow, we only edit THIS file.
#   app.py does not need to change at all. This is called "separation of concerns".
#
# NOTE ON PACKAGE:
#   We use the NEW 'google-genai' package (not the old 'google-generativeai').
#   The old one is deprecated (officially discontinued by Google).
#   The new one is: from google import genai

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv


# ─────────────────────────────────────────────
# MODEL NAME — change here if Google releases a newer model
# ─────────────────────────────────────────────
# gemini-flash-lite-latest: lightweight, fast, always-on Flash model.
# Using 'latest' alias means we don't need to update this when Google
# releases a new version — it automatically uses the newest one.
# The 'lite' variant is more stable under high demand and free-tier friendly.
GEMINI_MODEL = "gemini-flash-lite-latest"


# ─────────────────────────────────────────────
# 1. LOAD THE API KEY
# ─────────────────────────────────────────────

def load_api_key() -> str:
    """
    Reads the Gemini API key from the environment.

    HOW IT WORKS:
      - Locally: reads from the .env file (via python-dotenv).
      - On Streamlit Cloud: reads from st.secrets (we set this in the
        Streamlit dashboard — it never touches our code or git).

    RETURNS:
      The API key string if found.

    RAISES:
      ValueError if the key is missing, so the app shows a clear error
      instead of crashing with a confusing message.
    """
    # Try loading from .env file (only matters when running locally)
    load_dotenv()

    # Check Streamlit secrets first (used in production on Streamlit Cloud)
    # We do this with a try/except because st.secrets only exists when
    # running inside Streamlit — it would error if we called it in run_tests.py
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY", None)
        if api_key:
            return api_key
    except Exception:
        pass  # Not running inside Streamlit — that's fine

    # Fall back to environment variable (set by .env file locally)
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key not found!\n"
            "Locally: create a .env file with GEMINI_API_KEY=your_key\n"
            "On Streamlit Cloud: add it in App Settings → Secrets"
        )

    return api_key


# ─────────────────────────────────────────────
# 2. SEND A MESSAGE AND GET A REPLY
# ─────────────────────────────────────────────

def get_gemini_response(
    api_key: str,
    system_prompt: str,
    chat_history: list,
    user_message: str,
) -> str:
    """
    Sends the student's message to Gemini and returns the tutor's reply.

    PARAMETERS:
      api_key       — The Gemini API key (loaded by load_api_key above).
      system_prompt — The tutor's rules (from tutor_prompt.py). Sent every time
                      so the model never "forgets" how to behave.
      chat_history  — List of past messages in Gemini format:
                      [{"role": "user"/"model", "parts": [{"text": "..."}]}]
                      This gives the AI memory of the conversation so far.
      user_message  — What the student just typed.

    RETURNS:
      The tutor's response as a plain string.
      On any error, returns a friendly message instead of crashing.

    HOW GEMINI MULTI-TURN CHAT WORKS:
      We build a list of Content objects (past messages) and send them along
      with the new message. Gemini sees the full conversation history and replies.
    """
    try:
        # Create the Gemini client with our API key
        client = genai.Client(api_key=api_key)

        # Convert our stored history into Gemini's Content format
        # Each item in chat_history looks like:
        #   {"role": "user" or "model", "parts": ["message text"]}
        contents = []
        for msg in chat_history:
            contents.append(
                types.Content(
                    role=msg["role"],
                    parts=[types.Part(text=msg["parts"][0])]
                )
            )

        # Add the new student message at the end
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=user_message)]
            )
        )

        # Send to Gemini with the system prompt (tutor behavior rules)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,   # Slightly creative but still consistent
                max_output_tokens=1024,  # Enough for a helpful hint, not too long
            ),
        )

        # Extract the text from the response.
        # Some Gemini models ("thinking" models) return multiple parts:
        # one "thought" part (internal reasoning) and one text part.
        # response.text returns None if there are mixed parts, so we
        # manually collect only the non-thought text parts.
        text_parts = []
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if not part.thought and part.text:
                    text_parts.append(part.text)

        if text_parts:
            return "\n".join(text_parts)

        # Fallback: if the above somehow fails, try response.text directly
        if response.text:
            return response.text

        return "⚠️ The tutor didn't generate a response. Please try again."

    except Exception as e:
        # Catch ANY error (network issue, invalid key, quota exceeded, etc.)
        # and return a friendly message instead of showing a scary Python traceback
        error_msg = str(e).lower()

        if "api_key" in error_msg or "invalid" in error_msg or "401" in error_msg:
            return (
                "⚠️ There seems to be a problem with the API key. "
                "Please check that your GEMINI_API_KEY is set correctly."
            )
        elif "quota" in error_msg or "limit" in error_msg or "429" in error_msg:
            return (
                "⚠️ We've hit the API usage limit for now. "
                "Please wait a minute and try again!"
            )
        elif "404" in error_msg:
            return (
                "⚠️ Could not reach the AI model. "
                "Please check your internet connection and try again."
            )
        else:
            return (
                "⚠️ Something went wrong while contacting the AI tutor. "
                "Please check your internet connection and try again. "
                f"(Error: {str(e)[:120]})"
            )


# ─────────────────────────────────────────────
# 3. GENERATE PARENT SUMMARY
# ─────────────────────────────────────────────

def generate_parent_summary(
    api_key: str,
    system_prompt: str,
    chat_history: list,
) -> str:
    """
    Generates a short, parent-friendly summary of the tutoring session.

    We do this by adding a special instruction at the end of the conversation,
    asking the tutor to summarize what happened. The tutor already knows how
    to write a parent summary because of Rule 10 in the system prompt.

    RETURNS:
      A 3–5 sentence summary paragraph, or an error message.
    """
    if not chat_history:
        return "No conversation yet! Start chatting with the tutor first."

    # We ask the AI to summarize using a special request message
    summary_request = (
        "Please generate a parent summary of this tutoring session "
        "following Rule 10 from your instructions."
    )

    return get_gemini_response(
        api_key=api_key,
        system_prompt=system_prompt,
        chat_history=chat_history,
        user_message=summary_request,
    )


# ─────────────────────────────────────────────
# 4. SCAN PROBLEM FROM IMAGE (Gemini Vision)
# ─────────────────────────────────────────────

def extract_math_from_image(
    api_key: str,
    image_bytes: bytes,
    mime_type: str,
) -> str:
    """
    Uses Gemini Vision to read a math problem from an uploaded image.

    HOW IT WORKS:
      Gemini is multimodal — it understands both text AND images in the
      same request. We send the image alongside a prompt asking it to
      extract only the math question text. That text is then treated as
      a normal student question by the tutor.

    PARAMETERS:
      api_key     — The Gemini API key.
      image_bytes — Raw bytes of the uploaded image file.
      mime_type   — MIME type e.g. "image/jpeg", "image/png".

    RETURNS:
      The extracted math problem as a plain text string, or a friendly
      error message on failure.
    """
    try:
        client = genai.Client(api_key=api_key)

        # Build a multimodal Content object with two parts:
        #   Part 1 — the image (inline_data / Blob)
        #   Part 2 — text instruction: what to do with the image
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=mime_type,
                                data=image_bytes,
                            )
                        ),
                        types.Part(text=(
                            "Look at this image carefully. "
                            "Extract the math problem, question, or equation shown in it. "
                            "Write it out as plain text exactly as it appears — "
                            "preserve all numbers, symbols, fractions, and words. "
                            "Output ONLY the math problem text, nothing else. "
                            "If you cannot find any math problem in the image, "
                            "respond with exactly: 'No math problem found in image.'"
                        )),
                    ],
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,       # Very low — precise extraction, not creative
                max_output_tokens=256,
            ),
        )

        # Extract text parts (handles thinking models too)
        text_parts = []
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if not part.thought and part.text:
                    text_parts.append(part.text)

        result = "\n".join(text_parts).strip() if text_parts else ""
        if not result:
            try:
                result = response.text or ""
            except Exception:
                pass

        if not result:
            return "Could not extract text from the image. Please try a clearer photo."

        return result

    except Exception as e:
        err = str(e).lower()
        if "429" in err or "quota" in err:
            return "API limit reached. Please wait a moment and try again."
        elif "image" in err or "media" in err or "mime" in err:
            return "Could not process this image format. Please try a JPG or PNG photo."
        else:
            return f"Image reading failed: {str(e)[:120]}"
