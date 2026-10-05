# slide-maker

An offline, lightning-fast presentation slide generator built on **Typst** and an editable **YAML** intermediate representation.

Designed for seamless **Human + Agentic AI** collaboration:
- **No web browser or headless Chromium**: Pure native binary compilation.
- **Editable Intermediate Representation**: Content lives in `slides.yaml`. Anyone (human or AI) can edit text, swap diagrams, or tweak stats at any time.
- **Instant Compilation**: Compiles full decks to publication-grade vector PDFs in milliseconds.
- **Rich Visuals**: First-class support for SVG vector diagrams, local images, LaTeX math (`$E=mc^2$`), and syntax-highlighted code.

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

## File Structure

```
slide-maker/
├── slides.yaml            # The intermediate representation (Content & Structure)
├── slides.typ             # Root compilation entry point
├── slide-maker            # CLI executable (build, watch, export-images)
├── assets/                # Local diagrams, SVGs, and graphics
│   └── consensus-diagram.svg
├── template/
│   ├── theme.typ          # Design system, layout components, and typography
│   └── main.typ           # Standalone entry point
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
