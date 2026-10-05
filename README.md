# slide-maker

An offline, lightning-fast presentation slide generator built on **Typst** and an editable **YAML** intermediate representation.

Designed for seamless **Human + Agentic AI** collaboration:
- **No web browser or headless Chromium**: Pure native binary compilation.
- **Editable Intermediate Representation**: Content lives in `slides.yaml`. Anyone (human or AI) can edit text, swap diagrams, or tweak stats at any time without touching code.
- **Agent Guide**: See [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md) for full schema documentation, layout rules, and prompting protocols.
- **Instant Compilation**: Compiles full decks to publication-grade vector PDFs in milliseconds.
- **Authentic Academic Typography**: Set in classical `Libertinus Serif` with LaTeX-standard `New Computer Modern` math.

---

## Quickstart

### Build PDF
```bash
./slide-maker build
# Produces slides.pdf in < 1 second
```

### Auto-Recompile on Edit (Watch Mode)
```bash
./slide-maker watch
# Automatically updates slides.pdf every time you save slides.yaml
```

### Export Slides to PNG
```bash
./slide-maker export-images
# Exports each slide as PNG to dist/slides/slide-1.png, slide-2.png, ...
```

---

## Theme & Color Customization (Zero Source Code Editing)

An AI agent or human can change themes, select color palettes, or specify exact hex codes directly in `slides.yaml`:

### 1. Built-in Academic Palettes
```yaml
meta:
  theme: "academic"          # "academic" (default) | "minimal" | "modern"
  palette: "crimson"         # "oxford" | "crimson" | "emerald" | "amber" | "slate" | "indigo"
```

| Palette | University / Aesthetic Focus | Primary Accent |
| :--- | :--- | :--- |
| **`oxford`** *(Default)* | Classic British collegiate navy | `#1e40af` (Oxford Blue) |
| **`crimson`** | Ivy League / Harvard / Stanford | `#991b1b` (Crimson) |
| **`emerald`** | Academic forest / Dartmouth | `#065f46` (Deep Emerald) |
| **`amber`** | Warm academic ochre / Princeton | `#92400e` (Amber Gold) |
| **`slate`** | Minimalist charcoal / Monochrome | `#334155` (Slate) |
| **`indigo`** | Contemporary Cambridge | `#4338ca` (Deep Indigo) |

### 2. Custom Hex Overrides & Fonts
Specify custom brand colors or font families directly:

```yaml
meta:
  theme: "academic"
  colors:
    accent: "#8B0000"        # Bullets, category rules, stat numbers
    primary: "#1A1A1A"       # Main headings and text
    muted: "#555555"         # Subtitles and metadata
    background: "#FAFAFA"    # Slide canvas color
    border: "#E0E0E0"        # Subtle divider lines
  font: "New Computer Modern" # "Libertinus Serif" | "New Computer Modern" | "DejaVu Serif"
```

---

## File Structure

```
slide-maker/
├── slides.yaml            # Intermediate representation (Content, Layouts, Theme)
├── slides.typ             # Root compilation entry point
├── slide-maker            # CLI executable (build, watch, export-images)
├── assets/                # Local diagrams, SVGs, and graphics
│   └── consensus-diagram.svg
├── template/
│   ├── theme.typ          # Dynamic theme dispatcher
│   └── themes/
│       ├── academic.typ   # Default academic theme
│       ├── minimal.typ    # Minimalist monochrome theme
│       ├── modern.typ     # Card / boxed modern theme
│       └── common.typ     # Shared math & text parsers
└── dist/
    └── slides/            # Exported PNGs (when requested)
```

---

## YAML Intermediate Schema

The presentation is declared entirely in `slides.yaml`:

```yaml
meta:
  title: "Course / Presentation Title"
  faculty: "Department / Organization Name"
  presenter: "Speaker Name"
  date: "Semester / Date"

slides:
  # 1. Title Slide
  - layout: "title"
    title: "Presentation Title"
    subtitle: "Supporting subtitle or abstract"
    faculty: "Academic Department"
    presenter: "Dr. Jane Doe"
    date: "Spring 2026"

  # 2. Content / Bullets Slide
  - layout: "content"
    category: "FOUNDATIONS"        # Optional category tag
    title: "Core Thesis Heading"
    subtitle: "Contextual subtitle"
    bullets:
      - "**Term**: Technical definition or rigorous explanation."
      - "**Mechanism**: Concrete operational detail with math $x^2 + y^2 = z^2$."
    callout: "Optional takeaway card highlighted at the bottom."

  # 3. Split Slide (Text + Diagram / Image)
  - layout: "split-diagram"        # or split-image
    category: "ARCHITECTURE"
    title: "Component Interaction"
    image: "assets/diagram.svg"     # Path to SVG/PNG/JPG
    caption: "Figure 1: Architectural data flow."
    image_position: "right"         # "right" (default) or "left"
    bullets:
      - "**Point A**: Description of diagram section."
      - "**Point B**: Protocol exchange details."

  # 4. Comparison Slide (2-Column Analysis)
  - layout: "comparison"
    category: "TRADE-OFFS"
    title: "Comparing Two Paradigms"
    left_title: "Approach A"
    left_bullets:
      - "**Characteristic**: Description."
    right_title: "Approach B"
    right_bullets:
      - "**Characteristic**: Description."
    conclusion: "Optional concluding synthesis bar."

  # 5. Stat Grid (Empirical Metrics)
  - layout: "stat-grid"
    category: "BENCHMARKS"
    title: "Empirical Evaluation"
    stats:
      - value: "99.9%"
        unit: "uptime"
        label: "Availability Metric"
        description: "Measured over 180 days"
      - value: "1.2"
        unit: "ms"
        label: "P99 Latency"
    summary: "**Key Takeaway**: Short synthesis explaining the metrics."

  # 6. Code Walkthrough
  - layout: "code"
    category: "IMPLEMENTATION"
    title: "State Transition Function"
    language: "python"
    code: |
      def transition(state, event):
          return state.apply(event)
    bullets:
      - "**State Machine**: Pure functional evaluation."
```

---

## Agent Prompt Template

When directing an AI agent to generate slides from raw notes or lecture materials, use this prompt:

```text
You are an expert Academic Curriculum Designer. Transform the provided notes into a structured lecture slide deck.

Output ONLY valid YAML matching the slide-maker schema into `slides.yaml`.

Design Rules:
1. Academic Rigor: Avoid filler buzzwords and marketing language. Focus on formal definitions, mechanisms, and concrete logic.
2. Layout Variety: Do not rely solely on flat bullet slides. Select the appropriate semantic layout for the material:
   - Use `split-diagram` or `split-image` when a structural diagram or graphic explains the concept.
   - Use `comparison` for trade-off analyses, opposing theories, or before/after evaluations.
   - Use `stat-grid` for empirical benchmarks, quantitative results, or performance numbers.
   - Use `code` for algorithmic implementations.
3. Visual Restraint: Use bold asterisks (**key term**) for typographic contrast on important entities.
```
