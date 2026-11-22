# Bundled font

`SymbolsNerdFont-Regular.woff2` is the [Nerd Fonts Symbols Only](https://github.com/ryanoasis/nerd-fonts)
font from release `v3.5.1`, converted from TTF to WOFF2 with `fonttools`.

It is used as a fallback for Nerd Font glyphs (Unicode private-use characters)
in door content. The font is loaded only when a page contains a character in
one of the ranges declared by the `@font-face` rule in `../../static/style.css`.

Licensed under the MIT License; see [LICENSE](LICENSE).
