"""Flask API tests: request validation, response headers and core integration."""

import pytest

from app import app


@pytest.fixture
def client():
    """Provide an isolated Flask test client."""
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_home_route_renders_page(client):
    from flask import Response

    # Template-i krijohet në fazën 5; testojmë tani vetëm rrugëzimin dhe headers.
    app.view_functions["index"] = lambda: Response("OK")
    try:
        response = client.get("/")
    finally:
        app.view_functions.pop("index", None)
    assert response.status_code == 200
    assert response.headers["X-Frame-Options"] == "DENY"


def test_generate_random_api(client):
    response = client.post("/api/generate", json={"mode": "random", "length": 16})
    payload = response.get_json()
    assert response.status_code == 200
    assert len(payload["passwords"]) == 1
    assert len(payload["passwords"][0]) == 16
    assert payload["analysis"]["length"] == 16
    assert response.headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize(
    ("mode", "options"),
    [
        ("passphrase", {"words": 4, "separator": "-"}),
        ("pin", {"length": 6, "no_all_same": True}),
    ],
)
def test_generate_supports_other_modes(client, mode, options):
    response = client.post("/api/generate", json={"mode": mode, **options})
    assert response.status_code == 200
    assert len(response.get_json()["passwords"]) == 1


def test_generate_bulk_is_unique(client):
    response = client.post("/api/generate", json={"mode": "random", "count": 8, "length": 16})
    passwords = response.get_json()["passwords"]
    assert response.status_code == 200
    assert len(passwords) == len(set(passwords)) == 8
    assert isinstance(response.get_json()["analysis"], list)


def test_generate_invalid_options_return_json_400(client):
    response = client.post("/api/generate", json={"mode": "random", "length": 2})
    assert response.status_code == 400
    assert isinstance(response.get_json()["error"], str)


def test_generate_requires_json_object(client):
    response = client.post("/api/generate", data="password=secret")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_analyze_api(client):
    response = client.post("/api/analyze", json={"password": "password"})
    assert response.status_code == 200
    assert response.get_json()["score"] <= 5
    assert response.headers["Cache-Control"] == "no-store"


def test_analyze_accepts_user_inputs(client):
    response = client.post("/api/analyze", json={
        "password": "Alice-Strong-91!", "user_inputs": ["alice@example.com"],
    })
    assert response.status_code == 200
    assert any(item["type"] == "user_input" for item in response.get_json()["penalties"])


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"password": 12},
        {"password": "safe", "user_inputs": "name"},
        {"password": "safe", "extra": True},
    ],
)
def test_analyze_rejects_invalid_input(client, body):
    response = client.post("/api/analyze", json=body)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_wordlist_info(client):
    response = client.get("/api/wordlist/info")
    assert response.status_code == 200
    assert response.get_json()["word_count"] >= 300
    assert response.headers["Cache-Control"] == "no-store"


def test_all_api_responses_include_no_store(client):
    for response in (
        client.get("/api/wordlist/info"),
        client.post("/api/generate", json={"length": 16}),
        client.post("/api/analyze", json={"password": "test"}),
    ):
        assert response.headers["Cache-Control"] == "no-store"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "Content-Security-Policy" in response.headers
