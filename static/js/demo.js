(() => {
  const messagesEl = document.getElementById("chatMessages");
  const inputEl = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const runBtn = document.getElementById("runScenarioBtn");
  const kbSearch = document.getElementById("kbSearch");
  const kbResults = document.getElementById("kbResults");

  let history = [];
  let busy = false;
  let businessId = typeof CURRENT_BUSINESS_ID !== "undefined" ? CURRENT_BUSINESS_ID : "abc-construction";

  function appendBubble(text, who) {
    const div = document.createElement("div");
    div.className = `bubble bubble-${who}`;
    div.textContent = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function setTyping(on) {
    let el = document.getElementById("typingInd");
    if (on) {
      if (!el) {
        el = document.createElement("div");
        el.id = "typingInd";
        el.className = "typing";
        el.textContent = "AI yazır…";
        messagesEl.appendChild(el);
      }
    } else if (el) {
      el.remove();
    }
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function updateMeta(data) {
    document.getElementById("metaIntent").textContent = data.detected_intent || "—";
    const conf = Math.round((data.confidence || 0) * 100);
    document.getElementById("metaConf").textContent = conf + "%";
    document.getElementById("confBar").style.width = conf + "%";
    document.getElementById("metaHuman").textContent = data.requires_human ? "Bəli" : "Xeyr";
    const badge = document.getElementById("leadBadge");
    badge.style.display = data.lead_potential ? "block" : "none";

    const rel = document.getElementById("relevantItems");
    const items = data.relevant_items || [];
    if (!items.length) {
      rel.innerHTML = '<span class="muted">Uyğun KB tapılmadı</span>';
    } else {
      rel.innerHTML =
        "<strong>Relevant KB</strong><ul style='margin:0.35rem 0 0;padding-left:1.1rem;'>" +
        items
          .slice(0, 4)
          .map((i) => `<li>${i.title} <span class="muted">(${i.score})</span></li>`)
          .join("") +
        "</ul>";
    }
  }

  async function sendMessage(text, { forceAbc = false } = {}) {
    if (!text || busy) return;
    busy = true;
    sendBtn.disabled = true;
    appendBubble(text, "customer");
    history.push(text);
    inputEl.value = "";
    setTyping(true);

    try {
      const res = await fetch("/api/demo/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": window.csrfToken,
        },
        body: JSON.stringify({
          business_id: forceAbc ? "abc-construction" : businessId,
          message: text,
          history: history.slice(0, -1),
          force_abc_scenario: forceAbc,
        }),
      });
      const data = await res.json();
      setTyping(false);
      if (data.skipped_reply || data.should_reply === false || !data.answer) {
        updateMeta(data);
      } else {
        appendBubble(data.answer, "ai");
        updateMeta(data);
      }
      if (data.toast) showToast(data.toast);
      if (forceAbc) {
        businessId = "abc-construction";
        const sel = document.getElementById("businessSelect");
        if (sel) sel.value = "abc-construction";
        const nameEl = document.getElementById("chatBizName");
        if (nameEl) nameEl.textContent = "ABC Construction";
      }
    } catch (err) {
      setTyping(false);
      appendBubble("Xəta baş verdi. Yenidən cəhd edin.", "ai");
      console.error(err);
    } finally {
      busy = false;
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  sendBtn?.addEventListener("click", () => sendMessage(inputEl.value.trim()));
  inputEl?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage(inputEl.value.trim());
  });

  runBtn?.addEventListener("click", async () => {
    if (busy) return;
    // Reset demo conversation for scenario
    await fetch("/api/business/switch/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": window.csrfToken,
      },
      body: JSON.stringify({ business_id: "abc-construction" }),
    });
    businessId = "abc-construction";
    history = [];
    messagesEl.innerHTML = "";
    const steps = Array.isArray(SCENARIO) ? SCENARIO : [];
    for (const step of steps) {
      await sendMessage(step, { forceAbc: true });
      await new Promise((r) => setTimeout(r, 350));
    }
  });

  let kbTimer;
  kbSearch?.addEventListener("input", () => {
    clearTimeout(kbTimer);
    kbTimer = setTimeout(async () => {
      const q = kbSearch.value.trim();
      if (!q) {
        kbResults.textContent = "";
        return;
      }
      const res = await fetch(`/api/knowledge/?q=${encodeURIComponent(q)}&business_id=${businessId}`);
      const data = await res.json();
      if (!data.length) {
        kbResults.textContent = "Nəticə yoxdur";
        return;
      }
      kbResults.innerHTML = data
        .slice(0, 5)
        .map((i) => `<div style="padding:0.35rem 0;border-top:1px solid var(--line);"><strong>${i.title}</strong><div class="muted">${(i.content || "").slice(0, 120)}</div></div>`)
        .join("");
    }, 250);
  });

  // Welcome line
  appendBubble("Salam! Sualınızı yazın və ya Demo Ssenari düyməsini basın.", "ai");
})();
