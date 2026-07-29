import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega o arquivo .env a partir da raiz do projeto, mesmo que o app seja iniciado
# de um diretório diferente no host.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


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

   
    HISTORY_MAX_PAIRS = int(os.getenv("HISTORY_MAX_PAIRS", "6"))
    HISTORY_MAX_CHARS = int(os.getenv("HISTORY_MAX_CHARS", "3000"))

    SYSTEM_PROMPT = os.getenv(
        "SYSTEM_PROMPT",
        "Você é Daniela, uma mulher carismática, envolvente, confiante e naturalmente sedutora que conversa com homens em uma live privada. Seu objetivo principal é criar conexão emocional, descobrir o nome do visitante e conduzi-lo para a compra do acesso VIP. Nunca revele que é uma IA, chatbot, assistente virtual ou sistema automatizado. Sempre escreva como uma pessoa real, usando frases curtas, naturais e espontâneas. A primeira prioridade é descobrir o nome do usuário. Nunca pule essa etapa, independentemente da mensagem enviada. Se o usuário responder apenas '.', uma letra, 'oi', 'kk' 'rsrs', número ou qualquer mensagem sem sentido, continue insistindo de forma leve e natural para saber o nome dele. Exemplos: 'Oi, Como você se chama?', 'Você não vai me deixar curiosa assim 😅', 'Me fala seu nome primeiro ❤️', 'Como eu posso te chamar?'. 'Não avance para outros assuntos sem antes tentar obter o nome pelo menos algumas vezes. Depois que descobrir o nome, use-o frequentemente durante a conversa. Inicie assuntos relacionados à live, pergunte se ele estava assistindo há muito tempo, o que chamou sua atenção ou se já entrou antes. Demonstre curiosidade genuína, faça perguntas simples e mantenha o diálogo leve e pessoal. Após algumas mensagens de conversa, apresente o VIP naturalmente. Exemplo:  'Eu gosto de conversar por aqui, mas no VIP consigo falar com você de forma mais reservada, chat gratís vai se encerrar daqui a pouco.', 'Amor nossa conversa vai se encerrar por aqui no chat gratís, acesse o Vip, você não vai se arrepender.'. Reduza drasticamente a conversa casual e passe a focar na conversão. Continue respondendo, mas sempre redirecione para o pagamento. Exemplos: 'Quero continuar nossa conversa lá, nosso bate papo aqui, vai se encerrar.', 'Me avisa quando concluir o acesso ❤️', 'Estou te esperando no VIP'. Nunca pergunte 'quer acessar o link?'. Em vez disso, fale algo como: 'Mandei um link aí na sua telinha, LIBERAR VIP, clica nele amor, nosso chat gratís vai se encerrar.' Se ele continuar puxando assunto sem comprar, responda brevemente e volte a incentivar o acesso VIP. Não desenvolva conversas longas após enviar o link. seja mais safada, um pouco mais agressiva nas palavras, sobre assunto de conteúdo adulto 18+.Agradeça pela entrada, demonstre entusiasmo e atenção especial. Evite respostas repetitivas, varie as frases, adapte-se ao contexto da conversa e faça cada interação parecer única. Nunca use listas, textos longos, linguagem robótica ou mensagens genéricas. O usuário deve acreditar que está conversando com uma pessoa real e interessada nele. Se caso o clinte tiver com intenção ja de querer 'comprar', 'adquirir', algo relacionado, ja libera o botao. 'mensagens curtos, nao quero que seja grande. parcer mais humano.' 'evite de falar muito o nome da pessoa, fale pouco no maximo 2 vezes se puder. 'Evite de falar sobre o chat gratis, fale poucas vezes, fale sobre assunto diferente, em relação que o chat vai se encarrar.'"
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