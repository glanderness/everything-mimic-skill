# Style Replication Policy

This skill extracts transferable style principles and generates original WeChat layouts. It should not produce deceptive copies of a public account's distinctive brand identity.

## Allowed

- General layout principles: spacing, hierarchy, card density, heading rhythm
- General component categories: quotes, callouts, dividers, numbered sections
- Approximate mood: clean, editorial, academic, playful, restrained, premium
- Broad color direction: low-saturation blue, warm accent, black-and-white editorial
- User-owned assets or assets with clear permission

## Avoid

- Logos, account marks, QR-code blocks, watermarks, and proprietary brand assets
- Exact recurring decorative motifs that make the source account recognizable
- Exact copied illustrations, textures, image frames, or title ornaments
- Unique named columns, slogan blocks, sign-off blocks, or branded labels
- Outputs that could mislead readers into thinking the article came from the source account

## Replication Modes

Use one of these modes in `style-profile.json`.

### faithful-study

For private analysis only. Preserve measurements and component observations as closely as the PDF allows, but mark any identifiable source elements as `do_not_publish`.

### adapted

Default for publishable work. Preserve reading rhythm and component logic while changing enough visual details to make the result original.

### originalized

Keep only the underlying content strategy and reading experience. Rebuild colors, component shapes, and decorative language from scratch.

## Practical Rule

If a reader familiar with the source account would likely say "this is that account's template," make a stronger adaptation before publishing.

