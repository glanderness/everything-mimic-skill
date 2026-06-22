---
name: wechat-style-layout
description: Use when extracting reusable WeChat official account article layout styles from PDF samples, turning those observations into editable style profiles, or applying a saved style profile to new Chinese articles as original WeChat-ready HTML/Markdown layouts.
---

# WeChat Style Layout

## Overview

Use this skill to build a reusable WeChat official account layout style from PDF samples, then apply that style to new articles. The goal is not pixel-perfect copying; it is to extract generalizable layout principles and generate original layouts with a similar reading rhythm.

## Core Contract

- Final output is body-only by default: no WeChat article title, author, account metadata, date, location, read/listen count, or native header area.
- Preserve the source style's text formatting and reading rhythm.
- Understand the whole article's image cadence, not only isolated images.
- Generate WeChat-compatible HTML by default.
- Always provide `preview.html` as the primary user-facing deliverable.
- Generated images should be saved as local assets and referenced from HTML.
- Default publishing handoff is local HTML plus local image folder plus upload map.
- Do not promise that pasted HTML will automatically carry local or hosted images into WeChat.

## Workflow

### 1. Style Extraction From PDFs

When the user provides one or more PDF samples:

1. Create a style folder under `wechat-style-runs/风格/`, using `style-id_中文风格名/`.
2. Render PDF pages and collect rough page/text metrics.
3. Inspect the rendered pages visually. For long PDFs, sample first page, middle page, and pages containing headings, quotes, cards, or images.
4. Name the extracted style based on visual elements and content state, not only the source account name.
5. Write `style-profile.json` with measurements, component rules, rhythm rules, image cadence, naming fields, and confidence notes.
6. Write `style-brief.md` as a human-readable summary.
7. If the source PDF contains recurring illustrations, diagrams, screenshots, or image captions, add image style rules.

Every extracted style must include:

- `style_display_name`
- `style_id`
- `source_label`

### 2. Apply Style To A New Article

When the user provides a new article and a saved style template:

1. Read the target `style-profile.json`.
2. Create an output folder under `wechat-style-runs/输出/`, using `YYYY-MM-DD_文章核心内容_风格名/`.
3. Segment the article globally: intro, sections, concepts, paragraphs, quotes, lists, image needs, captions, and closing.
4. Treat the WeChat article title and metadata as editor/page chrome, not body content.
5. Apply both structural rhythm and visual styling.
6. Mirror the template's global image cadence. If the source uses one concept image per major section, prepare one image for each major section.
7. Generate WeChat-compatible HTML.
8. Generate `preview.html`.
9. Run a self-check for mobile readability, image rhythm, unsupported CSS, over-decoration, and body-only output.

## Output Standards

Default root folder structure:

- `wechat-style-runs/输出/`: user-facing article outputs.
- `wechat-style-runs/风格/`: reusable style templates.
- `wechat-style-runs/README.md`: root index listing available style ids.

Each output project should contain:

- `article.wechat.html`
- `preview.html`
- `assets/`
- `DELIVERY.md`
- optional `wechat-image-upload-map.md`
- `layout-notes.md`
- `self-check.md`

Each style folder should contain:

- `style-profile.json`
- `style-brief.md`
- optional `inspection.json`
- optional `pages/`
- `self-check.md`

## Replication Boundary

Extract reusable principles:

- spacing
- hierarchy
- reading rhythm
- component categories
- approximate palette mood
- image cadence

Do not copy:

- logos
- QR codes
- fixed brand marks
- original illustrations
- exact proprietary motifs
- source-specific labels that do not fit the new article

Prefer adapted, publishable, original layouts.

## Rendering Notes

WeChat layouts should be mobile-first, conservative in CSS, and robust when pasted into article editors.

Avoid:

- complex CSS selectors
- scripts
- canvas-only output
- animation required for meaning
- layout systems that collapse when pasted into WeChat
- rich webpage-only components

Prefer:

- `section`, `p`, `span`, `img`
- inline CSS
- simple wrappers
- local image assets
- explicit image upload maps

## Scripts

- `scripts/inspect_pdf.py`: render PDF pages and write a rough JSON inspection report.
- `scripts/render_preview.py`: insert body HTML into a preview shell.
- `scripts/save_style_template.py`: save an approved run as a reusable template.
- `scripts/extract_session_images.py`: decode built-in Codex Desktop image generation results from session JSONL into a project's `assets/` folder.

