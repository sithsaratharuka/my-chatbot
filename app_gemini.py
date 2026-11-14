import os

from flask import Flask, jsonify, request, send_from_directory
from google import genai
from google.genai import types

# ---------------------------------------------------------------
# SETTINGS: change these to customise your bot
# ---------------------------------------------------------------
BOT_NAME = "SITHASARA THARUKA"
# Model names change often. Check https://aistudio.google.com for the current one.
MODEL = "gemini-3.8-flash"
SYSTEM_PROMPT = """You are a friendly, helpful assistant named Helper.
Keep answers clear and short. Reply in the same language the user writes in
(for example Sinhala, Tamil or English).
If you don't know something, say so honestly instead of guessing."""
# ---------------------------------------------------------------

app = Flask(__name__, static_folder="static")
client = genai.Client()  # reads GEMINI_API_KEY from the environment


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/config")
def config():
    return jsonify({"name": BOT_NAME})


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])

    # Convert our history into Gemini's format ("assistant" is called "model")
    contents = []
    for m in messages[-30:]:
        role, text = m.get("role"), m.get("content")
        if role in ("user", "assistant") and isinstance(text, str) and text.strip():
            contents.append(
                types.Content(
                    role="user" if role == "user" else "model",
                    parts=[types.Part.from_text(text=text)],
                )
            )

    if not contents or contents[-1].role != "user":
        return jsonify({"error": "Send a message first."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1000,
            ),
        )
        return jsonify({"reply": response.text or "(No reply. Try rephrasing.)"})
    except Exception as e:  # keep it simple: show the error to the user
        return jsonify({"error": f"API error: {e}"}), 500


if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("Set the GEMINI_API_KEY environment variable first.")
    app.run(host="127.0.0.1", port=5000, debug=True)
