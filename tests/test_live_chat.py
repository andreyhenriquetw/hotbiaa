import importlib
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


def test_shared_messages_survive_module_reload(tmp_path, monkeypatch):
    import app as app_module

    storage_path = tmp_path / "shared_messages.json"
    monkeypatch.setattr(app_module, "MESSAGES_STORE_PATH", str(storage_path), raising=False)

    client = app_module.app.test_client()
    response = client.post('/api/post-message', json={"role": "user", "content": "persistido"})
    assert response.status_code == 200

    reloaded_module = importlib.reload(app_module)
    monkeypatch.setattr(reloaded_module, "MESSAGES_STORE_PATH", str(storage_path), raising=False)

    response = reloaded_module.app.test_client().get('/api/live-state')
    payload = response.get_json()
    assert payload["messages"][-1]["content"] == "persistido"


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
