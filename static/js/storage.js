const STORAGE_KEY = "hotia_state_v1";
const PAYMENT_TTL_MS = 24 * 60 * 60 * 1000;

function defaultState() {
  return {
    history: [],
    vipButtonVisible: false,
    videoCallButtonVisible: false,
    payment: null,
    paymentConfirmed: false,
    paymentConfirmedNotified: false,
    viewerName: "",
    viewerColor: "",
    sessionId: "",
  };
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultState();
    return { ...defaultState(), ...JSON.parse(raw) };
  } catch {
    return defaultState();
  }
}

function saveState(partial) {
  const current = loadState();
  const next = { ...current, ...partial, updatedAt: Date.now() };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next;
}

function saveHistory(history) {
  saveState({ history });
}

function saveVipButtonVisible(visible) {
  saveState({ vipButtonVisible: visible });
}

function saveVideoCallButtonVisible(visible) {
  saveState({ videoCallButtonVisible: visible });
}

function savePayment(payment) {
  saveState({
    payment: {
      ...payment,
      active: true,
      createdAt: Date.now(),
    },
  });
}

function clearPayment() {
  saveState({ payment: null });
}

function markPaymentConfirmed() {
  saveState({
    payment: null,
    paymentConfirmed: true,
    paymentConfirmedNotified: false,
  });
}

function markPaymentConfirmedNotified() {
  saveState({ paymentConfirmedNotified: true });
}

function clearPaymentConfirmed() {
  saveState({ paymentConfirmed: false, paymentConfirmedNotified: false });
}

function isPaymentValid(payment) {
  if (!payment?.active || !payment?.transactionId) return false;
  if (!payment.createdAt) return true;
  return Date.now() - payment.createdAt < PAYMENT_TTL_MS;
}

function getValidPayment() {
  const state = loadState();
  if (!isPaymentValid(state.payment)) {
    if (state.payment) clearPayment();
    return null;
  }
  return state.payment;
}
