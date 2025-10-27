from flask import Flask, render_template, request
import requests
import hashlib

app = Flask(__name__)

# Leak-Lookup API
LEAK_LOOKUP_API_KEY = "c54c5a0636a99ab6d286b8faeae89f92"
LEAK_LOOKUP_URL = "https://leak-lookup.com/api/search"

# HIBP API (no key needed)
HIBP_API_URL = "https://api.pwnedpasswords.com/range/"


def check_email_or_username(query):
    """Check if email or username is breached using Leak-Lookup."""
    payload = {
        "key": LEAK_LOOKUP_API_KEY,
        "type": "email" if "@" in query else "username",
        "query": query
    }

    response = requests.post(LEAK_LOOKUP_URL, data=payload)
    data = response.json()

    if data.get("error") == "false" and data.get("message"):
        return data["message"], None
    elif data.get("error") == "false" and not data.get("message"):
        return None, "No breaches found ✅"
    else:
        return None, data.get("message", "An error occurred while checking.")


def check_password(password):
    """Check password breaches using Have I Been Pwned (HIBP)."""
    sha1_password = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1_password[:5]
    suffix = sha1_password[5:]

    response = requests.get(HIBP_API_URL + prefix)
    hashes = (line.split(":") for line in response.text.splitlines())

    for h, count in hashes:
        if h == suffix:
            return f"⚠️ This password has been found {count} times in breaches!"
    return "✅ This password is safe (not found in any breaches)."


@app.route("/", methods=["GET", "POST"])
def index():
    email_result = None
    password_result = None
    breaches = []
    error_message = None

    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "email_check":
            query = request.form["query"].strip()
            breaches, error_message = check_email_or_username(query)

        elif form_type == "password_check":
            password = request.form["password"].strip()
            password_result = check_password(password)

    return render_template(
        "index.html",
        email_result=email_result,
        password_result=password_result,
        breaches=breaches,
        error_message=error_message
    )


if __name__ == "_main_":
    app.run(debug=True)
