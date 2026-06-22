# Image Style Generation

Use this guide when a WeChat style template includes recurring images, cover slides, diagrams, screenshots, or illustration systems.

## Workflow

### 0. Analyze Global Image Cadence

Before generating individual images, inspect the whole reference article and identify its image rhythm:

- Does every major section have an image?
- Does the image appear before or after the heading?
- Does the pattern repeat as `heading -> image -> caption -> prose`?
- Are images explanatory slides, screenshots, diagrams, photos, or cards?
- How many paragraphs usually sit between images?

Write this as an explicit rule in `style-profile.json`, for example:

```json
{
  "image_cadence": {
    "major_section_rule": "Every numbered major section should include one full-width concept slide immediately after the h2 and before the explanatory prose.",
    "caption_rule": "Every section image gets a short centered gray caption.",
    "required": true
  }
}
```

Do not treat images as optional decoration when the reference uses them as the backbone of section rhythm.

### 1. Extract Image Style

For each important source image type, record:

- Role: hero image, section divider, concept diagram, screenshot, quote card, closing QR card
- Composition: banner, card grid, flow line, left-title/right-diagram, full-width screenshot
- Visual language: paper texture, sketch, flat vector, collage, screenshot, photo
- Palette: background, accent colors, text colors, border colors
- Typography: headline size, title weight, caption treatment
- Content logic: what the image explains, not just what it looks like
- Reusable motifs: path, cards, icons, labels, frames, badges
- Assets to avoid: logos, QR codes, account marks, branded motifs, exact illustrations

Add a compact `image_style` section to `style-profile.json`.

### 2. Generate Adapted Original Images

Use the image generation tool for bitmap assets. Prompt for the target article's subject while preserving the template's general visual language.

Default prompt structure:

```text
Asset type: WeChat article <hero/section/diagram> image
Primary request: <new article subject>
Style: <template image style>
Composition: <layout and focal structure>
Text: <exact text, keep minimal>
Palette: <template palette>
Constraints: original image; no source logos; no QR codes unless user provided; no copyrighted or recognizable source art
Avoid: <known failure modes>
```

Keep in-image text short. Generated Chinese microcopy can drift, so prefer:

- one large title
- one short subtitle
- product names or short labels only

For detailed explanations, put text in HTML below the image instead of inside the image.

### 3. QA Before Integration

Reject and regenerate if:

- The topic is wrong
- Any required text is misspelled
- It includes unrelated brands, companies, tickers, logos, QR codes, watermarks, or source-specific art
- It produces dense unreadable tables
- It conflicts with the article's claim or tone

Record rejected outputs briefly in `layout-notes.md` if they reveal a prompt risk.

### 4. Save And Integrate

For project-bound images:

1. Move or copy the final generated image into the article run folder, usually `assets/`.
2. Use a stable filename such as `hero.png`, `section-01.png`, or `closing-qr.png`.
3. Replace placeholder blocks in `article.wechat.html` with `<img>` tags using local relative paths for preview.
4. Keep captions in HTML, not embedded in the image, unless the source style requires embedded captions.
5. Re-render `preview.html` and visually check mobile fit.

Never leave a referenced article image only in a model-generated default cache folder.

### 4.1. Codex Desktop Built-In Image Persistence

When using the built-in image generation tool inside Codex Desktop, the generated image may not appear as a normal file in a predictable `generated_images/` folder. In this environment, the result can still be recovered without configuring an API Key:

1. Locate the active Codex session JSONL under `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`.
2. Find records whose payload contains an image generation result, typically:
   - `payload.type == "image_generation_call"` or the related image generation end event.
   - `payload.result` containing a base64-encoded PNG.
3. Decode the base64 result into the current output project's `assets/` folder.
4. Give each decoded image a stable semantic filename, such as `hero-image2.png`, `section-01-image2.png`, or `co-create-image2.png`.
5. Update `article.wechat.html` to reference those local files.
6. Update `wechat-image-upload-map.md` so the user knows which local file corresponds to each image position.
7. Re-render `preview.html` and verify the images load from the output folder.

Use `scripts/extract_session_images.py` to automate this when possible. Keep any HTML-rendered fallback images as backups, for example `hero-html.png`, so the project preserves both the fallback and the generated bitmap version.

## Required Output Check

Before final delivery, count major sections and section images:

- Number of major `h2` sections
- Number of section images after `h2`
- Any intentionally missing image and why

If the template requires one image per major section, these counts should match.
