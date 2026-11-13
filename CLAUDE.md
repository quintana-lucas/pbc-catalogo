# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static catalog site template (currently configured for the client "Planta Baja Cocina"): products come from a published Google Sheets CSV, with a cart and ordering via WhatsApp. Repo content and UI copy are in Spanish (rioplatense). `README.md` documents the per-client setup and every `config.json` key; `docs/diseno-acceso-catering.md` is the agreed design for the landing page / per-module navigation / paper comanda (not implemented yet, tasks are in the `/cola` queue).

## Commands

- Build: `python3 build.py` (standard library only, nothing to install; on Windows use `python build.py`). Output goes to `_site/` (git-ignored); open `_site/index.html`.
- There are no tests and no linter. To verify a change, build and inspect the generated pages in a browser (the check is the build succeeding plus looking at the result at mobile width).
- Deploy: `.github/workflows/publicar.yml` runs `build.py` on push to `main`, manually, and hourly (08–22 Argentina time, only if the sheet changed) and publishes `_site/` to GitHub Pages.

Env vars read by `build.py`: `SHEET_CSV_URL` (overrides `planilla_csv`), `SOLO_SI_CAMBIA`, `FORZAR`, `QUIENES_SOMOS`.

## Architecture

Everything client-specific lives in `config.json`; `build.py`, `plantilla/` and the workflow are meant to stay client-agnostic.

`build.py` is a single-file generator, not a framework:
- **Templating** is plain `str.replace` of `{{MARCA}}` placeholders (`rellenar()`). `plantilla/encabezado.html` is injected into every page via `{{ENCABEZADO}}` first. A new placeholder has to be added both in the template and in the `reemplazos` dict of the page that uses it; unreplaced `{{...}}` silently ships to the output.
- **Theming**: `config.json` colors/fonts become CSS variables (`COLORES` map in `build.py` → `--principal`, `--tinta`, `--linea`...) emitted by `estilos_marca()` and prepended to `plantilla/base.css` as `{{ESTILOS_BASE}}`. Templates should use the variables, never hard-coded colors.
- **Data flow to the browser**: Python serializes products / catering options into a `<script id="datos" type="application/json">{{DATOS}}</script>` block; the inline JS at the bottom of `index.html` and `pedidos-especiales.html` reads it. All cart, quote and WhatsApp-message logic is client-side inline JS in those two templates.
- **Pages**: `index.html` (catalog), `pedidos-especiales.html` (catering quote, only when `pedidos_especiales.activo`), `quienes-somos.html` (only when `quienes_somos_modo` is `pagina`; `modal` renders a `<dialog>` inside the catalog instead). The header icons are built in `redes()` and shared across pages, with `pagina_actual` marking the current one.
- **Publish safety**: `main()` refuses to publish (exit 1, site stays as it was) if the sheet lacks `Nombre`/`Precio`, is empty, or has fewer than half the products of the live site (`productos.json` fetched from `dominio`; `FORZAR` bypasses). Hourly runs skip publishing when products are unchanged. Keep these guards intact when editing `main()`.
- **Two CSV sources**: products (`planilla_csv` → fallback `data/productos.csv`) and catering (`pedidos_especiales.catering_csv` → fallback `data/catering.csv`, with a log warning). Headers are matched ignoring case and accents (`normalizar()`), and `Descipción` (typo) is accepted on purpose.
- Warnings use the `::warning::` GitHub Actions syntax so they show up in the Action log.

## Gotchas

- The header logo must link to the catalog (`./`) on every page, including the catalog itself (where it sits inside the `<h1>`). `marca()` in `build.py` enforces it; keep it when changing the header.
- `config.json` key `pedidos_especiales` keeps its name even though the UI calls the module "Catering"; the design doc says not to rename it.
- Product photos are matched case-sensitively against `img/` (servers are case-sensitive); `revisar_fotos()` fixes the case or falls back to the emoji and warns.
- `config.json` has a blank `dominio`, so the live-site comparison and canonical/OG metadata are skipped until it is set.
- `.claude/worktrees/` holds Claude worktrees; the main checkout is read-only for edits, so work in a worktree.
