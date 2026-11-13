---
name: Planta Baja Cocina
description: Warm, homemade ordering catalog on cream paper, with burgundy, olive and gold.
colors:
  burgundy: "#7a1f22"
  burgundy-deep: "#5e1619"
  olive: "#4b5a2c"
  olive-deep: "#3a4722"
  marigold: "#d9a23a"
  cream: "#f6efe2"
  plate-white: "#ffffff"
  cocoa-ink: "#2b211c"
  soft-cocoa: "#6b5d52"
  oat-line: "#e6dccb"
  terracotta-alert: "#a8431c"
typography:
  display:
    fontFamily: "Bricolage Grotesque, Georgia, serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1.1
  headline:
    fontFamily: "Bricolage Grotesque, Georgia, serif"
    fontSize: "1.6rem"
    fontWeight: 700
    lineHeight: 1.2
  title:
    fontFamily: "Figtree, system-ui, sans-serif"
    fontSize: "1.1rem"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "Figtree, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Figtree, system-ui, sans-serif"
    fontSize: "0.8rem"
    fontWeight: 800
    letterSpacing: "0.04em"
rounded:
  sm: "10px"
  md: "14px"
  lg: "16px"
  xl: "18px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "16px"
  lg: "24px"
  xl: "40px"
components:
  button-add:
    backgroundColor: "{colors.burgundy}"
    textColor: "{colors.plate-white}"
    rounded: "{rounded.pill}"
    padding: "9px 16px"
  button-add-hover:
    backgroundColor: "{colors.burgundy-deep}"
  button-order:
    backgroundColor: "{colors.olive}"
    textColor: "{colors.plate-white}"
    rounded: "{rounded.pill}"
    padding: "13px 22px"
  button-order-hover:
    backgroundColor: "{colors.olive-deep}"
  chip:
    backgroundColor: "{colors.plate-white}"
    textColor: "{colors.cocoa-ink}"
    rounded: "{rounded.pill}"
    padding: "8px 16px"
  chip-selected:
    backgroundColor: "{colors.olive}"
    textColor: "{colors.plate-white}"
  product-card:
    backgroundColor: "{colors.plate-white}"
    textColor: "{colors.cocoa-ink}"
    rounded: "{rounded.lg}"
  option-card:
    backgroundColor: "{colors.plate-white}"
    textColor: "{colors.cocoa-ink}"
    rounded: "{rounded.md}"
    padding: "14px 16px"
  input:
    backgroundColor: "{colors.plate-white}"
    textColor: "{colors.cocoa-ink}"
    rounded: "{rounded.sm}"
    padding: "11px 13px"
---

# Design System: Planta Baja Cocina

## Overview

**Creative North Star: "The Family Kitchen Table"**

The site should feel like a table set by someone who cooks for you: warm cream paper, white plates (cards), burgundy and olive from the logo, and a thin marigold line under the header. Everything is rounded and soft. Nothing looks corporate, glossy or cold. It is warm and homemade, and it stays quick to use on a phone.

Density is moderate: a product grid with generous 16px gutters, one clear action per card, and a floating order bar. Expression comes from the palette, the rounded forms and the friendly Bricolage Grotesque titles, not from decoration. The client's colors and fonts live in `config.json`; this document records the PBC values currently configured.

**Key Characteristics:**
- Cream page, white cards, cocoa-brown ink (never pure black on pure white).
- Burgundy for "add to cart", olive for "send the order" and navigation chips.
- Pills and 16px-rounded cards; soft, low shadows.
- Bricolage Grotesque for titles, Figtree for everything else.
- Emoji stand in when a product has no photo.

## Colors

A warm, earthy palette drawn from the logo: a deep wine red, an olive green and a touch of gold on cream paper.

### Primary
- **Cellar Burgundy** (#7a1f22): the "Agregar" button and the checked border of selected catering options. Pressed/hover state is **Burgundy Deep** (#5e1619).

### Secondary
- **Olive Grove** (#4b5a2c): the selected category chip, the header icon buttons, and the order actions ("Enviar pedido", "Cotizar catering"). Hover is **Olive Grove Deep** (#3a4722). White text sits on both.

### Tertiary
- **Marigold Gold** (#d9a23a): only the 3px rule under the header and the left border of the instructions notice. Never a fill for buttons or text.

### Neutral
- **Cream Paper** (#f6efe2): page background and the quantity stepper track.
- **Plate White** (#ffffff): cards, header, inputs, chips, modal and the comanda.
- **Cocoa Ink** (#2b211c): all text and titles (titles use ink, not burgundy).
- **Soft Cocoa** (#6b5d52): descriptions, presentation text, footer and "Consultar".
- **Oat Line** (#e6dccb): borders and dividers.
- **Terracotta Alert** (#a8431c): "Sin stock" and warnings only.

### Named Rules
**The Two-Verb Rule.** Burgundy means "put this in my order"; olive means "send it / go there". A button of the wrong color confuses the flow.

**The Gold Whisper Rule.** Marigold appears only as a thin line, never as a surface. Its rarity is the point.

**The Ink Titles Rule.** Section titles and headings use Cocoa Ink; color is reserved for actions.

## Typography

**Display Font:** Bricolage Grotesque (with Georgia, serif fallback)
**Body Font:** Figtree (with system-ui, sans-serif fallback)

**Character:** A rounded, slightly quirky grotesque for titles paired with a friendly, highly legible sans for text. Warm without being a script font. Both are loaded from Google Fonts (400, 600, 800) and set per client in `config.json`.

### Hierarchy
- **Display** (700, 2rem, 1.1): page title on Catering and the estimated total in the comanda.
- **Headline** (700, 1.6rem): category headings (with emoji) and the «¿Quiénes somos?» dialog title.
- **Title** (800 / 700, 1.25rem / 1.1rem): catering form section legends (Bricolage) and product names (Figtree).
- **Body** (400, 1rem, line-height 1.45): descriptions at .92rem in Soft Cocoa; keep intro text to about 62ch.
- **Label** (800, .8rem, +.04em, uppercase): "Sin stock". Prices are 800 with tabular numerals wherever amounts are compared.

### Named Rules
**The Tabular Money Rule.** Amounts in the cotizador use tabular numerals so columns of pesos align.

## Layout

A centered wrapper (max 1100px on the catalog, 1040px on Catering) with 16px side gutters. The catalog is a responsive grid of cards (`minmax(230px, 1fr)`, 16px gap) that becomes two columns with a 10px gap at 480px and below. A sticky category bar (chips + search, solid cream background with a soft shadow) stays at the top while scrolling.

The header is white with the logo centered, optional badges (sellos) at the left and round icon buttons at the right. At 640px and below the badges and icons drop to a row under the logo. Catering is a two-column layout (form 1.1fr, comanda .9fr, 40px gap) that stacks at 760px. Spacing rhythm: 6, 10, 12, 16, 24, 40px.

On mobile, descriptions are hidden and replaced by an "i" button with a small tooltip balloon, to keep cards short. The floating order bar sits 16px from the bottom edge, so the footer keeps 100px of bottom padding.

## Elevation & Depth

A hybrid. Resting cards use a soft two-layer shadow (`0 1px 2px rgba(0,0,0,.06), 0 6px 20px rgba(0,0,0,.07)`); form fields and option cards are flat with a 1.5px Oat Line border. Floating elements lift higher: the order bar (`0 10px 30px rgba(0,0,0,.18)`) and the dialog (`0 10px 40px rgba(0,0,0,.3)`, dark 50% backdrop).

### Named Rules
**The Float-Means-Action Rule.** Only things that follow the visitor (the order bar, the sticky category bar) or interrupt them (the dialog) get strong depth. Content stays calm.

## Shapes

Pills (999px) for every button, chip and search field; round (50%) 40px icon buttons in the header (34px under 480px). Cards are 16px, the order bar 18px, option cards 14px, notices 10-12px, inputs 10px. Selected catering options get a burgundy border plus a 1px burgundy ring. The comanda has a zigzag bottom edge, like a torn ticket (to be reworked into a ruled paper sheet per `docs/diseno-acceso-catering.md`). Product photos are shown whole (`object-fit: contain` on white), never cropped; products without a photo show an emoji on a faint olive tint.

## Components

### Buttons
- **Shape:** pill (999px).
- **Add (primary):** Cellar Burgundy, white text, 9px 16px, weight 800; hover Burgundy Deep.
- **Order (secondary):** Olive Grove, white text, 13px 22px (9px 16px in the order bar); hover Olive Grove Deep.
- **Ghost:** transparent with Soft Cocoa text ("Vaciar"); hover fills Cream.
- **Secondary on paper:** white with an inset 1.5px Oat Line ring ("Copiar resumen").
- **Header icons:** 40px round Olive Grove buttons with white glyphs.

### Chips
- **Style:** white, 1px control-edge border, Cocoa Ink text, 8px 16px, weight 600.
- **State:** selected is Olive Grove with white text and border; the row scrolls horizontally without a scrollbar.

### Cards / Containers
- **Corner Style:** 16px.
- **Background:** Plate White on Cream Paper.
- **Shadow Strategy:** the resting two-layer shadow.
- **Internal Padding:** 14px 16px (10px 12px on small phones); photo area is 4:3.
- **Sold out:** only the photo fades (55%, grayscale); the name and price turn Soft Cocoa and the "Sin stock" label stays full-strength Terracotta Alert, so every text keeps at least 4.5:1.

### Inputs / Fields
- **Style:** 1.5px control-edge border (`--borde-control`, ink mixed 55% into white, about 3.6:1; Oat Line is too faint to mark a field), white, 10px radius, 11px 13px padding; the search box is a pill. Oat Line stays for decorative dividers and card borders.
- **Focus:** browser default today (no custom focus ring yet).
- **Quantity stepper:** pill track in Cream with two white 32px round buttons.

### Navigation
- Header with icon buttons (WhatsApp, Instagram, Catering, optional «¿Quiénes somos?»), each with `aria-label` and `title`; the current page uses `aria-current`. The sticky category chips are the in-page navigation.

### The Comanda (signature)
The summary of a catering quote: white paper, 1.5px Oat Line border, zigzag bottom edge, dashed dividers between lines, amounts in tabular numerals and a large total in Bricolage Grotesque. It updates live (`aria-live`). Planned: a ruled-notebook look and a fixed bar on mobile.

## Do's and Don'ts

### Do:
- **Do** use Cellar Burgundy to add an item and Olive Grove to send or navigate.
- **Do** keep cream as the page background and white for surfaces that hold content.
- **Do** keep every tappable control at least 34px, and prefer 40px for header icons.
- **Do** read colors and fonts from the `config.json` variables (`--principal`, `--secundario`, `--acento`, `--fondo`, `--tinta`...), never hard-coded hex.
- **Do** keep working when a product has no photo, no price or is out of stock.

### Don't:
- **Don't** replace the established identity (logo, burgundy / olive / gold on cream, «Hecho con amor»); this is a confirmed commitment.
- **Don't** use marigold as a fill or for text.
- **Don't** color titles; they stay Cocoa Ink.
- **Don't** crop product photos or add decorative imagery that competes with them.
- **Don't** add pure black text or cold gray surfaces.
