// Modern Theme (Card / Boxed Style)
#import "common.typ": *

#let color-primary = rgb("#0f172a")
#let color-accent = rgb("#1d4ed8")
#let color-accent-subtle = rgb("#eff6ff")
#let color-text-dark = rgb("#0f172a")
#let color-text-muted = rgb("#64748b")
#let color-border = rgb("#e2e8f0")
#let color-bg-card = rgb("#f8fafc")
#let color-tag-bg = rgb("#f1f5f9")

#let setup(meta: (:), body) = {
  let title = meta.at("title", default: "Presentation")
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
          text(size: 8.5pt, fill: color-text-muted, weight: "medium", tracking: 0.5pt, upper(faculty)),
          text(size: 8.5pt, fill: color-text-muted, tracking: 0.3pt, title)
        )
        line(length: 100%, stroke: 0.5pt + color-border)
      }
    },
    footer: context {
      let page-num = counter(page).get().first()
      if page-num > 1 {
        line(length: 100%, stroke: 0.5pt + color-border)
        v(2pt)
        grid(
          columns: (1fr, auto),
          align: (left, right),
          text(size: 7.5pt, fill: color-text-muted)[Presentation Series],
          text(size: 8pt, fill: color-text-muted, weight: "bold")[#page-num]
        )
      }
    }
  )

  set text(
    font: ("Inter", "DejaVu Sans"),
    size: 13pt,
    fill: color-text-dark,
    spacing: 120%
  )

  body
}

#let slide-header(title, category: none, subtitle: none) = {
  if category != none {
    place(
      top + left,
      dx: 0pt, dy: -18pt,
      rect(
        fill: color-accent-subtle,
        radius: 3pt,
        inset: (x: 7pt, y: 3pt),
        stroke: 0.5pt + rgb("#bfdbfe"),
        text(size: 8pt, weight: "bold", fill: color-accent, tracking: 0.8pt, upper(category))
      )
    )
  }
  
  v(0.4em)
  text(size: 20pt, weight: "bold", fill: color-primary)[#title]
  
  if subtitle != none {
    v(-4pt)
    text(size: 11pt, fill: color-text-muted, weight: "medium")[#subtitle]
  }
  v(0.6em)
}

#let render-title-slide(slide, meta) = {
  let title = slide.at("title", default: meta.at("title", default: "Lecture Title"))
  let subtitle = slide.at("subtitle", default: meta.at("subtitle", default: ""))
  let faculty = slide.at("faculty", default: meta.at("faculty", default: ""))
  let presenter = slide.at("presenter", default: meta.at("presenter", default: ""))
  let date = slide.at("date", default: meta.at("date", default: ""))

  place(top + left, dx: -2.0cm, dy: -1.5cm,
    rect(
      width: 0.5cm,
      height: 100% + 3.1cm,
      fill: color-accent
    )
  )

  v(18%)
  if faculty != "" {
    text(size: 11pt, weight: "bold", fill: color-accent, tracking: 1.2pt)[#upper(faculty)]
    v(0.4em)
  }
  text(size: 28pt, weight: "extrabold", fill: color-primary)[#title]
  
  if subtitle != "" {
    v(0.3em)
    text(size: 15pt, fill: color-text-muted, weight: "medium")[#subtitle]
  }

  v(2.5em)
  line(length: 30%, stroke: 1.5pt + color-accent)
  v(1.2em)

  grid(
    columns: (auto, auto),
    gutter: 2.5em,
    if presenter != "" [
      #text(size: 9pt, weight: "bold", fill: color-text-muted)[PRESENTER] \
      #text(size: 12pt, weight: "semibold", fill: color-primary)[#presenter]
    ],
    if date != "" [
      #text(size: 9pt, weight: "bold", fill: color-text-muted)[DATE] \
      #text(size: 12pt, weight: "semibold", fill: color-primary)[#date]
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
    rect(
      fill: none,
      stroke: none,
      width: 100%,
      inset: (x: 0pt, y: 5pt),
      grid(
        columns: (16pt, 1fr),
        align: (top + left, top + left),
        text(fill: color-accent, size: 14pt)[•],
        render-text(b)
      )
    )
  }

  if "callout" in slide {
    v(1.2em)
    rect(
      fill: color-accent-subtle,
      stroke: (left: 3pt + color-accent),
      radius: (right: 4pt),
      width: 100%,
      inset: 10pt,
      [
        #text(size: 9pt, weight: "bold", fill: color-accent)[KEY TAKEAWAY] \
        #v(2pt)
        #text(size: 11pt, fill: color-primary, weight: "medium")[#render-text(slide.callout)]
      ]
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
      rect(
        fill: none,
        stroke: none,
        width: 100%,
        inset: (x: 0pt, y: 5pt),
        grid(
          columns: (14pt, 1fr),
          align: (top + left, top + left),
          text(fill: color-accent, size: 13pt)[•],
          render-text(b)
        )
      )
    }
  ]

  let visual-col = [
    #align(center + horizon)[
      #rect(
        fill: color-bg-card,
        stroke: 0.5pt + color-border,
        radius: 6pt,
        inset: 10pt,
        [
          #if img-path != none {
            image(img-path, fit: "contain", height: 5.4cm)
          } else {
            text(fill: color-text-muted)[(No visual provided)]
          }
          #if caption != none {
            v(4pt)
            text(size: 9pt, fill: color-text-muted, style: "italic")[#caption]
          }
        ]
      )
    ]
  ]

  let cols = if image-pos == "left" { (1.1fr, 1fr) } else { (1fr, 1.1fr) }
  grid(
    columns: cols,
    gutter: 1.8cm,
    if image-pos == "left" { visual-col } else { text-col },
    if image-pos == "left" { text-col } else { visual-col }
  )
}

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
    gutter: 1.0cm,
    rect(
      fill: color-bg-card,
      stroke: 0.5pt + color-border,
      radius: 6pt,
      inset: 10pt,
      width: 100%,
      [
        #text(size: 12pt, weight: "bold", fill: color-primary)[#left-title]
        #line(length: 100%, stroke: 1pt + color-accent)
        #v(4pt)
        #for b in left-bullets {
          grid(
            columns: (12pt, 1fr),
            inset: (y: 3pt),
            text(fill: color-accent, size: 11pt)[•],
            text(size: 11pt)[#render-text(b)]
          )
        }
      ]
    ),
    rect(
      fill: color-bg-card,
      stroke: 0.5pt + color-border,
      radius: 6pt,
      inset: 10pt,
      width: 100%,
      [
        #text(size: 12pt, weight: "bold", fill: color-primary)[#right-title]
        #line(length: 100%, stroke: 1pt + rgb("#0284c7"))
        #v(4pt)
        #for b in right-bullets {
          grid(
            columns: (12pt, 1fr),
            inset: (y: 3pt),
            text(fill: rgb("#0284c7"), size: 11pt)[•],
            text(size: 11pt)[#render-text(b)]
          )
        }
      ]
    )
  )

  if "conclusion" in slide {
    v(0.6em)
    rect(
      fill: color-tag-bg,
      radius: 4pt,
      width: 100%,
      inset: (x: 10pt, y: 7pt),
      text(size: 9.5pt, fill: color-text-dark, weight: "medium")[
        *Synthesis:* #render-text(slide.conclusion)
      ]
    )
  }
}

#let render-stat-grid-slide(slide, meta) = {
  slide-header(
    slide.at("title", default: "Key Metrics & Empirical Results"),
    category: slide.at("category", default: "EVALUATION")
  )

  let stats = slide.at("stats", default: ())
  let count = stats.len()
  let cols = ()
  for i in range(count) { cols.push(1fr) }

  grid(
    columns: cols,
    gutter: 1.0cm,
    ..stats.map(s => {
      rect(
        fill: color-bg-card,
        stroke: 0.5pt + color-border,
        radius: 6pt,
        inset: (x: 12pt, y: 16pt),
        align(center)[
          #text(size: 28pt, weight: "extrabold", fill: color-accent)[#s.at("value", default: "0")]
          #if "unit" in s [ #text(size: 13pt, weight: "bold", fill: color-text-muted)[#s.unit] ]
          #v(6pt)
          #text(size: 10pt, weight: "bold", fill: color-primary)[#s.at("label", default: "")]
          #if "description" in s [
            #v(2pt)
            #text(size: 8.5pt, fill: color-text-muted)[#s.description]
          ]
        ]
      )
    })
  )

  if "summary" in slide {
    v(1.4em)
    rect(
      fill: color-accent-subtle,
      stroke: (left: 3pt + color-accent),
      radius: (right: 4pt),
      width: 100%,
      inset: 10pt,
      render-text(slide.summary)
    )
  }
}

#let render-code-slide(slide, meta) = {
  slide-header(
    slide.at("title", default: "Code Implementation"),
    category: slide.at("category", default: "IMPLEMENTATION")
  )

  let code-str = slide.at("code", default: "")
  let lang = slide.at("language", default: "python")
  let bullets = slide.at("bullets", default: ())

  grid(
    columns: (1.3fr, 1fr),
    gutter: 1.2cm,
    rect(
      fill: rgb("#1e293b"),
      radius: 6pt,
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
          columns: (12pt, 1fr),
          inset: (y: 6pt),
          text(fill: color-accent)[•],
          render-text(b)
        )
      }
    ]
  )
}

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
