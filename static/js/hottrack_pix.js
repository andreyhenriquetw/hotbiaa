// ============================================================
//  SISTEMA HOTTRACK + PIX (Versão Corrigida)
//  – Registro de clique (/api/registerClick)
//  – Geração de PIX (/api/pix/generate)
//  – Consulta de status (/api/pix/status) com polling
// ============================================================
(function () {
  "use strict";

  var CONFIG = {
    API_BASE_URL: "https://hot-track.com",
    API_KEY: "ec5cd163-3448-472f-9a36-a57a20e1d0ee",
    PRESSEL_ID: 240,
    VALUE_CENTS: 1999,
    PRODUCT_NAME: "Acesso VIP Completo",
    POLLING_INTERVAL: 4000,
    MAX_POLLING_TIME: 300000,
  };

  var storedClickId = null;
  var currentTransactionId = null;

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

  async function generatePix(clickId) {
    var payload = {
      click_id: clickId,
      value_cents: CONFIG.VALUE_CENTS,
      product: { name: CONFIG.PRODUCT_NAME },
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
    return { qrCodeText: data.qr_code_text, transactionId: txn };
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

  async function startPixFlow() {
    try {
      if (!storedClickId) {
        storedClickId = await registerClick();
        console.log("click_id obtido:", storedClickId);
      }

      var result = await generatePix(storedClickId);
      currentTransactionId = result.transactionId;
      console.log("PIX gerado:", result.qrCodeText);
      console.log("transaction_id:", currentTransactionId);

      alert(
        "📋 Código PIX:\n\n" +
          result.qrCodeText +
          "\n\nAguardando pagamento...",
      );

      var startTime = Date.now();
      var finished = false;
      while (!finished) {
        await new Promise(function (resolve) {
          setTimeout(resolve, CONFIG.POLLING_INTERVAL);
        });

        if (Date.now() - startTime > CONFIG.MAX_POLLING_TIME) {
          alert("⏰ Tempo esgotado. Gere um novo PIX.");
          finished = true;
          break;
        }

        var status = await checkStatus(currentTransactionId);
        console.log("Status atual:", status);

        switch (status) {
          case "paid":
            alert("✅ Pagamento confirmado! Redirecionando...");
            finished = true;
            break;
          case "expired":
            alert("❌ PIX expirado. Gere um novo.");
            finished = true;
            break;
          default:
            break;
        }
      }
    } catch (err) {
      console.error("Erro no fluxo PIX:", err);
      alert("⚠️ Ocorreu um erro. Tente novamente.");
    }
  }

  window.startPix = startPixFlow;

  document.addEventListener("DOMContentLoaded", function () {
    var pixBtn = document.getElementById("pix-btn");
    if (!pixBtn) return;
    pixBtn.addEventListener("click", function () {
      startPixFlow();
    });
  });
})();
