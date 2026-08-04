import json
import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from threading import Lock

from config import Config
from services.pix_service import create_pix_charge, get_pix_status
from services.pushinpay_service import create_checkout, get_checkout_status
from services.tracking_service import TrackingService


def _trim_history(messages: list[dict], max_pairs: int = None, max_chars: int = None) -> list[dict]:
    """Trunca o histórico para economizar tokens.

    Estratégia simples:
    - Mantém no máximo `max_pairs` pares (user+assistant) mais recentes.
    - Garante que o total de caracteres não exceda `max_chars`, removendo
      mensagens mais antigas se necessário.
    - Trunca mensagens individuais muito longas para evitar excessos.
    """
    from config import Config

    if max_pairs is None:
        max_pairs = Config.HISTORY_MAX_PAIRS
    if max_chars is None:
        max_chars = Config.HISTORY_MAX_CHARS

    if not messages:
        return []

    # Keep last max_pairs*2 entries (user+assistant)
    keep = messages[-(max_pairs * 2) :]

    # Ensure overall length under max_chars by dropping oldest
    total = sum(len((m.get("content") or "")) for m in keep)
    while total > max_chars and len(keep) > 1:
        total -= len((keep[0].get("content") or ""))
        keep = keep[1:]

    # Truncate any remaining individual messages that are still huge
    max_individual = max(256, max_chars // 4)
    for m in keep:
        c = m.get("content") or ""
        if len(c) > max_individual:
            # Keep the most recent part of the message (tail)
            m["content"] = c[-max_individual:]

    return keep

app = Flask(__name__)

_shared_messages_lock = Lock()
_model_stream_state = {"enabled": False, "frame": None, "updated_at": None}
_model_stream_lock = Lock()
MESSAGES_STORE_PATH = str(Path(__file__).resolve().parent / "data" / "shared_messages.json")


def _normalize_message(message: dict, *, default_role: str = "user") -> dict:
    role = (message.get("role") or default_role).strip() or default_role
    content = (message.get("content") or "").strip()
    return {
        "role": role,
        "content": content,
        "viewerName": message.get("viewerName"),
        "senderColor": message.get("senderColor"),
        "sessionId": message.get("sessionId"),
        "type": message.get("type") or "text",
        "images": message.get("images") or [],
    }


def _ensure_store_exists() -> Path:
    path = Path(MESSAGES_STORE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    return path


def _load_messages_from_store() -> list[dict]:
    path = _ensure_store_exists()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(payload, list):
        return []

    return [_normalize_message(message) for message in payload if isinstance(message, dict)]


def _save_messages_to_store(messages: list[dict]) -> None:
    path = _ensure_store_exists()
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp_path, path)


def _get_state():
    with _shared_messages_lock:
        return {"messages": _load_messages_from_store()}


def _append_message(message: dict):
    with _shared_messages_lock:
        messages = _load_messages_from_store()
        messages.append(_normalize_message(message))
        _save_messages_to_store(messages)
        return list(messages)


def clear_shared_messages():
    with _shared_messages_lock:
        _save_messages_to_store([])


def _get_model_stream_state():
    with _model_stream_lock:
        return {
            "enabled": bool(_model_stream_state.get("enabled")),
            "frame": _model_stream_state.get("frame"),
            "updated_at": _model_stream_state.get("updated_at"),
        }


def _set_model_stream_state(enabled: bool, frame: str | None = None):
    with _model_stream_lock:
        _model_stream_state["enabled"] = bool(enabled)
        _model_stream_state["frame"] = frame if enabled else None
        _model_stream_state["updated_at"] = None if not enabled else _model_stream_state.get("updated_at")
        if enabled:
            from datetime import datetime

            _model_stream_state["updated_at"] = datetime.utcnow().isoformat() + "Z"


@app.route("/")
def index():
    return render_template(
        "index.html",
        video_url=Config.BACKGROUND_VIDEO_URL,
        poster_url=Config.BACKGROUND_POSTER_URL,
        live_stream_hls_url=Config.LIVE_STREAM_HLS_URL,
        config={
            "META_PIXEL_ID": Config.META_PIXEL_ID,
            "CLARITY_PROJECT_ID": Config.CLARITY_PROJECT_ID,
        },
    )


@app.route("/private")
def private():
    return render_template(
        "private.html",
        video_url=Config.BACKGROUND_VIDEO_URL,
        poster_url=Config.BACKGROUND_POSTER_URL,
        live_stream_hls_url=Config.LIVE_STREAM_HLS_URL,
        config={
            "META_PIXEL_ID": Config.META_PIXEL_ID,
            "CLARITY_PROJECT_ID": Config.CLARITY_PROJECT_ID,
        },
    )


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Mensagem vazia."}), 400

    message = {"role": "user", "content": user_message}
    _append_message(message)
    return jsonify({"response": "", "messages": _get_state()["messages"]})


@app.route("/api/live-state", methods=["GET"])
def live_state():
    return jsonify(_get_state())


@app.route("/api/post-message", methods=["POST"])
def post_message():
    data = request.get_json(silent=True) or {}
    role = (data.get("role") or "user").strip() or "user"
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Mensagem vazia."}), 400

    viewer_name = (data.get("viewerName") or "").strip() or None
    sender_color = (data.get("senderColor") or "").strip() or None
    session_id = (data.get("sessionId") or "").strip() or None

    message = {
        "role": role,
        "content": content,
        "viewerName": viewer_name,
        "senderColor": sender_color,
        "sessionId": session_id,
    }
    _append_message(message)
    return jsonify({"ok": True, "messages": _get_state()["messages"]})


@app.route("/api/model/stream", methods=["POST"])
def model_stream():
    data = request.get_json(silent=True) or {}
    enabled = bool(data.get("enabled"))
    frame = (data.get("frame") or "").strip() or None

    if not enabled:
        _set_model_stream_state(False, None)
        return jsonify({"ok": True, "enabled": False})

    if not frame:
        return jsonify({"error": "frame é obrigatório."}), 400

    _set_model_stream_state(True, frame)
    return jsonify({"ok": True, "enabled": True})


@app.route("/api/model/stream-state", methods=["GET"])
def model_stream_state():
    return jsonify(_get_model_stream_state())


@app.route("/model")
def model_admin():
    return render_template("model.html")


@app.route("/track", methods=["POST"])
def track_event():
    data = request.get_json(silent=True) or {}
    event_name = (data.get("event_name") or "PageView").strip()
    payload = data.get("payload") or {}
    ok, detail = TrackingService.send_event(event_name, payload, request_context=request)
    return jsonify({"ok": ok, "event_name": event_name, "detail": detail})


@app.route("/track/pageview", methods=["GET"])
def track_pageview():
    ok, detail = TrackingService.send_event(
        "PageView",
        {
            "page": request.args.get("page", "home"),
            "page_url": request.args.get("page_url") or request.url,
        },
        request_context=request,
    )
    return jsonify({"ok": ok, "detail": detail})


@app.route("/debug/pixel", methods=["GET"])
def debug_pixel():
    """Rota de debug leve para checar o META_PIXEL_ID exposto pelo servidor.

    Não retorna tokens ou segredos — apenas o ID do pixel e um booleano indicando
    se está presente.
    """
    from config import Config as _Config

    clarity_id = getattr(_Config, "CLARITY_PROJECT_ID", None)
    return jsonify(
        {
            "META_PIXEL_ID": _Config.META_PIXEL_ID,
            "CLARITY_PROJECT_ID": clarity_id,
            "has_pixel": bool(_Config.META_PIXEL_ID),
            "has_clarity": bool(clarity_id),
        }
    )


@app.route("/pix/create", methods=["POST"])
def pix_create():
    data = request.get_json(silent=True) or {}
    plan_id = (data.get("plan_id") or "").strip()
    amount = data.get("amount")
    description = data.get("description", "Cobrança PIX")

    if not plan_id or not amount:
        return jsonify({"error": "Plano e valor são obrigatórios."}), 400

    try:
        charge = create_pix_charge(
            plan_id=plan_id,
            amount=amount,
            description=description,
        )
        return jsonify(charge)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502


@app.route("/pix/status", methods=["GET"])
def pix_status():
    transaction_id = (request.args.get("transaction_id") or "").strip()
    if not transaction_id:
        return jsonify({"error": "transaction_id é obrigatório."}), 400

    try:
        status = get_pix_status(transaction_id)
        return jsonify(status)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502


@app.route("/pushinpay/create", methods=["POST"])
def pushinpay_create():
    data = request.get_json(silent=True) or {}
    plan = (data.get("plan") or "").strip()
    amount = data.get("amount")

    if not plan:
        return jsonify({"error": "plan é obrigatório."}), 400

    try:
        result = create_checkout(token=None, plan=plan, amount=amount)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502


@app.route("/pushinpay/status", methods=["GET"])
def pushinpay_status():
    transaction_id = (request.args.get("transaction_id") or "").strip()
    if not transaction_id:
        return jsonify({"error": "transaction_id é obrigatório."}), 400

    try:
        status = get_checkout_status(transaction_id)
        return jsonify(status)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
