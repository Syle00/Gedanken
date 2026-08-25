// Smoke-Test fuer die Render-Funktionen in tools/dashboard.html.
// Laeuft ohne Browser: minimaler DOM-Stub, echtes /api/state (Server muss laufen).
// Aufruf: node tools/test_dashboard_html.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert";

const html = readFileSync("tools/dashboard.html", "utf-8");
const js = html.slice(html.lastIndexOf("<script>") + 8, html.lastIndexOf("</script>"));

const panels = {};
function machSection(id) {
  const kopf = { querySelector: () => null, append: () => {} };
  const inhalt = { set innerHTML(v) { panels[id] = v; }, get innerHTML() { return panels[id]; } };
  return { querySelector: (s) => (s === "h2" ? kopf : inhalt) };
}
const kopfEl = { textContent: "", innerHTML: "" };
const datenEl = { textContent: "", innerHTML: "" };
globalThis.document = {
  getElementById: (id) =>
    id === "kopf" ? kopfEl : id === "daten" ? datenEl : machSection(id),
  createElement: () => ({ className: "", textContent: "" }),
};
globalThis.setInterval = () => {};
globalThis.window = { prompt: () => null };

const state = await (await fetch("http://127.0.0.1:8787/api/state")).json();
globalThis.fetch = async () => ({ json: async () => state });

const mod = new Function(js + ';globalThis.__tick = tick;');
mod();
await globalThis.__tick();

assert.match(kopfEl.textContent, /·\s*NY\s*\d\d:\d\d/, "Kopfzeile ohne NY-Zeit: " + kopfEl.textContent);
assert.ok(datenEl.innerHTML.includes("1s bis"), "Datenabdeckung fehlt: " + datenEl.innerHTML);
for (const id of ["p-heute", "p-markt", "p-runs"])
  assert.ok(panels[id] && panels[id].length > 10, `Panel ${id} leer`);
// Fehler eines Panels reisst die anderen nicht mit
const kaputt = { ...state, markt: { data: null, error: "Testfehler", age_s: 0 } };
globalThis.fetch = async () => ({ json: async () => kaputt });
await globalThis.__tick();
assert.ok(panels["p-markt"].includes("Testfehler"), "Fehlertext fehlt");
assert.ok(panels["p-heute"].length > 10, "Heute-Panel mitgerissen");
console.log("dashboard.html: alle Checks bestanden");
