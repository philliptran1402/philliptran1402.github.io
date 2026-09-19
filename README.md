# philliptran1402.github.io

Personal landing page — [philliptran1402.github.io](https://philliptran1402.github.io/)

A single static HTML file. No framework, no build step, no package manager, no lockfile.
What is in the repository is exactly what is served.

## Why it is built this way

A landing page is read-mostly, changes a few times a year, and has to be online when
someone follows a link from a CV. Those constraints argue against a toolchain, not for one.

| Decision | Rationale |
|---|---|
| Single HTML file, no framework | Nothing to build means nothing to break. A broken build on a personal site fails silently and is usually discovered months later, by which point the link has already been shared. |
| CSS inlined in `<head>` | One round trip for first paint. No flash of unstyled content, no separate stylesheet to cache-bust. At this size, splitting it out would cost more than it saves. |
| 11 lines of vanilla JS | Scroll reveal via `IntersectionObserver`, with a fallback that shows everything if the API is missing. The page is fully readable with JavaScript disabled. |
| Two external asset dependencies | Google Fonts and an image proxy for the circular avatar. Both degrade gracefully — see *Trade-offs*. |
| No analytics | Nothing to disclose in a cookie banner, nothing to slow down first paint. GitHub's own repository traffic insights already answer the only question worth asking. |

## Footprint

Measured on the committed file, not estimated:

| Metric | Value |
|---|---|
| HTML, uncompressed | 17.8 KB |
| HTML, gzip | 5.6 KB |
| HTML, brotli | 4.7 KB |
| Blocking requests for first paint | 1 (the document) |
| JavaScript | 11 lines, no dependencies |
| Build time | none |

## Structure

```
.
├── index.html   # the entire site: markup, styles, and the reveal script
└── README.md
```

Sections inside `index.html`, in document order: header (avatar, name, role, links),
About, What I work on, Selected work, Stack, and the contact footer.

## Local development

No dependencies to install. Either open the file directly:

```bash
open index.html
```

or serve it over HTTP, which is closer to production because it exercises relative
paths and caching headers:

```bash
python3 -m http.server 4173   # then visit http://127.0.0.1:4173
```

## Deployment

Pushing to `main` publishes the site. GitHub Pages is configured to deploy from the
branch root, so there is no workflow file and no deploy step to maintain.

```bash
git push origin main          # live within a minute or two
```

Two constraints worth writing down, because both are easy to get wrong and neither
produces a useful error message:

- **The repository name is load-bearing.** A user site is served at the domain root
  only when the repository is named exactly `<username>.github.io`. Any other name is
  published as a project site under `/<repository>/` instead.
- **Pages must be pointed at branch `main`, folder `/ (root)`** under *Settings → Pages*.
  A repository with Pages enabled but a misconfigured source returns 404 at the public
  URL while still reporting the feature as enabled.

## Editing

| To change | Edit |
|---|---|
| Name, role, location, header links | the `<header>` block |
| Bio | the first `<section>` |
| Domains | the `div.card` elements |
| Projects | the `div.proj` elements |
| Stack | the `div.stack-row` elements |
| Colours, spacing, radius | the `:root` custom properties in `<style>` |

The avatar is pulled live from the GitHub account, so changing the picture there
updates this page with no commit.

## Accessibility and progressive enhancement

- Semantic landmarks (`header`, `section`, `footer`), one `h1`, descriptive `alt` text.
- `prefers-reduced-motion: reduce` disables both the reveal transitions and smooth scrolling.
- Content is visible without JavaScript; the reveal script only adds motion.
- Colour pairs on the dark background were chosen to stay legible at body size rather
  than to maximise contrast ratio on the accent colour alone.

## Accepted trade-offs

Stated explicitly, because a page this small should not pretend to be a platform:

- **No CMS, no content collections.** Adding a project means editing HTML. That is the
  right cost at roughly a handful of edits per year; it would be the wrong cost at fifty.
- **Bilingual content is not supported.** The page is English-only by choice. Adding a
  second locale would justify a static site generator, and that decision has not been made.
- **The circular avatar depends on a third-party image proxy** (`wsrv.nl`), because GitHub
  strips `style` attributes from rendered Markdown and CSS masking is therefore unavailable
  in the profile README that shares this asset. If that proxy is unavailable the image fails
  to load rather than degrading to a square. Committing a pre-cropped PNG removes the
  dependency and is the correct fix if uptime ever matters more than convenience.
- **Google Fonts is a render-blocking third party.** The system font stack is declared first
  in every rule, so text is readable before the webfont arrives — but the request is still on
  the critical path. Self-hosting the two families would remove it.
