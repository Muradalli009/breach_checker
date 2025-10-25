from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = "c54c5a0636a99ab6d286b8faeae89f92"
API_URL = "https://leak-lookup.com/api/search"


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    breaches = []
    error_message = None

    if request.method == "POST":
        query = request.form["query"]

        payload = {
            "key": API_KEY,
            "type": "email",  # You can change to "username" or "domain"
            "query": query
        }

        response = requests.post(API_URL, data=payload)

        try:
            data = response.json()
            if data.get("error") == "false" and data.get("message"):
                breaches = data["message"]
            elif data.get("error") == "false" and not data.get("message"):
                result = "No breaches found ✅"
            else:
                error_message = data.get("message", "An error occurred.")
        except Exception:
            error_message = "Invalid API response."

    return render_template(
        "index.html",
        result=result,
        breaches=breaches,
        error_message=error_message
    )


if __name__ == "_main_":
    app.run(debug=True)
