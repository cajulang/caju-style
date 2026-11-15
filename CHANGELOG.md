# Changelog

All notable changes to caju style. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-11-15

### Security
- Arbitrary values were written into the stylesheet verbatim, so a utility such as
  `w-[1px;}body{display:none}]`, `[color:red;}*{background:url(...)}]` or
  `before:content-['</style><script>...']` could end its rule (or an inline `<style>`) and add CSS
  or HTML of its own (audit finding M-14). A utility with `;`, `{`, `}`, `<`, a control character,
  `>` in its value, a backslash other than `\_`, a comment, or unbalanced quotes, brackets or
  parentheses is now refused: it is left out of the stylesheet and `css.unknown` reports it as
  `"def: utility (refused: why)"`. `css.unsafe(utility)` tells why.
- Class names escape `<` and control characters as code points (`\3c `).
- `css.for_style_tag(text)`: a stylesheet made safe to inline in a `<style>` element.
- The README documents that `style.raw`, base selectors, theme values and custom variants are
  trusted (written as they are).

### Added
- Dark mode by media query: `style.dark_mode("media")` makes `dark:` apply under
  `@media (prefers-color-scheme: dark)`; `style.dark_mode("selector")` (the default) keeps
  `&:is(.dark *)`. `style.custom_variant` accepts an at-rule (`"@media (height >= 50rem)"`).
- Grid placement: `col-start-*`, `col-end-*`, `row-start-*`, `row-end-*` (numbers, `auto`,
  negatives, arbitrary values), `col-*`, `row-*`, `col-auto`, `row-auto`, `row-span-full`,
  `col-span-[...]`, `grid-rows-none`, `grid-cols-subgrid`, `grid-rows-subgrid`, `grid-flow-dense`,
  `grid-flow-row-dense`, `grid-flow-col-dense`, `auto-cols-auto/min/max`, `auto-rows-auto/max`.
- `space-x-*`, `space-y-*`, `space-x-reverse`, `space-y-reverse`, and `divide-x`, `divide-y` (with
  widths, colors, styles and `-reverse`), on `:where(& > :not(:last-child))` as in Tailwind 4.
- `flex-row-reverse`, `flex-col-reverse`, `flex-wrap-reverse`, `flex-initial`.
- `place-content-*`, `place-self-*`, `justify-items-*`, `justify-self-*`; `self-*`, `items-*`,
  `justify-*` gain `normal` / `baseline` where Tailwind has them.
- `start-*`, `end-*`, `inset-s-*`, `inset-e-*`; negative and arbitrary `order-*` and `z-*`.
- `line-clamp-none`, `aspect-auto`, `aspect-<fraction>`, `aspect-video` with its theme value,
  `object-<position>`, `text-ellipsis`, `text-clip`, `visible`, `invisible`, `collapse`,
  `isolate`, `isolation-auto`, `box-border`, `box-content`.

### Fixed
- An unknown keyword (`self-zz`, `items-zz`, `overflow-zz`, `place-items-zz`, `whitespace-zz`,
  `inset-x-zz`) wrote an empty or bogus declaration; it is now reported by `css.unknown`.
- `-z-10` wrote `z-index: 10`.
- `aspect-video` referred to `--aspect-video` without defining it.
- `will-change-scroll` is `scroll-position`, as in Tailwind.

## [0.1.0] - 2026-11-13

### Added
- First release: `style.def`, `style.pick`, `style.base`, `style.raw`, `style.theme`,
  `style.theme_inline_value`, `style.custom_variant`, `style.sheet`; `css.compile`,
  `css.compile_sheets`, `css.minify`, `css.unknown`.
