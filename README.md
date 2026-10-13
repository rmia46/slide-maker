# slide-maker

An offline, high-speed presentation slide generator built with **Typst** and an editable **YAML** intermediate representation.

Designed for seamless **Human + Agentic AI** collaboration:
- **Zero Web Dependencies**: Compiles directly via native binary; no Node.js, headless Chromium, or browser servers.
- **Zero-Edit Terminal Workflow**: Paste LLM output into the terminal or build directly from your clipboard with `./slide-maker paste`.
- **Instant Compilation**: Renders 40+ vector slides to sharp PDF in ~1.5 seconds.
- **Authentic Academic Typography**: Classical serif typesetting (`Libertinus Serif`) paired with Knuth's LaTeX-grade math (`New Computer Modern`).
- **Token-Saving Prompt Template**: Copy [`PROMPT.md`](PROMPT.md) into online web LLMs (DeepSeek, Gemini, Claude, ChatGPT) to generate ready-to-build decks for free.
- **Autonomous Agent Guide**: Dedicated specification in [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md).

---

## Quickstart

### 1. Instant Paste & Build (Zero-Edit Workflow)
Paste generated YAML from web models directly into the terminal or from your clipboard:

```bash
# Option A: Paste directly in terminal, then press [Ctrl+D] to build
./slide-maker paste

# Option B: Copy from browser, then build directly from clipboard
./slide-maker paste -c

# Option C: Pipe directly from a file or command
cat my_slides.yaml | ./slide-maker paste
```
* **Auto-Sanitization**: Strips markdown code fences (```` ```yaml ````) and introductory/concluding chat.
* **Pre-Flight Validation**: Validates YAML syntax with exact line/column pointers.
* **Automated Backup**: Preserves your previous working deck at `slides.yaml.bak`.
* **Verbose Diagnostics**: Highlights syntax errors or Typst math issues with actionable fix suggestions.

### 2. Manual Commands
```bash
# Compile slides.yaml -> slides.pdf
./slide-maker build

# Validate syntax and slide count without compiling
./slide-maker check

# Watch mode: auto-recompiles on every save to slides.yaml
./slide-maker watch

# Export each slide as high-res PNG (default: dist/slides/)
./slide-maker export-images [output_dir]

# Export to native editable PowerPoint deck (default: slides.pptx)
./slide-maker export-pptx [output.pptx]
```

---

## Themes & Customization (Zero Source Code Editing)

All design adjustments are controlled directly through `meta` in `slides.yaml` without touching Typst source files:

### 1. Built-in Academic Palettes
```yaml
meta:
  theme: "academic"          # "academic" (default) | "minimal" | "modern"
  palette: "oxford"          # Built-in presets below
```

| Palette | Aesthetic Focus | Accent Color |
| :--- | :--- | :--- |
| **`oxford`** *(Default)* | Classic British collegiate navy | `#1e40af` (Oxford Blue) |
| **`crimson`** | Ivy League / Harvard / Stanford | `#991b1b` (Crimson) |
| **`emerald`** | Academic forest / Dartmouth | `#065f46` (Deep Emerald) |
| **`amber`** | Warm academic ochre / Princeton | `#92400e` (Amber Gold) |
| **`slate`** | Minimalist charcoal / Monochrome | `#334155` (Slate) |
| **`indigo`** | Contemporary Cambridge | `#4338ca` (Deep Indigo) |

### 2. Custom Hex Colors & Font Overrides
```yaml
meta:
  theme: "academic"
  colors:
    accent: "#8B0000"        # Bullets, category rules, stat numbers
    primary: "#1A1A1A"       # Main headings and text
    muted: "#555555"         # Subtitles and metadata
    background: "#FAFAFA"    # Slide canvas color
    border: "#E0E0E0"        # Subtle divider lines
  font: "Libertinus Serif"   # "Libertinus Serif" | "New Computer Modern" | "DejaVu Serif"
```

---

## Supported Slide Layouts

Declare slides in `slides.yaml` using any of the following semantic layouts:

### 1. Title Slide (`layout: "title"`)
```yaml
- layout: "title"
  title: "Consensus Protocols in Distributed Storage"
  subtitle: "Formal Mechanisms of Raft, Multi-Paxos, and Viewstamped Replication"
  faculty: "Department of Computer Sciences"
  presenter: "Prof. Alan Kay"
  date: "Fall Semester 2026"
```

### 2. Bullets / Content (`layout: "content"`)
```yaml
- layout: "content"
  category: "FOUNDATIONS"
  title: "The Consensus Problem: Formal Bounds"
  subtitle: "State Machine Replication under Asynchronous Network Assumptions"
  bullets:
    - "**FLP Impossibility Result**: Asynchronous consensus is impossible with crash failures."
    - "**Partially Synchronous Models**: Practical systems circumvent FLP using randomized timers $\Delta$."
    - "**State Machine Replication**: Replicas execute identical transitions from $S_0$."
  callout: "Consensus guarantees linearizability across network partitions."
```

### 3. Split Slide with Diagram / Image (`layout: "split-diagram"` or `"split-image"`)
*Visual takes 55%+ of slide width, sized up to 7.4cm high so text/details are clearly visible.*
```yaml
- layout: "split-diagram"
  category: "PROTOCOL MECHANICS"
  title: "Raft: Quorum-Based Log Replication"
  image: "assets/consensus-diagram.svg"   # Path relative to root
  caption: "Figure 1: Leader appends entries before dispatching AppendEntries RPCs."
  image_position: "right"                # "right" (default) or "left"
  bullets:
    - "**Client Proposal**: Client issues mutation $v=42$ exclusively to leader."
    - "**Commit Threshold**: Once replicated across $\\lfloor N/2 \\rfloor + 1$, entry commits."
```

### 4. Full-Width Diagram (`layout: "diagram"` or `"image"`)
*Uses 100% of the slide canvas for large architecture diagrams, flowcharts, or parse trees.*
```yaml
- layout: "diagram"
  category: "SYSTEMS ARCHITECTURE"
  title: "End-to-End Compiler Pipeline"
  image: "assets/compiler-pipeline.svg"
  caption: "Figure 2: Complete frontend lexing, parsing, and execution pipeline."
  takeaway: "Separating scanning from parsing isolates regular languages from CFGs."
```

### 5. Side-by-Side Comparison (`layout: "comparison"`)
```yaml
- layout: "comparison"
  category: "TRADE-OFFS"
  title: "Comparative Analysis: Raft vs Multi-Paxos"
  left_title: "Raft (Strong Leader)"
  left_bullets:
    - "**Log Discrepancy Prevention**: Unidirectional log flow from Leader to Followers."
  right_title: "Multi-Paxos (Decentralized)"
  right_bullets:
    - "**Flexible Roles**: Any replica can propose; amortized phase-1."
  conclusion: "Raft minimizes bugs in control planes; Paxos excels in active-active DBs."
```

### 6. Quantitative Metrics Grid (`layout: "stat-grid"`)
```yaml
- layout: "stat-grid"
  category: "EVALUATION"
  title: "Empirical Performance Under Cluster Degradation"
  stats:
    - value: "14.2k"
      unit: "ops/sec"
      label: "Peak Write Throughput"
    - value: "3.1"
      unit: "ms"
      label: "P99 Commit Latency"
  summary: "**Empirical Finding**: Randomized timeouts prevent split-vote livelocks with >99.7% probability."
```

### 7. Code Walkthrough (`layout: "code"`)
*Code block occupies 58% of the slide width; font size auto-scales up to 11.5pt for readability.*
```yaml
- layout: "code"
  category: "IMPLEMENTATION"
  title: "Scanner & Whitespace Stripper"
  language: "c"
  code: |
    void skip_whitespace() {
        while (*src && isspace(*src)) src++;
    }
  bullets:
    - "**Stream Pointer**: Global `src` pointer tracks current character position."
    - "**Lexical Phase**: Strips whitespace between tokens."
```

---

## File Structure

```
slide-maker/
├── slides.yaml            # Intermediate presentation data (Content & Theme)
├── slides.typ             # Root compilation entry point
├── slide-maker            # CLI executable (build, paste, check, watch, export-images)
├── PROMPT.md              # Copy-paste system prompt for web LLMs
├── AGENT_INSTRUCTIONS.md  # Detailed schema rules for autonomous agents
├── assets/                # SVGs, images, and diagrams
├── scripts/
│   └── builder.py         # Ingestion, validation, and diagnostics engine
├── template/
│   ├── theme.typ          # Dynamic theme dispatcher
│   └── themes/
│       ├── academic.typ   # Default academic theme
│       ├── minimal.typ    # Minimalist monochrome theme
│       ├── modern.typ     # Card / boxed modern theme
│       └── common.typ     # Shared math, palette, and font resolvers
└── dist/
    └── slides/            # Rendered PNG slide images
```
