// Academic Theme (Default)
// Characteristics: Large readable typography, projector-optimized space taking,
// zero web-card clutter, pure academic hierarchy.

#import "common.typ": *

#let color-primary = rgb("#0f172a")       // Deep Slate
#let color-accent = rgb("#1e40af")        // Academic Cobalt / Navy
#let color-text-dark = rgb("#0f172a")     // Primary text
#let color-text-muted = rgb("#475569")    // Secondary text
#let color-border = rgb("#cbd5e1")        // Subtle rule lines

#let setup(meta: (:), body) = {
  let title = meta.at("title", default: "Academic Lecture")
  let faculty = meta.at("faculty", default: "")

  set document(title: title, author: meta.at("presenter", default: "Faculty"))
  set page(
    paper: "presentation-16-9",
    margin: (x: 2.2cm, top: 2.2cm, bottom: 2.0cm),
    header-ascent: 35%,
    footer-descent: 35%,
    header: context {
      let page-num = counter(page).get().first()
      if page-num > 1 {
        grid(
          columns: (1fr, auto),
          align: (left, right),
          text(size: 9.5pt, fill: color-text-muted, weight: "semibold", tracking: 0.5pt, upper(faculty)),
          text(size: 9.5pt, fill: color-text-muted, tracking: 0.3pt, title)
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
        grid(
          columns: (1fr, auto),
          align: (left, right),
          text(size: 8.5pt, fill: color-text-muted, style: "italic")[Lecture Series],
          text(size: 9.5pt, fill: color-primary, weight: "bold")[#page-num]
        )
      }
    }
  )

  set text(
    font: ("Libertinus Serif", "New Computer Modern", "DejaVu Serif"),
    size: 13.5pt,
    fill: color-text-dark
  )
  set par(leading: 0.55em)

  body
}

// Header for Academic Content Slides
#let slide-header(title, category: none, subtitle: none) = {
  v(-0.2em)
  if category != none {
    text(size: 9pt, weight: "bold", fill: color-accent, tracking: 1.2pt)[#upper(category)]
    v(-6pt)
  }
  
  text(size: 22pt, weight: "bold", fill: color-primary)[#title]
  
  if subtitle != none {
    v(-5pt)
    text(size: 11.5pt, fill: color-text-muted, weight: "medium")[#subtitle]
  }
  v(1pt)
  line(length: 100%, stroke: 1.2pt + color-accent)
  v(0.4em)
}

// 1. Title Slide
#let render-title-slide(slide, meta) = {
  let title = slide.at("title", default: meta.at("title", default: "Lecture Title"))
  let subtitle = slide.at("subtitle", default: meta.at("subtitle", default: ""))
  let faculty = slide.at("faculty", default: meta.at("faculty", default: "Department of Computer Science"))
  let presenter = slide.at("presenter", default: meta.at("presenter", default: ""))
  let date = slide.at("date", default: meta.at("date", default: ""))

  v(10%)
  if faculty != "" {
    text(size: 11pt, weight: "bold", fill: color-accent, tracking: 1.5pt)[#upper(faculty)]
    v(0.5em)
  }
  
  text(size: 30pt, weight: "extrabold", fill: color-primary)[#title]
  
  if subtitle != "" {
    v(0.3em)
    text(size: 15pt, fill: color-text-muted, weight: "regular")[#subtitle]
  }

  v(1.6em)
  line(length: 100%, stroke: 2pt + color-accent)
  v(1.0em)

  grid(
    columns: (auto, auto),
    gutter: 4em,
    if presenter != "" [
      #text(size: 9pt, weight: "bold", fill: color-text-muted)[PRESENTER] \
      #v(1pt)
      #text(size: 13pt, weight: "semibold", fill: color-primary)[#presenter]
    ],
    if date != "" [
      #text(size: 9pt, weight: "bold", fill: color-text-muted)[DATE] \
      #v(1pt)
      #text(size: 13pt, weight: "semibold", fill: color-primary)[#date]
    ]
  )
}

// 2. Bullets Slide (Space-optimized, clean typography)
#let render-bullets-slide(slide, meta) = {
  slide-header(
    slide.at("title", default: "Slide Title"),
    category: slide.at("category", default: none),
    subtitle: slide.at("subtitle", default: none)
  )

  let bullets = slide.at("bullets", default: ())
  let count = bullets.len()
  let spacing = if count <= 3 { 0.6em } else if count <= 4 { 0.3em } else { 0.2em }

  for b in bullets {
    grid(
      columns: (18pt, 1fr),
      align: (top + left, top + left),
      text(fill: color-accent, size: 14pt)[•],
      text(size: 13pt)[#render-text(b)]
    )
    v(spacing)
  }

  if "callout" in slide {
    v(0.5em)
    rect(
      stroke: (left: 3.5pt + color-accent),
      fill: none,
      width: 100%,
      inset: (left: 12pt, y: 4pt),
      [
        #text(size: 8.5pt, weight: "bold", fill: color-accent, tracking: 0.8pt)[KEY TAKEAWAY] \
        #v(1pt)
        #text(size: 11.5pt, fill: color-primary, weight: "medium", style: "italic")[#render-text(slide.callout)]
      ]
    )
  }
}

// 3. Split Image / Diagram Slide (Direct placement, large visual)
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
        align: (top + left, top + left),
        text(fill: color-accent, size: 13pt)[•],
        text(size: 13pt)[#render-text(b)]
      )
      v(0.5em)
    }
  ]

  let visual-col = [
    #align(center + horizon)[
      #if img-path != none {
        image(img-path, fit: "contain", height: 5.4cm)
      } else {
        text(fill: color-text-muted)[(No visual provided)]
      }
      #if caption != none {
        v(3pt)
        text(size: 9.5pt, fill: color-text-muted, style: "italic")[#caption]
      }
    ]
  ]

  let cols = if image-pos == "left" { (1.1fr, 1fr) } else { (1fr, 1.15fr) }
  grid(
    columns: cols,
    gutter: 1.2cm,
    if image-pos == "left" { visual-col } else { text-col },
    if image-pos == "left" { text-col } else { visual-col }
  )
}

// 4. Comparison Slide (Clean dual columns, no heavy cards)
#let render-comparison-slide(slide, meta) = {
  slide-header(
    slide.at("title", default: "Comparative Analysis"),
    category: slide.at("category", default: "TRADE-OFFS"),
    subtitle: slide.at("subtitle", default: none)
  )

  let left-title = slide.at("left_title", default: "Option A")
  let right-title = slide.at("right_title", default: "Option B")
  let left-bullets = slide.at("left_bullets", default: ())
  let right-bullets = slide.at("right_bullets", default: ())

  grid(
    columns: (1fr, 1fr),
    gutter: 1.5cm,
    [
      #text(size: 14pt, weight: "bold", fill: color-primary)[#left-title]
      #v(2pt)
      #line(length: 100%, stroke: 1.5pt + color-accent)
      #v(0.4em)
      #for b in left-bullets {
        grid(
          columns: (14pt, 1fr),
          inset: (y: 2pt),
          text(fill: color-accent, size: 12pt)[•],
          text(size: 12pt)[#render-text(b)]
        )
      }
    ],
    [
      #text(size: 14pt, weight: "bold", fill: color-primary)[#right-title]
      #v(2pt)
      #line(length: 100%, stroke: 1.5pt + rgb("#0369a1"))
      #v(0.4em)
      #for b in right-bullets {
        grid(
          columns: (14pt, 1fr),
          inset: (y: 2pt),
          text(fill: rgb("#0369a1"), size: 12pt)[•],
          text(size: 12pt)[#render-text(b)]
        )
      }
    ]
  )

  if "conclusion" in slide {
    v(1fr)
    rect(
      stroke: (left: 3pt + color-accent),
      fill: none,
      width: 100%,
      inset: (left: 10pt, y: 3pt),
      text(size: 11pt, fill: color-text-dark, weight: "medium")[
        *Synthesis:* #render-text(slide.conclusion)
      ]
    )
  }
}

// 5. Stat Grid (Large bold academic metrics, no card outlines)
#let render-stat-grid-slide(slide, meta) = {
  slide-header(
    slide.at("title", default: "Key Metrics & Empirical Results"),
    category: slide.at("category", default: "EVALUATION")
  )

  let stats = slide.at("stats", default: ())
  let count = stats.len()
  let cols = ()
  for i in range(count) { cols.push(1fr) }

  v(0.5em)
  grid(
    columns: cols,
    gutter: 1.2cm,
    ..stats.map(s => [
      #text(size: 34pt, weight: "extrabold", fill: color-accent)[#s.at("value", default: "0")]
      #if "unit" in s [ #text(size: 14pt, weight: "bold", fill: color-text-muted)[ #s.unit] ] \
      #v(2pt)
      #text(size: 12pt, weight: "bold", fill: color-primary)[#s.at("label", default: "")]
      #if "description" in s [
        #v(2pt)
        #text(size: 9.5pt, fill: color-text-muted)[#s.description]
      ]
    ])
  )

  if "summary" in slide {
    v(1fr)
    rect(
      stroke: (left: 3.5pt + color-accent),
      fill: none,
      width: 100%,
      inset: (left: 10pt, y: 5pt),
      text(size: 12pt)[#render-text(slide.summary)]
    )
  }
}

// 6. Code Slide
#let render-code-slide(slide, meta) = {
  slide-header(
    slide.at("title", default: "Code Implementation"),
    category: slide.at("category", default: "IMPLEMENTATION")
  )

  let code-str = slide.at("code", default: "")
  let lang = slide.at("language", default: "python")
  let bullets = slide.at("bullets", default: ())

  grid(
    columns: (1.35fr, 1fr),
    gutter: 1.2cm,
    rect(
      fill: rgb("#1e293b"),
      radius: 4pt,
      inset: 10pt,
      width: 100%,
      [
        #set text(font: ("JetBrainsMono NF", "DejaVu Sans Mono"), size: 9pt, fill: rgb("#f8fafc"))
        #raw(code-str, lang: lang, block: true)
      ]
    ),
    [
      #for b in bullets {
        grid(
          columns: (14pt, 1fr),
          inset: (y: 4pt),
          text(fill: color-accent, size: 12pt)[•],
          text(size: 12.5pt)[#render-text(b)]
        )
      }
    ]
  )
}

// Dispatcher for Academic Theme
#let render-slide(slide, meta) = {
  let layout = slide.at("layout", default: slide.at("type", default: "content"))
  
  if layout == "title" {
    render-title-slide(slide, meta)
  } else if layout == "split-diagram" or layout == "split-image" {
    render-split-slide(slide, meta)
  } else if layout == "comparison" {
    render-comparison-slide(slide, meta)
  } else if layout == "stat-grid" {
    render-stat-grid-slide(slide, meta)
  } else if layout == "code" {
    render-code-slide(slide, meta)
  } else {
    render-bullets-slide(slide, meta)
  }
}
