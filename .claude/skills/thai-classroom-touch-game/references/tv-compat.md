# Smart-TV compatibility and testing

Classroom smart TVs and interactive boards often run old Chromium or WebKit
browsers that never update. Write for them and test the degraded paths.

## 1. JavaScript: ES5 only

Allowed: `var`, `function`, ES5 array methods (`forEach`, `map`, `filter`,
`indexOf`), `JSON`, `Object.keys`, `Object.defineProperty`,
`requestAnimationFrame`, `classList` without the second `toggle` argument
(the template uses its own `addCls/rmCls/setCls` helpers anyway).

Avoid, with the replacement to use:

| Avoid | Use |
|---|---|
| arrow functions, template literals, `let`/`const`, `class`, destructuring, default params, spread | `function`, string concatenation, `var` |
| `?.`, `??` | explicit checks: `a && a.b`, `x != null ? x : y` |
| `Array.from`, `.includes`, `.find`, `Object.assign` | loops, `indexOf` |
| `NodeList.forEach` | `for` loop over `querySelectorAll` |
| `element.remove()`, `.closest()` | `parentNode.removeChild`, walk up manually |
| `async`/`await`, unguarded `Promise` | callbacks and `setTimeout`. Call `.then` only after checking it exists (`document.fonts.ready`, fullscreen, `audio.resume`) and catch rejections with `.then(null, fn)` |

Check with `scripts/check_static.py`, which parses the script as strict
ES5 when Node plus acorn is available.

## 2. CSS

Avoid: flex `gap`, `inset`, the `aspect-ratio` property, `:is()`, `:where()`,
`:has()`, `light-dark()`, `min()`/`max()`/`clamp()` in values, CSS nesting,
`@container`, and `color-mix()`.

Fine: flexbox with margins, `calc()` with custom properties (Chrome 49+),
`vh`/`vw`, transforms, `@keyframes`, `repeating-linear-gradient`,
`radial-gradient` with length stops, and media queries on `aspect-ratio` and
`orientation`.

Put `var()` only in normal declarations. Keyframes use `%` or `em` instead
of u units, because custom properties inside `@keyframes` are unreliable on
old engines.

## 3. Input

- `if (window.PointerEvent)` use pointer events, else touch events
  (`passive:false` when supported, detected with the `Object.defineProperty`
  trick) plus mouse events. Call `preventDefault` on touchstart so no
  emulated mouse events follow.
- Set `touch-action:none` on body and on pieces. Prevent `touchmove`,
  `gesturestart`, `contextmenu`, `dragstart` and `selectstart` globally.
- Use `user-scalable=no` in the viewport meta (many TVs ignore it, but it
  costs nothing).

## 4. Storage, fullscreen, audio

- **Storage**: wrap *every* access in try/catch, including reading
  `window.localStorage` itself, which throws in sandboxed frames. Validate
  the loaded object's shape and version, fall back to fresh stats, and show
  the teacher whether saving works.
- **Fullscreen**: `requestFullscreen || webkitRequestFullscreen ||
  webkitRequestFullScreen || msRequestFullscreen`, called inside the tap.
  Ignore promise rejections, hide the button when none exists, and update
  its label on `fullscreenchange`/`webkitfullscreenchange`.
- **Audio**: `window.AudioContext || window.webkitAudioContext`. Create or
  resume it in the first user gesture, and never before (Chrome logs a
  warning). Wrap every play in try/catch. No Web Audio means silence and
  nothing else.

## 5. The 16:9 stage on real screens

| Screen | What happens |
|---|---|
| TV in fullscreen (1920×1080, 3840×2160) | the stage fills exactly |
| TV browser with toolbar (e.g. 1920×950), wider than 16:9 | the stage fills the height, and the awning and background continue to the sides |
| laptop 16:10 (1440×900), 4:3 (1024×768) | the stage fills the width at the top, with a wooden counter below |
| portrait panel or phone | the stage sits at the top, with the counter and the "หมุนจอเป็นแนวนอน" hint below |

## 6. Test matrix

Run all of these before delivering; `scripts/check_layout.js` covers most of them automatically:

1. 1920×1080 with mouse taps through the whole game, then again with drags.
2. Touch input (Playwright `hasTouch`, CDP `Input.dispatchTouchEvent` for
   drags).
3. Pointer Events removed (`window.PointerEvent = undefined`), using touch.
4. `localStorage` throwing (an init script that redefines the getter to
   throw).
5. `prefers-reduced-motion: reduce`.
6. Web Audio missing (`window.AudioContext = undefined`).
7. Google Fonts blocked (fallback font).
8. Viewports 1366×768, 1440×900, 1024×768, 3840×2160, 1920×950 and
   820×1000.
9. A static check, and an ES5 parse.

For every run, check: no console errors (a blocked font request is
expected), controls at or below 40%, minimum sizes met, and screenshots that
look right. Wait about 1 s after a screen change before measuring. Wait for
`#nextWrap.show` instead of using fixed sleeps.

Playwright tips: Chromium may be pre-installed, so try `require('playwright')`
before installing anything. Use `deviceScaleFactor: 1` for checks. To test
with the real font offline, download the Mali CSS and woff2 files once and
serve them with `page.route` (the example play-through accepts `--fonts
<dir>`).

## 7. Hosted preview pages (for example Claude Artifacts)

Hosts that wrap your HTML in their own page skeleton need the game's
`<!DOCTYPE>`, `<html>`, `<head>` and `<body>` stripped (keep the `<title>`,
font `<link>`s, `<style>` and body content). Drop the viewport meta, because
the host adds its own. Google Fonts and
inline scripts are allowed. Fullscreen may be refused inside the preview
frame. That is fine, since the button handles the rejection.
