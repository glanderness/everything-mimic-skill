# Style Extraction Guide

Use this guide when converting PDF samples into a reusable WeChat article style profile.

## Inputs To Inspect

- Rendered page screenshots from `scripts/inspect_pdf.py`
- Extracted text blocks and bounding boxes when available
- User-provided context about the account, topic, or intended adaptation

## What To Extract

### Style Naming

Every extracted style must receive a reusable name. Do not name a style only after the source account or article title. The name should help the user remember when to call this style again.

Create three fields:

- `style_display_name`: short Chinese name, usually 4-10 characters, based on the visible style and content state.
- `style_id`: stable lowercase identifier for folders, templates, and future references. Use ASCII letters, numbers, and hyphens only.
- `source_label`: source account/article label for internal traceability. This is not reader-facing content and should not be printed in final article HTML by default.

Good style names combine 2-3 of these signals:

- dominant visual device: blue labels, serif headings, beige cards, hand-drawn slides, numbered cards
- content posture: interview, explainer, founder profile, product walkthrough, course notes, investment memo
- reading rhythm: sparse editorial, dense notes, image-led, Q&A, chaptered analysis
- emotional temperature: calm, sharp, warm, academic, energetic

Examples:

```json
{
  "style_display_name": "蓝标访谈体",
  "style_id": "blue-label-interview",
  "source_label": "Yiwei / SurferGarage sample"
}
```

```json
{
  "style_display_name": "暖米课程图解体",
  "style_id": "warm-course-diagram",
  "source_label": "WorkBuddy training share sample"
}
```

Naming rule: if two samples come from the same account but have different article states, create different style names. If two accounts share a similar layout grammar, name the reusable grammar rather than the account.

### Page And Layout

- Apparent content width
- Outer margins and inner padding
- Section spacing
- Paragraph spacing
- Image width and caption placement
- Whether the page feels dense, airy, editorial, card-based, newsletter-like, or magazine-like

Important: separate WeChat editor chrome from article body. The printed PDF may show article title, author/account, original badge, date, location, and read/listen count. Extract their style only if the user asks for archive-style preview. For publishable body HTML, treat them as non-body metadata and exclude them from `article.wechat.html`.

### Typography

- Body size estimate
- Heading levels and size contrast
- Body line-height estimate
- Font family category: system sans, serif/Songti, rounded sans, handwritten/display
- Weight pattern: regular body, bold headings, highlighted phrases
- Alignment: left, centered, mixed

Do not overstate font identity unless embedded font names and visual evidence agree.

### Color

Capture:

- Body text color
- Muted text color
- Main accent color
- Secondary accent color
- Background color or texture
- Highlight block color
- Border/divider colors

Prefer approximate hex values with confidence notes. If exact color extraction is unreliable, describe hue, saturation, and contrast.

### Components

Look for recurring components:

- Opening title block
- Section heading
- Subheading
- Quote block
- Highlight sentence
- Numbered card
- Divider
- Image caption
- Callout/tip box
- Closing block
- Author note or source note

For each component, describe structure, not just appearance:

```json
{
  "component": "h2",
  "role": "section opener",
  "structure": "short heading with left accent bar and generous top spacing",
  "visual_rules": {
    "font_size": "20px",
    "font_weight": "700",
    "accent": "4px vertical bar"
  },
  "usage_rule": "Use once per major section; avoid stacking two headings without body text."
}
```

### Reading Rhythm

Extract the article's pacing:

- Average paragraph length
- Frequency of emphasis components
- How often images appear
- Whether openings are direct, lyrical, narrative, or data-led
- How sections end: summary sentence, transition, quote, or visual divider

This is often more important than CSS.

## Style Profile Shape

Use this top-level shape for `style-profile.json`:

```json
{
  "name": "style-display-name",
  "style_display_name": "style-display-name",
  "style_id": "stable-style-id",
  "source_label": "source account/article label for internal traceability",
  "source_samples": [],
  "replication_mode": "adapted",
  "confidence_summary": "",
  "layout": {},
  "typography": {},
  "colors": {},
  "components": {},
  "rhythm": {},
  "content_rules": {},
  "wechat_css_rules": {},
  "avoid": [],
  "open_questions": []
}
```

## Confidence Labels

Use:

- `high`: directly visible across multiple pages or supported by extracted metrics
- `medium`: visually likely but not mechanically confirmed
- `low`: inferred from limited evidence or impossible to confirm from PDF

Prefer useful uncertainty over false precision.
