const BASE = "http://localhost:8000";

/* ---------- Predict ---------- */
document.getElementById("predictBtn").addEventListener("click", predict);

async function predict() {
  const text = document.getElementById("predictInput").value;

  const res = await fetch(`${BASE}/predict?review=${encodeURIComponent(text)}`, {
    method: "POST"
  });

  const data = await res.json();
  document.getElementById("predictResult").innerHTML =
    `Sentiment: <b>${data.sentiment}</b>`;
}

/* ---------- Chat ---------- */
document.getElementById("chatBtn").addEventListener("click", chat);

async function chat() {
  const text = document.getElementById("chatInput").value;

  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_input: text })
  });

  const data = await res.json();
  document.getElementById("chatResult").innerHTML =
    `<b>Sentiment:</b> ${data.sentiment}<br><br><b>AI:</b> ${data.reply}`;
}

/* ---------- File Upload ---------- */
document.getElementById("fileBtn").addEventListener("click", analyzeFile);

async function analyzeFile() {
  const file = document.getElementById("fileInput").files[0];
  if (!file) return alert("Upload file first");

  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${BASE}/analyze-file`, {
    method: "POST",
    body: form
  });

  const data = await res.json();
  renderFileResults(data);
}

function renderFileResults(data) {
  const i = data.insights;

  document.getElementById("fileResult").innerHTML = `
    <h3>Statistics</h3>
    <div class="stats">
      <span class="good">Good: ${data.statistics.good}</span>
      <span class="neutral">Neutral: ${data.statistics.neutral}</span>
      <span class="bad">Bad: ${data.statistics.bad}</span>
      <span>Total: ${data.statistics.total_reviews}</span>
    </div>

    <h3>Summary</h3>
    <p>${i.summary}</p>

    <h3>Strengths</h3>
    <ul>${i.strengths.map(x=>`<li>${x}</li>`).join("")}</ul>

    <h3>Weaknesses</h3>
    <ul>${i.weaknesses.map(x=>`<li>${x}</li>`).join("")}</ul>

    <h3>Recommendations</h3>
    <ul>${i.recommendations.map(x=>`<li>${x}</li>`).join("")}</ul>

    <h3>Trends</h3>
    <p><b>Positive:</b> ${i.trends.positive}</p>
    <p><b>Negative:</b> ${i.trends.negative}</p>
  `;
}

/* ---------- History ---------- */
document.getElementById("historyBtn").addEventListener("click", loadHistory);

async function loadHistory() {
  const res = await fetch(`${BASE}/history`);
  const data = await res.json();

  const list = document.getElementById("historyList");
  list.innerHTML = "";

  data.forEach(h => {
    const li = document.createElement("li");
    li.innerHTML = `<b>${h.sentiment}</b> — ${h.user_input}`;
    list.appendChild(li);
  });
}
