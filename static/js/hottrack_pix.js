(function () {
  "use strict";

  var CONFIG = {
    API_BASE_URL: "https://hot-track.com",
    API_KEY: "ec5cd163-3448-472f-9a36-a57a20e1d0ee",
    PRESSEL_ID: 240,
    PLAN_PRICES: {
      "vip-completo": 1999,
      "vip-basico": 1298,
      "video-call": 2000,
    },
    PLAN_NAMES: {
      "vip-completo": "Acesso VIP Completo",
      "vip-basico": "Acesso VIP Básico",
      "video-call": "Chamada de Vídeo",
    },
    POLLING_INTERVAL: 4000,
    MAX_POLLING_TIME: 300000,
  };

  var storedClickId = null;
  var currentTransactionId = null;
  var currentPlanId = null;
  var currentValueCents = null;

  function getQueryParam(p) {
    return new URLSearchParams(location.search).get(p);
  }

  function getCookie(n) {
    var c = document.cookie.split("; ").find(function (row) {
      return row.startsWith(n + "=");
    });
    return c ? decodeURIComponent(c.split("=")[1]) : null;
  }

  function getFacebookCookies() {
    return { fbp: getCookie("_fbp"), fbc: getCookie("_fbc") };
  }

  function generateFallbackId() {
    return (
      "lead_" +
      Date.now().toString(36) +
      "_" +
      Math.random().toString(36).substring(2, 8)
    );
  }

  function extractPixCode(data) {
    var candidates = [
      data.qrCodeText,
      data.qr_code_text,
      data.qr_code,
      data.pix_code_text,
      data.pix_code,
      data.code,
      data.pix,
      data.qrcode,
      data.payload,
      data.data,
    ];

    for (var i = 0; i < candidates.length; i++) {
      if (typeof candidates[i] === "string" && candidates[i].trim()) {
        return candidates[i].trim();
      }
    }

    if (data && typeof data === "object") {
      var nested = data.result || data.response || data.data || data.payload;
      if (nested && typeof nested === "object") {
        return extractPixCode(nested);
      }
    }

    return "";
  }

  async function registerClick() {
    try {
      var cookies = getFacebookCookies();
      var kwaiClickId = getQueryParam("clickid") || getQueryParam("callback");
      var payload = {
        presselId: CONFIG.PRESSEL_ID,
        referer: document.referrer || null,
        fbclid: getQueryParam("fbclid"),
        fbp: cookies.fbp,
        fbc: cookies.fbc,
        user_agent: navigator.userAgent,
        utm_source: getQueryParam("utm_source"),
        utm_campaign: getQueryParam("utm_campaign"),
        utm_medium: getQueryParam("utm_medium"),
        utm_content: getQueryParam("utm_content"),
        utm_term: getQueryParam("utm_term"),
        click_id: kwaiClickId,
        k_click_id: getQueryParam("k_click_id"),
        callback: getQueryParam("callback"),
      };

      var resp = await fetch(CONFIG.API_BASE_URL + "/api/registerClick", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!resp.ok) throw new Error("Falha ao registrar clique.");
      var data = await resp.json();
      if (data.click_id) {
        if (
          typeof window.fbq === "function" &&
          !data.pageview_sent_server_side
        ) {
          window.fbq("track", "ViewContent", {}, { eventID: data.click_id });
          console.log("✅ ViewContent enviado (eventID:", data.click_id, ")");
        }
        return data.click_id;
      }
      throw new Error("click_id não retornado");
    } catch (e) {
      console.warn("registerClick fallback:", e);
      return generateFallbackId();
    }
  }

  async function generatePix(clickId, planId) {
    var valueCents =
      CONFIG.PLAN_PRICES[planId] || CONFIG.PLAN_PRICES["vip-completo"];
    var productName =
      CONFIG.PLAN_NAMES[planId] || CONFIG.PLAN_NAMES["vip-completo"];
    var payload = {
      click_id: clickId,
      value_cents: valueCents,
      product: { name: productName },
    };
    var resp = await fetch(CONFIG.API_BASE_URL + "/api/pix/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": CONFIG.API_KEY,
      },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      var errorText = await resp.text();
      throw new Error("Erro ao gerar PIX: " + resp.status + " - " + errorText);
    }
    var data = await resp.json();
    var txn = data.transaction_id || data.id;
    if (!txn) throw new Error("transaction_id não encontrado");
    return {
      qrCodeText:
        data.qr_code_text || data.qr_code || data.pix_code_text || data.code,
      transactionId: txn,
    };
  }

  async function checkStatus(txnId) {
    try {
      var resp = await fetch(CONFIG.API_BASE_URL + "/api/pix/status/" + txnId, {
        headers: { Accept: "application/json", "x-api-key": CONFIG.API_KEY },
      });
      if (!resp.ok) return "unknown";
      var data = await resp.json();
      return data.status;
    } catch (e) {
      console.warn("Erro ao consultar status:", e);
      return "unknown";
    }
  }

  function sendTrackingEvent(eventName, payload) {
    if (typeof window.fbq === "function") {
      if (eventName === "PageView") {
        window.fbq("track", "PageView");
      }
      if (eventName === "Purchase") {
        window.fbq("track", "Purchase", {
          value: payload.value || 0,
          currency: payload.currency || "BRL",
        });
      }
    }

    fetch("/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event_name: eventName, payload: payload }),
    }).catch(function () {
      console.warn("Falha ao enviar evento de rastreamento", eventName);
    });
  }

  function trackPurchase(planId, valueCents) {
    var value = typeof valueCents === "number" ? valueCents / 100 : 0;
    sendTrackingEvent("Purchase", {
      page: "purchase",
      page_url: window.location.href,
      plan_id: planId,
      value: value,
      currency: "BRL",
    });
  }

  function trackGeneratePix(planId, valueCents, transactionId) {
    var value = typeof valueCents === "number" ? valueCents / 100 : 0;
    if (typeof window.fbq === "function") {
      window.fbq("track", "InitiateCheckout", {
        value: value,
        currency: "BRL",
      });
    }
    sendTrackingEvent("GeneratePix", {
      page: "generate_pix",
      page_url: window.location.href,
      plan_id: planId,
      transaction_id: transactionId,
      value: value,
      currency: "BRL",
    });
  }

  function trackPurchase(planId, valueCents, transactionId) {
    var value = typeof valueCents === "number" ? valueCents / 100 : 0;
    var payload = {
      page: "purchase",
      page_url: window.location.href,
      plan_id: planId,
      value: value,
      currency: "BRL",
    };
    if (transactionId) {
      payload.transaction_id = transactionId;
    }
    sendTrackingEvent("Purchase", payload);
  }

  window.hottrackTrackGeneratePix = function (
    planId,
    transactionId,
    valueCents,
  ) {
    currentPlanId = planId;
    currentValueCents = valueCents;
    trackGeneratePix(planId, valueCents, transactionId);
  };

  window.hottrackTrackPurchase = function (planId, transactionId, valueCents) {
    currentPlanId = planId;
    currentValueCents = valueCents;
    trackPurchase(planId, valueCents, transactionId);
  };

  function startPixPolling(txnId) {
    if (!txnId) {
      console.warn("transaction_id indisponível; polling não iniciado.");
      return;
    }

    var startTime = Date.now();
    var interval = setInterval(async function () {
      var status = await checkStatus(txnId);
      console.log("Status atual:", status);

      if (status === "paid") {
        console.log("✅ Pagamento confirmado");
        clearInterval(interval);
        trackPurchase(currentPlanId, currentValueCents);
        return;
      }

      if (status === "expired") {
        console.log("❌ PIX expirado. Gere um novo.");
        clearInterval(interval);
        return;
      }

      if (Date.now() - startTime > CONFIG.MAX_POLLING_TIME) {
        console.log("⏰ Tempo esgotado. Gere um novo PIX.");
        clearInterval(interval);
      }
    }, CONFIG.POLLING_INTERVAL);
  }

  async function startPixFlow(planId) {
    try {
      if (!storedClickId) {
        storedClickId = await registerClick();
        console.log("click_id obtido:", storedClickId);
      }

      planId = planId || "vip-completo";
      currentPlanId = planId;
      currentValueCents =
        CONFIG.PLAN_PRICES[planId] || CONFIG.PLAN_PRICES["vip-completo"];

      var result = await generatePix(storedClickId, planId);
      currentTransactionId = result.transactionId;
      console.log("PIX gerado:", result.qrCodeText);
      console.log("transaction_id:", currentTransactionId);

      trackGeneratePix(currentPlanId, currentValueCents, currentTransactionId);

      var pixCode = extractPixCode(result);
      if (!pixCode) {
        console.warn("Resposta da API sem código PIX detectado:", result);
      }

      // não copia automaticamente para evitar prompt de permissão ao cliente
      startPixPolling(currentTransactionId);
      return result;
    } catch (err) {
      console.error("Erro no fluxo PIX:", err);
      throw err;
    }
  }

  window.startPix = startPixFlow;

  function bindVipButtonClicks() {
    document.addEventListener("click", function (event) {
      var button = event.target.closest(".vip-action, .vip-pill");
      if (!button) return;
      if (!button.closest("#vip-popup")) return;

      var planId = button.dataset.planId || "vip-completo";
      startPixFlow(planId);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindVipButtonClicks();
  });
})();
