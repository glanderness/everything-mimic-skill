# Image Style Generation

Use this guide when a WeChat style template includes recurring images, cover slides, diagrams, screenshots, or illustration systems.

## 1. Analyze Global Image Cadence

Before generating individual images, inspect the whole reference article and identify its image rhythm:

- Does every major section have an image?
- Does the image appear before or after the heading?
- Does the pattern repeat as `heading -> image -> caption -> prose`?
- Are images explanatory slides, screenshots, diagrams, photos, or cards?
- How many paragraphs usually sit between images?

Do not treat images as optional decoration when the reference uses them as the backbone of section rhythm.

## 2. Extract Image Style

For each important source image type, record:

- role
- composition
- visual language
- palette
- typography
- content logic
- reusable motifs
- assets to avoid

## 3. Generate Adapted Original Images

Use image generation for bitmap assets when needed. Prompt for the target article's subject while preserving the template's general visual language.

Keep in-image text short. Generated Chinese microcopy can drift, so prefer:

- one large title
- one short subtitle
- product names or short labels only

For detailed explanations, put text in HTML below the image instead of inside the image.

## 4. Save And Integrate

For project-bound images:

1. Move or copy the final generated image into the article run folder, usually `assets/`.
2. Use stable filenames such as `hero.png`, `section-01.png`, or `closing-qr.png`.
3. Replace placeholder blocks in `article.wechat.html` with `<img>` tags using local relative paths for preview.
4. Keep captions in HTML unless the source style requires embedded captions.
5. Re-render `preview.html`.

## 5. Codex Desktop Built-In Image Persistence

When using the built-in image generation tool inside Codex Desktop, the generated image may not appear as a normal file in a predictable `generated_images/` folder. It can still be recovered without configuring an API Key:

1. Locate the active Codex session JSONL under `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`.
2. Find records where `payload.type` contains `image_generation` and `payload.result` contains a base64 PNG.
3. Decode the base64 result into the current output project's `assets/` folder.
4. Give each decoded image a stable semantic filename.
5. Update `article.wechat.html`, `wechat-image-upload-map.md`, and `preview.html`.

Use `scripts/extract_session_images.py` to automate this.

