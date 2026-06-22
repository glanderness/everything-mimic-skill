# WeChat Rendering Rules

## Conservative HTML

微信公众号编辑器会清理或改写部分 HTML/CSS。为了提高复制粘贴成功率：

- Prefer `section`, `p`, `span`, `strong`, `em`, `img`.
- Use inline CSS for important visual styles.
- Keep nesting shallow.
- Use fixed, simple spacing values.
- Keep images as real `<img>` tags.

## Avoid

- JavaScript
- canvas-only content
- complex animations
- CSS pseudo-elements
- advanced selectors
- `position: fixed`
- layout-critical `grid`
- layout-critical `flex`
- external CSS dependencies
- web fonts required for meaning

## Image Transfer

Do not assume images will paste into WeChat from a local HTML file. Default delivery:

1. User pastes formatted text/body into WeChat editor.
2. User uploads images from the output project's `assets/` folder.
3. User follows `wechat-image-upload-map.md` for placement.

