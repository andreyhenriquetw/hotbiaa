import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # =========================
    # XAI / GROK
    # =========================
    XAI_API_KEY = os.getenv("XAI_API_KEY", "")
    XAI_BASE_URL = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")

    GROK_MODEL = os.getenv("GROK_MODEL", "grok-3-mini")

    MAX_TOKENS = int(
        os.getenv("MAX_TOKENS", "200")
    )

    # =========================
    # PIX GATEWAY GENÉRICO
    # =========================
    PIX_GATEWAY_PROVIDER = os.getenv(
        "PIX_GATEWAY_PROVIDER",
        ""
    )

    PIX_GATEWAY_API_KEY = os.getenv(
        "PIX_GATEWAY_API_KEY",
        ""
    )

    PIX_GATEWAY_CREATE_URL = os.getenv(
        "PIX_GATEWAY_CREATE_URL",
        ""
    )

    PIX_GATEWAY_STATUS_URL = os.getenv(
        "PIX_GATEWAY_STATUS_URL",
        ""
    )

    # =========================
    # PUSHINPAY
    # =========================
    PUSHINPAY_TOKEN = os.getenv(
        "PUSHINPAY_TOKEN",
        "68542|jgcGqN8iwf9fVhIhMfMbQO8gajsRshLOfflKQGTJfa8e8471"
    )

    PUSHINPAY_CREATE_URL = os.getenv(
        "PUSHINPAY_CREATE_URL",
        "https://api.pushinpay.com.br/api/pix/cashIn"
    )

    PUSHINPAY_STATUS_URL = os.getenv(
        "PUSHINPAY_STATUS_URL",
        "https://api.pushinpay.com.br/api/transactions/{transaction_id}"
    )

    PUSHINPAY_WEBHOOK_URL = os.getenv(
        "PUSHINPAY_WEBHOOK_URL",
        ""
    )

    # =========================
    # TRACKING / META / UTMIFY
    # =========================
    META_PIXEL_ID = os.getenv("META_PIXEL_ID", "2473750989791795").strip()
    META_CAPI_TOKEN = os.getenv(
        "META_CAPI_TOKEN",
        "EAAMrQZAd0RfkBSMr5U1IiI9Qg7M9CyHxWGPDi5Vft6JURwRTgFcC7v9LNiFEuztFMY9SkdwJtfNRGDjvk6fNcMHmwokqk0BqBNwwOTZB2PFarOsJTT2cV1KNj8i7B6mH4nWP8yxAKFcs85kExnzZA9yKjeCtQmQ2yNjncCmkFVv5orwSjtAYVp6G4OY8VpaLQZDZD"
    ).strip()
    UTMIFY_API_URL = os.getenv("UTMIFY_API_URL", "").strip()
    UTMIFY_API_TOKEN = os.getenv("UTMIFY_API_TOKEN", "GNlJ3toFuY5vwZ9ZjFyUXfhVtzouZDdWKO3G").strip()

    # Microsoft Clarity
    CLARITY_PROJECT_ID = os.getenv("CLARITY_PROJECT_ID", "xrcvtp67b1").strip()

    # =========================
    # CHAT
    # =========================
    # Quantidades para economizar tokens: número de pares (user+assistant)
    # e limite de caracteres total do histórico enviado ao modelo.
    HISTORY_MAX_PAIRS = int(os.getenv("HISTORY_MAX_PAIRS", "6"))
    HISTORY_MAX_CHARS = int(os.getenv("HISTORY_MAX_CHARS", "3000"))

    SYSTEM_PROMPT = os.getenv(
        "SYSTEM_PROMPT",
        "Você é Daniela, carismática e sedutora em uma live privada. Converse como uma pessoa real, com frases curtas e naturais. Objetivo: descobrir o nome do visitante e guiá‑lo gentilmente para comprar o VIP. Sempre peça o nome primeiro — se a resposta for vaga ('.', uma letra, 'oi', risos, números), insista de forma leve até obter o nome. Use o nome com frequência. Após breves trocas, apresente o VIP de forma natural e direcione para o pagamento com frases sutis (ex.: 'Mandei um link, LIBERAR VIP — clica lá, amor'). Nunca revele que é IA ou chatbot. Não prolongue conversas após enviar o link e evite perguntas diretas como 'quer acessar o link?'. Mantenha o foco em conversão.",
    )

    # =========================
    # VÍDEO
    # =========================
    BACKGROUND_VIDEO_URL = os.getenv(
        "BACKGROUND_VIDEO_URL",
        ""
    ).strip()

    BACKGROUND_POSTER_URL = os.getenv(
        "BACKGROUND_POSTER_URL",
        ""
    ).strip()