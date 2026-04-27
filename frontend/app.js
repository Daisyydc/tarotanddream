const body = document.body;
const starsCanvas = document.getElementById("starsCanvas");
const introSequence = document.getElementById("introSequence");
const introCardOrbit = document.getElementById("introCardOrbit");
const skipIntroBtn = document.getElementById("skipIntroBtn");
const modeCard = document.getElementById("modeCard");
const rotateModeBtn = document.getElementById("rotateModeBtn");
const modeTip = document.getElementById("modeTip");
const modeCardZone = document.getElementById("modeCardZone");
const scrollPanel = document.getElementById("scrollPanel");
const scrollKicker = document.getElementById("scrollKicker");
const scrollTitle = document.getElementById("scrollTitle");
const scrollBody = document.getElementById("scrollBody");
const backToModeBtn = document.getElementById("backToModeBtn");
const transitionOverlay = document.getElementById("transitionOverlay");
const transitionClockWrap = document.getElementById("transitionClockWrap");
const transitionClock = document.getElementById("transitionClock");
const transitionText = document.getElementById("transitionText");
const selectedCardOverlay = document.getElementById("selectedCardOverlay");
const selectedCardShell = document.getElementById("selectedCardShell");
const selectedCardCaption = document.getElementById("selectedCardCaption");

const tplTarotForm = document.getElementById("tpl-tarot-form");
const tplDreamForm = document.getElementById("tpl-dream-form");

const LOADING_TEXTS = [
  "命运的纹路正在这张牌上慢慢显现……",
  "请先别移开视线，回应正在从灰烬里聚拢……",
  "金色的光还在重组，下一层信息马上浮现……"
];

const state = {
  activeMode: "tarot",
  cardFlipped: false,
  tarotSession: null,
  selectedGroup: "",
  tarotQuestion: "",
  stage: "intro",
  introFinished: false,
  introTimers: []
};

function postJSON(url, data) {
  return fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  }).then(async (resp) => {
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(text || "请求失败");
    }
    return resp.json();
  });
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function cloneTemplate(tpl) {
  return tpl.content.cloneNode(true);
}

function normalizeText(text) {
  return (text || "").replace(/\r\n/g, "\n").trim();
}

function buildParticleText(text) {
  const wrapper = document.createElement("div");
  wrapper.className = "message-text";
  const normalized = normalizeText(text);
  let delay = 0;

  for (const char of normalized) {
    const span = document.createElement("span");
    span.className = "char";

    if (char === "\n") {
      span.classList.add("nl");
      span.textContent = "";
    } else if (char === " ") {
      span.classList.add("space");
      span.textContent = " ";
    } else {
      span.textContent = char;
    }

    span.style.animationDelay = `${delay}ms`;
    delay += char === "\n" ? 16 : 12;
    wrapper.appendChild(span);
  }

  return wrapper;
}

function buildMessageShell(text, { centered = false } = {}) {
  const shell = document.createElement("div");
  shell.className = `message-shell${centered ? " centered" : ""}`;
  shell.appendChild(buildParticleText(text));
  return shell;
}

function setScrollMeta(kicker, title) {
  scrollKicker.textContent = kicker;
  scrollTitle.textContent = title;
}

function showScroll({ forming = true } = {}) {
  modeCardZone.classList.add("hidden");
  scrollPanel.classList.remove("hidden");
  if (forming) {
    scrollPanel.classList.remove("is-forming");
    void scrollPanel.offsetWidth;
    scrollPanel.classList.add("is-forming");
  }
  body.classList.add("mode-open");
  backToModeBtn.classList.remove("hidden");
}

function hideScroll() {
  scrollPanel.classList.add("hidden");
  backToModeBtn.classList.add("hidden");
  body.classList.remove("mode-open");
}

function setModeTip() {
  modeTip.textContent = state.cardFlipped
    ? "当前是解梦模式。点击卡牌，开始解梦仪式。"
    : "当前是塔罗模式。点击卡牌，开启占卜仪式。";
}

function switchCardFace() {
  state.cardFlipped = !state.cardFlipped;
  state.activeMode = state.cardFlipped ? "dream" : "tarot";
  modeCard.classList.toggle("is-flipped", state.cardFlipped);
  setModeTip();
}

function renderTarotForm() {
  state.stage = "tarot_form";
  setScrollMeta("Tarot Ritual", "请写下你的问题");
  scrollBody.innerHTML = "";
  scrollBody.appendChild(cloneTemplate(tplTarotForm));
  showScroll({ forming: true });

  const tarotQuestion = scrollBody.querySelector("#tarotQuestion");
  const startTarotBtn = scrollBody.querySelector("#startTarotBtn");
  if (state.tarotQuestion) tarotQuestion.value = state.tarotQuestion;

  startTarotBtn.addEventListener("click", async () => {
    const question = tarotQuestion.value.trim();
    if (!question) {
      alert("请先输入你的问题。");
      return;
    }

    state.tarotQuestion = question;
    startTarotBtn.disabled = true;
    startTarotBtn.textContent = "命运之轮开始转动……";

    try {
      const data = await runSoftTransitionTask({
        text: "命运正在投影牌面……",
        minMs: 950,
        task: async () => {
          const result = await postJSON("/api/tarot/start", { question });
          state.tarotSession = result;
          state.selectedGroup = "";
          renderTarotChoose(result);
          return result;
        }
      });
      state.tarotSession = data;
    } catch (err) {
      alert("开始占卜失败：" + err.message);
    } finally {
      startTarotBtn.disabled = false;
      startTarotBtn.textContent = "开始塔罗仪式";
    }
  });
}

function createLoadingLine() {
  const line = document.createElement("div");
  line.className = "loading-line";
  line.innerHTML = `
    <span>${LOADING_TEXTS[Math.floor(Math.random() * LOADING_TEXTS.length)]}</span>
    <span class="loading-dots"><span></span><span></span><span></span></span>
  `;
  return line;
}

function extractBaseName(cardText) {
  return cardText.replace("正位", "").replace("逆位", "").trim();
}

function isReversed(cardText) {
  return cardText.startsWith("逆位");
}

function getCardImageSrc(cardText) {
  const baseName = extractBaseName(cardText);
  return `/frontend/assets/cards/${baseName}.jpg`;
}

function buildChoiceCard(groupName, group) {
  const wrap = document.createElement("div");
  wrap.className = "tarot-choice-card";
  wrap.dataset.group = groupName;

  const reversed = isReversed(group.signpost);
  const imageSrc = getCardImageSrc(group.signpost);

  wrap.innerHTML = `
    <div class="choice-badge">${groupName}</div>
    <div class="choice-visual">
      <img src="${imageSrc}" alt="${groupName}组指示牌" class="${reversed ? "reversed" : ""}" loading="lazy" />
    </div>
    <div class="choice-caption">第 ${groupName} 组</div>
    <div class="choice-note">不用先分析牌意，只看哪一张最先把你的注意力牵住。</div>
    <button class="primary-btn choice-action" type="button">选择这一组</button>
  `;

  const img = wrap.querySelector("img");
  img.addEventListener("error", () => {
    const fallback = document.createElement("div");
    fallback.className = "choice-fallback";
    fallback.textContent = "✦ 命运之牌 ✦";
    img.replaceWith(fallback);
  });

  return wrap;
}

function renderTarotChoose(data) {
  state.stage = "tarot_choose";
  setScrollMeta("Tarot Ritual", "选择最先吸引你的那一张");
  scrollBody.innerHTML = "";

  const stage = document.createElement("div");
  stage.className = "message-stage";
  stage.appendChild(buildMessageShell(data.assistant_message));

  const intro = document.createElement("div");
  intro.className = "ritual-copy";
  intro.innerHTML = `<p>先看画面、光线和你最直接的感觉。现在不要分析，先选择。</p>`;
  stage.appendChild(intro);

  const grid = document.createElement("div");
  grid.className = "tarot-group-grid";

  ["A", "B", "C"].forEach((groupName) => {
    const card = buildChoiceCard(groupName, data.groups[groupName]);
    const btn = card.querySelector("button");
    btn.addEventListener("click", async () => {
      if (!state.tarotSession) return;
      state.selectedGroup = groupName;

      grid.querySelectorAll(".tarot-choice-card").forEach((item) => {
        item.classList.toggle("is-active", item.dataset.group === groupName);
        item.classList.toggle("is-dimmed", item.dataset.group !== groupName);
      });

      const loadingLine = createLoadingLine();
      if (!stage.querySelector(".loading-line")) stage.appendChild(loadingLine);

      try {
        const result = await runSelectedCardTask({
          cardText: data.groups[groupName].signpost,
          caption: "命运正在显影……",
          minMs: 1450,
          settleMs: 180,
          task: () => postJSON("/api/tarot/select", {
            session_id: state.tarotSession.session_id,
            question: state.tarotSession.question,
            group: groupName,
            cards_text: state.tarotSession.groups[groupName].cards_text
          })
        });
        renderTarotVerify(result);
      } catch (err) {
        alert("选组失败：" + err.message);
        grid.querySelectorAll(".tarot-choice-card").forEach((item) => {
          item.classList.remove("is-active", "is-dimmed");
        });
      } finally {
        loadingLine.remove();
      }
    });
    grid.appendChild(card);
  });

  stage.appendChild(grid);
  scrollBody.appendChild(stage);
}

function renderTarotVerify(data) {
  state.stage = "tarot_verify";
  setScrollMeta("Tarot Resonance", "这组牌像不像你现在的状态？");
  scrollBody.innerHTML = "";

  const stage = document.createElement("div");
  stage.className = "message-stage";
  stage.appendChild(buildMessageShell(data.verification_message));

  const actions = document.createElement("div");
  actions.className = "scroll-actions";

  const continueBtn = document.createElement("button");
  continueBtn.className = "primary-btn";
  continueBtn.type = "button";
  continueBtn.textContent = "有共鸣，继续解读";

  const redrawBtn = document.createElement("button");
  redrawBtn.className = "secondary-btn";
  redrawBtn.type = "button";
  redrawBtn.textContent = "重新抽牌";

  continueBtn.addEventListener("click", async () => {
    if (!state.tarotSession || !state.selectedGroup) return;
    continueBtn.disabled = true;
    redrawBtn.disabled = true;
    try {
      await runSoftTransitionTask({
        text: "轮盘正在揭开下一层迷雾……",
        minMs: 900,
        task: async () => {
          const payload = await postJSON("/api/tarot/confirm", {
            session_id: state.tarotSession.session_id,
            question: state.tarotSession.question,
            group: state.selectedGroup,
            cards_text: state.tarotSession.groups[state.selectedGroup].cards_text
          });
          renderTarotFinal(payload.final_reading);
          return payload;
        }
      });
    } catch (err) {
      alert("生成最终解读失败：" + err.message);
    } finally {
      continueBtn.disabled = false;
      redrawBtn.disabled = false;
    }
  });

  redrawBtn.addEventListener("click", async () => {
    if (!state.tarotQuestion) return;
    continueBtn.disabled = true;
    redrawBtn.disabled = true;
    try {
      const data = await runSoftTransitionTask({
        text: "新的牌阵正在重新铺开……",
        minMs: 900,
        task: async () => {
          const result = await postJSON("/api/tarot/start", { question: state.tarotQuestion });
          state.tarotSession = result;
          state.selectedGroup = "";
          renderTarotChoose(result);
          return result;
        }
      });
      state.tarotSession = data;
    } catch (err) {
      alert("重新抽牌失败：" + err.message);
    } finally {
      continueBtn.disabled = false;
      redrawBtn.disabled = false;
    }
  });

  actions.append(continueBtn, redrawBtn);
  stage.appendChild(actions);
  scrollBody.appendChild(stage);
}

function renderTarotFinal(text) {
  state.stage = "tarot_final";
  setScrollMeta("Tarot Reading", "卷轴已经展开最后一层回应");
  scrollBody.innerHTML = "";

  const stage = document.createElement("div");
  stage.className = "message-stage";
  stage.appendChild(buildMessageShell(text));

  const actions = document.createElement("div");
  actions.className = "scroll-actions";

  const restartBtn = document.createElement("button");
  restartBtn.className = "secondary-btn";
  restartBtn.type = "button";
  restartBtn.textContent = "再问一个新问题";
  restartBtn.addEventListener("click", async () => {
    await runSoftTransitionTask({
      text: "命运正在把卷轴带回起点……",
      minMs: 780,
      task: async () => {
        renderTarotForm();
        return true;
      }
    });
  });

  actions.appendChild(restartBtn);
  stage.appendChild(actions);
  scrollBody.appendChild(stage);
}

function renderDreamForm() {
  state.stage = "dream_form";
  setScrollMeta("Dream Ritual", "请写下你的梦境");
  scrollBody.innerHTML = "";
  scrollBody.appendChild(cloneTemplate(tplDreamForm));
  showScroll({ forming: true });

  const dreamText = scrollBody.querySelector("#dreamText");
  const startDreamBtn = scrollBody.querySelector("#startDreamBtn");

  startDreamBtn.addEventListener("click", async () => {
    const text = dreamText.value.trim();
    if (!text) {
      alert("请先输入梦境描述。");
      return;
    }

    startDreamBtn.disabled = true;
    startDreamBtn.textContent = "梦境正在重组……";

    try {
      await runSoftTransitionTask({
        text: "梦里的碎片正在重新聚拢……",
        minMs: 900,
        task: async () => {
          const result = await postJSON("/api/dream/analyze", { dream_text: text });
          renderDreamResult(result.assistant_message);
          return result;
        }
      });
    } catch (err) {
      alert("解梦失败：" + err.message);
    } finally {
      startDreamBtn.disabled = false;
      startDreamBtn.textContent = "开始解梦";
    }
  });
}

function renderDreamResult(text) {
  state.stage = "dream_result";
  setScrollMeta("Dream Reading", "梦里的象征已经浮出表面");
  scrollBody.innerHTML = "";

  const stage = document.createElement("div");
  stage.className = "message-stage";
  stage.appendChild(buildMessageShell(text));

  const actions = document.createElement("div");
  actions.className = "scroll-actions";

  const againBtn = document.createElement("button");
  againBtn.className = "secondary-btn";
  againBtn.type = "button";
  againBtn.textContent = "换一个梦继续问";
  againBtn.addEventListener("click", async () => {
    await runSoftTransitionTask({
      text: "梦境正在回到入口……",
      minMs: 780,
      task: async () => {
        renderDreamForm();
        return true;
      }
    });
  });

  actions.appendChild(againBtn);
  stage.appendChild(actions);
  scrollBody.appendChild(stage);
}

function prepareSelectedMode() {
  if (state.activeMode === "tarot") {
    renderTarotForm();
  } else {
    renderDreamForm();
  }
}

function resetToModeCard() {
  hideScroll();
  scrollBody.innerHTML = "";
  modeCardZone.classList.remove("hidden");
  state.stage = "landing";
}

async function runSoftTransitionTask({ text = "命运正在整理牌面……", direction = "forward", minMs = 1450, settleMs = 220, task }) {
  transitionText.textContent = text;
  transitionClockWrap.classList.remove("swing-forward", "swing-backward", "is-running");
  transitionClock.classList.remove("spin-forward", "spin-backward", "is-running");
  void transitionClock.offsetWidth;
  void transitionClockWrap.offsetWidth;
  const dirClass = direction === "backward" ? "backward" : "forward";
  transitionClockWrap.classList.add(`swing-${dirClass}`, "is-running");
  transitionClock.classList.add(`spin-${dirClass}`, "is-running");

  body.classList.add("transition-active");
  transitionOverlay.classList.remove("hidden");
  requestAnimationFrame(() => transitionOverlay.classList.add("active"));

  const startedAt = performance.now();
  try {
    const result = await task();
    const elapsed = performance.now() - startedAt;
    if (elapsed < minMs) {
      await sleep(minMs - elapsed);
    }
    await sleep(settleMs);
    return result;
  } finally {
    transitionOverlay.classList.remove("active");
    await sleep(420);
    transitionClockWrap.classList.remove("swing-forward", "swing-backward", "is-running");
    transitionClock.classList.remove("spin-forward", "spin-backward", "is-running");
    transitionOverlay.classList.add("hidden");
    body.classList.remove("transition-active");
  }
}

async function runSelectedCardTask({ cardText, caption, minMs = 1450, settleMs = 180, task }) {
  body.classList.add("scene-blur-active");
  selectedCardCaption.textContent = caption;
  selectedCardShell.classList.remove("is-running");

  const reversed = isReversed(cardText);
  const src = getCardImageSrc(cardText);
  selectedCardShell.innerHTML = `<img src="${src}" alt="选中的牌" class="${reversed ? "reversed" : ""}" />`;

  const img = selectedCardShell.querySelector("img");
  img.addEventListener("error", () => {
    selectedCardShell.innerHTML = `<div class="choice-fallback">✦ 命运之牌 ✦</div>`;
  }, { once: true });

  selectedCardOverlay.classList.remove("hidden");
  requestAnimationFrame(() => {
    selectedCardOverlay.classList.add("active");
    selectedCardShell.classList.add("is-running");
  });

  const startedAt = performance.now();
  try {
    const result = await task();
    const elapsed = performance.now() - startedAt;
    if (elapsed < minMs) {
      await sleep(minMs - elapsed);
    }
    await sleep(settleMs);
    return result;
  } finally {
    selectedCardOverlay.classList.remove("active");
    await sleep(240);
    selectedCardShell.classList.remove("is-running");
    selectedCardOverlay.classList.add("hidden");
    body.classList.remove("scene-blur-active");
  }
}

function buildIntroCards() {
  introCardOrbit.innerHTML = "";
  const total = 22;
  const w = window.innerWidth;
  const h = window.innerHeight;
  const centerIndex = (total - 1) / 2;
  const stackSpread = Math.min(w * 0.0045, 4.5);
  const stackLift = Math.min(h * 0.26, 210);
  const spreadX = Math.min(w * 0.022, 26);
  const spreadLift = Math.min(h * 0.11, 96);
  const fanRadiusX = Math.min(w * 0.205, 250);
  const fanRadiusY = Math.min(h * 0.16, 150);
  const sweepRadiusX = Math.min(w * 0.19, 230);
  const sweepDrop = Math.min(h * 0.15, 160);

  for (let i = 0; i < total; i += 1) {
    const card = document.createElement("div");
    card.className = "intro-card";
    const progress = total === 1 ? 0 : i / (total - 1);
    const side = progress * 2 - 1;
    const stackOffset = (i - centerIndex) * stackSpread;

    const spreadOffsetX = (i - centerIndex) * spreadX;
    const spreadOffsetY = Math.abs(i - centerIndex) * 0.75;
    const spreadRotate = side * 6;

    const fanAngleDeg = -76 + progress * 152;
    const fanAngleRad = fanAngleDeg * Math.PI / 180;
    const fanX = Math.sin(fanAngleRad) * fanRadiusX;
    const fanY = Math.cos(fanAngleRad) * fanRadiusY - spreadLift;
    const fanRotate = -26 + progress * 52;

    const sweepX = side * sweepRadiusX;
    const sweepY = Math.abs(side) * 24 + sweepDrop;
    const sweepRotate = -16 + progress * 32;
    const delay = Math.abs(i - centerIndex) * 12;

    card.style.setProperty("--stack-offset", `${stackOffset}px`);
    card.style.setProperty("--stack-y", `${stackLift}px`);
    card.style.setProperty("--spread-x", `${spreadOffsetX}px`);
    card.style.setProperty("--spread-y", `${spreadOffsetY}px`);
    card.style.setProperty("--spread-rotate", `${spreadRotate}deg`);
    card.style.setProperty("--fan-x", `${fanX}px`);
    card.style.setProperty("--fan-y", `${fanY}px`);
    card.style.setProperty("--fan-rotate", `${fanRotate}deg`);
    card.style.setProperty("--sweep-x", `${sweepX}px`);
    card.style.setProperty("--sweep-y", `${sweepY}px`);
    card.style.setProperty("--sweep-rotate", `${sweepRotate}deg`);
    card.style.setProperty("--delay", `${delay}ms`);
    introCardOrbit.appendChild(card);
  }
}

function clearIntroTimers() {
  state.introTimers.forEach((id) => clearTimeout(id));
  state.introTimers = [];
}

function finishIntro() {
  if (state.introFinished) return;
  state.introFinished = true;
  clearIntroTimers();
  introSequence.classList.add("is-fading");
  body.classList.add("intro-complete");
  state.stage = "landing";

  setTimeout(() => {
    introSequence.classList.add("hidden");
  }, 320);
  modeCardZone.classList.remove("hidden");
}

function startIntro() {
  buildIntroCards();
  introSequence.classList.remove("hidden", "is-fading", "is-running");
  state.introFinished = false;
  state.stage = "intro";
  body.classList.remove("intro-complete");

  requestAnimationFrame(() => introSequence.classList.add("is-running"));

  state.introTimers.push(setTimeout(finishIntro, 4550));
}

function initStars() {
  const ctx = starsCanvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  let stars = [];
  let w = 0;
  let h = 0;

  function resize() {
    w = window.innerWidth;
    h = window.innerHeight;
    starsCanvas.width = Math.floor(w * dpr);
    starsCanvas.height = Math.floor(h * dpr);
    starsCanvas.style.width = `${w}px`;
    starsCanvas.style.height = `${h}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const count = Math.min(240, Math.max(120, Math.floor((w * h) / 9800)));
    stars = Array.from({ length: count }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      r: Math.random() * 1.4 + 0.35,
      a: Math.random() * 0.7 + 0.18,
      s: Math.random() * 0.14 + 0.025,
      vx: (Math.random() - 0.5) * 0.04
    }));

    if (!state.introFinished) buildIntroCards();
  }

  function drawNebula() {
    const nebulae = [
      { x: w * 0.5, y: h * 0.24, r: Math.min(w, h) * 0.26, color: "rgba(171, 112, 255, 0.05)" },
      { x: w * 0.34, y: h * 0.66, r: Math.min(w, h) * 0.22, color: "rgba(79, 116, 255, 0.04)" },
      { x: w * 0.66, y: h * 0.74, r: Math.min(w, h) * 0.24, color: "rgba(255, 112, 70, 0.05)" }
    ];

    for (const item of nebulae) {
      const g = ctx.createRadialGradient(item.x, item.y, 0, item.x, item.y, item.r);
      g.addColorStop(0, item.color);
      g.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(item.x, item.y, item.r, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function frame() {
    ctx.clearRect(0, 0, w, h);
    drawNebula();

    for (const star of stars) {
      star.y += star.s;
      star.x += star.vx;
      if (star.y > h + 4) {
        star.y = -4;
        star.x = Math.random() * w;
      }
      if (star.x < -4) star.x = w + 4;
      if (star.x > w + 4) star.x = -4;

      ctx.beginPath();
      ctx.fillStyle = `rgba(255, 241, 198, ${star.a})`;
      ctx.shadowBlur = 10;
      ctx.shadowColor = "rgba(255, 215, 128, 0.28)";
      ctx.arc(star.x, star.y, star.r, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.shadowBlur = 0;
    requestAnimationFrame(frame);
  }

  resize();
  frame();
  window.addEventListener("resize", resize);
}

skipIntroBtn.addEventListener("click", finishIntro);
rotateModeBtn.addEventListener("click", switchCardFace);
modeCard.addEventListener("click", async () => {
  await runSoftTransitionTask({
    direction: state.activeMode === "tarot" ? "forward" : "backward",
    text: state.activeMode === "tarot" ? "嘀嗒……嘀嗒……" : "嘀嗒……嘀嗒……",
    minMs: 1500,
    task: async () => {
      prepareSelectedMode();
      return true;
    }
  });
});
backToModeBtn.addEventListener("click", resetToModeCard);

setModeTip();
initStars();
startIntro();
