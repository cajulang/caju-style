# caju style

Utility-first CSS for [Caju](https://github.com/aecdanjundex/cajulang), compiled to semantic
classes. You write styles with the utility vocabulary of Tailwind CSS, in Caju, and each style
becomes **one class with a readable name**: the elements carry `class="hero-title"` instead of a
dozen utilities, and the names stay readable instead of being shortened. The stylesheet is written
by Caju: there is no Node and no Tailwind.

```caju
import style "github.com/aecdanjundex/caju-style"

let card = style.def("card", "flex flex-col gap-3 rounded-[20px] bg-card p-7 ring-1 ring-border")
let card_title = style.def("card-title", "text-xl font-bold sm:text-2xl")

fn Card(p: CardProps) -> *ui.Node {
  return (
    <div class={card}>
      <h3 class={card_title}>{p.title}</h3>
    </div>
  )
}
```

```html
<div class="card"><h3 class="card-title">…</h3></div>
```

```css
.card {
  display: flex;
  flex-direction: column;
  gap: calc(var(--spacing) * 3);
  border-radius: 20px;
  …
}
```

## The vocabulary

The utilities are Tailwind CSS 4's, with the same declarations:

- layout: `flex`, `grid`, `grid-cols-*`, `gap-*`, `items-*`, `justify-*`, `absolute`,
  `inset-*`, `z-*`, `overflow-*`, `sr-only`...
- sizes and spacing: `w-*`, `h-*`, `size-*`, `min-*`, `max-*`, `p-*`, `m-*` (the spacing scale,
  fractions, `-` for negatives);
- typography: `text-*` (sizes and colors), `font-*`, `leading-*`, `tracking-*`, `whitespace-*`,
  `break-*`, `uppercase`, `italic`, `antialiased`, `tabular-nums`...;
- colors with opacity (`bg-primary/80`, as `color-mix()` with a fallback);
- borders, rings, shadows, outlines, radii;
- transforms, transitions, animations (`animate-spin` and the `animate-in` / `fade-in` /
  `zoom-in` / `slide-in-*` family);
- `content-['›']` for `before:` and `after:`, `order-*`, `border-collapse`;
- arbitrary values and properties: `w-[640px]`, `grid-cols-[3rem_minmax(0,1fr)]`,
  `[mask-image:linear-gradient(...)]`, `shadow-[inset_0_0_0_1px_var(--color-border)]`.

Variants work as in Tailwind:

- `hover:`, `focus-visible:`, `active:`, `disabled:`, `first:`, `last:`;
- `sm:` … `2xl:`, `max-*:`, `dark:`, `motion-reduce:`, `supports-[...]:`;
- `aria-*:`, `data-*:`, `has-*:`, `not-*:`, `in-*:`, `group-*:`, `peer-*:`;
- `*:`, `**:`, `[&_svg]:` and other arbitrary selectors.

`hover:` applies only where hovering exists (`@media (hover: hover)`), as in Tailwind 4.
`tools/check.sh` compares the output with Tailwind's, utility by utility, on the 595 utilities of
a real site (`testdata/`), and all of them match.

## The API

`style` is the registry, small enough for a program in the browser:

| | |
|---|---|
| `style.def(name, utilities) -> str` | a class named `name`; returns the name, for `class={...}` |
| `style.pick(cond, yes, no) -> str` | one of two styles: `class={style.pick(on, tab_on, tab)}` |
| `style.base(selector, utilities)` | a rule in the base layer for any selector (`"body"`, `"code, pre"`) |
| `style.raw(css)` | CSS written as is (`@font-face`, the palette's custom properties) |
| `style.theme(name, value)` | a theme value, used as `var(--name)` (`"color-brand"`, `"font-sans"`) |
| `style.theme_inline_value(name, value)` | a theme value written into the rules themselves |
| `style.custom_variant(name, selectors)` | a variant: `"data-open"`, `"&:where([data-state=\"open\"])"` |
| `style.sheet(name) -> str` | the defs that follow go to their own stylesheet (a page's styles) |
| `style.registry()` | everything registered, for the compiler |

`css` is the compiler, which only the build imports:

| | |
|---|---|
| `css.compile(style.registry()) -> str` | the stylesheet |
| `css.compile_sheets(style.registry()) -> map[str]str` | split by `style.sheet`: `""` is the main one, each other has just its classes |
| `css.minify(text) -> str` | without indentation, line breaks and comments |
| `css.unknown(style.registry()) -> []str` | the utilities it does not know, as `"def: utility"` |

A build step writes the stylesheet after importing the program, so every `style.def` has run:

```caju
import style "github.com/aecdanjundex/caju-style"
import css "github.com/aecdanjundex/caju-style/css"
import "std/fs"
import "std/os"
import "./theme"
import "./app"

theme.setup()
reg := style.registry()
for _, w := range css.unknown(reg) { os.eprintln("unknown utility in " + w) }
fs.write_file("public/site.css", css.minify(css.compile(reg)), 420)
```

## Composing

A def can include another one with `@name`, and the utilities that come later replace the ones
they conflict with, as tailwind-merge does: `text-[15px]` replaces `text-sm`, `px-5` replaces
`px-3`, `border-dashed` keeps `border`.

```caju
let button = style.def("button", "inline-flex h-9 items-center gap-2 rounded-lg px-3 text-sm font-medium transition-colors disabled:opacity-50")
let button_primary = style.def("button-primary", "@button bg-primary text-primary-foreground hover:bg-primary/80")
let button_large = style.def("button-large", "@button-primary h-11 px-5 text-[15px] font-bold")
```

State that comes from data reads better as a data attribute than as more classes:

```caju
let cell = style.def("memory-cell", "h-11 min-w-12 border px-3 data-[wide]:min-w-24 data-[tone=ptr]:bg-accent data-[tone=meta]:bg-muted")

<div class={cell} data-tone={tone} data-wide={wide}>{value}</div>
```

## A sheet per page

A site loads faster when each page brings only its own styles. A page's module starts with
`let SHEET = style.sheet("home")`, and its defs go to that sheet. `css.compile_sheets` returns:

- the main stylesheet: the theme, the reset, the base rules and the shared defs (cache it);
- one sheet per page, with only that page's classes in the utilities layer. Load it after the main
  one, or inline it in the page's `<head>` so it costs no request.

On the cajulang site the main stylesheet went from 16.9 to 9.5 KB gzipped, and each page inlines
1 to 3 KB.

## The output

The stylesheet has the shape of Tailwind's:

- the cascade layers `theme, base, components, utilities`;
- the theme variables the rules use (the default theme, then yours);
- the reset (Tailwind's preflight);
- the base rules;
- one rule for each def and variant, ordered as Tailwind orders variants;
- the raw CSS, the registered custom properties (`@property`) and the keyframes used.

Rules with the same body share it (`.button:focus-visible, .button-primary:focus-visible {…}`),
which keeps the families made with `@name` from repeating themselves. Each element is meant to
have one def's class: the cascade between two defs on the same element is not defined.

The cost of readable classes is a larger stylesheet than Tailwind's, because each class has its own
combination of declarations, while the HTML gets smaller. On the
[cajulang site](https://github.com/aecdanjundex/cajulang-ui-site) (seven pages), the total
transfer went down by 10% (see its PERF.md).

## Tests

```sh
caju test                 # the registry and the compiler
CAJU=caju tools/check.sh  # every utility of testdata/tokens.txt against Tailwind's output (Python 3)
```

## License

MIT. The reset and the registered properties are Tailwind CSS's (MIT, Tailwind Labs).
