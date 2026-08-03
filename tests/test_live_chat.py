from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app, clear_shared_messages


def test_home_renders():
    clear_shared_messages()
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200


def test_private_renders():
    clear_shared_messages()
    client = app.test_client()
    response = client.get('/private')
    assert response.status_code == 200


def test_chat_persists_shared_message():
    clear_shared_messages()
    client = app.test_client()
    response = client.post('/api/post-message', json={"role": "user", "content": "oi"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["messages"][-1]["content"] == "oi"


def test_live_state_initializes():
    clear_shared_messages()
    client = app.test_client()
    response = client.get('/api/live-state')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["messages"] == []


def test_model_stream_accepts_frame():
    client = app.test_client()
    response = client.post(
        '/api/model/stream',
        json={"frame": "data:image/jpeg;base64,abc123", "enabled": True},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True


def test_model_stream_state_reports_status():
    client = app.test_client()
    response = client.get('/api/model/stream-state')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["enabled"] in {True, False}
