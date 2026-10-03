from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)

API_KEY = os.getenv("AI_API_KEY")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_blog():
    data = request.get_json()
    topic = data.get("topic", "").strip()

    if not topic:
        return jsonify({"error": "Please enter a blog topic"}), 400

    if not API_KEY:
        return jsonify({"error": "AI API key is not configured"}), 500

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    prompt = f"""
Write a simple and informative blog about:

{topic}

Include:
1. Title
2. Introduction
3. Main Points
4. Conclusion

Use simple English.
Make the blog clear and easy to understand.
"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            url, headers=headers, json=payload, timeout=60
        )
        result = response.json()

        if response.status_code != 200:
            return jsonify({
                "error": result.get("error", {}).get(
                    "message", "AI API error"
                )
            }), response.status_code

        blog = result["choices"][0]["message"]["content"]
        return jsonify({"blog": blog})

    except requests.exceptions.RequestException:
        return jsonify({"error": "Unable to connect to AI service."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
