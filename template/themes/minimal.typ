// Minimalist Theme (Typographic & Restrained)
#import "common.typ": *

#let color-primary = rgb("#18181b")       // Zinc 900
#let color-accent = rgb("#3f3f46")        // Zinc 700
#let color-text-dark = rgb("#18181b")
#let color-text-muted = rgb("#71717a")    // Zinc 500
#let color-border = rgb("#e4e4e7")        // Zinc 200

#let setup(meta: (:), body) = {
  let title = meta.at("title", default: "Presentation")
  set document(title: title)
  set page(
    paper: "presentation-16-9",
    margin: (x: 2.2cm, top: 1.6cm, bottom: 1.4cm),
    header: context {
      let page-num = counter(page).get().first()
      if page-num > 1 {
        grid(
          columns: (1fr, auto),
          align: (left, right),
          text(size: 9pt, fill: color-text-muted, tracking: 0.5pt, upper(meta.at("faculty", default: ""))),
          text(size: 9pt, fill: color-text-muted, title)
        )
        v(2pt)
        line(length: 100%, stroke: 0.5pt + color-border)
      }
    },
    footer: context {
      let page-num = counter(page).get().first()
      if page-num > 1 {
        line(length: 100%, stroke: 0.5pt + color-border)
        v(3pt)
        align(right, text(size: 9pt, fill: color-text-muted)[#page-num])
      }
    }
  )

  set text(
    font: ("Inter", "DejaVu Sans"),
    size: 16.5pt,
    fill: color-text-dark,
    spacing: 120%
  )

  body
}

#let slide-header(title, category: none, subtitle: none) = {
  v(0.2em)
  if category != none {
    text(size: 9.5pt, weight: "bold", fill: color-text-muted, tracking: 1.5pt)[#upper(category)]
    v(-4pt)
  }
  text(size: 24pt, weight: "bold", fill: color-primary)[#title]
  if subtitle != none {
    v(-4pt)
    text(size: 13pt, fill: color-text-muted)[#subtitle]
  }
  v(3pt)
  line(length: 100%, stroke: 0.8pt + color-primary)
  v(0.6em)
}

#let render-title-slide(slide, meta) = {
  let title = slide.at("title", default: meta.at("title", default: "Title"))
  let subtitle = slide.at("subtitle", default: meta.at("subtitle", default: ""))
  let faculty = slide.at("faculty", default: meta.at("faculty", default: ""))
  let presenter = slide.at("presenter", default: meta.at("presenter", default: ""))
  let date = slide.at("date", default: meta.at("date", default: ""))

  v(14%)
  if faculty != "" {
    text(size: 12pt, weight: "medium", fill: color-text-muted, tracking: 1.5pt)[#upper(faculty)]
    v(0.4em)
  }
  text(size: 36pt, weight: "bold", fill: color-primary)[#title]
  if subtitle != "" {
    v(0.4em)
    text(size: 17pt, fill: color-text-muted)[#subtitle]
  }
  v(2em)
  line(length: 100%, stroke: 1.2pt + color-primary)
  v(1.2em)
  grid(
    columns: (auto, auto),
    gutter: 4em,
    if presenter != "" [
      #text(size: 10pt, fill: color-text-muted)[AUTHOR] \
      #text(size: 14pt, weight: "semibold")[#presenter]
    ],
    if date != "" [
      #text(size: 10pt, fill: color-text-muted)[DATE] \
      #text(size: 14pt, weight: "semibold")[#date]
    ]
  )
}

#let render-bullets-slide(slide, meta) = {
  slide-header(
    slide.at("title", default: "Slide Title"),
    category: slide.at("category", default: none),
    subtitle: slide.at("subtitle", default: none)
  )

  let bullets = slide.at("bullets", default: ())
  for b in bullets {
    grid(
      columns: (20pt, 1fr),
      text(fill: color-accent, size: 14pt)[—],
      text(size: 16pt)[#render-text(b)]
    )
    v(0.9em)
  }

  if "callout" in slide {
    v(1fr)
    rect(
      stroke: (left: 2pt + color-primary),
      fill: none,
      inset: (left: 12pt, y: 4pt),
      text(size: 13pt, style: "italic")[#render-text(slide.callout)]
    )
  }
}

#let render-split-slide(slide, meta) = {
  slide-header(
    slide.at("title", default: "Slide Title"),
    category: slide.at("category", default: none),
    subtitle: slide.at("subtitle", default: none)
  )

  let image-pos = slide.at("image_position", default: "right")
  let img-path = resolve-image-path(slide.at("image", default: none))
  let caption = slide.at("caption", default: none)
  let bullets = slide.at("bullets", default: ())

  let text-col = [
    #for b in bullets {
      grid(
        columns: (16pt, 1fr),
        text(fill: color-accent, size: 14pt)[—],
        text(size: 15pt)[#render-text(b)]
      )
      v(0.7em)
    }
  ]

  let visual-col = [
    #align(center + horizon)[
      #if img-path != none {
        image(img-path, fit: "contain", height: 6.0cm)
      }
      #if caption != none {
        v(4pt)
        text(size: 10pt, fill: color-text-muted, style: "italic")[#caption]
      }
    ]
  ]

  grid(
    columns: if image-pos == "left" { (1.1fr, 1fr) } else { (1fr, 1.15fr) },
    gutter: 1.5cm,
    if image-pos == "left" { visual-col } else { text-col },
    if image-pos == "left" { text-col } else { visual-col }
  )
}

#let render-comparison-slide(slide, meta) = {
  slide-header(
    slide.at("title", default: "Comparative Analysis"),
    category: slide.at("category", default: "COMPARISON")
  )

  grid(
    columns: (1fr, 1fr),
    gutter: 2.0cm,
    [
      #text(size: 16pt, weight: "bold")[#slide.at("left_title", default: "")]
      #v(2pt)
      #line(length: 100%, stroke: 1pt + color-primary)
      #v(0.5em)
      #for b in slide.at("left_bullets", default: ()) {
        grid(columns: (14pt, 1fr), text(fill: color-accent)[—], text(size: 14pt)[#render-text(b)])
        v(0.3em)
      }
    ],
    [
      #text(size: 16pt, weight: "bold")[#slide.at("right_title", default: "")]
      #v(2pt)
      #line(length: 100%, stroke: 1pt + color-primary)
      #v(0.5em)
      #for b in slide.at("right_bullets", default: ()) {
        grid(columns: (14pt, 1fr), text(fill: color-accent)[—], text(size: 14pt)[#render-text(b)])
        v(0.3em)
      }
    ]
  )

  if "conclusion" in slide {
    v(1fr)
    line(length: 100%, stroke: 0.5pt + color-border)
    v(4pt)
    text(size: 12pt, weight: "medium")[*Synthesis:* #render-text(slide.conclusion)]
  }
}

#let render-stat-grid-slide(slide, meta) = {
  slide-header(
    slide.at("title", default: "Metrics"),
    category: slide.at("category", default: "METRICS")
  )

  let stats = slide.at("stats", default: ())
  let cols = ()
  for i in range(stats.len()) { cols.push(1fr) }

  v(1em)
  grid(
    columns: cols,
    gutter: 1.5cm,
    ..stats.map(s => [
      #text(size: 42pt, weight: "bold")[#s.at("value", default: "0")]
      #if "unit" in s [ #text(size: 15pt, fill: color-text-muted)[#s.unit] ] \
      #v(2pt)
      #text(size: 13pt, weight: "semibold")[#s.at("label", default: "")]
      #if "description" in s [
        #v(2pt)
        #text(size: 10.5pt, fill: color-text-muted)[#s.description]
      ]
    ])
  )

  if "summary" in slide {
    v(1fr)
    text(size: 13.5pt)[#render-text(slide.summary)]
  }
}

#let render-code-slide(slide, meta) = {
  slide-header(
    slide.at("title", default: "Code"),
    category: slide.at("category", default: "CODE")
  )

  grid(
    columns: (1.35fr, 1fr),
    gutter: 1.4cm,
    rect(
      fill: rgb("#f4f4f5"),
      stroke: 0.5pt + color-border,
      radius: 3pt,
      inset: 10pt,
      width: 100%,
      [
        #set text(font: ("JetBrainsMono NF", "DejaVu Sans Mono"), size: 10pt, fill: color-primary)
        #raw(slide.at("code", default: ""), lang: slide.at("language", default: "python"), block: true)
      ]
    ),
    [
      #for b in slide.at("bullets", default: ()) {
        grid(columns: (14pt, 1fr), text(fill: color-accent)[—], text(size: 14pt)[#render-text(b)])
        v(0.5em)
      }
    ]
  )
}

#let render-slide(slide, meta) = {
  let layout = slide.at("layout", default: slide.at("type", default: "content"))
  if layout == "title" { render-title-slide(slide, meta) }
  else if layout == "split-diagram" or layout == "split-image" { render-split-slide(slide, meta) }
  else if layout == "comparison" { render-comparison-slide(slide, meta) }
  else if layout == "stat-grid" { render-stat-grid-slide(slide, meta) }
  else if layout == "code" { render-code-slide(slide, meta) }
  else { render-bullets-slide(slide, meta) }
}
