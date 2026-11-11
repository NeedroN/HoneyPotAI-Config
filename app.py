"""
Small web panel for the bot: a chat page for testing prompts and a
/health endpoint for the uptime monitor. Run with: python app.py
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request
from openai import OpenAI


load_dotenv()

app = Flask(__name__)
ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
PORT = int(os.getenv("PORT", "5000"))


# Tiny test page, no build step needed.
PAGE = """
<!doctype html>
<title>chat bot panel</title>
<style>
  body { font-family: system-ui; max-width: 640px; margin: 40px auto; }
  #log div { margin: 6px 0; }
  input { width: 80%; padding: 6px; }
</style>

<h2>Test the bot</h2>
<div id="log"></div>
<form id="f"><input id="q" placeholder="Say something..."> <button>Send</button></form>

<script>
  f.onsubmit = async (e) => {
    e.preventDefault();
    const text = q.value;
    q.value = "";
    log.innerHTML += "<div><b>you:</b> " + text + "</div>";

    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await r.json();
    log.innerHTML += "<div><b>bot:</b> " + (data.reply || data.error) + "</div>";
  };
</script>
"""


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.get("/health")
def health():
    return jsonify(ok=True, model=MODEL)


@app.post("/api/chat")
def chat():
    """
    One message in, one reply out. No memory here, it's just for testing prompts.
    """

    message = (request.get_json(silent=True) or {}).get("message", "").strip()

    if not message:
        return jsonify(error="empty message"), 400

    try:
        response = ai.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": message}],
            max_tokens=400,
        )
    except Exception as error:
        return jsonify(error=str(error)), 502

    return jsonify(reply=response.choices[0].message.content.strip())


if __name__ == "__main__":
    # TODO: put this behind the admin login before deploying
    app.run(host="0.0.0.0", port=PORT, debug=True)
