// Theme System Dispatcher
#import "themes/academic.typ" as theme-academic
#import "themes/modern.typ" as theme-modern
#import "themes/minimal.typ" as theme-minimal

#let get-theme-module(theme-name) = {
  if theme-name == "modern" {
    theme-modern
  } else if theme-name == "minimal" {
    theme-minimal
  } else {
    // Default is academic
    theme-academic
  }
}

// Master Presentation Setup (dispatches to chosen theme)
#let presentation(meta: (:), body) = {
  let theme-name = meta.at("theme", default: "academic")
  let mod = get-theme-module(theme-name)
  (mod.setup)(meta: meta, body)
}

// Deck Renderer (dispatches slide layout to chosen theme)
#let render-deck(data) = {
  let meta = data.at("meta", default: (:))
  let theme-name = meta.at("theme", default: "academic")
  let mod = get-theme-module(theme-name)

  let slides = data.at("slides", default: ())
  let total = slides.len()

  for (i, slide) in slides.enumerate() {
    (mod.render-slide)(slide, meta)
    if i < total - 1 {
      pagebreak()
    }
  }
}
