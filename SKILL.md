---
name: everything-mimic-skill
description: Use when extracting reusable structure, style, rhythm, and platform constraints from reference content, comparing them with a new content task, and applying the resulting template. The current MVP focuses on WeChat official account article layout styles from PDF samples and WeChat-ready HTML outputs.
---

# Everything Mimic Skill

## Overview

Use this skill to build a reusable mimic system from reference content, then apply that system to new content. The long-term goal is not limited to WeChat layout. It is to observe any high-quality sample, extract its structure, rhythm, expression logic, visual language, medium constraints, and delivery rules, then turn those observations into an editable template.

The current MVP starts with WeChat official account article layout because it is a concrete, high-friction use case: it combines text formatting, visual rhythm, image placement, platform compatibility, and publishing handoff. In this first scenario, the skill extracts reusable WeChat article layout styles from PDF samples and applies them to new Chinese articles as original WeChat-ready HTML.

The goal is not pixel-perfect copying. It is to extract generalizable principles and generate original work with a similar reading experience.

## Core Contract

- Treat WeChat article layout as the first implementation scenario of a broader mimic framework.
- For any future medium, separate universal mimic logic from platform-specific output rules.
- Mimic through structure, rhythm, constraints, and reusable principles rather than direct copying.
- Final output is body-only by default. The generated `article.wechat.html` must not include the WeChat article title, subtitle/dek, author, account metadata, date, location, read/listen count, or native header area unless the user explicitly asks for a full archive-style page.
- When a PDF reference contains an article title, author, account name, date, or other publication chrome, treat those as source metadata for style analysis only. Do not treat them as body blocks to mimic in the final WeChat editor output.
- Preserve the source style's text formatting and reading rhythm.
- Understand the whole article's image cadence, not only isolated images.
- If the reference article uses images, diagrams, screenshots, or cover/section cards as part of its rhythm, the adapted output must include matching original image assets by default. Do not silently replace required images with text-only placeholders.
- For image-dependent styles, use image generation, preferably Image2 or the best available image generation tool, to create adapted original images based on the reference image logic and the new article content.
- Generate WeChat-compatible HTML by default.
- Always provide `preview.html` as the primary user-facing deliverable.
- Generated images should be saved as local assets and referenced from HTML.
- Default publishing handoff is local HTML plus local image folder plus upload map.
- Do not promise that pasted HTML will automatically carry local or hosted images into WeChat.

## Required Reference Loading

Before applying this skill, load the relevant reference files instead of relying only on this summary:

- Always read `references/core-principles.md` for body-only output, text formatting, image rhythm, WeChat compatibility, and self-check rules.
- Read `references/image-style-generation.md` whenever the source or target article involves images, diagrams, screenshots, generated illustrations, cover cards, section cards, or image captions.
- Read `references/wechat-rendering-rules.md` before finalizing HTML intended for WeChat paste/edit workflows.

These reference files contain operational constraints. Do not treat them as optional background reading.

## Workflow

### 1. Style Extraction From PDFs

When the user provides one or more PDF samples:

1. Create a style folder under `wechat-style-runs/风格/`, using `style-id_中文风格名/`.
2. Render PDF pages and collect rough page/text metrics.
3. Inspect the rendered pages visually. For long PDFs, sample first page, middle page, and pages containing headings, quotes, cards, or images.
4. Separate publication chrome from body content. Article titles, author lines, account metadata, dates, and platform controls may appear in the PDF but should be recorded as metadata, not body components.
5. Name the extracted style based on visual elements and content state, not only the source account name.
6. Write `style-profile.json` with measurements, component rules, rhythm rules, image cadence, naming fields, and confidence notes.
7. Write `style-brief.md` as a human-readable summary.
8. If the source PDF contains recurring illustrations, diagrams, screenshots, or image captions, add image style rules.

Every extracted style must include:

- `style_display_name`
- `style_id`
- `source_label`

### 2. Apply Style To A New Article

When the user provides a new article and a saved style template:

1. Read the target `style-profile.json`.
2. Create an output folder under `wechat-style-runs/输出/`, using `具体日期_文章核心内容_风格名/`.
3. Segment the article globally: intro, sections, concepts, paragraphs, quotes, lists, image needs, captions, and closing.
4. Treat the WeChat article title, subtitle/dek, author, account name, date, and metadata as editor/page chrome, not body content. Exclude them from `article.wechat.html` unless explicitly requested.
5. Apply both structural rhythm and visual styling.
6. Mirror the template's global image cadence. If the source uses one concept image per major section, prepare one image for each major section.
7. If images are required, generate adapted original images before finalizing the HTML. Use Image2 or the best available image generation tool to mimic the reference image's role, composition, palette, typography density, and content logic without copying source-specific logos, QR codes, or proprietary art.
8. Save generated images into the output project's `assets/` folder, reference them from `article.wechat.html`, and create/update `wechat-image-upload-map.md`.
9. Generate WeChat-compatible HTML.
10. Generate `preview.html`.
11. Run a self-check for mobile readability, body-only output, image rhythm, image presence, upload map completeness, unsupported CSS, and over-decoration.

### 3. Image Generation And Integration

When the source style depends on article images, use this minimum process:

1. Extract image intent: why the original author placed the image there, what content it explains, and how it controls reading rhythm.
2. Extract image form: role, composition, aspect ratio, background, palette, typography, density, icons/diagrams/screenshots, caption treatment, and placement relative to headings and paragraphs.
3. Generate adapted original images for the new article with Image2 or the best available image generation tool. Keep in-image text short and use the new article's concepts, not the source article's wording.
4. Do not copy source logos, QR codes, account marks, watermarks, exact diagrams, or recognizable original illustrations.
5. Save the final generated images locally under `assets/` with stable semantic filenames.
6. Insert the images into `article.wechat.html` at the matching cadence positions.
7. Add captions in HTML when the source style uses captions.
8. Provide `wechat-image-upload-map.md` so the user can manually upload the local images into the WeChat editor if pasted HTML does not carry images.

Never leave a required image as a text placeholder such as "image here" or only as a generated preview outside the project folder.

### 4. Body-Only WeChat Output

For WeChat publishing, the body HTML is not the full article page. The WeChat editor already has separate fields for title, author/account, cover, summary, and metadata.

Default final output:

- Include: body paragraphs, section headings inside the article body, quotes, cards, generated images, captions, lists, dividers, and closing notes.
- Exclude: article title, subtitle/dek, author, account name, date, location, read/listen count, platform header, sharing footer, and other native WeChat chrome.

If the user supplies a title in the new article text, use it only to infer the output folder name and content theme unless they explicitly request an in-body title block.

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

- `scripts/render_preview.py`: insert body HTML into a preview shell.
- `scripts/extract_session_images.py`: decode built-in Codex Desktop image generation results from session JSONL into a project's `assets/` folder.
