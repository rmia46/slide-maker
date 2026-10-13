#!/usr/bin/env python3
"""
Slide-Maker Strict Type & Schema Checker (Compiler-Grade Diagnostics).
Inspects slides.yaml with exact line/column locations, colorized compiler-style
diagnostic snippets, type verification, and actionable fix hints.
"""

import sys
import os
import re
from pathlib import Path

# ANSI colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

try:
    import yaml
except ImportError:
    yaml = None

VALID_THEMES = {"academic", "minimal", "modern"}
VALID_PALETTES = {"oxford", "crimson", "emerald", "amber", "slate", "indigo"}
VALID_LAYOUTS = {
    "title", "content", "split", "split-diagram", "split-image",
    "diagram", "image", "full_diagram", "comparison", "stat-grid", "code"
}

SCHEMA_SPEC = {
    "title": {
        "required": [],
        "fields": {
            "title": (str, "Main lecture title"),
            "subtitle": (str, "Subtitle or lecture scope"),
            "faculty": (str, "Academic institution or department"),
            "presenter": (str, "Name of the presenter / faculty"),
            "date": (str, "Date or semester identifier"),
        }
    },
    "content": {
        "required": ["title", "bullets"],
        "fields": {
            "title": (str, "Slide heading"),
            "category": (str, "Uppercase category tag"),
            "subtitle": (str, "Slide sub-heading"),
            "bullets": (list, "List of bullet points"),
            "callout": (str, "Key takeaway callout box"),
        }
    },
    "split": {
        "required": ["title", "image"],
        "fields": {
            "title": (str, "Slide heading"),
            "category": (str, "Uppercase category tag"),
            "subtitle": (str, "Slide sub-heading"),
            "image": (str, "Relative path to image/diagram"),
            "image_position": (str, "Position: 'right' or 'left'"),
            "caption": (str, "Figure caption below visual"),
            "bullets": (list, "List of bullet points"),
            "callout": (str, "Key takeaway callout box"),
        }
    },
    "diagram": {
        "required": ["title", "image"],
        "fields": {
            "title": (str, "Slide heading"),
            "category": (str, "Uppercase category tag"),
            "subtitle": (str, "Slide sub-heading"),
            "image": (str, "Relative path to image/diagram"),
            "caption": (str, "Figure caption below visual"),
            "takeaway": (str, "Full-width takeaway callout"),
            "callout": (str, "Full-width takeaway callout"),
        }
    },
    "comparison": {
        "required": ["title", "left_title", "right_title"],
        "fields": {
            "title": (str, "Slide heading"),
            "category": (str, "Uppercase category tag"),
            "subtitle": (str, "Slide sub-heading"),
            "left_title": (str, "Left column heading"),
            "right_title": (str, "Right column heading"),
            "left_bullets": (list, "List of left column points"),
            "right_bullets": (list, "List of right column points"),
            "conclusion": (str, "Comparative synthesis callout"),
        }
    },
    "stat-grid": {
        "required": ["title", "stats"],
        "fields": {
            "title": (str, "Slide heading"),
            "category": (str, "Uppercase category tag"),
            "stats": (list, "List of metric objects with value, unit, label"),
            "summary": (str, "Bottom summary callout"),
        }
    },
    "code": {
        "required": ["title", "code"],
        "fields": {
            "title": (str, "Slide heading"),
            "category": (str, "Uppercase category tag"),
            "code": (str, "Code snippet text"),
            "language": (str, "Syntax highlighting language"),
            "bullets": (list, "Explanation bullets next to code"),
        }
    }
}

# Alias normalizations
LAYOUT_ALIASES = {
    "split-diagram": "split",
    "split-image": "split",
    "image": "diagram",
    "full_diagram": "diagram",
}

class Diagnostic:
    def __init__(self, severity: str, message: str, line: int = None, col: int = 1, file_path: str = "slides.yaml", hint: str = None):
        self.severity = severity # 'error' or 'warning'
        self.message = message
        self.line = line
        self.col = col
        self.file_path = file_path
        self.hint = hint

    def format(self, lines: list[str]) -> str:
        color = RED if self.severity == "error" else YELLOW
        prefix = f"{BOLD}{color}{self.severity.upper()}{RESET}"
        loc = f"{BOLD}{CYAN}{self.file_path}:{self.line}:{self.col}{RESET}" if self.line else f"{BOLD}{CYAN}{self.file_path}{RESET}"
        out = [f"{prefix}: {BOLD}{self.message}{RESET}", f"  --> {loc}"]

        if self.line and 1 <= self.line <= len(lines):
            # Print snippet around error
            start = max(1, self.line - 1)
            end = min(len(lines), self.line + 1)
            out.append(f"   {BLUE}|{RESET}")
            for l_num in range(start, end + 1):
                raw_l = lines[l_num - 1]
                gutter = f"{l_num:4d} {BLUE}|{RESET} "
                if l_num == self.line:
                    out.append(f" {BOLD}{gutter}{RESET}{raw_l}")
                    pointer = " " * (len(f" {gutter}") + self.col - 1) + f"{color}^^^ {self.severity}{RESET}"
                    out.append(pointer)
                else:
                    out.append(f" {DIM}{gutter}{raw_l}{RESET}")
            out.append(f"   {BLUE}|{RESET}")

        if self.hint:
            out.append(f"  {BOLD}{GREEN}= note / fix:{RESET} {self.hint}")
        return "\n".join(out)

class LineLoader(yaml.SafeLoader if yaml else object):
    pass

def setup_line_loader():
    if not yaml:
        return
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        d = loader.construct_mapping(node)
        d["__line__"] = node.start_mark.line + 1
        d["__col__"] = node.start_mark.column + 1
        return d
    LineLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)

setup_line_loader()

def validate_yaml_string(yaml_str: str, root_dir: Path, filename: str = "slides.yaml") -> tuple[bool, list[Diagnostic]]:
    diagnostics = []
    lines = yaml_str.splitlines()

    if not yaml:
        diagnostics.append(Diagnostic("warning", "PyYAML is not installed. Full type checking requires 'pip install -r requirements.txt'.", file_path=filename))
        return True, diagnostics

    # 1. Parse YAML syntax
    try:
        data = yaml.load(yaml_str, Loader=LineLoader)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = (mark.line + 1) if mark else 1
        col = (mark.column + 1) if mark else 1
        prob = getattr(exc, "problem", str(exc))
        hint = "Check indentation and ensure unescaped colons, quotes, or backslashes are resolved."
        diagnostics.append(Diagnostic("error", f"YAML syntax error: {prob}", line=line, col=col, file_path=filename, hint=hint))
        return False, diagnostics

    if not isinstance(data, dict):
        diagnostics.append(Diagnostic("error", f"Expected root structure to be a YAML mapping/dictionary, got {type(data).__name__}.", line=1, file_path=filename, hint="The file must start with top-level 'meta:' and 'slides:' keys."))
        return False, diagnostics

    # 2. Check 'meta' Section
    if "meta" not in data:
        diagnostics.append(Diagnostic("warning", "Missing 'meta' block.", line=1, file_path=filename, hint="Add 'meta:\n  theme: academic\n  palette: oxford\n  title: ...'"))
    else:
        meta = data["meta"]
        m_line = meta.get("__line__", 1) if isinstance(meta, dict) else 1
        if not isinstance(meta, dict):
            diagnostics.append(Diagnostic("error", f"'meta' must be a mapping, got {type(meta).__name__}.", line=m_line, file_path=filename))
        else:
            theme = meta.get("theme")
            if theme and theme not in VALID_THEMES:
                diagnostics.append(Diagnostic("warning", f"Unknown theme '{theme}'.", line=m_line, file_path=filename, hint=f"Supported themes: {', '.join(sorted(VALID_THEMES))}"))

            palette = meta.get("palette")
            if palette and palette not in VALID_PALETTES:
                diagnostics.append(Diagnostic("warning", f"Unknown palette '{palette}'.", line=m_line, file_path=filename, hint=f"Built-in academic palettes: {', '.join(sorted(VALID_PALETTES))}"))

            colors = meta.get("colors")
            if colors is not None and not isinstance(colors, dict):
                diagnostics.append(Diagnostic("error", f"'meta.colors' must be a dictionary of hex colors, got {type(colors).__name__}.", line=m_line, file_path=filename))
            elif isinstance(colors, dict):
                for c_name, c_val in colors.items():
                    if c_name.startswith("__"): continue
                    if not isinstance(c_val, str) or not re.match(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", c_val):
                        diagnostics.append(Diagnostic("error", f"Invalid hex color for 'meta.colors.{c_name}': '{c_val}'.", line=m_line, file_path=filename, hint="Colors must be valid 3 or 6 digit hex strings like '#1e40af'."))

    # 3. Check 'slides' Section
    if "slides" not in data:
        diagnostics.append(Diagnostic("error", "Missing required top-level 'slides:' list.", line=1, file_path=filename, hint="Define your presentation slides under 'slides:\n  - layout: title\n    ...'"))
        return False, diagnostics

    slides = data["slides"]
    if not isinstance(slides, list):
        diagnostics.append(Diagnostic("error", f"'slides' must be a list of slide items, got {type(slides).__name__}.", line=1, file_path=filename))
        return False, diagnostics

    if len(slides) == 0:
        diagnostics.append(Diagnostic("error", "'slides' list is empty. Presentation has 0 slides.", line=1, file_path=filename))
        return False, diagnostics

    # 4. Strict Type & Schema Checking per Slide
    for idx, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            diagnostics.append(Diagnostic("error", f"Slide #{idx} must be a dictionary object, got {type(slide).__name__}.", file_path=filename))
            continue

        s_line = slide.get("__line__", 1)
        s_col = slide.get("__col__", 1)

        raw_layout = slide.get("layout", slide.get("type", "content"))
        if not isinstance(raw_layout, str):
            diagnostics.append(Diagnostic("error", f"Slide #{idx}: 'layout' must be a string, got {type(raw_layout).__name__}.", line=s_line, col=s_col, file_path=filename))
            continue

        layout = LAYOUT_ALIASES.get(raw_layout, raw_layout)
        if layout not in SCHEMA_SPEC:
            diagnostics.append(Diagnostic("warning", f"Slide #{idx}: Unrecognized layout '{raw_layout}'.", line=s_line, col=s_col, file_path=filename, hint=f"Valid layouts: {', '.join(sorted(VALID_LAYOUTS))}"))

        spec = SCHEMA_SPEC.get(layout, SCHEMA_SPEC["content"])

        # Check required fields
        for req in spec["required"]:
            if req not in slide or slide[req] is None or (isinstance(slide[req], (str, list)) and len(slide[req]) == 0):
                diagnostics.append(Diagnostic("error", f"Slide #{idx} ('{slide.get('title', 'Untitled')}'): Missing required field '{req}' for layout '{raw_layout}'.", line=s_line, col=s_col, file_path=filename, hint=f"Add '{req}: ...' to slide #{idx}."))

        # Check field types
        for field, (expected_type, desc) in spec["fields"].items():
            if field in slide and slide[field] is not None:
                val = slide[field]
                if not isinstance(val, expected_type):
                    diagnostics.append(Diagnostic("error", f"Slide #{idx}: Field '{field}' expected {expected_type.__name__} ({desc}), got {type(val).__name__}.", line=s_line, col=s_col, file_path=filename, hint=f"Change '{field}' value to {expected_type.__name__}."))

        # Layout-specific validations
        if layout in ("split", "diagram"):
            img_path = slide.get("image")
            if img_path:
                full_img = root_dir / img_path
                if not full_img.exists():
                    diagnostics.append(Diagnostic("warning", f"Slide #{idx}: Referenced visual asset not found: '{img_path}'.", line=s_line, col=s_col, file_path=filename, hint=f"Place the file at {full_img} or check spelling."))

        if layout == "stat-grid":
            stats = slide.get("stats", [])
            if isinstance(stats, list):
                for s_i, st in enumerate(stats, start=1):
                    if not isinstance(st, dict):
                        diagnostics.append(Diagnostic("error", f"Slide #{idx}: Metric item #{s_i} in 'stats' must be a dictionary with 'value' and 'label'.", line=s_line, col=s_col, file_path=filename))
                    elif "value" not in st or "label" not in st:
                        diagnostics.append(Diagnostic("error", f"Slide #{idx}: Metric item #{s_i} is missing required 'value' or 'label' key.", line=s_line, col=s_col, file_path=filename))

        # Bullet density checks
        bullets = slide.get("bullets", [])
        if isinstance(bullets, list) and len(bullets) > 5:
            diagnostics.append(Diagnostic("warning", f"Slide #{idx} ('{slide.get('title', 'Untitled')}'): Contains {len(bullets)} bullets (optimal is 3-5).", line=s_line, col=s_col, file_path=filename, hint="Consider splitting into two slides to avoid vertical text crowding on screen."))

        # Typst math syntax verification
        for k in ["title", "subtitle", "callout", "takeaway", "conclusion", "summary"]:
            txt = slide.get(k)
            if isinstance(txt, str) and "$" in txt:
                # Count dollar signs to ensure balanced math mode
                dollar_count = txt.count("$")
                if dollar_count % 2 != 0:
                    diagnostics.append(Diagnostic("error", f"Slide #{idx}: Unbalanced math delimiter '$' in '{k}': \"{txt}\".", line=s_line, col=s_col, file_path=filename, hint="Typst math requires matched pairs like '$alpha$'."))

    has_errors = any(d.severity == "error" for d in diagnostics)
    return (not has_errors), diagnostics

def main():
    root = Path(__file__).resolve().parent.parent
    target_yaml = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "slides.yaml"

    if not target_yaml.exists():
        print(f"{RED}✗ Error: File not found: {target_yaml}{RESET}", file=sys.stderr)
        sys.exit(1)

    yaml_text = target_yaml.read_text(encoding="utf-8")
    is_valid, diags = validate_yaml_string(yaml_text, root, filename=target_yaml.name)
    lines = yaml_text.splitlines()

    print(f"\n{BOLD}{CYAN}⚡ Checking {target_yaml.name}...{RESET}\n")

    errors_count = 0
    warns_count = 0

    for d in diags:
        if d.severity == "error":
            errors_count += 1
        else:
            warns_count += 1
        print(d.format(lines))
        print()

    if errors_count == 0 and warns_count == 0:
        print(f"{BOLD}{GREEN}✓ Clean compilation pass!{RESET} All {len(yaml.safe_load(yaml_text).get('slides', []))} slides conform to strict schema.\n")
        sys.exit(0)
    elif errors_count == 0:
        print(f"{BOLD}{GREEN}✓ Valid with {warns_count} warning(s).{RESET}\n")
        sys.exit(0)
    else:
        print(f"{BOLD}{RED}✗ Verification failed with {errors_count} error(s) and {warns_count} warning(s).{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
