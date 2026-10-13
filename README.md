# slide-maker

An offline, high-speed presentation generator built with **Typst** and an editable **YAML** intermediate representation.

Designed for seamless **Human + AI** workflow:
- **Zero Web Dependencies**: Compiles directly to vector PDF via native binary in ~1.5 seconds.
- **Zero-Edit Terminal Workflow**: Paste LLM-generated YAML into the terminal or build directly from your clipboard.
- **Academic Typography**: Classical serif typesetting (`Libertinus Serif`) with LaTeX-grade math (`New Computer Modern`).
- **Editable PowerPoint Export**: Export directly to widescreen `.pptx` decks while keeping layout and text editable.
- **Token-Saving Workflow**: Copy [`PROMPT.md`](PROMPT.md) into web LLMs (Claude, Gemini, DeepSeek, ChatGPT) to generate entire slide decks without burning API tokens.

---

## 1. Requirements & Setup

### Core Requirement (PDF & Images)
The core compiler requires only the standalone **Typst** binary:

- **Arch Linux**: `pacman -S typst`
- **macOS**: `brew install typst`
- **Linux (Binary)**:
  ```bash
  curl -fsSL https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz | tar -xJ
  mv typst-*/typst ~/.local/bin/
  ```

### Optional: Python Environment (For PPTX Export)
Building PDF slides requires no Python packages. To export editable PowerPoint decks (`./slide-maker export-pptx`) or enable deep YAML schema validation:

```bash
# Using uv (fastest):
uv venv .venv && uv pip install -r requirements.txt

# Or using python3 venv:
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```
> `./slide-maker` automatically detects and uses `.venv/` if present. If your slides include SVG diagrams, install `librsvg` (`rsvg-convert`) or `inkscape` for automatic SVG-to-PPTX rasterization.

---

## 2. How to Use

The workflow separates content generation from rendering so you never have to hand-format slides:

```
[Web AI / Agent] ──(Copy YAML)──> [Terminal / Clipboard] ──(./slide-maker paste)──> [PDF & PPTX]
```

### Step-by-Step Workflow:
1. **Generate**: Copy the prompt instructions from [`PROMPT.md`](PROMPT.md) into any web AI (DeepSeek, Claude, Gemini, ChatGPT) alongside your topic notes.
2. **Copy**: Copy the generated YAML block from the AI's response.
3. **Build**: Run either:
   ```bash
   ./slide-maker paste -c          # Builds directly from clipboard
   ```
   or
   ```bash
   ./slide-maker paste             # Paste into terminal, then press Ctrl+D
   ```
4. **Done**: The tool auto-sanitizes code fences, validates syntax, backs up the previous deck to `slides.yaml.bak`, and compiles `slides.pdf`.

### CLI Commands Reference:
| Command | Description |
| :--- | :--- |
| `./slide-maker paste [-c]` | Ingests YAML from terminal input or clipboard (`-c`), auto-validates, and compiles. |
| `./slide-maker build` | Compiles existing `slides.yaml` into `slides.pdf`. |
| `./slide-maker check` | Validates YAML syntax, schema keys, and slide count without compiling. |
| `./slide-maker watch` | Auto-recompiles `slides.pdf` on every save to `slides.yaml`. |
| `./slide-maker export-pptx [out.pptx]` | Converts deck into an editable widescreen PowerPoint file (`slides.pptx`). |
| `./slide-maker export-images [dir]` | Renders each slide into a high-res PNG (default: `dist/slides/`). |
| `./slide-maker help` | Displays command options and usage examples. |

---

## 3. Themes & Customization

All styling is configured in the `meta` block of `slides.yaml` without touching Typst templates.

### Built-in Palettes:
```yaml
meta:
  theme: "academic"          # "academic" (default) | "minimal" | "modern"
  palette: "crimson"         # Choose one from table below
```

| Palette | Aesthetic | Primary Accent |
| :--- | :--- | :--- |
| **`oxford`** *(Default)* | Classic British collegiate navy | `#1e40af` (Oxford Blue) |
| **`crimson`** | Ivy League / Harvard / Stanford | `#991b1b` (Crimson) |
| **`emerald`** | Academic forest / Dartmouth | `#065f46` (Deep Emerald) |
| **`amber`** | Warm academic ochre / Princeton | `#92400e` (Amber Gold) |
| **`slate`** | Minimalist charcoal / Monochrome | `#334155` (Slate) |
| **`indigo`** | Contemporary Cambridge | `#4338ca` (Deep Indigo) |

### Custom Colors & Fonts:
Override individual colors or typography directly:
```yaml
meta:
  theme: "academic"
  colors:
    accent: "#8B0000"        # Accent color (bullets, categories, rules)
    primary: "#1A1A1A"       # Headings and body text
    muted: "#555555"         # Subtitles and metadata
    background: "#FAFAFA"    # Slide canvas color
    border: "#E0E0E0"        # Divider lines
  font: "Libertinus Serif"   # "Libertinus Serif" | "New Computer Modern" | "DejaVu Serif"
```

---

## 4. Supported Slide Layouts

Declare slides in `slides.yaml` under `slides:` using semantic layouts:

| Layout | Purpose | Key Fields |
| :--- | :--- | :--- |
| **`title`** | Presentation title slide | `title`, `subtitle`, `faculty`, `presenter`, `date` |
| **`content`** | Academic bullet points with callout | `title`, `subtitle`, `category`, `bullets`, `callout` |
| **`split`** / **`split-diagram`** | 50/50 text and large image/diagram | `image`, `image_position` (`right`\|`left`), `caption`, `bullets` |
| **`diagram`** / **`image`** | Full-slide architecture diagram / chart | `image`, `caption`, `takeaway` |
| **`comparison`** | Side-by-side contrast columns | `left_title`, `left_bullets`, `right_title`, `right_bullets`, `conclusion` |
| **`stat-grid`** | Prominent quantitative metrics | `stats: [{value, unit, label, description}]`, `summary` |
| **`code`** | Monospace code block with explanation | `language`, `code`, `bullets` |

*(See [`slides.yaml`](slides.yaml) for a complete 40-slide working reference.)*

---

## 5. Project Structure

```
slide-maker/
├── slides.yaml            # Intermediate slide data (content & styling)
├── slides.typ             # Root Typst compilation template
├── slide-maker            # Main CLI tool (build, paste, watch, pptx)
├── requirements.txt       # Optional Python dependencies (python-pptx)
├── PROMPT.md              # Token-saving prompt to copy into web LLMs
├── AGENT_INSTRUCTIONS.md  # Formal schema specifications for coding agents
├── assets/                # Slide diagrams, images, and figures
├── scripts/
│   ├── builder.py         # Ingestion, validation, and paste engine
│   └── export_pptx.py     # Native PowerPoint exporter
└── template/
    ├── theme.typ          # Dynamic theme dispatcher
    └── themes/
        ├── academic.typ   # Primary academic layout
        ├── minimal.typ    # Minimal monochrome layout
        ├── modern.typ     # Contemporary boxed layout
        └── common.typ     # Shared math, palettes, and font resolvers
```
