"""Web dashboard helpers."""

from __future__ import annotations

from pathlib import Path

from chronos_safe.config.settings import SETTINGS


def _relative_paths(root: Path, patterns: tuple[str, ...]) -> list[str]:
    results: list[str] = []
    for pattern in patterns:
        for path in sorted(root.rglob(pattern)):
            if path.is_file():
                results.append(path.relative_to(root).as_posix())
    return results


def build_catalog_payload() -> dict[str, object]:
    return {
        "fixtures": _relative_paths(SETTINGS.data_root / "fixtures", ("*.json",)),
        "processed_datasets": sorted(
            [
                path.relative_to(SETTINGS.project_root).as_posix()
                for path in (SETTINGS.data_root / "processed").glob("*")
                if path.is_dir()
            ]
        ),
        "checkpoints": _relative_paths(SETTINGS.models_root / "checkpoints", ("*.pt",)),
        "scalers": _relative_paths(SETTINGS.models_root / "checkpoints", ("scaler.json",)),
        "ood_guards": _relative_paths(SETTINGS.models_root / "checkpoints", ("ood_guard.json",)),
        "reports": _relative_paths(SETTINGS.reports_root / "validation", ("*.json", "*.txt")),
        "defaults": {
            "generalist_dataset_dir": str((SETTINGS.data_root / "processed" / "generalist").as_posix()),
            "specialist_dataset_dir": str((SETTINGS.data_root / "processed" / "specialist").as_posix()),
            "generalist_checkpoint_dir": str((SETTINGS.models_root / "checkpoints" / "generalist").as_posix()),
            "specialist_checkpoint_dir": str((SETTINGS.models_root / "checkpoints" / "specialist").as_posix()),
            "simulation_output_path": str((SETTINGS.reports_root / "validation" / "simulation.json").as_posix()),
            "default_fixture": "apophis/apophis_fixture.json",
        },
    }


def render_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CHRONOS-SAFE Control Center</title>
  <link rel="icon" type="image/png" href="/static/chronosfav.png">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --bg: #050d1b;
      --bg-deep: #020712;
      --panel: rgba(7, 18, 38, 0.82);
      --panel-strong: rgba(10, 26, 52, 0.92);
      --ink: #ecf6ff;
      --muted: #8fa7c5;
      --line: rgba(108, 170, 255, 0.18);
      --accent: #4db5ff;
      --accent-2: #1f7bff;
      --accent-soft: #8eddff;
      --danger: #ff7b7b;
      --warning: #ffca70;
      --success: #57efb0;
      --shadow: 0 24px 64px rgba(2, 8, 18, 0.55);
      --radius: 20px;
      --mono: "Consolas", "SFMono-Regular", monospace;
      --serif: "Palatino Linotype", "Book Antiqua", "Times New Roman", serif;
      --sans: "Bahnschrift", "Aptos", "Trebuchet MS", "Segoe UI", sans-serif;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: var(--sans);
      color: var(--ink);
      position: relative;
      overflow-x: hidden;
      background:
        radial-gradient(circle at 12% 18%, rgba(77, 181, 255, 0.22), transparent 30%),
        radial-gradient(circle at 84% 10%, rgba(143, 221, 255, 0.16), transparent 26%),
        radial-gradient(circle at 50% 110%, rgba(31, 123, 255, 0.18), transparent 34%),
        linear-gradient(180deg, #071426 0%, #040b16 46%, #020712 100%);
      min-height: 100vh;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: 0.72;
      background-image:
        radial-gradient(circle at 12% 18%, rgba(255,255,255,0.9) 0 1px, transparent 1.5px),
        radial-gradient(circle at 72% 24%, rgba(143,221,255,0.85) 0 1px, transparent 1.5px),
        radial-gradient(circle at 38% 70%, rgba(255,255,255,0.82) 0 1px, transparent 1.5px),
        radial-gradient(circle at 86% 62%, rgba(143,221,255,0.8) 0 1px, transparent 1.5px),
        radial-gradient(circle at 18% 88%, rgba(255,255,255,0.7) 0 1px, transparent 1.5px),
        radial-gradient(circle at 55% 42%, rgba(143,221,255,0.56) 0 1px, transparent 1.5px);
      animation: starDrift 28s linear infinite alternate;
    }

    body::after {
      content: "";
      position: fixed;
      inset: -18% -10% auto;
      height: 44vh;
      pointer-events: none;
      background:
        radial-gradient(circle at 30% 40%, rgba(77, 181, 255, 0.16), transparent 34%),
        radial-gradient(circle at 66% 22%, rgba(143, 221, 255, 0.12), transparent 28%);
      filter: blur(26px);
      animation: auroraFloat 15s ease-in-out infinite alternate;
    }

    @keyframes starDrift {
      from { transform: translate3d(0, 0, 0); }
      to { transform: translate3d(0, 16px, 0); }
    }

    @keyframes auroraFloat {
      from { transform: translate3d(-1%, 0, 0) scale(1); opacity: 0.9; }
      to { transform: translate3d(2%, 2%, 0) scale(1.05); opacity: 1; }
    }

    @keyframes panelRise {
      from {
        opacity: 0;
        transform: translateY(12px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .shell {
      width: min(1200px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
      position: relative;
      z-index: 1;
    }

    .hero {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 20px;
      margin-bottom: 22px;
    }

    .hero-card, .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
      animation: panelRise 420ms ease both;
    }

    .hero-card {
      padding: 28px;
      position: relative;
      overflow: hidden;
    }

    .hero-card::before {
      content: "";
      position: absolute;
      inset: -24% auto auto 62%;
      width: 220px;
      height: 220px;
      border-radius: 50%;
      border: 1px solid rgba(143, 221, 255, 0.12);
      box-shadow:
        0 0 0 28px rgba(77, 181, 255, 0.04),
        0 0 0 58px rgba(143, 221, 255, 0.03);
      opacity: 0.85;
      transform: rotate(16deg);
    }

    .hero-card::after {
      content: "";
      position: absolute;
      inset: auto -40px -54px auto;
      width: 220px;
      height: 220px;
      background: radial-gradient(circle, rgba(77, 181, 255, 0.22) 0%, rgba(77, 181, 255, 0.02) 62%, transparent 72%);
      border-radius: 50%;
      filter: blur(10px);
    }

    h1, h2 {
      margin: 0;
      font-family: var(--serif);
      font-weight: 700;
      letter-spacing: -0.03em;
    }

    h1 {
      font-size: clamp(2.2rem, 5vw, 4rem);
      line-height: 0.93;
      text-shadow: 0 0 24px rgba(77, 181, 255, 0.12);
    }
    h2 { font-size: 1.2rem; margin-bottom: 14px; }

    .subtitle {
      color: var(--muted);
      max-width: 62ch;
      margin-top: 14px;
      line-height: 1.55;
    }

    .badge-row {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 18px;
    }

    .badge {
      padding: 8px 12px;
      border-radius: 999px;
      font-size: 0.88rem;
      border: 1px solid var(--line);
      background: rgba(8, 20, 38, 0.74);
      color: var(--ink);
    }

    .stats {
      padding: 24px;
      display: grid;
      gap: 12px;
      align-content: start;
    }

    .stat {
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px 16px;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    .stat strong {
      display: block;
      font-size: 1.35rem;
      margin-top: 6px;
      color: var(--accent-soft);
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }

    .guide-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
      margin-bottom: 18px;
    }

    .guide-card {
      padding: 18px;
      background: linear-gradient(180deg, rgba(10, 22, 42, 0.92), rgba(8, 18, 34, 0.78));
    }

    .guide-step {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 34px;
      height: 34px;
      border-radius: 50%;
      background: rgba(77, 181, 255, 0.12);
      color: var(--accent);
      font-weight: 800;
      margin-bottom: 10px;
      border: 1px solid rgba(77, 181, 255, 0.18);
      box-shadow: 0 0 18px rgba(77, 181, 255, 0.12);
    }

    .guide-card p {
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
      font-size: 0.92rem;
    }

    .summary-panel {
      padding: 22px;
      margin-bottom: 18px;
      display: grid;
      gap: 14px;
      background: linear-gradient(135deg, rgba(8, 22, 44, 0.88), rgba(7, 17, 32, 0.78));
      position: relative;
      overflow: hidden;
    }

    .summary-panel::after {
      content: "";
      position: absolute;
      inset: auto -90px -110px auto;
      width: 260px;
      height: 260px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(143, 221, 255, 0.18), transparent 68%);
      pointer-events: none;
    }

    .summary-copy {
      color: var(--muted);
      line-height: 1.55;
      max-width: 72ch;
    }

    .summary-actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }

    .summary-actions button {
      flex: 1 1 240px;
      width: auto;
    }

    .summary-note {
      font-size: 0.9rem;
      color: var(--muted);
    }

    .explanation-panel {
      margin-bottom: 18px;
      display: grid;
      gap: 16px;
      background: linear-gradient(135deg, rgba(9, 22, 42, 0.88), rgba(5, 14, 27, 0.8));
    }

    .explanation-panel .summary-copy {
      margin: 0;
      max-width: 86ch;
    }

    .usage-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }

    .usage-item {
      padding: 14px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(8, 18, 34, 0.72);
      color: var(--muted);
      line-height: 1.45;
      font-size: 0.9rem;
    }

    .usage-item strong {
      display: block;
      color: var(--ink);
      margin-bottom: 6px;
      font-size: 0.96rem;
    }

    .simulator-panel {
      margin-bottom: 18px;
      display: grid;
      gap: 16px;
    }

    .simulator-heading {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 16px;
      align-items: start;
    }

    .simulator-copy {
      margin: 0;
      color: var(--muted);
      line-height: 1.55;
      max-width: 78ch;
    }

    .example-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      min-width: min(360px, 100%);
    }

    .example-actions button {
      flex: 1 1 160px;
      width: auto;
    }

    .simulation-controls {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }

    .simulation-controls .wide {
      grid-column: 1 / -1;
    }

    .payload-editor {
      border: 1px solid rgba(108, 170, 255, 0.16);
      border-radius: 14px;
      overflow: hidden;
      background: rgba(4, 16, 31, 0.82);
    }

    .payload-editor-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      border-bottom: 1px solid rgba(108, 170, 255, 0.14);
      background: rgba(77, 181, 255, 0.04);
    }

    .payload-editor-head h3 {
      margin: 0;
      font-size: 0.98rem;
      font-family: var(--serif);
    }

    .payload-help {
      margin: 4px 0 0;
      max-width: 70ch;
    }

    .payload-editor-head button {
      width: auto;
      flex: 0 0 auto;
      padding: 9px 12px;
    }

    .simulation-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .simulation-actions button {
      flex: 1 1 220px;
      width: auto;
    }

    details.advanced-shell {
      margin-top: 18px;
    }

    details.advanced-shell > summary {
      list-style: none;
      cursor: pointer;
      padding: 18px 20px;
      border-radius: var(--radius);
      border: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(9, 20, 40, 0.86), rgba(6, 14, 28, 0.8));
      box-shadow: var(--shadow);
      font-weight: 700;
      color: var(--accent-soft);
    }

    details.advanced-shell > summary::-webkit-details-marker {
      display: none;
    }

    details.advanced-shell[open] > summary {
      border-bottom-left-radius: 10px;
      border-bottom-right-radius: 10px;
      margin-bottom: 12px;
    }

    .visual-section {
      margin-bottom: 18px;
    }

    #trajectory-plot {
      width: 100%;
      min-height: 520px;
      border-radius: 16px;
      background:
        radial-gradient(circle at 50% 50%, rgba(41, 95, 255, 0.1), transparent 34%),
        linear-gradient(180deg, #05101e 0%, #020712 100%);
      border: 1px solid rgba(108, 170, 255, 0.18);
      overflow: hidden;
      box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.04),
        0 20px 36px rgba(2, 8, 18, 0.36);
    }

    .plot-meta {
      margin-top: 12px;
      font-family: var(--mono);
      font-size: 0.86rem;
      color: var(--accent-soft);
    }

    .panel {
      padding: 20px;
    }

    form {
      display: grid;
      gap: 12px;
    }

    .row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }

    label {
      display: grid;
      gap: 6px;
      font-size: 0.92rem;
      color: var(--muted);
    }

    .field-title {
      color: var(--ink);
      font-weight: 700;
    }

    .field-help,
    .payload-help {
      color: var(--muted);
      font-size: 0.82rem;
      line-height: 1.38;
    }

input, select, textarea, button {
      width: 100%;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: rgba(8, 20, 38, 0.92);
      padding: 11px 12px;
      font: inherit;
      color: var(--ink);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    textarea {
      min-height: 156px;
      resize: vertical;
      border-radius: 0;
      border: 0;
      background: #04101f;
      font-family: var(--mono);
      line-height: 1.45;
      white-space: pre;
      overflow: auto;
    }

    input:focus, select:focus, textarea:focus {
      outline: none;
      border-color: rgba(143, 221, 255, 0.44);
      box-shadow:
        0 0 0 3px rgba(77, 181, 255, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    button {
      border: none;
      background: linear-gradient(135deg, #1f7bff, #4db5ff);
      color: white;
      font-weight: 700;
      cursor: pointer;
      transition: transform 160ms ease, opacity 160ms ease, box-shadow 160ms ease;
      box-shadow: 0 14px 28px rgba(31, 123, 255, 0.24);
    }

    button.secondary {
      background: linear-gradient(135deg, #0d2b63, #2b95ff);
      box-shadow: 0 14px 28px rgba(13, 43, 99, 0.24);
    }

    button.danger {
      background: linear-gradient(135deg, #8e1f2e, #ff6b73);
      box-shadow: 0 14px 28px rgba(142, 31, 46, 0.24);
    }

    button:hover {
      transform: translateY(-1px);
      box-shadow: 0 18px 32px rgba(31, 123, 255, 0.28);
    }
    button:disabled { opacity: 0.55; cursor: wait; transform: none; }

    .toolbar {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }

    .toolbar button {
      flex: 1 1 220px;
      width: auto;
    }

    .hint {
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.45;
      margin-top: 8px;
    }

    .status {
      font-family: var(--mono);
      font-size: 0.88rem;
      padding: 10px 12px;
      border-radius: 12px;
      background: rgba(77, 181, 255, 0.1);
      border: 1px solid rgba(77, 181, 255, 0.16);
      color: var(--accent-soft);
      margin-bottom: 12px;
      white-space: pre-wrap;
    }

    .results-shell {
      display: grid;
      gap: 16px;
    }

    .risk-banner {
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 14px;
      align-items: center;
      padding: 16px 18px;
      border-radius: 16px;
      border: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(10, 24, 46, 0.94), rgba(8, 18, 34, 0.82));
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    .risk-banner[data-level="green"] {
      background: linear-gradient(135deg, rgba(7, 36, 33, 0.94), rgba(5, 23, 21, 0.82));
      border-color: rgba(87, 239, 176, 0.22);
    }

    .risk-banner[data-level="yellow"] {
      background: linear-gradient(135deg, rgba(55, 34, 7, 0.94), rgba(34, 21, 5, 0.84));
      border-color: rgba(255, 202, 112, 0.22);
    }

    .risk-banner[data-level="red"] {
      background: linear-gradient(135deg, rgba(56, 14, 20, 0.94), rgba(34, 8, 12, 0.84));
      border-color: rgba(255, 123, 123, 0.22);
    }

    .risk-light {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      box-shadow: 0 0 0 6px rgba(255, 255, 255, 0.08), 0 0 20px currentColor;
      background: #9aa5ae;
    }

    .risk-banner[data-level="green"] .risk-light {
      background: var(--success);
      color: var(--success);
    }

    .risk-banner[data-level="yellow"] .risk-light {
      background: var(--warning);
      color: var(--warning);
    }

    .risk-banner[data-level="red"] .risk-light {
      background: var(--danger);
      color: var(--danger);
    }

    .risk-copy {
      display: grid;
      gap: 4px;
    }

    .risk-kicker {
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-size: 0.74rem;
      color: var(--muted);
      font-weight: 700;
    }

    .risk-title {
      font-size: 1.02rem;
      font-family: var(--serif);
      font-weight: 700;
    }

    .risk-description {
      color: var(--muted);
      font-size: 0.9rem;
      line-height: 1.45;
    }

    .risk-pill {
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(6, 16, 32, 0.82);
      border: 1px solid var(--line);
      font-size: 0.82rem;
      font-weight: 700;
      white-space: nowrap;
      color: var(--ink);
    }

    .risk-explain {
      display: grid;
      gap: 10px;
      padding: 14px 16px;
      border-radius: 14px;
      border: 1px solid rgba(108, 170, 255, 0.16);
      background: rgba(8, 18, 34, 0.72);
    }

    .risk-explain[data-level="green"] {
      border-color: rgba(87, 239, 176, 0.2);
      background: rgba(7, 36, 33, 0.34);
    }

    .risk-explain[data-level="yellow"] {
      border-color: rgba(255, 202, 112, 0.2);
      background: rgba(55, 34, 7, 0.34);
    }

    .risk-explain[data-level="red"] {
      border-color: rgba(255, 123, 123, 0.24);
      background: rgba(56, 14, 20, 0.34);
    }

    .risk-explain h3 {
      margin: 0;
      font-size: 1rem;
      font-family: var(--serif);
    }

    .risk-reason-list {
      display: grid;
      gap: 8px;
    }

    .risk-reason-row {
      display: grid;
      grid-template-columns: minmax(0, 0.78fr) minmax(0, 1.42fr);
      gap: 12px;
      padding-top: 8px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 0.88rem;
      line-height: 1.45;
    }

    .risk-reason-row:first-child {
      border-top: 0;
      padding-top: 0;
    }

    .risk-reason-row strong {
      color: var(--ink);
    }

    .risk-reason-row span {
      color: var(--muted);
    }

    .results-topline {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .results-title {
      display: grid;
      gap: 4px;
    }

    .results-kicker {
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-size: 0.78rem;
      color: var(--accent);
      font-weight: 700;
    }

    .results-heading {
      font-size: 1.25rem;
      font-family: var(--serif);
      margin: 0;
    }

    .results-subtitle {
      margin: 0;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.45;
    }

    .results-badges {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .results-badge {
      padding: 7px 11px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(6, 16, 32, 0.82);
      font-size: 0.82rem;
      color: var(--ink);
    }

    .results-grid {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 16px;
    }

    .metric-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }

    .metric-card {
      padding: 14px 16px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(10, 24, 48, 0.96), rgba(8, 17, 32, 0.88));
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    .metric-card span {
      display: block;
      color: var(--muted);
      font-size: 0.84rem;
      margin-bottom: 6px;
    }

    .metric-card strong {
      display: block;
      font-size: 1.16rem;
      font-family: var(--mono);
      color: var(--ink);
      word-break: break-word;
    }

    .results-stack {
      display: grid;
      gap: 12px;
    }

    .detail-card {
      padding: 14px 16px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(8, 18, 34, 0.84);
    }

    .detail-card h3 {
      margin: 0 0 10px;
      font-size: 1rem;
      font-family: var(--serif);
    }

    .kv-list {
      display: grid;
      gap: 8px;
    }

    .kv-row {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 12px;
      align-items: start;
      font-size: 0.88rem;
    }

    .kv-key {
      color: var(--muted);
      word-break: break-word;
    }

    .kv-value {
      font-family: var(--mono);
      color: var(--ink);
      text-align: right;
      word-break: break-word;
    }

    .fallback-list {
      display: grid;
      gap: 10px;
      max-height: 280px;
      overflow: auto;
    }

    .fallback-item {
      padding: 11px 12px;
      border-radius: 12px;
      background: rgba(55, 14, 20, 0.4);
      border: 1px solid rgba(255, 123, 123, 0.14);
    }

    .fallback-item strong {
      display: block;
      font-size: 0.9rem;
      margin-bottom: 4px;
      color: var(--danger);
    }

    .fallback-item span {
      display: block;
      color: var(--muted);
      font-size: 0.84rem;
      line-height: 1.4;
      font-family: var(--mono);
    }

    .empty-card {
      padding: 18px;
      border-radius: 14px;
      border: 1px dashed var(--line);
      color: var(--muted);
      background: rgba(6, 14, 28, 0.54);
      font-size: 0.9rem;
    }

    .json-card {
      padding: 0;
      overflow: hidden;
      background: #04101f;
      border-color: rgba(108, 170, 255, 0.16);
    }

    .json-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      border-bottom: 1px solid rgba(108, 170, 255, 0.14);
      background: rgba(77, 181, 255, 0.04);
    }

    .json-head h3 {
      margin: 0;
      color: #eef3f7;
    }

    .json-tag {
      font-family: var(--mono);
      font-size: 0.78rem;
      color: #9db2c5;
    }

    .json-pre {
      margin: 0;
      padding: 16px;
      max-height: 360px;
      overflow: auto;
      font-family: var(--mono);
      font-size: 0.84rem;
      line-height: 1.5;
      color: #dfe8ef;
      white-space: pre-wrap;
      word-break: break-word;
    }

    @media (max-width: 980px) {
      .hero,
      .grid,
      .row,
      .results-grid,
      .metric-grid,
      .guide-grid,
      .usage-grid,
      .simulator-heading,
      .simulation-controls {
        grid-template-columns: 1fr;
      }

      .simulation-controls .wide {
        grid-column: auto;
      }

      .results-topline {
        align-items: flex-start;
      }

      .results-badges {
        width: 100%;
      }

      .risk-banner {
        grid-template-columns: 1fr;
        align-items: start;
      }

      .risk-pill {
        justify-self: start;
      }

      .risk-reason-row {
        grid-template-columns: 1fr;
        gap: 4px;
      }

      .kv-row {
        grid-template-columns: 1fr;
        gap: 4px;
      }

      .kv-value {
        text-align: left;
      }

      #trajectory-plot {
        min-height: 420px;
      }

      .hero-card,
      .panel {
        padding: 18px;
      }

      .shell {
        width: min(100vw - 18px, 1200px);
      }
    }

    @media (max-width: 680px) {
      body::before,
      body::after {
        opacity: 0.5;
      }

      .shell {
        width: min(100vw - 12px, 1200px);
        padding: 12px 0 24px;
      }

      .hero {
        gap: 14px;
        margin-bottom: 14px;
      }

      .hero-card,
      .panel {
        border-radius: 16px;
        padding: 16px;
      }

      .hero-card::before {
        width: 160px;
        height: 160px;
        inset: -20% auto auto 70%;
      }

      .hero-card::after {
        width: 150px;
        height: 150px;
        inset: auto -30px -40px auto;
      }

      h1 {
        font-size: clamp(1.8rem, 10vw, 2.8rem);
        line-height: 0.96;
      }

      h2 {
        font-size: 1.05rem;
        margin-bottom: 10px;
      }

      .subtitle,
      .summary-copy,
      .summary-note,
      .hint,
      .results-subtitle,
      .risk-description {
        font-size: 0.92rem;
      }

      .badge-row,
      .results-badges {
        gap: 8px;
      }

      .badge,
      .results-badge,
      .risk-pill {
        font-size: 0.78rem;
        padding: 7px 10px;
      }

      .guide-card,
      .stat,
      .metric-card,
      .detail-card {
        padding: 14px;
      }

      .summary-actions,
      .example-actions,
      .simulation-actions,
      .toolbar {
        gap: 8px;
      }

      .summary-actions button,
      .example-actions button,
      .simulation-actions button,
      .toolbar button {
        flex: 1 1 100%;
      }

      #trajectory-plot {
        min-height: 320px;
      }

      .plot-meta,
      .status,
      .json-pre {
        font-size: 0.8rem;
      }

      .results-heading {
        font-size: 1.08rem;
      }

      .metric-card strong {
        font-size: 1rem;
      }

      .fallback-list {
        max-height: 220px;
      }

      .json-pre {
        max-height: 280px;
        padding: 12px;
      }

      details.advanced-shell > summary {
        padding: 14px 16px;
        font-size: 0.95rem;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="hero-card">
        <p style="margin:0 0 10px;color:var(--accent-soft);font-weight:700;letter-spacing:0.16em;text-transform:uppercase;">Orbital Mission Control</p>
        <h1>CHRONOS-SAFE</h1>
        <p class="subtitle">
          Plataforma hibrida para simulacao orbital segura, com uma camada visual feita para demonstracao, avaliacao e leitura tecnica.
          Abra a demo 3D, rode o caso Apophis e leia risco, erro acumulado, fallback e comparacao contra a referencia fisica.
        </p>
        <div class="badge-row">
          <span class="badge">Demo 3D instantanea</span>
          <span class="badge">Fallback seguro</span>
          <span class="badge">Validacao Apophis</span>
          <span class="badge">Pronto para Render</span>
        </div>
      </div>
      <aside class="hero-card stats">
        <div class="stat">
          <span>Mission status</span>
          <strong id="health-value">carregando...</strong>
        </div>
        <div class="stat">
          <span>Cenarios detectados</span>
          <strong id="fixtures-count">0</strong>
        </div>
        <div class="stat">
          <span>Modelos detectados</span>
          <strong id="checkpoints-count">0</strong>
        </div>
      </aside>
    </section>

    <section class="guide-grid">
      <article class="hero-card guide-card">
        <div class="guide-step">1</div>
        <h2>Veja a orbita</h2>
        <p>Abra a demo 3D e confirme que a plataforma entrega uma simulacao visual palpavel no navegador.</p>
      </article>
      <article class="hero-card guide-card">
        <div class="guide-step">2</div>
        <h2>Rode o Apophis</h2>
        <p>Use o teste principal da pesquisa para comparar o modo hibrido com a referencia fisica em um cenario realista.</p>
      </article>
      <article class="hero-card guide-card">
        <div class="guide-step">3</div>
        <h2>Leia o semaforo</h2>
        <p>O relatorio resume o risco em verde, amarelo ou vermelho e explica rapidamente o motivo da classificacao.</p>
      </article>
    </section>

    <section class="panel explanation-panel">
      <div>
        <span class="results-kicker">O que esta ferramenta faz</span>
        <h2>Simulacao orbital com leitura de risco</h2>
        <p class="summary-copy">
          O CHRONOS-SAFE ajuda a testar cenarios orbitais de forma visual. Voce escolhe um cenario, define quantos passos a simulacao deve rodar,
          ajusta o tamanho do passo de tempo e, se quiser, conecta um modelo de IA treinado. A ferramenta desenha a trajetoria em 3D e transforma
          os resultados tecnicos em uma leitura simples: verde quando o comportamento esta estavel, amarelo quando merece atencao e vermelho quando
          o erro, o drift fisico ou os fallbacks indicam instabilidade.
        </p>
      </div>
      <div class="usage-grid">
        <div class="usage-item">
          <strong>1. Configure os dados</strong>
          Escolha o fixture, altere passos e dt, ou edite diretamente o JSON do payload antes de rodar.
        </div>
        <div class="usage-item">
          <strong>2. Rode a simulacao</strong>
          Use o botao de simulacao para enviar os dados ao backend e atualizar a orbita 3D.
        </div>
        <div class="usage-item">
          <strong>3. Interprete o semaforo</strong>
          Confira a cor do risco, os principais indicadores, os eventos de fallback e o JSON tecnico.
        </div>
      </div>
    </section>

    <section class="panel summary-panel">
      <h2>Comece aqui</h2>
      <p class="summary-copy">
        Se voce esta em banca, avaliacao tecnica ou demonstracao no Render, use somente os dois botoes abaixo.
        O primeiro abre a visualizacao orbital 3D. O segundo roda o caso Apophis, que e o teste principal desta pesquisa
        para verificar erro acumulado, estabilidade de rollout e capacidade de fallback seguro.
      </p>
      <div class="summary-actions">
        <button id="quick-demo-button" type="button">1. Ver demo 3D</button>
        <button id="quick-apophis-button" type="button" class="secondary">2. Rodar teste Apophis</button>
      </div>
      <p class="summary-note">
        Depois disso, leia o semaforo de risco e a leitura rapida do relatorio. A area avancada fica escondida mais abaixo e so e necessaria para reproducao tecnica.
      </p>
    </section>

    <section class="panel simulator-panel">
      <div class="simulator-heading">
        <div>
          <span class="results-kicker">Dados da simulacao</span>
          <h2>Monte sua propria simulacao</h2>
          <p class="simulator-copy">
            Altere os parametros abaixo para testar outro numero de passos, outro intervalo de tempo ou outro artefato de IA. O JSON mostra exatamente
            o que sera enviado para o endpoint de simulacao e tambem pode ser editado manualmente.
          </p>
        </div>
        <div class="example-actions">
          <button id="green-example-button" type="button">Exemplo verde</button>
          <button id="red-example-button" type="button" class="danger">Exemplo vermelho</button>
        </div>
      </div>
      <form id="simulate-form" class="simulation-controls">
        <label>
          <span class="field-title">Fixture</span>
          <span class="field-help">Arquivo que define os corpos celestes, massas, posicoes e velocidades iniciais do cenario.</span>
          <select name="fixture_name" data-select="fixtures"></select>
        </label>
        <label>
          <span class="field-title">Passos</span>
          <span class="field-help">Quantidade de avancos numericos. Mais passos mostram uma janela maior da orbita e tambem acumulam mais erro.</span>
          <input type="number" name="steps" value="180" min="1">
        </label>
        <label>
          <span class="field-title">dt (dias)</span>
          <span class="field-help">Tamanho de cada salto no tempo. Valores menores tendem a ser mais precisos; valores maiores podem acelerar e instabilizar.</span>
          <input type="number" name="dt_days" value="1.0" min="0.01" step="0.01">
        </label>
        <label>
          <span class="field-title">Checkpoint</span>
          <span class="field-help">Modelo de IA treinado para sugerir uma correcao residual na aceleracao dos corpos.</span>
          <select name="checkpoint_path" data-select="checkpoints" data-allow-empty="true"></select>
        </label>
        <label>
          <span class="field-title">Scaler</span>
          <span class="field-help">Arquivo que normaliza massas, posicoes e velocidades para a escala usada durante o treino da IA.</span>
          <select name="scaler_path" data-select="scalers" data-allow-empty="true"></select>
        </label>
        <label>
          <span class="field-title">OOD guard</span>
          <span class="field-help">Guarda de seguranca que identifica estados fora do dominio de treino e aciona fallback fisico quando necessario.</span>
          <select name="ood_guard_path" data-select="ood_guards" data-allow-empty="true"></select>
        </label>
        <div class="payload-editor wide">
          <div class="payload-editor-head">
            <div>
              <h3>Payload JSON editavel</h3>
              <p class="payload-help">Mostra os mesmos parametros em formato tecnico para reproducao, depuracao ou chamadas diretas ao endpoint.</p>
            </div>
            <button id="sync-payload-button" type="button" class="secondary">Atualizar JSON</button>
          </div>
          <textarea id="simulation-payload-editor" spellcheck="false"></textarea>
        </div>
        <div class="simulation-actions wide">
          <button type="submit">Simular com estes dados</button>
          <button id="run-payload-button" type="button" class="secondary">Rodar JSON editado</button>
        </div>
      </form>
      <p class="hint">O exemplo verde usa a simulacao padrao estavel. O exemplo vermelho e demonstrativo: ele mostra como o relatorio fica quando drift e fallbacks passam do limite seguro.</p>
    </section>

    <section class="panel visual-section">
      <div class="toolbar">
        <button id="preview-button" type="button">Ver demo 3D</button>
        <button id="run-apophis-now-button" type="button" class="secondary">Rodar teste Apophis</button>
        <button id="clear-plot-button" type="button" class="secondary">Limpar Visual</button>
      </div>
      <div id="trajectory-plot"></div>
      <div id="plot-meta" class="plot-meta">Aguardando trajetoria para renderizar.</div>
      <p class="hint">A visualizacao 3D usa um endpoint compacto de trajetoria e fica facil de hospedar no Render porque tudo roda em HTML + JS puro dentro da FastAPI.</p>
    </section>

    <details class="advanced-shell">
      <summary>Modo avancado: gerar dados, treinar IA e validar Apophis manualmente</summary>
      <div class="grid">
      <section class="panel">
        <h2>1. Criar dados de treino</h2>
        <div class="row">
          <form id="generalist-form">
            <label>Saida
              <input type="text" name="output_dir" data-fill="generalist_dataset_dir">
            </label>
            <div class="row">
              <label>Amostras
                <input type="number" name="num_samples" value="128" min="1">
              </label>
              <label>dt (dias)
                <input type="number" name="dt_days" value="1.0" min="0.01" step="0.01">
              </label>
            </div>
            <div class="row">
              <label>Min corpos
                <input type="number" name="min_bodies" value="2" min="2">
              </label>
              <label>Max corpos
                <input type="number" name="max_bodies" value="6" min="2">
              </label>
            </div>
            <button type="submit">Gerar Generalista</button>
          </form>

          <form id="specialist-form">
            <label>Saida
              <input type="text" name="output_dir" data-fill="specialist_dataset_dir">
            </label>
            <label>Fixture
              <select name="fixture_name" data-select="fixtures"></select>
            </label>
            <div class="row">
              <label>Amostras
                <input type="number" name="num_samples" value="64" min="1">
              </label>
              <label>dt (dias)
                <input type="number" name="dt_days" value="1.0" min="0.01" step="0.01">
              </label>
            </div>
            <button type="submit" class="secondary">Gerar Especialista</button>
          </form>
        </div>
        <p class="hint">Esses arquivos servem para treinar o modelo. Se voce so quer avaliar o sistema visualmente, pode ignorar esta etapa.</p>
      </section>

      <section class="panel">
        <h2>2. Treinar modelos de IA</h2>
        <div class="row">
          <form id="train-generalist-form">
            <label>Dataset generalista
              <input type="text" name="dataset_dir" data-fill="generalist_dataset_dir">
            </label>
            <label>Saida do checkpoint
              <input type="text" name="output_dir" data-fill="generalist_checkpoint_dir">
            </label>
            <div class="row">
              <label>Epocas
                <input type="number" name="epochs" value="10" min="1">
              </label>
              <label>Batch
                <input type="number" name="batch_size" value="8" min="1">
              </label>
            </div>
            <button type="submit">Treinar Generalista</button>
          </form>

          <form id="train-specialist-form">
            <label>Dataset especialista
              <input type="text" name="dataset_dir" data-fill="specialist_dataset_dir">
            </label>
            <label>Checkpoint base
              <select name="base_checkpoint" data-select="checkpoints" data-allow-empty="true"></select>
            </label>
            <label>Saida do checkpoint
              <input type="text" name="output_dir" data-fill="specialist_checkpoint_dir">
            </label>
            <div class="row">
              <label>Epocas
                <input type="number" name="epochs" value="6" min="1">
              </label>
              <label>Batch
                <input type="number" name="batch_size" value="8" min="1">
              </label>
            </div>
            <button type="submit" class="secondary">Treinar Especialista</button>
          </form>
        </div>
        <p class="hint">Treino e opcional para avaliacao. Se `torch` nao estiver pronto no ambiente, a demonstracao 3D e a validacao basica continuam funcionando.</p>
      </section>

      <section class="panel">
        <h2>3. Teste principal com Apophis</h2>
        <form id="apophis-form">
          <div class="row">
            <label>Passos
              <input type="number" name="steps" value="180" min="1">
            </label>
            <label>dt (dias)
              <input type="number" name="dt_days" value="1.0" min="0.01" step="0.01">
            </label>
          </div>
          <div class="row">
            <label>Checkpoint
              <select name="checkpoint_path" data-select="checkpoints" data-allow-empty="true"></select>
            </label>
            <label>Scaler
              <select name="scaler_path" data-select="scalers" data-allow-empty="true"></select>
            </label>
          </div>
          <div class="row">
            <label>OOD guard
              <select name="ood_guard_path" data-select="ood_guards" data-allow-empty="true"></select>
            </label>
            <div></div>
          </div>
          <button type="submit" class="secondary">Validar Apophis</button>
        </form>
      </section>
      </div>
    </details>

    <section class="panel" style="margin-top:18px;">
      <div class="toolbar">
        <button id="refresh-button" type="button">Atualizar catalogo</button>
        <button id="health-button" type="button" class="secondary">Verificar saude</button>
      </div>
      <div id="status-box" class="status">Pronto.</div>
      <div class="results-shell">
        <div class="results-topline">
          <div class="results-title">
            <span class="results-kicker">Relatorio guiado</span>
            <h2 id="results-heading" class="results-heading">Nenhuma execucao ainda</h2>
            <p id="results-subtitle" class="results-subtitle">Execute uma acao para ver metricas principais, comparacao com a referencia fisica e o detalhe tecnico formatado.</p>
          </div>
          <div id="results-badges" class="results-badges"></div>
        </div>
        <div id="risk-banner" class="risk-banner" data-level="neutral">
          <div class="risk-light"></div>
          <div class="risk-copy">
            <span class="risk-kicker">Semaforo de risco</span>
            <strong id="risk-title" class="risk-title">Aguardando execucao</strong>
            <span id="risk-description" class="risk-description">Rode a demo ou a validacao Apophis para classificar o comportamento do sistema.</span>
          </div>
          <span id="risk-pill" class="risk-pill">neutro</span>
        </div>
        <div id="risk-explain" class="risk-explain" data-level="neutral">
          <h3>Por que este semaforo?</h3>
          <div id="risk-reason-body" class="risk-reason-list">
            <div class="risk-reason-row">
              <strong>Aguardando dados</strong>
              <span>Quando uma simulacao rodar, esta area traduz erro, drift fisico e fallbacks para uma explicacao de fisica orbital.</span>
            </div>
          </div>
        </div>
        <div class="results-grid">
          <div class="results-stack">
            <div id="metric-grid" class="metric-grid"></div>
            <div class="detail-card">
              <h3>Leitura rapida</h3>
              <div id="primary-details-body" class="kv-list"></div>
            </div>
          </div>
          <div class="results-stack">
            <div class="detail-card">
              <h3>Eventos de fallback</h3>
              <div id="fallback-body" class="fallback-list"></div>
            </div>
            <div class="detail-card json-card">
              <div class="json-head">
                <h3>JSON tecnico</h3>
                <span class="json-tag">payload completo</span>
              </div>
              <pre id="output-box" class="json-pre">{}</pre>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>

  <script>
    const state = { catalog: null };
    const orbitPalette = ["#ffd166", "#7dd3fc", "#38bdf8", "#3b82f6", "#60a5fa", "#22d3ee", "#a5b4fc", "#2dd4bf", "#93c5fd"];
    const simulationFieldNames = ["fixture_name", "steps", "dt_days", "checkpoint_path", "scaler_path", "ood_guard_path"];

    function setStatus(message) {
      document.getElementById("status-box").textContent = message;
    }

    function formatValue(value) {
      if (typeof value === "number") {
        if (!Number.isFinite(value)) return String(value);
        const abs = Math.abs(value);
        if (abs >= 1000) return value.toFixed(2);
        if (abs >= 1) return value.toFixed(4);
        if (abs >= 0.001) return value.toFixed(6);
        return value.toExponential(3);
      }
      if (value === null || value === undefined) return "n/a";
      if (typeof value === "boolean") return value ? "sim" : "nao";
      return String(value);
    }

    function badgeHtml(text) {
      return `<span class="results-badge">${text}</span>`;
    }

    function metricCardHtml(label, value) {
      return `<div class="metric-card"><span>${label}</span><strong>${formatValue(value)}</strong></div>`;
    }

    function makeReason(title, detail) {
      return { title, detail };
    }

    function makeRisk(level, title, description, pill, reasons) {
      return {
        level,
        title,
        description,
        pill: pill || level,
        reasons: reasons || [],
      };
    }

    function isFiniteNumber(value) {
      return typeof value === "number" && Number.isFinite(value);
    }

    function metricText(value, unit) {
      if (!isFiniteNumber(value)) {
        return "nao informado no payload";
      }
      return `${formatValue(value)}${unit ? ` ${unit}` : ""}`;
    }

    function fallbackReasonSummary(events) {
      if (!events || events.length === 0) {
        return "";
      }
      const labels = {
        energy_drift: "drift de energia",
        angular_momentum_drift: "drift de momento angular",
        speed_limit: "velocidade fora do limite",
        distance_limit: "distancia fora do limite",
        ood_score: "estado fora do dominio de treino",
      };
      const counts = {};
      events.forEach((event) => {
        const reason = event.reason || "fallback";
        counts[reason] = (counts[reason] || 0) + 1;
      });
      return Object.entries(counts)
        .map(([reason, count]) => `${count}x ${labels[reason] || reason}`)
        .join(", ");
    }

    function addMetricReason(reasons, condition, title, value, unit, detail) {
      if (!condition) {
        return;
      }
      reasons.push(makeReason(title, `${metricText(value, unit)}. ${detail}`));
    }

    function validationRiskReasons(payload, level, values) {
      if (level === "green") {
        return [
          makeReason("Referencia fisica proxima", "Os erros contra o motor de referencia ficaram abaixo dos limites didaticos, entao a trajetoria hibrida acompanha a solucao fisica esperada."),
          makeReason("Conservacao controlada", "Energia e momento angular variaram muito pouco, como se espera em uma simulacao gravitacional numericamente estavel."),
          makeReason("Sem fallback", "O sistema nao precisou abandonar o modo hibrido para recorrer ao motor fisico de seguranca."),
        ];
      }

      const limits = level === "red"
        ? { finalError: 1e-2, earthError: 1e-2, fallbackCount: 4, energyDrift: 1e-4, angularDrift: 1e-6 }
        : { finalError: 1e-3, earthError: 1e-3, fallbackCount: 0, energyDrift: 1e-6, angularDrift: 1e-8 };
      const reasons = [];
      const events = payload.fallback_events || [];
      const fallbackDetail = fallbackReasonSummary(events);

      addMetricReason(
        reasons,
        !isFiniteNumber(values.finalError) || values.finalError > limits.finalError,
        "Erro final de posicao",
        values.finalError,
        "AU",
        "A trajetoria hibrida terminou longe da referencia fisica; 1 AU e aproximadamente a distancia media entre Terra e Sol."
      );
      addMetricReason(
        reasons,
        !isFiniteNumber(values.earthError) || values.earthError > limits.earthError,
        "Distancia Terra-Apophis",
        values.earthError,
        "AU",
        "A diferenca na distancia de encontro altera a leitura de risco do cenario e indica erro acumulado no movimento relativo."
      );
      addMetricReason(
        reasons,
        values.fallbackCount > limits.fallbackCount,
        "Fallbacks acionados",
        values.fallbackCount,
        "",
        `Fallback significa trocar para o motor fisico de referencia porque a etapa hibrida deixou de parecer confiavel.${fallbackDetail ? ` Motivos registrados: ${fallbackDetail}.` : ""}`
      );
      addMetricReason(
        reasons,
        !isFiniteNumber(values.energyDrift) || values.energyDrift > limits.energyDrift,
        "Drift de energia",
        values.energyDrift,
        "",
        "Em um sistema gravitacional isolado, a energia total deve variar pouco; drift alto sugere que o calculo esta criando ou perdendo energia numericamente."
      );
      addMetricReason(
        reasons,
        !isFiniteNumber(values.angularDrift) || values.angularDrift > limits.angularDrift,
        "Drift de momento angular",
        values.angularDrift,
        "",
        "O momento angular mede a conservacao do giro orbital; drift alto indica que a orbita esta mudando por erro numerico, nao apenas pela gravidade modelada."
      );

      if (!reasons.length) {
        reasons.push(makeReason("Classificacao agregada", "Nenhuma metrica isolada dominou a classificacao, mas o conjunto ficou fora da faixa verde."));
      }
      return reasons;
    }

    function trajectoryRiskReasons(payload, level, values) {
      if (level === "green") {
        return [
          makeReason("Orbita numericamente estavel", "A energia e o momento angular ficaram dentro da faixa esperada para uma simulacao curta de corpos celestes."),
          makeReason("Sem fallback", "Nenhum passo precisou ser recalculado pelo motor fisico de seguranca."),
        ];
      }

      const limits = level === "red"
        ? { fallbackCount: 3, energyDrift: 1e-4, angularDrift: 1e-6 }
        : { fallbackCount: 0, energyDrift: 1e-6, angularDrift: 1e-8 };
      const reasons = [];
      const events = payload.fallback_events || [];
      const fallbackDetail = fallbackReasonSummary(events);

      addMetricReason(
        reasons,
        values.fallbackCount > limits.fallbackCount,
        "Fallbacks acionados",
        values.fallbackCount,
        "",
        `A simulacao precisou recorrer ao motor de referencia em passos de risco.${fallbackDetail ? ` Motivos registrados: ${fallbackDetail}.` : ""}`
      );
      addMetricReason(
        reasons,
        !isFiniteNumber(values.energyDrift) || values.energyDrift > limits.energyDrift,
        "Drift de energia",
        values.energyDrift,
        "",
        "A energia deveria ficar quase conservada; drift alto e sinal de integracao instavel ou passo temporal agressivo."
      );
      addMetricReason(
        reasons,
        !isFiniteNumber(values.angularDrift) || values.angularDrift > limits.angularDrift,
        "Drift de momento angular",
        values.angularDrift,
        "",
        "O giro global da orbita deveria mudar pouco; drift alto aponta deformacao numerica da trajetoria."
      );

      if (!reasons.length) {
        reasons.push(makeReason("Classificacao agregada", "A trajetoria ficou fora da faixa verde pelo conjunto das metricas de estabilidade."));
      }
      return reasons;
    }

    function classifyValidationRisk(payload) {
      const finalError = Math.abs(payload.comparison_metrics?.final_position_error_au ?? Number.POSITIVE_INFINITY);
      const earthError = Math.abs(payload.comparison_metrics?.earth_apophis_distance_error_au ?? Number.POSITIVE_INFINITY);
      const energyDrift = Math.abs(payload.hybrid_metrics?.energy_drift ?? Number.POSITIVE_INFINITY);
      const angularDrift = Math.abs(payload.hybrid_metrics?.angular_momentum_drift ?? Number.POSITIVE_INFINITY);
      const fallbackCount = payload.fallback_count ?? 0;
      const values = { finalError, earthError, energyDrift, angularDrift, fallbackCount };

      if (
        finalError <= 1e-3 &&
        earthError <= 1e-3 &&
        fallbackCount === 0 &&
        energyDrift <= 1e-6 &&
        angularDrift <= 1e-8
      ) {
        return makeRisk(
          "green",
          "Risco baixo",
          "O caso Apophis ficou proximo da referencia fisica, sem fallback e com drift fisico controlado.",
          "verde",
          validationRiskReasons(payload, "green", values)
        );
      }

      if (
        finalError <= 1e-2 &&
        earthError <= 1e-2 &&
        fallbackCount <= 4 &&
        energyDrift <= 1e-4 &&
        angularDrift <= 1e-6
      ) {
        return makeRisk(
          "yellow",
          "Risco moderado",
          "O caso Apophis permaneceu utilizavel, mas ja mostra erro acumulado, drift ou fallback em nivel de atencao.",
          "amarelo",
          validationRiskReasons(payload, "yellow", values)
        );
      }

      return makeRisk(
        "red",
        "Risco alto",
        "A validacao Apophis mostrou erro, drift ou fallback em nivel que pede revisao antes de vender o resultado como robusto.",
        "vermelho",
        validationRiskReasons(payload, "red", values)
      );
    }

    function classifyTrajectoryRisk(payload) {
      const energyDrift = Math.abs(payload.metrics?.energy_drift ?? Number.POSITIVE_INFINITY);
      const angularDrift = Math.abs(payload.metrics?.angular_momentum_drift ?? Number.POSITIVE_INFINITY);
      const fallbackCount = (payload.fallback_events || []).length;
      const values = { energyDrift, angularDrift, fallbackCount };

      if (fallbackCount === 0 && energyDrift <= 1e-6 && angularDrift <= 1e-8) {
        return makeRisk(
          "green",
          "Trajetoria estavel",
          "A visualizacao foi gerada com comportamento numerico estavel e sem fallback.",
          "verde",
          trajectoryRiskReasons(payload, "green", values)
        );
      }

      if (fallbackCount <= 3 && energyDrift <= 1e-4 && angularDrift <= 1e-6) {
        return makeRisk(
          "yellow",
          "Trajetoria com atencao",
          "A simulacao ainda e legivel, mas ja houve fallback ou drift acima do ideal.",
          "amarelo",
          trajectoryRiskReasons(payload, "yellow", values)
        );
      }

      return makeRisk(
        "red",
        "Trajetoria instavel",
        "A simulacao mostrou sinais fortes de instabilidade numerica ou necessidade excessiva de fallback.",
        "vermelho",
        trajectoryRiskReasons(payload, "red", values)
      );
    }

    function kvRowsHtml(entries) {
      if (!entries.length) {
          return `<div class="empty-card">Nenhum destaque adicional para esta execucao.</div>`;
      }
      return entries.map(([key, value]) => `
        <div class="kv-row">
          <div class="kv-key">${key}</div>
          <div class="kv-value">${formatValue(value)}</div>
        </div>
      `).join("");
    }

    function fallbackRowsHtml(events) {
      if (!events || events.length === 0) {
        return `<div class="empty-card">Nenhum fallback registrado nesta execucao.</div>`;
      }
      return events.slice(0, 8).map((event) => `
        <div class="fallback-item">
          <strong>${event.reason || "fallback"}</strong>
          <span>step=${event.step} | t=${formatValue(event.time_days)} d</span>
          <span>bodies=${(event.affected_bodies || []).join(", ") || "n/a"}</span>
          <span>score=${formatValue(event.score)} | action=${event.action || "n/a"}</span>
        </div>
      `).join("");
    }

    function riskReasonRowsHtml(reasons) {
      if (!reasons || reasons.length === 0) {
        return `
          <div class="risk-reason-row">
            <strong>Sem motivo detalhado</strong>
            <span>Use as metricas e o JSON tecnico para inspecao manual desta resposta.</span>
          </div>
        `;
      }
      return reasons.map((reason) => `
        <div class="risk-reason-row">
          <strong>${reason.title}</strong>
          <span>${reason.detail}</span>
        </div>
      `).join("");
    }

    function renderRiskBanner(risk) {
      const banner = document.getElementById("risk-banner");
      banner.setAttribute("data-level", risk.level || "neutral");
      document.getElementById("risk-title").textContent = risk.title || "Sem classificacao";
      document.getElementById("risk-description").textContent = risk.description || "Sem descricao disponivel.";
      document.getElementById("risk-pill").textContent = risk.pill || "neutro";
      const explanation = document.getElementById("risk-explain");
      explanation.setAttribute("data-level", risk.level || "neutral");
      document.getElementById("risk-reason-body").innerHTML = riskReasonRowsHtml(risk.reasons);
    }

    function buildReportModel(payload) {
      if (payload && payload.benchmark) {
        const hybrid = payload.benchmark.hybrid || {};
        const hybridMetrics = (hybrid.metrics || {});
        const summaryMetrics = [
          ["Speedup vs referencia", hybridMetrics.speedup_vs_reference],
          ["Fallbacks acionados", payload.fallback_count],
          ["Erro final de posicao (AU)", payload.comparison_metrics?.final_position_error_au],
          ["Drift de energia", payload.hybrid_metrics?.energy_drift],
        ];
        const detailEntries = [
          ["Cenario", payload.fixture_name],
          ["Passos", payload.steps],
          ["Passo temporal (dias)", payload.dt_days],
          ["Checkpoint usado", payload.checkpoint_path],
          ["Scaler usado", payload.scaler_path],
          ["Erro medio de posicao (AU)", payload.comparison_metrics?.mean_position_error_au],
          ["Erro medio de velocidade (AU/day)", payload.comparison_metrics?.mean_velocity_error_au_day],
          ["Erro na distancia Terra-Apophis (AU)", payload.comparison_metrics?.earth_apophis_distance_error_au],
          ["Tempo do modo hibrido (s)", hybrid.runtime_seconds],
          ["Taxa de fallback", hybridMetrics.fallback_rate],
        ];
        return {
          heading: "Relatorio de validacao do Apophis",
          subtitle: "Comparacao entre a referencia fisica e o modo hibrido, com foco em erro acumulado, estabilidade, seguranca e trajetorias sobrepostas no 3D.",
          badges: [
            badgeHtml("apophis"),
            badgeHtml(`passos ${payload.steps}`),
            badgeHtml(`fallbacks ${payload.fallback_count}`),
            badgeHtml(`speedup ${formatValue(hybridMetrics.speedup_vs_reference)}x`),
            badgeHtml(payload.checkpoint_path ? "com IA" : "sem IA"),
          ],
          metricCards: summaryMetrics,
          detailEntries,
          fallbackEvents: payload.fallback_events || [],
          risk: classifyValidationRisk(payload),
        };
      }

      if (payload && payload.frames && payload.ids) {
        const metrics = payload.metrics || {};
        return {
          heading: "Visualizacao da trajetoria",
          subtitle: "Trajetoria 3D pronta para inspecao interativa no navegador.",
          badges: [
            badgeHtml("trajetoria"),
            badgeHtml(`corpos ${payload.ids.length}`),
            badgeHtml(`passos ${Math.max(payload.frames.length - 1, 0)}`),
            badgeHtml(`fallbacks ${(payload.fallback_events || []).length}`),
          ],
          metricCards: [
            ["Corpos", payload.ids.length],
            ["Passos", Math.max(payload.frames.length - 1, 0)],
            ["Drift de energia", metrics.energy_drift],
            ["Drift angular", metrics.angular_momentum_drift],
          ],
          detailEntries: [
            ["Origem", payload.source],
            ["Passo temporal (dias)", payload.dt_days],
            ["Distancia Terra-Apophis final (AU)", metrics.earth_apophis_distance_final_au],
            ["Eventos de fallback", (payload.fallback_events || []).length],
          ],
          fallbackEvents: payload.fallback_events || [],
          risk: classifyTrajectoryRisk(payload),
        };
      }

      if (payload && payload.best_val_loss !== undefined) {
        const history = payload.history || [];
        return {
          heading: "Treino concluido",
          subtitle: "Resumo do ajuste supervisionado do modelo residual e artefatos gerados para simulacao.",
          badges: [
            badgeHtml("treino"),
            badgeHtml(`melhor epoca ${payload.best_epoch}`),
            badgeHtml(`epocas ${history.length}`),
          ],
          metricCards: [
            ["Melhor epoca", payload.best_epoch],
            ["Melhor val loss", payload.best_val_loss],
            ["Entradas no historico", history.length],
            ["Status", "concluido"],
          ],
          detailEntries: [
            ["Dataset", payload.dataset_dir],
            ["Saida", payload.output_dir],
            ["Checkpoint", payload.checkpoint_path],
            ["Scaler", payload.scaler_path],
            ["OOD guard", payload.ood_guard_path],
            ...(history.length ? Object.entries(history[history.length - 1]) : []),
          ],
          fallbackEvents: [],
          risk: makeRisk("green", "Treino concluido", "O backend finalizou o treino e salvou o resumo principal desta execucao.", "verde"),
        };
      }

      if (payload && payload.kind && payload.output_dir) {
        return {
          heading: "Geracao de dataset concluida",
          subtitle: "Persistencia concluida para a etapa de dados do pipeline.",
          badges: [
            badgeHtml("dataset"),
            badgeHtml(payload.kind),
          ],
          metricCards: [
            ["Tipo", payload.kind],
            ["Saida", payload.output_dir],
          ],
          detailEntries: Object.entries(payload),
          fallbackEvents: [],
          risk: makeRisk("green", "Dataset gerado", "A etapa de dados terminou corretamente e os artefatos foram persistidos.", "verde"),
        };
      }

      if (payload && payload.status && payload.version) {
        return {
          heading: "Saude do servico",
          subtitle: "Resposta simples do backend para confirmar disponibilidade.",
          badges: [
            badgeHtml(`status ${payload.status}`),
            badgeHtml(`versao ${payload.version}`),
          ],
          metricCards: [
            ["Status", payload.status],
            ["Versao", payload.version],
          ],
          detailEntries: Object.entries(payload),
          fallbackEvents: [],
          risk: makeRisk("green", "Servico disponivel", "A API respondeu normalmente e esta pronta para uso.", "verde"),
        };
      }

      return {
        heading: "Resposta tecnica",
        subtitle: "Payload recebido do backend.",
        badges: [badgeHtml("generico")],
        metricCards: [],
        detailEntries: Object.entries(payload || {}),
        fallbackEvents: [],
        risk: makeRisk("yellow", "Leitura manual", "Esta resposta nao tem classificacao automatica forte. Use o JSON tecnico para inspecao detalhada.", "amarelo"),
      };
    }

    function renderExecutionPanel(payload) {
      const report = buildReportModel(payload);
      document.getElementById("results-heading").textContent = report.heading;
      document.getElementById("results-subtitle").textContent = report.subtitle;
      document.getElementById("results-badges").innerHTML = report.badges.join("");
      document.getElementById("metric-grid").innerHTML = report.metricCards.length
        ? report.metricCards.map(([label, value]) => metricCardHtml(label, value)).join("")
        : `<div class="empty-card">Nenhuma metrica principal disponivel para esta resposta.</div>`;
      document.getElementById("primary-details-body").innerHTML = kvRowsHtml(report.detailEntries);
      document.getElementById("fallback-body").innerHTML = fallbackRowsHtml(report.fallbackEvents);
      renderRiskBanner(report.risk || makeRisk("yellow", "Sem classificacao", "Nao foi possivel classificar o risco desta resposta.", "amarelo"));
    }

    function setOutput(payload) {
      const text = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
      renderExecutionPanel(payload);
      document.getElementById("output-box").textContent = text;
    }

    function hexToRgba(hex, alpha) {
      const normalized = hex.replace("#", "");
      const value = normalized.length === 3
        ? normalized.split("").map((char) => char + char).join("")
        : normalized;
      const numeric = Number.parseInt(value, 16);
      const r = (numeric >> 16) & 255;
      const g = (numeric >> 8) & 255;
      const b = numeric & 255;
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    function setSelectValueByName(formId, fieldName, value) {
      const element = document.querySelector(`#${formId} [name="${fieldName}"]`);
      if (!element || !value) {
        return;
      }
      const optionExists = Array.from(element.options || []).some((option) => option.value === value);
      if (optionExists) {
        element.value = value;
      }
    }

    function setFieldValueByName(formId, fieldName, value) {
      const element = document.querySelector(`#${formId} [name="${fieldName}"]`);
      if (!element) {
        return;
      }
      const normalizedValue = value === null || value === undefined ? "" : String(value);
      if (element.tagName === "SELECT") {
        const optionExists = Array.from(element.options || []).some((option) => option.value === normalizedValue);
        if (optionExists) {
          element.value = normalizedValue;
        }
        return;
      }
      element.value = normalizedValue;
    }

    function simulationDefaults() {
      return {
        fixture_name: state.catalog?.defaults?.default_fixture || "apophis/apophis_fixture.json",
        steps: 180,
        dt_days: 1.0,
        checkpoint_path: null,
        scaler_path: null,
        ood_guard_path: null,
      };
    }

    function simulationPayloadFromForm() {
      return formPayload("simulate-form", simulationDefaults());
    }

    function updateSimulationPayloadEditor(payload) {
      const editor = document.getElementById("simulation-payload-editor");
      if (!editor) {
        return;
      }
      editor.value = JSON.stringify(payload || simulationPayloadFromForm(), null, 2);
    }

    function applySimulationPreset(values) {
      const payload = { ...simulationDefaults(), ...values };
      simulationFieldNames.forEach((fieldName) => setFieldValueByName("simulate-form", fieldName, payload[fieldName]));
      updateSimulationPayloadEditor(payload);
      return payload;
    }

    function readSimulationPayloadEditor() {
      const editor = document.getElementById("simulation-payload-editor");
      try {
        return JSON.parse(editor.value || "{}");
      } catch (error) {
        setOutput({
          error: `JSON invalido: ${error.message}`,
          endpoint: "/simulate/trajectory",
        });
        setStatus(`Erro: JSON invalido (${error.message})`);
        return null;
      }
    }

    function buildRedExamplePayload() {
      const frames = [
        [[0, 0, 0], [1.0, 0.0, 0.0], [1.12, 0.04, 0.0]],
        [[0, 0, 0], [0.78, 0.56, 0.02], [0.92, 0.78, 0.08]],
        [[0, 0, 0], [0.18, 0.98, 0.05], [0.42, 1.28, 0.16]],
        [[0, 0, 0], [-0.64, 0.72, 0.12], [-0.25, 1.58, 0.34]],
        [[0, 0, 0], [-1.18, -0.1, 0.18], [0.28, 1.9, 0.58]],
        [[0, 0, 0], [-0.42, -1.34, 0.3], [1.42, 2.18, 0.84]],
      ];
      return {
        source: "exemplo_didatico_vermelho",
        ids: ["Sun", "Earth", "Apophis"],
        frames,
        dt_days: 7.0,
        metrics: {
          energy_drift: 0.025,
          angular_momentum_drift: 0.00024,
          earth_apophis_distance_final_au: 2.18,
        },
        fallback_events: [
          { step: 2, time_days: 14, reason: "energy_drift", affected_bodies: ["Sun", "Earth", "Apophis"], score: 0.91, action: "fallback_to_reference_engine" },
          { step: 3, time_days: 21, reason: "angular_momentum_drift", affected_bodies: ["Sun", "Earth", "Apophis"], score: 0.94, action: "fallback_to_reference_engine" },
          { step: 4, time_days: 28, reason: "speed_limit", affected_bodies: ["Apophis"], score: 0.97, action: "fallback_to_reference_engine" },
          { step: 5, time_days: 35, reason: "distance_limit", affected_bodies: ["Earth", "Apophis"], score: 0.99, action: "fallback_to_reference_engine" },
        ],
        note: "Payload demonstrativo para mostrar o semaforo vermelho quando a simulacao acumula drift e varios fallbacks.",
      };
    }

    function showRedExample() {
      const payload = buildRedExamplePayload();
      setOutput(payload);
      renderTrajectory3D(payload);
      setStatus("Exemplo vermelho carregado no relatorio; este exemplo e demonstrativo e nao foi enviado ao backend.");
    }

    function applyTrainingArtifacts(payload) {
      if (!payload || !payload.checkpoint_path) {
        return;
      }
      const targets = [
        ["simulate-form", "checkpoint_path", payload.checkpoint_path],
        ["simulate-form", "scaler_path", payload.scaler_path],
        ["simulate-form", "ood_guard_path", payload.ood_guard_path],
        ["apophis-form", "checkpoint_path", payload.checkpoint_path],
        ["apophis-form", "scaler_path", payload.scaler_path],
        ["apophis-form", "ood_guard_path", payload.ood_guard_path],
        ["train-specialist-form", "base_checkpoint", payload.checkpoint_path],
      ];
      targets.forEach(([formId, fieldName, value]) => setSelectValueByName(formId, fieldName, value));
    }

    async function autoPreviewTrainingArtifacts(payload) {
      if (!payload || !payload.checkpoint_path) {
        return;
      }
      await callApi(
        "/simulate/trajectory",
        {
          fixture_name: state.catalog?.defaults?.default_fixture || "apophis/apophis_fixture.json",
          steps: 180,
          dt_days: 1.0,
          checkpoint_path: payload.checkpoint_path,
          scaler_path: payload.scaler_path,
          ood_guard_path: payload.ood_guard_path,
        },
        null
      );
    }

    function renderTrajectory3D(payload) {
      if (!window.Plotly || !payload.ids) {
        return;
      }
      const traces = [];
      if (payload.reference_frames && payload.hybrid_frames) {
        payload.ids.forEach((bodyId, index) => {
          const color = orbitPalette[index % orbitPalette.length];
          traces.push({
            type: "scatter3d",
            mode: "lines",
            name: `${bodyId} ref`,
            x: payload.reference_frames.map((frame) => frame[index][0]),
            y: payload.reference_frames.map((frame) => frame[index][1]),
            z: payload.reference_frames.map((frame) => frame[index][2]),
            line: {
              color: hexToRgba(color, 0.34),
              width: bodyId.toLowerCase() === "sun" ? 4 : 2,
            },
            hovertemplate: `${bodyId} ref<br>x=%{x:.4f}<br>y=%{y:.4f}<br>z=%{z:.4f}<extra></extra>`,
          });
          traces.push({
            type: "scatter3d",
            mode: "lines+markers",
            name: `${bodyId} hybrid`,
            x: payload.hybrid_frames.map((frame) => frame[index][0]),
            y: payload.hybrid_frames.map((frame) => frame[index][1]),
            z: payload.hybrid_frames.map((frame) => frame[index][2]),
            line: {
              color,
              width: bodyId.toLowerCase() === "sun" ? 8 : 4,
            },
            marker: {
              color,
              size: bodyId.toLowerCase() === "sun" ? 5 : 3,
            },
            hovertemplate: `${bodyId} hybrid<br>x=%{x:.4f}<br>y=%{y:.4f}<br>z=%{z:.4f}<extra></extra>`,
          });
        });
      } else if (payload.frames) {
        payload.ids.forEach((bodyId, index) => {
          const color = orbitPalette[index % orbitPalette.length];
          traces.push({
            type: "scatter3d",
            mode: "lines+markers",
            name: bodyId,
            x: payload.frames.map((frame) => frame[index][0]),
            y: payload.frames.map((frame) => frame[index][1]),
            z: payload.frames.map((frame) => frame[index][2]),
            line: {
              color,
              width: bodyId.toLowerCase() === "sun" ? 8 : 4,
            },
            marker: {
              color,
              size: bodyId.toLowerCase() === "sun" ? 5 : 3,
            },
            hovertemplate: `${bodyId}<br>x=%{x:.4f}<br>y=%{y:.4f}<br>z=%{z:.4f}<extra></extra>`,
          });
        });
      } else {
        return;
      }

      const layout = {
        margin: { l: 0, r: 0, t: 0, b: 0 },
        paper_bgcolor: "#030814",
        plot_bgcolor: "#030814",
        font: { color: "#ecf6ff" },
        legend: {
          bgcolor: "rgba(6,14,28,0.72)",
          bordercolor: "rgba(108,170,255,0.14)",
          borderwidth: 1,
        },
        scene: {
          bgcolor: "#030814",
          xaxis: { title: "X", color: "#d8eaff", gridcolor: "#143055", zerolinecolor: "#2e6fb0" },
          yaxis: { title: "Y", color: "#d8eaff", gridcolor: "#143055", zerolinecolor: "#2e6fb0" },
          zaxis: { title: "Z", color: "#d8eaff", gridcolor: "#143055", zerolinecolor: "#2e6fb0" },
          camera: {
            eye: { x: 1.55, y: 1.16, z: 0.92 },
          },
        },
      };

      Plotly.newPlot("trajectory-plot", traces, layout, {
        responsive: true,
        displaylogo: false,
        scrollZoom: true,
      });
      const stepCount = payload.frames
        ? payload.frames.length - 1
        : payload.hybrid_frames
          ? payload.hybrid_frames.length - 1
          : 0;
      const fallbackCount = (payload.fallback_events || []).length;
      const modeLabel = payload.reference_frames && payload.hybrid_frames ? "Comparacao referencia vs hibrido" : "Trajetoria simulada";
      const meta = `${modeLabel} | Corpos: ${payload.ids.length} | Passos: ${stepCount} | dt_days: ${payload.dt_days} | Fallbacks: ${fallbackCount}`;
      document.getElementById("plot-meta").textContent = meta;
    }

    function clearTrajectoryPlot() {
      if (!window.Plotly) {
        return;
      }
      Plotly.purge("trajectory-plot");
      document.getElementById("plot-meta").textContent = "Visual limpo.";
    }

    function fillDefaults(catalog) {
      document.querySelectorAll("[data-fill]").forEach((input) => {
        const key = input.getAttribute("data-fill");
        if (catalog.defaults[key]) {
          input.value = catalog.defaults[key];
        }
      });
    }

    function fillSelects(catalog) {
      document.querySelectorAll("[data-select]").forEach((select) => {
        const key = select.getAttribute("data-select");
        const allowEmpty = select.getAttribute("data-allow-empty") === "true";
        const values = catalog[key] || [];
        const previousValue = select.value;
        select.innerHTML = "";
        if (allowEmpty) {
          const empty = document.createElement("option");
          empty.value = "";
          empty.textContent = "(nenhum)";
          select.appendChild(empty);
        }
        values.forEach((value) => {
          const option = document.createElement("option");
          option.value = key === "fixtures" ? value : value.startsWith("models/") || value.startsWith("data/") || value.startsWith("reports/") ? value : `${key === "checkpoints" || key === "scalers" || key === "ood_guards" ? "models/checkpoints/" : ""}${value}`;
          option.textContent = value;
          select.appendChild(option);
        });
        if (!allowEmpty && values.length === 0) {
          const option = document.createElement("option");
          option.value = "";
          option.textContent = "(vazio)";
          select.appendChild(option);
        }
        const desiredValue = previousValue || (key === "fixtures" ? catalog.defaults?.default_fixture : "");
        const desiredOptionExists = Array.from(select.options || []).some((option) => option.value === desiredValue);
        if (desiredValue && desiredOptionExists) {
          select.value = desiredValue;
        }
      });
      document.getElementById("fixtures-count").textContent = String((catalog.fixtures || []).length);
      document.getElementById("checkpoints-count").textContent = String((catalog.checkpoints || []).length);
    }

    async function loadHealth() {
      const response = await fetch("/health");
      const payload = await response.json();
      document.getElementById("health-value").textContent = `${payload.status} v${payload.version}`;
      return payload;
    }

    async function loadCatalog() {
      const response = await fetch("/ui/catalog");
      const payload = await response.json();
      state.catalog = payload;
      fillDefaults(payload);
      fillSelects(payload);
      updateSimulationPayloadEditor();
      return payload;
    }

    async function callApi(url, body, button) {
      try {
        if (button) button.disabled = true;
        setStatus(`Executando ${url}...`);
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        const payload = await response.json();
        setOutput(payload);
        if ((payload.frames && payload.ids) || (payload.reference_frames && payload.hybrid_frames && payload.ids)) {
          renderTrajectory3D(payload);
        }
        if (!response.ok) {
          throw new Error(payload.detail || `Falha HTTP ${response.status}`);
        }
        setStatus(`Concluido: ${url}`);
        await loadCatalog();
        applyTrainingArtifacts(payload);
        if (url.startsWith("/train/") && payload.checkpoint_path) {
          setStatus(`Concluido: ${url} | artefatos ligados ao simulador 3D`);
          await autoPreviewTrainingArtifacts(payload);
        }
      } catch (error) {
        setOutput({ error: error.message, endpoint: url });
        setStatus(`Erro: ${error.message}`);
      } finally {
        if (button) button.disabled = false;
      }
    }

    function formToObject(form) {
      const data = new FormData(form);
      const payload = {};
      for (const [key, value] of data.entries()) {
        if (value === "") {
          payload[key] = null;
          continue;
        }
        if (["num_samples", "min_bodies", "max_bodies", "epochs", "batch_size", "steps"].includes(key)) {
          payload[key] = Number(value);
        } else if (["dt_days"].includes(key)) {
          payload[key] = Number(value);
        } else {
          payload[key] = value;
        }
      }
      return payload;
    }

    function formPayload(formId, defaults) {
      const form = document.getElementById(formId);
      if (!form) {
        return defaults;
      }
      return { ...defaults, ...formToObject(form) };
    }

    function bindForm(id, url) {
      const form = document.getElementById(id);
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        await callApi(url, formToObject(form), form.querySelector("button[type='submit']"));
      });
    }

    document.getElementById("refresh-button").addEventListener("click", async () => {
      setStatus("Atualizando catalogo...");
      await loadCatalog();
      setStatus("Catalogo atualizado.");
    });

    document.getElementById("health-button").addEventListener("click", async () => {
      setStatus("Validando saude do servico...");
      const payload = await loadHealth();
      setOutput(payload);
      setStatus("Saude do servico atualizada.");
    });

    document.getElementById("preview-button").addEventListener("click", async () => {
      const payload = formPayload("simulate-form", {
        fixture_name: state.catalog?.defaults?.default_fixture || "apophis/apophis_fixture.json",
        steps: 180,
        dt_days: 1.0,
        checkpoint_path: null,
        scaler_path: null,
        ood_guard_path: null,
      });
      await callApi("/simulate/trajectory", payload, document.getElementById("preview-button"));
    });

    document.getElementById("green-example-button").addEventListener("click", async () => {
      const payload = applySimulationPreset(simulationDefaults());
      await callApi("/simulate/trajectory", payload, document.getElementById("green-example-button"));
    });

    document.getElementById("red-example-button").addEventListener("click", () => {
      showRedExample();
    });

    document.getElementById("quick-demo-button").addEventListener("click", async () => {
      document.getElementById("preview-button").click();
    });

    document.getElementById("run-apophis-now-button").addEventListener("click", async () => {
      const payload = formPayload("apophis-form", {
        fixture_name: state.catalog?.defaults?.default_fixture || "apophis/apophis_fixture.json",
        steps: 180,
        dt_days: 1.0,
        checkpoint_path: null,
        scaler_path: null,
        ood_guard_path: null,
      });
      await callApi("/validate/apophis", payload, document.getElementById("run-apophis-now-button"));
    });

    document.getElementById("quick-apophis-button").addEventListener("click", async () => {
      document.getElementById("run-apophis-now-button").click();
    });

    document.getElementById("clear-plot-button").addEventListener("click", () => {
      clearTrajectoryPlot();
    });

    document.getElementById("sync-payload-button").addEventListener("click", () => {
      updateSimulationPayloadEditor();
      setStatus("Payload JSON atualizado a partir dos campos da simulacao.");
    });

    document.getElementById("run-payload-button").addEventListener("click", async () => {
      const payload = readSimulationPayloadEditor();
      if (!payload) {
        return;
      }
      await callApi("/simulate/trajectory", payload, document.getElementById("run-payload-button"));
    });

    document.getElementById("simulate-form").addEventListener("input", (event) => {
      if (event.target?.id === "simulation-payload-editor") {
        return;
      }
      updateSimulationPayloadEditor();
    });

    document.getElementById("simulate-form").addEventListener("change", (event) => {
      if (event.target?.id === "simulation-payload-editor") {
        return;
      }
      updateSimulationPayloadEditor();
    });

    bindForm("generalist-form", "/generate/generalist");
    bindForm("specialist-form", "/generate/specialist");
    bindForm("train-generalist-form", "/train/generalist");
    bindForm("train-specialist-form", "/train/specialist");
    bindForm("simulate-form", "/simulate/trajectory");
    bindForm("apophis-form", "/validate/apophis");

    (async () => {
      try {
        await loadHealth();
        const catalog = await loadCatalog();
        setOutput(catalog);
        setStatus("Interface pronta.");
        await callApi(
          "/simulate/trajectory",
          {
            fixture_name: catalog.defaults.default_fixture,
            steps: 180,
            dt_days: 1.0,
            checkpoint_path: null,
            scaler_path: null,
            ood_guard_path: null,
          },
          null
        );
      } catch (error) {
        setStatus(`Falha ao inicializar interface: ${error.message}`);
      }
    })();
  </script>
</body>
</html>
"""
