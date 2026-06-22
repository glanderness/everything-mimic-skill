# WeChat Rendering Rules

Use conservative HTML/CSS that survives common WeChat article editor pipelines.

Primary target: successful copy/paste into the WeChat official account editor. Browser preview quality matters, but it is secondary to whether the formatting survives the real publishing workflow.

## HTML

- Prefer semantic `section`, `p`, `h1`, `h2`, `blockquote`, `figure`, `figcaption`, `ul`, and `ol`.
- Keep wrappers shallow. Avoid deeply nested layout structures.
- Use inline styles or simple scoped styles when the target editor supports them.
- Avoid JavaScript in final article HTML.
- Avoid rich web-app containers or framework output in final article HTML. Do not ship React/Vue/Svelte-rendered app shells, hydration markup, canvas-only content, SVG-heavy layout, shadow DOM, externally loaded CSS/JS, or layout that depends on runtime scripts.
- Do not assume local `<img src="assets/...">` files will paste into WeChat. Local images must be uploaded to the WeChat editor or hosted on an allowed public/CDN URL before publishing.
- For WeChat publishing, body HTML should not include the article title or account metadata. The user enters title, author, cover, and summary in separate WeChat editor fields.

## CSS

- Design for a mobile reading width around 360-430px.
- Use percentage widths and max-widths for images.
- Keep body text around 15-16px unless the style profile says otherwise.
- Use line-height around 1.75-2.05 for Chinese long-form reading.
- Avoid fixed pixel heights for text containers.
- Avoid hover-only interactions.
- Avoid animations as essential content.
- Use web-safe/system font stacks unless the user controls the rendering environment.
- Treat browser preview fidelity and WeChat paste fidelity as different targets. When the user plans to paste into the WeChat editor, prefer a conservative "paste-safe" variant even if it looks less refined in a browser.
- Avoid `display:flex`, `gap`, CSS grid, absolute positioning, pseudo-elements, CSS triangles, `clip-path`, transforms, negative margins, and decorative zero-size elements in the final copyable article body. These often get stripped or reflowed by WeChat-like editors.
- Avoid browser-only visual systems such as sticky sections, scroll effects, hover states, media queries that carry essential layout meaning, CSS variables required for rendering, complex selectors, external fonts, background images carrying essential text, and decorative effects that disappear when copied.
- Prefer plain `p` and `section` blocks with inline `background`, `color`, `padding`, `margin`, `border`, `font-size`, `font-weight`, and `line-height`.
- Keep compound headings atomic. Do not build one visible heading from several separately styled inline/flex pieces if line breaks would make it confusing after paste.
- Keep label chips on separate lines when metadata is optional. Inline label groups are vulnerable to awkward wrapping in narrow editor canvases.
- Prefer solid heading bars or simple left borders over CSS triangle arrows. If an arrow/marker is essential, make it part of an image asset rather than CSS.
- Use left-aligned closing/CTA text unless the style profile strongly requires centered text; centered multi-line Chinese text can break awkwardly after paste.

## Copy/Paste Compatibility

Before final delivery, mentally test every styled block with this question: if WeChat removes advanced CSS and recomputes line breaks, will the reader still see the intended structure?

Prefer these copy-safe patterns:

- paragraph blocks with inline font, color, margin, and line-height
- simple blue/colored heading bars built from one `p` or `section`
- simple borders for dividers and emphasis
- images as real `<img>` assets, not CSS backgrounds when the image carries meaning
- short inline emphasis spans inside normal paragraphs

Avoid these copy-risky patterns:

- multi-column, flex, grid, or absolute-positioned layouts
- CSS triangles, pseudo-elements, generated content, or decorative zero-size elements
- split headings assembled from multiple inline blocks
- script-rendered components, canvas-only graphics, or interactive widgets
- external stylesheet dependencies and class-only styling without inline fallback
- text embedded only in background images when the text needs to remain editable

## Components

- Do not overuse emphasis blocks. They should support scanning, not turn every paragraph into a card.
- Keep highlight components short.
- Captions should be visually subordinate to images.
- Use dividers sparingly between major sections.

## Final QA

Before delivering:

- Check that text is readable on mobile.
- Check that headings are visually distinct from body text.
- Check that images and captions do not overflow.
- Check that color contrast is sufficient.
- Check that the article still feels like one coherent style after adaptation.
- Check that the final body does not depend on rich-page-only rendering and should still hold together after copy/paste into WeChat.
- Provide an image upload map when the article contains local image assets: image order, local file path, insertion position, and caption.
