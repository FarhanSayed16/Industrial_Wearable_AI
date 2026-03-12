# Images for README and documentation

Add your images here and reference them from the main **README.md** or from **docs/RESEARCH_PAPER.md**.

## Suggested files (README)

| File | Description |
|------|-------------|
| `readme-hero.png` | System overview or dashboard home (e.g. 1200×600 or 16:9) |
| `readme-dashboard.png` | Supervisor dashboard — Live Overview (workers, KPIs, alerts) |
| `readme-wearable.png` | Wearable device photo (ESP32 + IMU on wrist or desk) |
| `readme-architecture.png` | High-level architecture diagram (export from `docs/uml/00-context.puml` or `02-component.puml`) |

Generate architecture diagram: from repo root, run `plantuml -tpng docs/uml/00-context.puml` (or use VS Code PlantUML extension) and save the output here as `readme-architecture.png`.

## Research paper figures

For **docs/RESEARCH_PAPER.md**, you can use **docs/figures/** or this folder. See **docs/uml/README.md** for the mapping from figure numbers to PlantUML files.
