// Shared utilities across themes

#let academic-palettes = (
  oxford: (
    primary: rgb("#0f172a"),
    accent: rgb("#1e40af"),       // Classic Oxford Cobalt
    muted: rgb("#475569"),
    border: rgb("#cbd5e1"),
    bg: rgb("#ffffff"),
  ),
  crimson: (
    primary: rgb("#1a0505"),
    accent: rgb("#991b1b"),       // Harvard / Stanford Crimson
    muted: rgb("#57534e"),
    border: rgb("#d6d3d1"),
    bg: rgb("#ffffff"),
  ),
  emerald: (
    primary: rgb("#022c22"),
    accent: rgb("#065f46"),       // Deep Academic Forest Emerald
    muted: rgb("#475569"),
    border: rgb("#cbd5e1"),
    bg: rgb("#ffffff"),
  ),
  amber: (
    primary: rgb("#1c1917"),
    accent: rgb("#92400e"),       // Deep Ochre / Amber
    muted: rgb("#57534e"),
    border: rgb("#d6d3d1"),
    bg: rgb("#ffffff"),
  ),
  slate: (
    primary: rgb("#0f172a"),
    accent: rgb("#334155"),       // Sophisticated Slate / Charcoal
    muted: rgb("#64748b"),
    border: rgb("#e2e8f0"),
    bg: rgb("#ffffff"),
  ),
  indigo: (
    primary: rgb("#0f172a"),
    accent: rgb("#4338ca"),       // Cambridge / Deep Indigo
    muted: rgb("#475569"),
    border: rgb("#cbd5e1"),
    bg: rgb("#ffffff"),
  )
)

#let resolve-colors(meta, fallback-palette: "oxford") = {
  let pal-name = meta.at("palette", default: fallback-palette)
  let base = academic-palettes.at(pal-name, default: academic-palettes.at(fallback-palette, default: academic-palettes.oxford))
  let custom = meta.at("colors", default: (:))

  (
    primary: if "primary" in custom { rgb(custom.primary) } else { base.primary },
    accent: if "accent" in custom { rgb(custom.accent) } else { base.accent },
    muted: if "muted" in custom { rgb(custom.muted) } else { base.muted },
    border: if "border" in custom { rgb(custom.border) } else { base.border },
    bg: if "background" in custom { rgb(custom.background) } else { base.bg },
  )
}

#let resolve-font(meta, default-font: ("Libertinus Serif", "New Computer Modern", "DejaVu Serif")) = {
  if "font" in meta {
    let f = meta.font
    if type(f) == str { (f, ..default-font) } else { f }
  } else {
    default-font
  }
}

#let render-text(txt) = {
  if type(txt) != str {
    return txt
  }
  let converted = txt.replace(regex("\*\*(.+?)\*\*"), m => "*" + m.captures.at(0) + "*")
  
  // Convert common LaTeX math commands to Typst math equivalents
  converted = converted.replace("\\Delta", "Delta")
                       .replace("\\alpha", "alpha")
                       .replace("\\beta", "beta")
                       .replace("\\gamma", "gamma")
                       .replace("\\lfloor", "floor(")
                       .replace("\\rfloor", ")")
                       .replace("\\leq", "<=")
                       .replace("\\geq", ">=")
                       .replace("\\times", "times")
                       .replace("\\in", "in")
  
  eval(converted, mode: "markup")
}

#let resolve-image-path(path) = {
  if path == none { return none }
  if path.starts-with("/") { path } else { "/" + path }
}
