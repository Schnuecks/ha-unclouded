// Unclouded sidebar panel. Plain web component without build step or dependencies;
// it talks to the integration through the unclouded/* WebSocket commands.

const STRINGS = {
  en: {
    intro: "What keeps working in your Home Assistant when the internet is down.",
    refresh: "Check again",
    verdict_fails: "Stops working",
    verdict_degraded: "Works partly",
    verdict_unknown: "Not sure",
    verdict_works: "Keeps working",
    hint_fails: "These automations do nothing without the internet.",
    hint_degraded: "These run, but some of their parts do not get through.",
    hint_unknown: "Nothing here is known to need the internet, but some parts could not be checked.",
    hint_works: "These only use things inside your home.",
    onlyNotifications: "only notifications",
    open: "Open",
    markImportant: "Mark as important: Home Assistant then reports under Repairs when it needs the internet",
    unmarkImportant: "Marked as important; click to remove",
    decide: "Please decide",
    decideHint:
      "These integrations do not say how they connect. If you know, choose it here; the automations are judged again right away.",
    automatic: "Automatic",
    choice_local: "Local",
    choice_cloud: "Cloud",
    choice_partial: "Partly local",
    yourChoice: "your choice",
    integrationNoEntry: "entities without config entry",
    none: "None.",
    part_trigger: "Trigger",
    part_condition: "Condition",
    part_action: "Action",
    via: "via",
    integrations: "Integrations",
    integrationsHint: "How each set-up integration connects. Automations are judged on this basis.",
    reach_cloud: "Cloud",
    reach_partial: "Partly local",
    reach_unknown: "Unknown",
    reach_local: "Local",
    reach_internal: "Inside Home Assistant",
    noAutomations: "There are no automations yet.",
    error: "Error",
    reasons: {
      iot_class_local: "talks to devices in your network",
      iot_class_cloud: "talks to a cloud service",
      iot_class_calculated: "computed inside Home Assistant",
      iot_class_missing: "the integration does not say how it connects",
      sonoff_local: "set up in local mode",
      sonoff_auto: "set up in auto mode: local for devices with LAN control, otherwise cloud",
      sonoff_cloud: "set up in cloud mode",
      xiaomi_miot_local: "set up in local mode",
      xiaomi_miot_auto: "set up in auto mode: local or cloud depending on device and value",
      xiaomi_miot_cloud: "set up in cloud mode",
      mobile_app: "local while the phone is at home, over the internet when it is away",
      mobile_app_presence: "the phone reports its position over the internet while away",
      mobile_app_push_relay: "push notifications go through a relay server on the internet",
      mobile_app_local_push: "arrives over local push while the phone is at home",
      mobile_app_no_push: "the phone has no way to receive push notifications",
      known_cloud: "uses a cloud service, whatever the integration declares",
      notify_unknown: "could not find out which integration sends this",
      entry_missing: "the integration behind it is no longer set up",
      device_missing: "the device no longer exists",
      user_override: "chosen by you",
    },
  },
  de: {
    intro: "Was in deinem Home Assistant weiterläuft, wenn das Internet weg ist.",
    refresh: "Neu prüfen",
    verdict_fails: "Fällt aus",
    verdict_degraded: "Läuft teilweise",
    verdict_unknown: "Unklar",
    verdict_works: "Läuft weiter",
    hint_fails: "Diese Automationen bewirken ohne Internet nichts.",
    hint_degraded: "Diese laufen, aber manche ihrer Teile kommen nicht durch.",
    hint_unknown: "Nichts davon braucht bekanntermaßen Internet, aber manche Teile ließen sich nicht prüfen.",
    hint_works: "Diese nutzen nur, was bei dir zu Hause ist.",
    onlyNotifications: "nur Benachrichtigungen",
    open: "Öffnen",
    markImportant: "Als wichtig markieren: Home Assistant meldet dann unter Reparaturen, wenn sie Internet braucht",
    unmarkImportant: "Als wichtig markiert; Klick nimmt die Markierung weg",
    decide: "Bitte festlegen",
    decideHint:
      "Diese Integrationen geben nicht an, wie sie sich verbinden. Wenn du es weißt, wähle es hier; die Automationen werden sofort neu bewertet.",
    automatic: "Automatisch",
    choice_local: "Lokal",
    choice_cloud: "Cloud",
    choice_partial: "Teilweise lokal",
    yourChoice: "deine Wahl",
    integrationNoEntry: "Entitäten ohne Einrichtung",
    none: "Keine.",
    part_trigger: "Auslöser",
    part_condition: "Bedingung",
    part_action: "Aktion",
    via: "über",
    integrations: "Integrationen",
    integrationsHint: "Wie sich jede eingerichtete Integration verbindet. Darauf beruht die Bewertung der Automationen.",
    reach_cloud: "Cloud",
    reach_partial: "Teilweise lokal",
    reach_unknown: "Unbekannt",
    reach_local: "Lokal",
    reach_internal: "In Home Assistant",
    noAutomations: "Es gibt noch keine Automationen.",
    error: "Fehler",
    reasons: {
      iot_class_local: "spricht mit Geräten im eigenen Netz",
      iot_class_cloud: "spricht mit einem Cloud-Dienst",
      iot_class_calculated: "wird in Home Assistant berechnet",
      iot_class_missing: "die Integration gibt nicht an, wie sie sich verbindet",
      sonoff_local: "im lokalen Modus eingerichtet",
      sonoff_auto: "im Auto-Modus eingerichtet: lokal für Geräte mit LAN-Steuerung, sonst Cloud",
      sonoff_cloud: "im Cloud-Modus eingerichtet",
      xiaomi_miot_local: "im lokalen Modus eingerichtet",
      xiaomi_miot_auto: "im Auto-Modus eingerichtet: je nach Gerät und Wert lokal oder Cloud",
      xiaomi_miot_cloud: "im Cloud-Modus eingerichtet",
      mobile_app: "lokal, solange das Handy zu Hause ist, unterwegs über das Internet",
      mobile_app_presence: "das Handy meldet seinen Standort unterwegs über das Internet",
      mobile_app_push_relay: "Push-Nachrichten laufen über einen Relay-Server im Internet",
      mobile_app_local_push: "kommt per lokalem Push an, solange das Handy zu Hause ist",
      mobile_app_no_push: "das Handy kann keine Push-Nachrichten empfangen",
      known_cloud: "nutzt einen Cloud-Dienst, egal was die Integration angibt",
      notify_unknown: "unklar, welche Integration das verschickt",
      entry_missing: "die Integration dahinter ist nicht mehr eingerichtet",
      device_missing: "das Gerät gibt es nicht mehr",
      user_override: "von dir festgelegt",
    },
  },
};

const VERDICTS = ["fails", "degraded", "unknown", "works"];
const REACHES = ["cloud", "partial", "unknown", "local", "internal"];
const LOCAL = ["local", "internal"];

const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );

class UncloudedPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._automations = null;
    this._entries = [];
    this._overrides = {};
    this._error = null;
    this._open = new Set();
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) {
      this._render();
      this._load();
    }
  }

  set narrow(narrow) {
    const changed = this._narrow !== narrow;
    this._narrow = narrow;
    if (changed && this._hass) this._render();
  }

  get _t() {
    const lang = (this._hass?.language || "en").split("-")[0];
    return STRINGS[lang] || STRINGS.en;
  }

  async _load() {
    try {
      const [automations, entries] = await Promise.all([
        this._hass.callWS({ type: "unclouded/automations" }),
        this._hass.callWS({ type: "unclouded/entries" }),
      ]);
      this._automations = automations.automations;
      this._entries = entries.entries;
      this._overrides = entries.overrides || {};
      this._error = null;
    } catch (err) {
      this._error = err.message || String(err);
    }
    this._render();
  }

  _reason(code) {
    return this._t.reasons[code] || code;
  }

  _entry(entryId) {
    return this._entries.find((e) => e.entry_id === entryId);
  }

  _refLabel(dep) {
    if (dep.kind === "device") {
      const d = this._hass.devices?.[dep.ref];
      return d ? d.name_by_user || d.name || dep.ref : dep.ref;
    }
    if (dep.kind === "entity") {
      const name = this._hass.states[dep.ref]?.attributes.friendly_name;
      return name ? `${name} (${dep.ref})` : dep.ref;
    }
    return dep.ref;
  }

  // One line per thing that needs the internet; the same thing used twice counts once.
  _problems(automation) {
    const seen = new Set();
    return automation.dependencies.filter((d) => {
      const key = `${d.part}|${d.ref}`;
      if (LOCAL.includes(d.reach) || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  _renderDependency(dep) {
    const t = this._t;
    const entry = dep.entry_id && this._entry(dep.entry_id);
    const via = entry ? ` ${esc(t.via)} ${esc(entry.title)}` : "";
    return `
      <li>
        <span class="part">${esc(t[`part_${dep.part}`])}</span>
        <code>${esc(this._refLabel(dep))}</code>${via}
        <span class="badge spaced ${esc(dep.reach)}">${esc(t[`reach_${dep.reach}`])}</span>
        <div class="muted">${esc(this._reason(dep.reason))}</div>
      </li>`;
  }

  _renderAutomation(automation) {
    const t = this._t;
    const problems = this._problems(automation);
    const link = automation.config_id
      ? `<a class="open" href="/config/automation/edit/${encodeURIComponent(automation.config_id)}">${esc(t.open)} ›</a>`
      : "";
    const flag = automation.only_notifications
      ? `<span class="badge note">${esc(t.onlyNotifications)}</span>`
      : "";
    const star = `<button class="star${automation.important ? " on" : ""}" data-important="${esc(automation.entity_id)}"
      title="${esc(automation.important ? t.unmarkImportant : t.markImportant)}">${automation.important ? "★" : "☆"}</button>`;
    const row = `${star}<span class="name">${esc(automation.name)}</span>${flag}${link}`;
    if (!problems.length) return `<li class="automation"><div class="row">${row}</div></li>`;
    const open = this._open.has(automation.entity_id) ? " open" : "";
    return `
      <li class="automation">
        <details data-id="${esc(automation.entity_id)}"${open}>
          <summary class="row">${row}</summary>
          <ul class="deps">${problems.map((d) => this._renderDependency(d)).join("")}</ul>
        </details>
      </li>`;
  }

  _renderVerdicts() {
    const t = this._t;
    if (!this._automations.length) return `<p class="muted">${esc(t.noAutomations)}</p>`;
    const groups = Object.fromEntries(VERDICTS.map((v) => [v, []]));
    for (const a of this._automations) groups[a.verdict].push(a);
    const byName = (a, b) => a.name.localeCompare(b.name);
    const tiles = VERDICTS.map(
      (v) => `
        <a class="tile ${v}${groups[v].length ? "" : " empty"}" href="#${v}">
          <span class="count">${groups[v].length}</span>
          <span>${esc(t[`verdict_${v}`])}</span>
        </a>`
    ).join("");
    const sections = VERDICTS.filter((v) => groups[v].length)
      .map(
        (v) => `
        <section class="card" id="${v}">
          <h2><span class="dot ${v}"></span>${esc(t[`verdict_${v}`])} · ${groups[v].length}</h2>
          <p class="muted">${esc(t[`hint_${v}`])}</p>
          <ul class="automations">
            ${groups[v].sort(byName).map((a) => this._renderAutomation(a)).join("")}
          </ul>
        </section>`
      )
      .join("");
    return `<div class="tiles">${tiles}</div>${sections}`;
  }

  // Select between what Unclouded found out and a choice of the user.
  _renderChoice(key, automatic, chosen) {
    const t = this._t;
    const options = [
      `<option value="">${esc(t.automatic)}: ${esc(t[`reach_${automatic}`])}</option>`,
      ...["local", "cloud", "partial"].map(
        (r) => `<option value="${r}"${chosen === r ? " selected" : ""}>${esc(t[`choice_${r}`])}</option>`
      ),
    ];
    return `<select class="choice${chosen ? " chosen" : ""}" data-override="${esc(key)}">${options.join("")}</select>`;
  }

  // Integrations nobody could classify: entries without iot_class and integrations
  // whose entities have no config entry. Ones already chosen stay listed to change them.
  _renderDecide() {
    const t = this._t;
    const rows = this._entries
      .filter((e) => e.automatic === "unknown")
      .map((e) => ({
        key: `entry:${e.entry_id}`,
        label: e.title,
        sub: e.domain,
        chosen: e.overridden ? e.reach : "",
      }));
    const domains = new Set();
    for (const a of this._automations)
      for (const d of a.dependencies)
        if (d.integration && (d.reach === "unknown" || this._overrides[`domain:${d.integration}`]))
          domains.add(d.integration);
    for (const domain of [...domains].sort())
      rows.push({
        key: `domain:${domain}`,
        label: domain,
        sub: t.integrationNoEntry,
        chosen: this._overrides[`domain:${domain}`] || "",
      });
    if (!rows.length) return "";
    return `
      <section class="card decide">
        <h2>${esc(t.decide)} · ${rows.length}</h2>
        <p class="muted">${esc(t.decideHint)}</p>
        <table>${rows
          .map(
            (r) => `
          <tr>
            <td>${esc(r.label)}<div class="muted">${esc(r.sub)}</div></td>
            <td>${this._renderChoice(r.key, "unknown", r.chosen)}</td>
          </tr>`
          )
          .join("")}</table>
      </section>`;
  }

  async _setOverride(key, reach) {
    await this._send({ type: "unclouded/set_override", key, reach: reach || null });
  }

  async _setImportant(entityId, important) {
    await this._send({ type: "unclouded/set_important", entity_id: entityId, important });
  }

  async _send(message) {
    try {
      await this._hass.callWS(message);
    } catch (err) {
      this._error = err.message || String(err);
      this._render();
      return;
    }
    await this._load();
  }

  _renderEntries() {
    const t = this._t;
    const rows = [...this._entries]
      .sort(
        (a, b) =>
          REACHES.indexOf(a.reach) - REACHES.indexOf(b.reach) || a.title.localeCompare(b.title)
      )
      .map(
        (e) => `
        <tr>
          <td>${esc(e.title)}<div class="muted">${esc(e.domain)}</div></td>
          <td>${this._renderChoice(`entry:${e.entry_id}`, e.automatic, e.overridden ? e.reach : "")}</td>
          <td class="muted">${esc(this._reason(e.reason))}</td>
        </tr>`
      )
      .join("");
    return `
      <details class="card" id="entries">
        <summary><h2>${esc(t.integrations)} · ${this._entries.length}</h2></summary>
        <p class="muted">${esc(t.integrationsHint)}</p>
        <table>${rows}</table>
      </details>`;
  }

  _render() {
    const t = this._t;
    let body = "";
    if (this._error) body = `<p class="error">${esc(t.error)}: ${esc(this._error)}</p>`;
    else if (this._automations)
      body = this._renderDecide() + this._renderVerdicts() + this._renderEntries();
    else body = `<p class="muted">…</p>`;
    this.shadowRoot.innerHTML = `
      <style>${STYLE}</style>
      <header>
        ${this._narrow ? `<button id="menu" class="icon" title="Menu">☰</button>` : ""}
        <h1>Unclouded</h1>
        <button id="refresh" class="icon small" title="${esc(t.refresh)}">⟳</button>
      </header>
      <main>
        <p class="intro">${esc(t.intro)}</p>
        ${body}
      </main>`;
    this._bind();
  }

  _bind() {
    const $ = (sel) => this.shadowRoot.querySelector(sel);
    $("#menu")?.addEventListener("click", () =>
      this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true }))
    );
    $("#refresh")?.addEventListener("click", () => {
      this._automations = null;
      this._render();
      this._load();
    });
    // In-page links would change the panel's URL; scroll instead.
    this.shadowRoot.querySelectorAll("a.tile").forEach((el) =>
      el.addEventListener("click", (e) => {
        e.preventDefault();
        $(el.getAttribute("href"))?.scrollIntoView({ behavior: "smooth" });
      })
    );
    this.shadowRoot.querySelectorAll("button[data-important]").forEach((el) =>
      el.addEventListener("click", (e) => {
        // The star sits in the summary; keep it from opening the details.
        e.preventDefault();
        e.stopPropagation();
        this._setImportant(el.dataset.important, !el.classList.contains("on"));
      })
    );
    this.shadowRoot.querySelectorAll("select[data-override]").forEach((el) =>
      el.addEventListener("change", () => this._setOverride(el.dataset.override, el.value))
    );
    this.shadowRoot.querySelectorAll("details[data-id]").forEach((el) =>
      el.addEventListener("toggle", () => {
        if (el.open) this._open.add(el.dataset.id);
        else this._open.delete(el.dataset.id);
      })
    );
  }
}

const STYLE = `
  :host { display: block; min-height: 100%; background: var(--primary-background-color);
    color: var(--primary-text-color); font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
    --uc-fails: var(--error-color, #db4437); --uc-degraded: var(--warning-color, #ff9800);
    --uc-unknown: var(--secondary-text-color, #888); --uc-works: var(--success-color, #43a047); }
  header { display: flex; align-items: center; gap: 8px; height: 56px; padding: 0 12px;
    background: var(--app-header-background-color, var(--primary-color));
    color: var(--app-header-text-color, #fff); }
  header h1 { font-size: 20px; font-weight: 400; margin: 0; flex: 1; }
  main { max-width: 860px; margin: 0 auto; padding: 16px; }
  .intro { margin: 0 0 16px; color: var(--secondary-text-color); }
  .card { display: block; background: var(--card-background-color, #fff); border-radius: var(--ha-card-border-radius, 12px);
    border: 1px solid var(--divider-color); padding: 16px; margin-bottom: 16px; }
  h2 { display: flex; align-items: center; gap: 8px; font-size: 18px; font-weight: 500; margin: 0 0 4px; }
  .tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
  .tile { display: flex; flex-direction: column; gap: 2px; padding: 12px 16px; text-decoration: none;
    color: var(--primary-text-color); background: var(--card-background-color, #fff);
    border: 1px solid var(--divider-color); border-left: 4px solid; border-radius: var(--ha-card-border-radius, 12px); }
  .tile .count { font-size: 28px; font-weight: 500; }
  .tile.fails { border-left-color: var(--uc-fails); }
  .tile.degraded { border-left-color: var(--uc-degraded); }
  .tile.unknown { border-left-color: var(--uc-unknown); }
  .tile.works { border-left-color: var(--uc-works); }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex: none; }
  .dot.fails { background: var(--uc-fails); }
  .dot.degraded { background: var(--uc-degraded); }
  .dot.unknown { background: var(--uc-unknown); }
  .dot.works { background: var(--uc-works); }
  ul { list-style: none; padding: 0; margin: 8px 0 0; }
  li.automation { padding: 8px 0; border-top: 1px solid var(--divider-color); }
  .row { display: flex; align-items: baseline; gap: 6px 8px; flex-wrap: wrap; }
  .row .name { flex: 1 1 200px; }
  div.row { padding-left: 18px; }
  a.open { font-size: 13px; white-space: nowrap; margin-left: auto; }
  summary { cursor: pointer; list-style: none; }
  summary::-webkit-details-marker { display: none; }
  li.automation summary::before { content: "▸"; width: 10px; color: var(--secondary-text-color); }
  li.automation details[open] summary::before { content: "▾"; }
  .tile.empty { opacity: .55; }
  button.star { font: inherit; font-size: 18px; line-height: 1; border: 0; background: transparent;
    padding: 0 2px; cursor: pointer; color: var(--secondary-text-color); align-self: center; }
  button.star.on { color: var(--warning-color, #ff9800); }
  select.choice { font: inherit; font-size: 13px; padding: 4px 6px; color: inherit; max-width: 100%;
    background: var(--secondary-background-color); border: 1px solid var(--divider-color); border-radius: 6px; }
  select.choice.chosen { border-color: var(--primary-color); }
  .card.decide { border-color: var(--warning-color, #ff9800); }
  #entries > summary h2::before { content: "▸"; color: var(--secondary-text-color); }
  #entries[open] > summary h2::before { content: "▾"; }
  ul.deps { margin: 6px 0 0 18px; font-size: 14px; }
  ul.deps li { padding: 4px 0; }
  .part { display: inline-block; min-width: 76px; color: var(--secondary-text-color); }
  .badge { display: inline-block; font-size: 12px; padding: 1px 8px; border-radius: 10px;
    border: 1px solid var(--divider-color); color: var(--secondary-text-color); white-space: nowrap; }
  .badge.spaced { margin-left: 4px; }
  .badge.cloud { color: var(--uc-fails); border-color: var(--uc-fails); }
  .badge.partial { color: var(--uc-degraded); border-color: var(--uc-degraded); }
  .badge.local, .badge.internal { color: var(--uc-works); border-color: var(--uc-works); }
  .badge.note { color: var(--primary-color); border-color: var(--primary-color); }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  td { padding: 6px 4px; border-top: 1px solid var(--divider-color); vertical-align: top; }
  td:nth-child(2) { white-space: nowrap; }
  .muted { color: var(--secondary-text-color); font-size: 13px; }
  p.muted { margin: 0 0 4px; }
  a { color: var(--primary-color); text-decoration: none; }
  a:hover { text-decoration: underline; }
  code { font-size: 13px; word-break: break-word; }
  button.icon { font: inherit; border: 0; background: transparent; color: inherit; font-size: 20px;
    padding: 4px 8px; cursor: pointer; }
  .error { color: var(--uc-fails); }
  @media (max-width: 600px) {
    main { padding: 8px; }
    .tiles { grid-template-columns: repeat(2, 1fr); }
    .part { min-width: 0; margin-right: 4px; }
  }
`;

// After an update the browser may load the new module next to the old one.
if (!customElements.get("unclouded-panel")) customElements.define("unclouded-panel", UncloudedPanel);
