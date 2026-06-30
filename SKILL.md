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
- Preserve the source style's component grammar, not only its color palette or general mood. Component grammar means the exact role and shape of headings, quote blocks, agenda lists, tables, callouts, dividers, captions, image blocks, code pills, and emphasis marks.
- Do not substitute a source component with a prettier or more familiar component just because it conveys similar information. A heading-plus-left-border-quote must not become a rounded callout card; a divider agenda list must not become a boxed list; a thin-line comparison table must not become a product card stack unless the reference uses those forms.
- Before generating HTML, identify each recurring reference component and name it. During generation, map every target article block to one of those components or explicitly mark it as a necessary adaptation.
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
- Read `references/style-extraction.md` when turning PDFs or reference samples into reusable style profiles.
- Read `references/style-replication-policy.md` whenever the task involves imitating, mimicking, cloning, copying, or closely matching a public reference style.
- Read `references/image-style-generation.md` whenever the source or target article involves images, diagrams, screenshots, generated illustrations, cover cards, section cards, or image captions.
- Read `references/wechat-rendering-rules.md` before finalizing HTML intended for WeChat paste/edit workflows.
- Read `references/wechat-image-transfer.md` when the user asks whether images can paste into WeChat, transfer with HTML, use hosted URLs, or sync through WeChat APIs.

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

### 1A. Style Extraction From A Single WeChat URL

When the user provides a single WeChat article URL instead of a PDF, treat the link as a valid style-extraction input. The default behavior is not to ask the user to print or upload a PDF. First use `scripts/wechat_url_to_pdf.mjs` as the lightweight capture path, then immediately continue into the normal PDF style-extraction workflow.

Flow:

1. Create an input capture folder under `wechat-style-runs/输入/`, using `具体日期_文章核心内容/` after the title is known. If the title is not known before capture, use a temporary URL slug folder and rename it after reading `capture-report.json`.
2. Run Chrome-based capture with the URL and output folder.
3. The script opens the rendered page, patches common WeChat lazy-loaded image attributes, scrolls through the whole article, waits for images, saves HTML and screenshot, then prints `source.pdf`.
4. Read `capture-report.json` and report the captured title, account name, publish time, PDF page count, image count, and failed image count.
5. If `failedImageCount` is nonzero, treat the capture as incomplete and inspect `fullpage.png`/`source.html` before extracting style unless the user explicitly accepts missing images.
6. Use the generated `source.pdf` as the input to the normal PDF style-extraction workflow.
7. Produce the same style extraction deliverables as a PDF workflow: `style-profile.json`, `style-brief.md`, optional rendered `pages/`, `inspection.json`, and `self-check.md`.
8. In the final response, give the user the extracted style name, concise style summary, confidence notes, and the style folder path.

This mode is intentionally single-article only for the MVP. Do not silently batch multiple links.

### 2. Apply Style To A New Article

When the user provides a new article and a saved style template:

1. Read the target `style-profile.json`.
2. Create an output folder under `wechat-style-runs/输出/`, using `具体日期_文章核心内容_风格名/`.
3. Segment the article globally: intro, sections, concepts, paragraphs, quotes, lists, image needs, captions, and closing.
4. Treat the WeChat article title, subtitle/dek, author, account name, date, and metadata as editor/page chrome, not body content. Exclude them from `article.wechat.html` unless explicitly requested.
5. Build a component inventory from the reference before styling the target article: heading types, quote/callout types, list/table types, emphasis patterns, code pills, image/caption blocks, dividers, and closing blocks.
6. Apply structural rhythm, visual styling, and component grammar together. If the source uses a red module heading plus a left-border quote, reproduce that component relationship; do not collapse it into a generic card.
7. Mirror the template's global image cadence. If the source uses one concept image per major section, prepare one image for each major section.
8. If images are required, generate adapted original images before finalizing the HTML. Use Image2 or the best available image generation tool to mimic the reference image's role, composition, palette, typography density, and content logic without copying source-specific logos, QR codes, or proprietary art.
9. Save generated images into the output project's `assets/` folder, reference them from `article.wechat.html`, and create/update `wechat-image-upload-map.md`.
10. Generate WeChat-compatible HTML.
11. Generate `preview.html`.
12. Run a self-check for mobile readability, body-only output, component fidelity, image rhythm, image presence, upload map completeness, unsupported CSS, and over-decoration.
13. Run a reference review: compare the generated output against the source style again, identify mismatches, revise the HTML/assets when feasible, and write `reference-review.md`.

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

### 5. Component Fidelity Gate

Before final delivery, run a component-level comparison against the reference. This is a hard gate, not an optional polish pass.

Required checks:

- Heading semantics: If the reference uses short module names, technical object names, or concept labels as headings, do not rewrite them into generic numbered essay headings unless the reference itself does that.
- Heading form: Match whether headings are standalone red serif titles, inline bold labels, centered blocks, section cards, or numbered headings. Do not preserve only the color while changing the component type.
- Quote/callout form: Distinguish left-border quote blocks, shaded callouts, bordered cards, and full-width background bands. Never replace one with another without a reason recorded in `layout-notes.md`.
- List form: Distinguish divider agenda lists, bullet lists, arrow lists, boxed lists, and checklist cards. If the reference uses thin horizontal dividers between list rows, reproduce dividers instead of wrapping the list in a large rounded box.
- Table form: Distinguish dense thin-line tables from card stacks. If the reference uses grid lines, compact rows, and high information density, do not turn the table into large low-density cards.
- Emphasis form: Preserve how red text, bold text, underline, code pills, brackets, and inline labels are used. Do not turn every important sentence into the same callout style.
- Container restraint: Do not introduce rounded cards, shadows, nested cards, thick borders, or product-UI styling unless the reference repeatedly uses those exact container types.
- Adaptation discipline: New content may change wording and section names, but the underlying component grammar must remain visibly traceable to the reference.

If a generated component fails this comparison, revise the HTML before delivering. The goal is at least 90% recognizable component-level similarity, not merely a similar palette.

### 6. Post-Generation Reference Review Gate

After generating `article.wechat.html`, `preview.html`, and assets, compare the finished output against the reference style before final delivery.

Required review steps:

- Re-open the reference style profile and its sampled pages/screenshots.
- Inspect the generated preview visually, preferably at a mobile-width viewport.
- Compare component grammar: headings, tables, quote blocks, image placement, captions, paragraph rhythm, and closing structure.
- Compare visual weight: whether body text, images, tables, and callouts compete in the same way as the reference.
- Compare image fidelity: whether generated images match the reference role, aspect ratio, density, palette, and content logic.
- Compare platform constraints: whether the final HTML still uses WeChat-compatible simple tags and inline styles.
- If a feasible mismatch is found, revise the output before delivery.
- Write `reference-review.md` in the output folder with findings, changes made, remaining gaps, and next recommended improvement.

This review is mandatory even when the initial self-check passes. Self-check verifies internal constraints; reference review verifies similarity to the actual target style.

## Output Standards

Default root folder structure:

- `wechat-style-runs/输入/`: captured source URLs converted to PDF/HTML/screenshots for later extraction.
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
- `reference-review.md`

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

- `scripts/inspect_pdf.py`: render PDF pages to PNG and write a rough JSON inspection report for style extraction.
- `scripts/wechat_url_to_pdf.mjs`: capture one WeChat article URL as `source.pdf`, `source.html`, `fullpage.png`, and `capture-report.json`.
- `scripts/render_preview.py`: insert body HTML into a preview shell.
- `scripts/save_style_template.py`: copy approved style files into a reusable template folder.
- `scripts/extract_session_images.py`: decode built-in Codex Desktop image generation results from session JSONL into a project's `assets/` folder.
- `scripts/wechat_uploadimg.py`: upload local article images through WeChat `media/uploadimg` and rewrite HTML image URLs.
- `scripts/wechat_create_draft.py`: create a WeChat Official Account draft from prepared HTML and cover image.
- `scripts/wechat_publish.py`: dry-run, submit, or poll WeChat publish tasks. It must not be used for real publishing unless the user explicitly approves the exact publish action.
