const symbols = {
  SPY: { name: "S&P 500 ETF", spot: 522.4, iv: 0.185, drift: 0.075, vol: 0.16, beta: 1.0 },
  AAPL: { name: "Apple", spot: 188.7, iv: 0.265, drift: 0.09, vol: 0.24, beta: 1.12 },
  MSFT: { name: "Microsoft", spot: 428.3, iv: 0.245, drift: 0.105, vol: 0.22, beta: 1.06 },
  NVDA: { name: "NVIDIA", spot: 109.6, iv: 0.54, drift: 0.16, vol: 0.48, beta: 1.75 },
  TSLA: { name: "Tesla", spot: 176.2, iv: 0.66, drift: 0.07, vol: 0.58, beta: 1.9 },
  AMZN: { name: "Amazon", spot: 184.1, iv: 0.31, drift: 0.095, vol: 0.29, beta: 1.22 },
  GOOGL: { name: "Alphabet", spot: 172.5, iv: 0.285, drift: 0.085, vol: 0.25, beta: 1.04 },
  META: { name: "Meta", spot: 478.9, iv: 0.34, drift: 0.11, vol: 0.32, beta: 1.28 }
};

const presets = {
  "Long Call": [{ type: "call", side: 1, qty: 1, offset: 0 }],
  "Long Put": [{ type: "put", side: 1, qty: 1, offset: 0 }],
  "Short Straddle": [
    { type: "call", side: -1, qty: 1, offset: 0 },
    { type: "put", side: -1, qty: 1, offset: 0 }
  ],
  "Long Straddle": [
    { type: "call", side: 1, qty: 1, offset: 0 },
    { type: "put", side: 1, qty: 1, offset: 0 }
  ],
  "Bull Call Spread": [
    { type: "call", side: 1, qty: 1, offset: -2 },
    { type: "call", side: -1, qty: 1, offset: 5 }
  ],
  "Bear Put Spread": [
    { type: "put", side: 1, qty: 1, offset: 3 },
    { type: "put", side: -1, qty: 1, offset: -6 }
  ],
  "Put Underwriting": [{ type: "put", side: -1, qty: 1, offset: -7 }],
  "Call Overwrite": [
    { type: "stock", side: 1, qty: 100, offset: 0 },
    { type: "call", side: -1, qty: 1, offset: 5 }
  ],
  "Iron Condor": [
    { type: "put", side: -1, qty: 1, offset: -8 },
    { type: "put", side: 1, qty: 1, offset: -15 },
    { type: "call", side: -1, qty: 1, offset: 8 },
    { type: "call", side: 1, qty: 1, offset: 15 }
  ],
  "Risk Reversal": [
    { type: "call", side: 1, qty: 1, offset: 6 },
    { type: "put", side: -1, qty: 1, offset: -6 }
  ]
};

const state = {
  view: "dashboard",
  symbol: "SPY",
  backtest: null
};

const $ = (id) => document.getElementById(id);
const fmt = (value, digits = 2) => Number(value).toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
const pct = (value, digits = 1) => `${fmt(value * 100, digits)}%`;
const money = (value) => `${value < 0 ? "-" : ""}$${fmt(Math.abs(value), 2)}`;

function seededRandom(seed) {
  let x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

function erf(x) {
  const sign = x < 0 ? -1 : 1;
  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const p = 0.3275911;
  const t = 1 / (1 + p * Math.abs(x));
  const y = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
  return sign * y;
}

function normCdf(x) {
  return 0.5 * (1 + erf(x / Math.sqrt(2)));
}

function normPdf(x) {
  return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
}

function bsm({ S, K, T, r = 0.045, q = 0, sigma, type = "call" }) {
  const tau = Math.max(T, 1 / 3650);
  const vol = Math.max(sigma, 0.001);
  const d1 = (Math.log(S / K) + (r - q + 0.5 * vol * vol) * tau) / (vol * Math.sqrt(tau));
  const d2 = d1 - vol * Math.sqrt(tau);
  const dfq = Math.exp(-q * tau);
  const dfr = Math.exp(-r * tau);
  const call = S * dfq * normCdf(d1) - K * dfr * normCdf(d2);
  const put = K * dfr * normCdf(-d2) - S * dfq * normCdf(-d1);
  const isCall = type === "call";
  const delta = isCall ? dfq * normCdf(d1) : -dfq * normCdf(-d1);
  const gamma = (dfq * normPdf(d1)) / (S * vol * Math.sqrt(tau));
  const vega = S * dfq * normPdf(d1) * Math.sqrt(tau) / 100;
  const thetaCall = (-(S * dfq * normPdf(d1) * vol) / (2 * Math.sqrt(tau)) - r * K * dfr * normCdf(d2) + q * S * dfq * normCdf(d1)) / 365;
  const thetaPut = (-(S * dfq * normPdf(d1) * vol) / (2 * Math.sqrt(tau)) + r * K * dfr * normCdf(-d2) - q * S * dfq * normCdf(-d1)) / 365;
  const rho = (isCall ? K * tau * dfr * normCdf(d2) : -K * tau * dfr * normCdf(-d2)) / 100;
  const probabilityItm = isCall ? normCdf(d2) : normCdf(-d2);
  const signedProb = isCall ? probabilityItm : -probabilityItm;
  const vanna = -dfq * normPdf(d1) * d2 / vol;
  const volga = S * dfq * normPdf(d1) * Math.sqrt(tau) * d1 * d2 / vol / 100;
  const charm = isCall
    ? -q * dfq * normCdf(d1) - (dfq * normPdf(d1) * (2 * (r - q) * tau - d2 * vol * Math.sqrt(tau))) / (2 * tau * vol * Math.sqrt(tau))
    : q * dfq * normCdf(-d1) - (dfq * normPdf(d1) * (2 * (r - q) * tau - d2 * vol * Math.sqrt(tau))) / (2 * tau * vol * Math.sqrt(tau));
  const dvegaDtime = vega * (r - q + (vol * vol - d1 * vol / Math.sqrt(tau)) / 2);
  return {
    price: Math.max(isCall ? call : put, 0),
    delta,
    gamma,
    vega,
    theta: isCall ? thetaCall : thetaPut,
    rho,
    vanna,
    charm: charm / 365,
    volga,
    dvegaDtime,
    probabilityItm,
    deltaProbDivergence: Math.abs(Math.abs(delta) - Math.abs(signedProb)),
    d1,
    d2
  };
}

function generateSeries(symbol, days = 760) {
  const cfg = symbols[symbol];
  const prices = [];
  const vols = [];
  let s = cfg.spot / Math.exp(cfg.drift * days / 252 - 0.5 * cfg.vol * Math.sqrt(days / 252));
  for (let i = 0; i < days; i += 1) {
    const shock = (seededRandom(i * 17 + symbol.length * 13) + seededRandom(i * 31 + 7) - 1) * 0.82;
    const regime = 1 + 0.65 * Math.sin(i / 57 + cfg.beta);
    const jump = seededRandom(i * 43 + cfg.spot) > 0.985 ? (seededRandom(i + 4) - 0.52) * cfg.vol * 0.42 : 0;
    const dailyVol = cfg.vol * regime / Math.sqrt(252);
    s *= Math.exp((cfg.drift - 0.5 * cfg.vol * cfg.vol) / 252 + dailyVol * shock + jump);
    prices.push(s);
    vols.push(Math.max(0.08, cfg.iv + 0.55 * Math.abs(shock) * cfg.iv + 0.05 * Math.sin(i / 29)));
  }
  const scale = cfg.spot / prices[prices.length - 1];
  return prices.map((p, i) => ({ day: i, price: p * scale, iv: vols[i] }));
}

function realizedVol(points, window = 30) {
  const out = [];
  for (let i = 1; i < points.length; i += 1) {
    const start = Math.max(1, i - window + 1);
    const returns = [];
    for (let j = start; j <= i; j += 1) returns.push(Math.log(points[j].price / points[j - 1].price));
    const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((a, b) => a + (b - mean) ** 2, 0) / Math.max(1, returns.length - 1);
    out.push(Math.sqrt(variance * 252));
  }
  return [out[0] || 0, ...out];
}

function getLegs(presetName, spot, offset = 0, qty = 1) {
  return presets[presetName].map((leg) => ({
    ...leg,
    qty: leg.qty * qty,
    strike: leg.type === "stock" ? 0 : spot * (1 + (leg.offset + offset) / 100)
  }));
}

function priceStrategy(legs, S, T, sigma, r = 0.045) {
  return legs.reduce((sum, leg) => {
    if (leg.type === "stock") return sum + leg.side * leg.qty * S;
    const px = bsm({ S, K: leg.strike, T, r, sigma, type: leg.type }).price * 100;
    return sum + leg.side * leg.qty * px;
  }, 0);
}

function payoffStrategy(legs, S, premium) {
  const gross = legs.reduce((sum, leg) => {
    if (leg.type === "stock") return sum + leg.side * leg.qty * S;
    const intrinsic = leg.type === "call" ? Math.max(S - leg.strike, 0) : Math.max(leg.strike - S, 0);
    return sum + leg.side * leg.qty * intrinsic * 100;
  }, 0);
  return gross - premium;
}

function strategyGreeks(legs, S, T, sigma) {
  const totals = { delta: 0, gamma: 0, theta: 0, vega: 0, rho: 0 };
  legs.forEach((leg) => {
    if (leg.type === "stock") {
      totals.delta += leg.side * leg.qty;
      return;
    }
    const g = bsm({ S, K: leg.strike, T, sigma, type: leg.type });
    Object.keys(totals).forEach((key) => {
      totals[key] += g[key] * leg.side * leg.qty * (key === "delta" ? 100 : 1);
    });
  });
  return totals;
}

function runBacktestForSymbol(symbol, presetName, daysToExpiry, offset, contracts, capital) {
  const data = generateSeries(symbol);
  const rv = realizedVol(data);
  let cash = capital;
  const equity = [];
  const tradePnls = [];
  const step = Math.max(5, Math.round(daysToExpiry * 0.55));
  for (let i = 0; i < data.length - daysToExpiry; i += step) {
    const S0 = data[i].price;
    const ST = data[i + daysToExpiry].price;
    const sigma = Math.max(data[i].iv, rv[i] * 0.85);
    const legs = getLegs(presetName, S0, offset, contracts);
    const premium = priceStrategy(legs, S0, daysToExpiry / 365, sigma);
    const pnl = payoffStrategy(legs, ST, premium);
    cash += pnl;
    equity.push({ x: i + daysToExpiry, y: cash });
    tradePnls.push(pnl);
  }
  const returns = equity.map((point, i) => i === 0 ? 0 : point.y / equity[i - 1].y - 1).slice(1);
  const mean = returns.reduce((a, b) => a + b, 0) / Math.max(1, returns.length);
  const stdev = Math.sqrt(returns.reduce((a, b) => a + (b - mean) ** 2, 0) / Math.max(1, returns.length - 1));
  let peak = capital;
  let maxDd = 0;
  equity.forEach((point) => {
    peak = Math.max(peak, point.y);
    maxDd = Math.min(maxDd, point.y / peak - 1);
  });
  return {
    symbol,
    equity,
    tradePnls,
    ending: cash,
    cagr: (cash / capital) ** (252 / Math.max(1, data.length)) - 1,
    sharpe: stdev ? (mean / stdev) * Math.sqrt(252 / step) : 0,
    maxDd,
    winRate: tradePnls.filter((x) => x > 0).length / Math.max(1, tradePnls.length),
    avgPnl: tradePnls.reduce((a, b) => a + b, 0) / Math.max(1, tradePnls.length)
  };
}

function canvasSetup(canvas) {
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.max(320, rect.width) * ratio;
  canvas.height = Number(canvas.getAttribute("height")) * ratio;
  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);
  return { ctx, w: canvas.width / ratio, h: canvas.height / ratio };
}

function drawAxes(ctx, w, h) {
  ctx.strokeStyle = "rgba(148, 163, 184, .16)";
  ctx.lineWidth = 1;
  for (let i = 1; i < 5; i += 1) {
    const y = 18 + ((h - 42) * i) / 5;
    ctx.beginPath();
    ctx.moveTo(42, y);
    ctx.lineTo(w - 12, y);
    ctx.stroke();
  }
}

function drawLineChart(canvas, series, opts = {}) {
  const { ctx, w, h } = canvasSetup(canvas);
  ctx.clearRect(0, 0, w, h);
  drawAxes(ctx, w, h);
  const allY = series.flatMap((s) => s.data.map((p) => p.y));
  const minY = opts.min ?? Math.min(...allY);
  const maxY = opts.max ?? Math.max(...allY);
  const pad = (maxY - minY) * 0.08 || 1;
  const yMin = minY - pad;
  const yMax = maxY + pad;
  const maxLen = Math.max(...series.map((s) => s.data.length));
  series.forEach((s) => {
    ctx.strokeStyle = s.color;
    ctx.lineWidth = s.width || 2;
    ctx.beginPath();
    s.data.forEach((p, i) => {
      const x = 42 + ((w - 58) * i) / Math.max(1, maxLen - 1);
      const y = 12 + (h - 44) * (1 - (p.y - yMin) / (yMax - yMin));
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  });
  ctx.fillStyle = "#98a4b7";
  ctx.font = "12px Cascadia Mono, Consolas, monospace";
  ctx.fillText(opts.label || "", 48, 18);
  ctx.fillText(fmt(yMax, 2), 6, 20);
  ctx.fillText(fmt(yMin, 2), 6, h - 20);
}

function drawHistogram(canvas, values) {
  const { ctx, w, h } = canvasSetup(canvas);
  ctx.clearRect(0, 0, w, h);
  drawAxes(ctx, w, h);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const bins = 28;
  const counts = Array.from({ length: bins }, () => 0);
  values.forEach((value) => {
    const index = Math.min(bins - 1, Math.max(0, Math.floor(((value - min) / (max - min || 1)) * bins)));
    counts[index] += 1;
  });
  const peak = Math.max(...counts);
  counts.forEach((count, i) => {
    const x = 44 + ((w - 62) * i) / bins;
    const barW = (w - 72) / bins;
    const barH = ((h - 52) * count) / peak;
    ctx.fillStyle = i < bins / 2 ? "rgba(239, 68, 68, .74)" : "rgba(34, 197, 94, .72)";
    ctx.fillRect(x, h - 26 - barH, Math.max(2, barW - 2), barH);
  });
  ctx.fillStyle = "#98a4b7";
  ctx.font = "12px Cascadia Mono, Consolas, monospace";
  ctx.fillText(`${money(min)} to ${money(max)}`, 48, 18);
}

function drawPayoff(canvas, legs, spot, sigma, days) {
  const xs = Array.from({ length: 90 }, (_, i) => spot * (0.58 + i * 0.011));
  const premium = priceStrategy(legs, spot, days / 365, sigma);
  drawLineChart(canvas, [{ color: "#38bdf8", data: xs.map((x) => ({ y: payoffStrategy(legs, x, premium) })) }], { label: "Expiry P&L" });
}

function drawHeatmap(canvas, symbol) {
  const cfg = symbols[symbol];
  const { ctx, w, h } = canvasSetup(canvas);
  ctx.clearRect(0, 0, w, h);
  const cols = 18;
  const rows = 10;
  for (let y = 0; y < rows; y += 1) {
    for (let x = 0; x < cols; x += 1) {
      const moneyness = 0.75 + x * 0.03;
      const tenor = 15 + y * 32;
      const skew = Math.max(0, 1.14 - moneyness) * 0.26;
      const term = 0.04 * Math.sin(tenor / 95 + cfg.beta);
      const iv = cfg.iv + skew + term;
      const t = Math.max(0, Math.min(1, (iv - 0.12) / 0.65));
      ctx.fillStyle = `rgba(${40 + t * 180}, ${115 + t * 80}, ${235 - t * 140}, .86)`;
      ctx.fillRect(42 + x * ((w - 60) / cols), 18 + y * ((h - 54) / rows), (w - 70) / cols, (h - 64) / rows);
    }
  }
  ctx.fillStyle = "#dbeafe";
  ctx.font = "12px Cascadia Mono, Consolas, monospace";
  ctx.fillText("Strike moneyness ->", 48, h - 18);
  ctx.save();
  ctx.translate(16, h - 70);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText("Tenor", 0, 0);
  ctx.restore();
}

function monteCarlo(symbol, presetName, days, offset, contracts, paths, hedgeDays) {
  const cfg = symbols[symbol];
  const legs = getLegs(presetName, cfg.spot, offset, contracts);
  const premium = priceStrategy(legs, cfg.spot, days / 365, cfg.iv);
  const values = [];
  for (let p = 0; p < paths; p += 1) {
    let S = cfg.spot;
    let hedge = 0;
    let hedgeCash = 0;
    for (let t = 1; t <= days; t += 1) {
      const z = seededRandom(p * 97 + t * 11) + seededRandom(p * 53 + t * 19) - 1;
      S *= Math.exp((cfg.drift - 0.5 * cfg.vol * cfg.vol) / 252 + (cfg.vol / Math.sqrt(252)) * z);
      if (t % hedgeDays === 0) {
        const g = strategyGreeks(legs, S, Math.max((days - t) / 365, 1 / 365), cfg.iv);
        const target = -g.delta;
        hedgeCash -= (target - hedge) * S + Math.abs(target - hedge) * S * 0.00035;
        hedge = target;
      }
    }
    const final = payoffStrategy(legs, S, premium) + hedge * S + hedgeCash;
    values.push(final);
  }
  return values;
}

function populateSelects() {
  const symbolOptions = Object.entries(symbols).map(([key, cfg]) => `<option value="${key}">${key} - ${cfg.name}</option>`).join("");
  ["quickSymbol", "greekSymbol", "strategySymbol", "surfaceSymbol"].forEach((id) => {
    $(id).innerHTML = symbolOptions;
    $(id).value = state.symbol;
  });
  $("basketSelect").innerHTML = Object.keys(symbols).map((key) => `<label><input type="checkbox" value="${key}" ${["SPY", "AAPL", "NVDA"].includes(key) ? "checked" : ""}>${key}</label>`).join("");
  $("strategyPreset").innerHTML = Object.keys(presets).map((key) => `<option>${key}</option>`).join("");
}

function renderMarketStrip() {
  $("marketStrip").innerHTML = Object.entries(symbols).slice(0, 4).map(([key, cfg], i) => {
    const change = (seededRandom(i + 9) - 0.47) * cfg.vol * 0.8;
    return `<div class="ticker-pill"><small>${key}</small><strong>${money(cfg.spot)}</strong><small class="${change >= 0 ? "up" : "down"}">${change >= 0 ? "+" : ""}${pct(change, 2)}</small></div>`;
  }).join("");
}

function renderDashboard() {
  const data = generateSeries(state.symbol);
  const rv = realizedVol(data);
  const latest = data[data.length - 1];
  $("dashSpot").textContent = money(latest.price);
  $("dashIv").textContent = pct(latest.iv);
  $("dashRv").textContent = pct(rv[rv.length - 1]);
  $("dashVrp").textContent = `${fmt((latest.iv - rv[rv.length - 1]) * 100, 1)} pts`;
  drawLineChart($("overviewChart"), [
    { color: "#38bdf8", data: data.slice(-240).map((d) => ({ y: d.price })) },
    { color: "#f59e0b", data: data.slice(-240).map((d, i) => ({ y: (rv[rv.length - 240 + i] || 0) * latest.price })) }
  ], { label: `${state.symbol} price plus scaled realized volatility` });
  const b = bsm({ S: latest.price, K: latest.price, T: 45 / 365, sigma: latest.iv, type: "call" });
  $("signalStack").innerHTML = [
    ["Delta divergence", `${fmt(b.deltaProbDivergence, 3)}`, "Delta and probability are visibly different for the selected tenor."],
    ["VRP spread", `${fmt((latest.iv - rv[rv.length - 1]) * 100, 1)} vol pts`, "IV is shown beside realized volatility because implied vol is an insurance price."],
    ["Skew regime", latest.iv > rv[rv.length - 1] * 1.35 ? "Sticky / carry heavy" : "Jumpy / responsive", "Long skew needs jumpy volatility; sticky regimes bleed through carry."],
    ["VIX roll posture", "Contango", "Long VIX products must overcome roll drag before they hedge anything."]
  ].map(([label, value, body]) => `<div class="signal"><small>${label}</small><strong>${value}</strong><p>${body}</p></div>`).join("");
}

function renderGreeks() {
  const symbol = $("greekSymbol").value;
  const cfg = symbols[symbol];
  if (!$("strikeInput").value) $("strikeInput").value = Math.round(cfg.spot);
  const S = cfg.spot;
  const K = Number($("strikeInput").value);
  const T = Number($("daysInput").value) / 365;
  const sigma = Number($("ivInput").value) / 100;
  const r = Number($("rateInput").value) / 100;
  const type = $("optionType").value;
  const g = bsm({ S, K, T, r, sigma, type });
  $("ivReadout").textContent = pct(sigma, 1);
  $("rateReadout").textContent = pct(r, 1);
  $("deltaValue").textContent = fmt(g.delta, 3);
  $("probValue").textContent = fmt(g.probabilityItm, 3);
  $("divergenceValue").textContent = fmt(g.deltaProbDivergence, 3);
  $("deltaBar").style.width = `${Math.min(100, Math.abs(g.delta) * 100)}%`;
  $("probBar").style.width = `${Math.min(100, g.probabilityItm * 100)}%`;
  $("greekMetrics").innerHTML = [
    ["Price", money(g.price)],
    ["Delta", fmt(g.delta, 4)],
    ["Gamma", fmt(g.gamma, 4)],
    ["Theta/day", money(g.theta)],
    ["Vega / 1 vol pt", money(g.vega)],
    ["Rho", money(g.rho)],
    ["Vanna", fmt(g.vanna, 4)],
    ["Volga", fmt(g.volga, 4)]
  ].map(([k, v]) => `<div class="metric"><small>${k}</small><strong>${v}</strong></div>`).join("");
  drawHeatmap($("surfaceCanvas"), symbol);
}

function renderStrategy() {
  const symbol = $("strategySymbol").value;
  const cfg = symbols[symbol];
  const preset = $("strategyPreset").value;
  const days = Number($("strategyDays").value);
  const offset = Number($("strikeOffset").value);
  const contracts = Number($("contractQty").value);
  const legs = getLegs(preset, cfg.spot, offset, contracts);
  drawPayoff($("pnlCanvas"), legs, cfg.spot, cfg.iv, days);
  const paths = monteCarlo(symbol, preset, days, offset, contracts, Number($("mcPaths").value), Number($("hedgeDays").value));
  drawHistogram($("mcCanvas"), paths);
  const mean = paths.reduce((a, b) => a + b, 0) / paths.length;
  $("mcCaption").textContent = `Mean hedged P&L ${money(mean)} across ${paths.length.toLocaleString()} paths. Wider hedge intervals increase path dependency.`;
  $("legsTable").innerHTML = `<table><thead><tr><th>Leg</th><th>Side</th><th>Qty</th><th>Strike</th><th>Entry</th><th>Delta</th><th>Prob ITM</th></tr></thead><tbody>${legs.map((leg) => {
    if (leg.type === "stock") return `<tr><td>Stock</td><td>${leg.side > 0 ? "Long" : "Short"}</td><td>${leg.qty}</td><td>-</td><td>${money(cfg.spot)}</td><td>${fmt(leg.side * leg.qty, 2)}</td><td>-</td></tr>`;
    const b = bsm({ S: cfg.spot, K: leg.strike, T: days / 365, sigma: cfg.iv, type: leg.type });
    return `<tr><td>${leg.type}</td><td>${leg.side > 0 ? "Long" : "Short"}</td><td>${leg.qty}</td><td>${money(leg.strike)}</td><td>${money(b.price)}</td><td>${fmt(b.delta, 3)}</td><td>${fmt(b.probabilityItm, 3)}</td></tr>`;
  }).join("")}</tbody></table>`;
}

function runBacktest() {
  const selected = Array.from($("basketSelect").querySelectorAll("input:checked")).map((option) => option.value);
  const basket = selected.length ? selected : [$("strategySymbol").value];
  const result = basket.map((symbol) => runBacktestForSymbol(
    symbol,
    $("strategyPreset").value,
    Number($("strategyDays").value),
    Number($("strikeOffset").value),
    Number($("contractQty").value),
    Number($("capitalInput").value)
  ));
  state.backtest = result;
  const combined = result[0].equity.map((_, i) => ({
    y: result.reduce((sum, item) => sum + (item.equity[i]?.y || item.ending), 0) / result.length
  }));
  drawLineChart($("backtestChart"), [
    { color: "#38bdf8", data: combined },
    ...result.slice(0, 4).map((item, i) => ({ color: ["#22c55e", "#f59e0b", "#818cf8", "#ef4444"][i], data: item.equity.map((p) => ({ y: p.y })), width: 1.3 }))
  ], { label: `Basket backtest: ${basket.join(", ")}` });
  const avg = (key) => result.reduce((sum, item) => sum + item[key], 0) / result.length;
  $("backtestMetrics").innerHTML = [
    ["Ending equity", money(combined[combined.length - 1].y)],
    ["CAGR", pct(avg("cagr"))],
    ["Sharpe", fmt(avg("sharpe"), 2)],
    ["Max drawdown", pct(avg("maxDd"))],
    ["Win rate", pct(avg("winRate"))],
    ["Average trade", money(avg("avgPnl"))],
    ["Stocks tested", String(result.length)],
    ["Short-vol warning", $("strategyPreset").value.includes("Short") || $("strategyPreset").value.includes("Underwriting") || $("strategyPreset").value.includes("Overwrite") ? "Equity-linked" : "Neutral"]
  ].map(([k, v]) => `<div class="metric"><small>${k}</small><strong>${v}</strong></div>`).join("");
}

function renderVolatility() {
  const symbol = $("surfaceSymbol").value;
  drawHeatmap($("volSurfaceCanvas"), symbol);
  const data = generateSeries(symbol);
  const rv = realizedVol(data);
  const vrp = data.map((d, i) => ({ y: (d.iv - rv[i]) * 100 }));
  drawLineChart($("vrpCanvas"), [{ color: "#f59e0b", data: vrp.slice(-220) }], { label: "IV - RV spread, vol points" });
  const volOfVol = Number($("volOfVol").value) / 100;
  const atmVol = symbols[symbol].iv;
  const varStrike = Math.sqrt(atmVol ** 2 + 0.25 * volOfVol ** 2 * atmVol ** 2);
  const spread = varStrike - atmVol;
  $("varianceMetrics").innerHTML = [
    ["Vol swap strike", pct(atmVol)],
    ["Variance strike", pct(varStrike)],
    ["Convexity premium", `${fmt(spread * 100, 2)} pts`],
    ["Vol-of-vol", pct(volOfVol)]
  ].map(([k, v]) => `<div class="metric"><small>${k}</small><strong>${v}</strong></div>`).join("");
  drawLineChart($("varianceCanvas"), [
    { color: "#38bdf8", data: Array.from({ length: 40 }, (_, i) => ({ y: atmVol + i * spread / 39 })) },
    { color: "#f59e0b", data: Array.from({ length: 40 }, () => ({ y: atmVol })) }
  ], { label: "Variance strike sits above vol swap through Jensen convexity" });
  const curve = [18.2, 19.4, 20.6, 21.1, 21.8, 22.4].map((v, i) => ({ y: v + Math.sin(i + symbols[symbol].beta) }));
  drawLineChart($("vixCanvas"), [{ color: "#818cf8", data: curve }], { label: "Synthetic VIX futures curve" });
  $("vixCaption").textContent = `Front-to-sixth month roll drag estimate: ${fmt((curve[curve.length - 1].y - curve[0].y) / curve[0].y * 100, 1)}% before spot VIX movement.`;
}

function renderEducation() {
  const lessons = [
    ["Delta is not probability", "Delta uses N(d1), while expiry probability uses N(d2). The gap grows with tenor and volatility.", "0.53 delta can pair with 0.47 probability."],
    ["The volatility risk premium", "Implied volatility often exceeds subsequent realized volatility because sellers are taking equity crash exposure.", "Short vol is not independent income."],
    ["Variance beats volatility", "Variance swap strikes exceed vol swap strikes when vol-of-vol exists because convexity rewards dispersion.", "Jensen's gap must be visible."],
    ["The VIX roll trap", "Contango means long VIX products can lose value while spot volatility merely sits still.", "Roll cost is part of the trade."],
    ["Skew regimes", "Long skew tends to need jumpy volatility. Sticky delta and sticky strike regimes can punish the carry.", "Regime matters more than label."],
    ["Discrete hedging", "Cheap volatility is not automatically profitable when hedging happens in chunks instead of continuously.", "Path dependency is the bill."]
  ];
  $("lessonGrid").innerHTML = lessons.map((lesson, idx) => {
    const bars = Array.from({ length: 12 }, (_, i) => `<span style="height:${18 + 45 * seededRandom(idx * 19 + i * 7)}px"></span>`).join("");
    return `<article class="lesson-card"><p class="eyebrow">Lesson ${idx + 1}</p><h2>${lesson[0]}</h2><p>${lesson[1]}</p><strong>${lesson[2]}</strong><div class="mini-viz">${bars}</div></article>`;
  }).join("");
}

function renderAll() {
  renderMarketStrip();
  renderDashboard();
  renderGreeks();
  renderStrategy();
  if (!state.backtest) runBacktest();
  renderVolatility();
  renderEducation();
}

function bindEvents() {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".nav-item").forEach((el) => el.classList.remove("is-active"));
      document.querySelectorAll(".view").forEach((el) => el.classList.remove("is-visible"));
      button.classList.add("is-active");
      $(button.dataset.view).classList.add("is-visible");
      $("pageTitle").textContent = button.textContent;
      state.view = button.dataset.view;
    });
  });
  ["quickSymbol", "greekSymbol", "strategySymbol", "surfaceSymbol"].forEach((id) => {
    $(id).addEventListener("change", () => {
      state.symbol = $(id).value;
      ["quickSymbol", "greekSymbol", "strategySymbol", "surfaceSymbol"].forEach((other) => { $(other).value = state.symbol; });
      $("strikeInput").value = Math.round(symbols[state.symbol].spot);
      renderAll();
    });
  });
  ["optionType", "strikeInput", "daysInput", "ivInput", "rateInput"].forEach((id) => $(id).addEventListener("input", renderGreeks));
  ["strategySymbol", "strategyPreset", "strategyDays", "strikeOffset", "contractQty", "mcPaths", "hedgeDays"].forEach((id) => $(id).addEventListener("input", renderStrategy));
  $("runBacktest").addEventListener("click", runBacktest);
  $("volOfVol").addEventListener("input", renderVolatility);
  $("surfaceSymbol").addEventListener("change", renderVolatility);
  $("copyResults").addEventListener("click", async () => {
    const payload = JSON.stringify(state.backtest, null, 2);
    await navigator.clipboard.writeText(payload);
    $("copyResults").textContent = "Copied";
    setTimeout(() => { $("copyResults").textContent = "Copy data"; }, 1200);
  });
  window.addEventListener("resize", () => renderAll());
  document.addEventListener("keydown", (event) => {
    const items = Array.from(document.querySelectorAll(".nav-item"));
    const index = items.findIndex((item) => item.classList.contains("is-active"));
    if (event.key.toLowerCase() === "j") items[Math.min(items.length - 1, index + 1)].click();
    if (event.key.toLowerCase() === "k") items[Math.max(0, index - 1)].click();
  });
}

populateSelects();
bindEvents();
renderAll();
