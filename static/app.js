const form = document.querySelector("#vocabulary-form");
const list = document.querySelector("#vocabulary-list");
const table = document.querySelector("table");
const emptyState = document.querySelector("#empty-state");
const count = document.querySelector("#count");
const message = document.querySelector("#form-message");

async function loadVocabulary() {
  const response = await fetch("/api/vocabulary");
  const entries = await response.json();
  list.replaceChildren(...entries.map((entry) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td><strong>${entry.kanji}</strong></td><td>${entry.reading}</td><td>${entry.meaning}</td><td>${entry.partOfSpeech}</td><td><span class="status">${entry.status}</span></td>`;
    return row;
  }));
  table.hidden = entries.length === 0;
  emptyState.hidden = entries.length > 0;
  count.textContent = `${entries.length} word${entries.length === 1 ? "" : "s"}`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const response = await fetch("/api/vocabulary", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(Object.fromEntries(new FormData(form))),
  });
  if (!response.ok) {
    message.textContent = "Please complete every field.";
    return;
  }
  form.reset();
  message.textContent = "Saved.";
  await loadVocabulary();
});

loadVocabulary().catch(() => { message.textContent = "Could not load vocabulary."; });