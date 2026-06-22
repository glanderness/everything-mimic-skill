# WeChat Image Transfer

Use this guide when the user wants images to move into the WeChat official account editor together with the article.

## Core Constraint

Local HTML image paths such as `assets/hero.png` or `file:///.../hero.png` are only valid on the user's computer. WeChat's editor does not upload those local files just because the rendered HTML was copied.

If images must appear after paste or sync, they need to be one of:

1. Uploaded manually through the WeChat editor.
2. Hosted at acceptable remote URLs before paste.
3. Synchronized by a third-party editor that uploads/transfers images.
4. Uploaded through WeChat Official Account APIs and referenced by returned WeChat image URLs.

## Default Handoff

### Local HTML Plus Image Folder

This is the default stable handoff.

Produce:

- `preview.html`
- `article.wechat.html`
- local `assets/` folder containing all images
- `wechat-image-upload-map.md`

Tell the user:

1. Open `preview.html`.
2. Copy the rendered article text/content into the WeChat editor.
3. Upload the provided images from `assets/` into the positions listed in `wechat-image-upload-map.md`.
4. Send a phone preview before publishing.

This avoids brittle assumptions about WeChat accepting local paths, external hotlinks, or base64 images.

## Experimental / Advanced Modes

### Mode B: Hosted Image URLs

Experimental, not default.

Host local images on a stable HTTPS asset host, replace `src="assets/..."` with those HTTPS URLs, and then test paste behavior.

Caveat: external image URLs may still fail, be filtered, or break later depending on WeChat/editor behavior and hotlink protections. Prefer WeChat-hosted URLs for publishable drafts.

Use this mode only when the user explicitly wants to test whether WeChat accepts hosted images.

Recommended workflow:

1. Generate all article images locally.
2. Upload them to a stable HTTPS host the user controls or accepts.
3. Create `image-url-map.json` mapping local asset paths to HTTPS URLs.
4. Generate `wechat-hosted.html` by replacing local `assets/...` paths with HTTPS URLs.
5. Ask the user to paste `wechat-hosted.html` into the WeChat editor and report whether images transfer.
6. If images do not transfer, fall back to Mode A or upgrade to Mode D.

### Mode C: Third-Party Editor Sync

Use a platform such as 135, Xiumi, or similar with WeChat account authorization/sync. These services usually save article images to their cloud and/or sync the draft into WeChat after authorization.

This is often the best no-code approach when the user accepts using a third-party editor.

### Mode D: WeChat API Draft Sync

Most automated and clean, but should not be the default because it requires WeChat Official Account developer credentials.

Flow:

1. Obtain and cache `access_token`.
2. Upload each in-article image with the WeChat "upload image for article content" endpoint.
3. Replace every HTML `img src` with the returned WeChat URL.
4. Upload or select the cover image material.
5. Create a WeChat draft with the processed HTML content.
6. User opens the draft in WeChat backend, previews, edits, and publishes.

Requirements:

- Official account AppID/AppSecret or a connected service with authorization.
- Correct IP whitelist for token/API calls.
- Images adjusted to WeChat endpoint limits. For `media/uploadimg`, keep images JPG/PNG and under 1MB unless the current official docs say otherwise.
- Secure secret storage. Never hardcode credentials in article files.

## Recommended Skill Behavior

Default order:

1. Use local HTML plus image folder with upload map.
2. If the user explicitly asks to reduce manual upload work, test hosted HTTPS image URLs.
3. If hosted URLs fail and the user wants deeper automation, consider third-party editor sync or WeChat API draft sync.

When credentials are unavailable, do not claim one-click WeChat image transfer. Offer:

- local image folder plus upload map as the stable baseline,
- a hosted-image URL experiment,
- a third-party sync workflow, or
- an API-sync implementation plan only if needed.

When credentials are available, generate:

- `wechat-ready.html` with WeChat-hosted image URLs
- `draft-sync-report.md`
- optional script output mapping local files to returned WeChat URLs
