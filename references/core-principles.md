# Core Principles

This document captures the product direction for the WeChat style layout skill.

## 1. Text Formatting And Layout Are The Baseline

The first responsibility is to preserve and reproduce the article's text formatting and layout language.

This includes:

- body typography
- line height
- paragraph spacing
- section spacing
- heading style
- divider usage
- quote/example/callout blocks
- caption treatment
- background and article surface
- density and reading rhythm

This is the basic foundation and must not be lost while adding images or automation. If the text layout does not match the reference style, the skill has failed even if the images look good.

## 2. Understand The Whole Image-Text Relationship

Images are not isolated decorations. The skill must analyze how the author uses images across the whole article.

For every reference article, identify:

- where images appear
- whether each major section has an image
- whether images appear before or after headings
- how many paragraphs usually appear between images
- image-to-text ratio across the article
- whether images explain concepts, summarize workflows, provide screenshots, decorate transitions, or serve as proof
- how captions are written and positioned
- how image style interacts with the article's argument

For the WorkBuddy-style reference, the important pattern is:

`major section heading -> full-width concept image -> centered gray caption -> explanatory prose`

That image cadence is part of the style. It should be treated as a global rhythm rule, not an optional visual component.

## 3. Prioritize The Large Framework Before Small Details

Some details are temporarily constrained by platform behavior. For example, WeChat does not reliably carry local or hosted images when pasting HTML.

The final article is not just a browser page. It must survive the user's real publishing path: preview HTML -> copy rendered content -> paste into the WeChat official account editor -> mobile preview -> publish. A layout that only works in a rich browser page but breaks after copying into WeChat is not a successful output.

For now, use the stable handoff:

- generate local HTML
- generate local images
- embed images for local preview
- provide an image folder
- provide an upload map for WeChat publishing

Do not let unresolved image-transfer details block the core system. First make sure the whole article structure, text rhythm, and image cadence are correct. Then improve smaller operational details later.

When there is a tradeoff between highly expressive browser-only layout and reliable WeChat copy/paste formatting, choose the reliable WeChat version by default. Avoid rich-page rendering techniques that WeChat editors commonly strip or reflow, including advanced layout systems, generated decorations, script-driven rendering, and fragile multi-piece visual components.

## 4. Build A Self-Check System

After each major step, run a simple self-check against the reference style.

Required self-checks:

- **Text layout check**: typography, line height, paragraph spacing, headings, dividers, callouts.
- **Image cadence check**: number of major sections versus number of section images; verify images appear in the right positions.
- **Image-content check**: each image should explain or reinforce the nearby section, not just decorate it.
- **Body boundary check**: final WeChat body HTML should not include title, author, date, account metadata, or native WeChat chrome.
- **Reader-facing content check**: final WeChat body HTML should only include information that belongs to the new article. Do not expose internal template metadata, reference account names, style source labels, debugging notes, or "style by ..." lines unless the user explicitly asks to publish them.
- **Copy/paste compatibility check**: final WeChat body HTML should avoid rich-page-only layout techniques and should preserve the main visual hierarchy when pasted into the official account editor.
- **Publishing handoff check**: if local images are used, provide `assets/` and `wechat-image-upload-map.md`.
- **Style consistency check**: the final output should feel like the same visual system as the reference, even when adapted.

For image-heavy templates, the self-check must include a simple count:

```text
major_sections: N
section_images: N
hero_images: 0 or 1
missing_images: none / listed with reason
```

If the image count does not match the template's global rhythm, the output is incomplete.
