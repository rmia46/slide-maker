#!/usr/bin/env python3
import sys
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

try:
    import yaml
except ImportError:
    yaml = None

# ANSI colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def log_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def log_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def log_warn(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def log_error(msg):
    print(f"{RED}✗ {BOLD}{msg}{RESET}")

def extract_yaml_from_text(raw_text: str) -> str:
    """Extract clean YAML, stripping markdown fences or preamble/postamble chatter."""
    text = raw_text.strip()
    
    # Check if enclosed in ```yaml ... ``` or ``` ... ```
    match = re.search(r"```(?:yaml)?\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # If starts with markdown fence without closing
    if text.startswith("```yaml") or text.startswith("```"):
        lines = text.splitlines()
        filtered = [l for l in lines[1:] if not l.startswith("```")]
        return "\n".join(filtered).strip()
    
    return text

def validate_yaml_content(yaml_str: str):
    """Validate YAML syntax and slide schema using compiler-grade diagnostics."""
    try:
        from checker import validate_yaml_string
        is_valid, diags = validate_yaml_string(yaml_str, ROOT_DIR, filename="pasted_input")
        lines = yaml_str.splitlines()
        errors = [d.format(lines) for d in diags if d.severity == "error"]
        warnings = [d.format(lines) for d in diags if d.severity == "warning"]
        return is_valid, None, errors, warnings
    except ImportError:
        pass

    errors = []
    warnings = []
    data = None

    if not yaml:
        warnings.append("PyYAML is not installed. Skipping deep schema pre-validation.")
        return True, None, errors, warnings

    try:
        data = yaml.safe_load(yaml_str)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        if mark:
            line = mark.line + 1
            col = mark.column + 1
            snippet = ""
            lines = yaml_str.splitlines()
            if 0 <= mark.line < len(lines):
                snippet = f"\n  --> Line {line}: {lines[mark.line]}\n      {' ' * (col - 1)}^ {getattr(exc, 'problem', '')}"
            errors.append(f"YAML Syntax Error at line {line}, col {col}:{snippet}")
        else:
            errors.append(f"YAML Syntax Error: {exc}")
        return False, None, errors, warnings

    if not isinstance(data, dict):
        errors.append("Invalid structure: Root of slides.yaml must be a dictionary/mapping with 'meta' and 'slides'.")
        return False, data, errors, warnings

    if "slides" not in data or not isinstance(data["slides"], list):
        errors.append("Missing or invalid 'slides': Expected a list of slide objects under 'slides:'.")
        return False, data, errors, warnings

    return (len(errors) == 0), data, errors, warnings

def compile_pdf() -> tuple[bool, str]:
    """Run typst compile and capture verbose diagnostics."""
    slides_typ = ROOT_DIR / "slides.typ"
    output_pdf = ROOT_DIR / "slides.pdf"

    if not shutil.which("typst"):
        return False, "Typst binary not found in PATH (~/.local/bin/typst)."

    start_time = time.time()
    res = subprocess.run(
        ["typst", "compile", str(slides_typ), str(output_pdf)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True
    )
    elapsed_ms = int((time.time() - start_time) * 1000)

    if res.returncode == 0:
        return True, f"Generated {output_pdf.name} in {elapsed_ms}ms"
    else:
        err_msg = res.stderr.strip() or res.stdout.strip()
        return False, err_msg

def get_clipboard_content() -> str:
    """Read clipboard using wl-paste or xclip."""
    for tool in [["wl-paste"], ["xclip", "-selection", "clipboard", "-o"], ["xsel", "-b", "-o"]]:
        if shutil.which(tool[0]):
            try:
                res = subprocess.run(tool, capture_output=True, text=True, check=True)
                if res.stdout.strip():
                    return res.stdout
            except Exception:
                continue
    return ""

def handle_paste(use_clipboard=False):
    """Receive raw input, validate, update slides.yaml, and run verbose build."""
    raw_input = ""

    if use_clipboard:
        log_info("Reading content from system clipboard...")
        raw_input = get_clipboard_content()
        if not raw_input:
            log_error("Clipboard is empty or clipboard tool (wl-paste/xclip) failed.")
            sys.exit(1)
    elif not sys.stdin.isatty():
        # Piped input
        raw_input = sys.stdin.read()
    else:
        print(f"\n{BOLD}{CYAN}══════════════════════════════════════════════════════════════════{RESET}")
        print(f" {BOLD}Paste your YAML or LLM response below.{RESET}")
        print(f" When finished, press {BOLD}[Ctrl+D]{RESET} on an empty line to build.")
        print(f"{BOLD}{CYAN}══════════════════════════════════════════════════════════════════{RESET}\n")
        try:
            raw_input = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nAborted.")
            sys.exit(0)

    if not raw_input.strip():
        log_error("No input provided. Aborting.")
        sys.exit(1)

    clean_yaml = extract_yaml_from_text(raw_input)
    is_valid, data, errors, warnings = validate_yaml_content(clean_yaml)

    # Print warnings
    for w in warnings:
        log_warn(w)

    # Handle errors
    if not is_valid:
        log_error("Pre-flight YAML validation failed:")
        for e in errors:
            print(f"  {RED}•{RESET} {e}")
        print("\nTip: Make sure backslashes in double-quotes are escaped, or use Typst math ($Delta$ instead of $\\Delta$).")
        sys.exit(1)

    # Backup existing slides.yaml
    slides_yaml_path = ROOT_DIR / "slides.yaml"
    bak_path = ROOT_DIR / "slides.yaml.bak"
    if slides_yaml_path.exists():
        shutil.copyfile(slides_yaml_path, bak_path)

    # Write new slides.yaml
    slides_yaml_path.write_text(clean_yaml)
    log_success("Updated slides.yaml successfully.")

    # Run build
    log_info("Compiling with Typst...")
    success, msg = compile_pdf()

    if success:
        log_success(msg)
        # Inspect page count
        try:
            res = subprocess.run(["pdfinfo", str(ROOT_DIR / "slides.pdf")], capture_output=True, text=True)
            for line in res.stdout.splitlines():
                if "Pages:" in line or "Page size:" in line:
                    print(f"  {CYAN}•{RESET} {line.strip()}")
        except Exception:
            pass
        print(f"\n{BOLD}{GREEN}✓ Presentation ready: {ROOT_DIR / 'slides.pdf'}{RESET}\n")
    else:
        log_error("Typst compilation failed!")
        print(f"\n{RED}{msg}{RESET}\n")
        if bak_path.exists():
            log_warn(f"Previous working copy preserved at: {bak_path}")
        sys.exit(1)

if __name__ == "__main__":
    use_clip = "--clipboard" in sys.argv or "-c" in sys.argv
    handle_paste(use_clipboard=use_clip)
