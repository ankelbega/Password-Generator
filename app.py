"""Flask routes for the local password generator application."""

from __future__ import annotations

from typing import Any

from flask import Flask, jsonify, render_template, request

from core.generator import generate_bulk
from core.strength import analyze
from core.wordlist import WORDLIST

app = Flask(__name__)


def _json_object() -> dict[str, Any]:
    """Read a JSON object body or raise a concise validation error."""
    if not request.is_json:
        raise ValueError("Kërkohet përmbajtje JSON.")
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Trupi i kërkesës duhet të jetë objekt JSON.")
    return data


@app.after_request
def add_security_headers(response: Any) -> Any:
    """Apply baseline security headers to every response."""
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; connect-src 'self'; font-src 'self'; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'",
    )
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
    return response


@app.get("/")
def index() -> str:
    """Serve the application's main page."""
    return render_template("index.html")


@app.post("/api/generate")
def api_generate() -> Any:
    """Generate one or more unique passwords using the requested mode."""
    try:
        data = _json_object()
        mode = data.pop("mode", "random")
        count = data.pop("count", 1)
        if not isinstance(mode, str):
            raise ValueError("Parametri 'mode' duhet të jetë tekst.")
        result = generate_bulk(count=count, mode=mode, **data)
        analyses = [analyze(password) for password in result["passwords"]]
        payload: dict[str, Any] = {
            "passwords": result["passwords"],
            "entropy_bits": result["entropy_bits"],
            "analysis": analyses[0] if count == 1 else analyses,
        }
        return jsonify(payload)
    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


@app.post("/api/analyze")
def api_analyze() -> Any:
    """Analyze a password without persisting or logging it."""
    try:
        data = _json_object()
        unknown = set(data) - {"password", "user_inputs"}
        if unknown:
            raise ValueError(f"Fushë e panjohur: {sorted(unknown)[0]}.")
        if "password" not in data:
            raise ValueError("Mungon fusha 'password'.")
        password = data["password"]
        if not isinstance(password, str):
            raise ValueError("Fusha 'password' duhet të jetë tekst.")
        user_inputs = data.get("user_inputs", [])
        if not isinstance(user_inputs, list):
            raise ValueError("Fusha 'user_inputs' duhet të jetë listë tekstesh.")
        return jsonify(analyze(password, user_inputs=user_inputs))
    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


@app.get("/api/wordlist/info")
def api_wordlist_info() -> Any:
    """Return the number of words available to passphrase generation."""
    return jsonify({"word_count": len(WORDLIST)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
