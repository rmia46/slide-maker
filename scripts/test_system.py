#!/usr/bin/env python3
"""
Test suite covering all slide-maker components:
1. Strict checker error detection (syntax, type mismatch, missing required, unbalanced math)
2. Valid schema verification across all layouts
3. Typst PDF compilation pass
4. High-resolution PNG slide image generation
5. Native editable PowerPoint export
6. Zero-edit paste pipeline auto-sanitization
"""

import sys
import os
import shutil
import tempfile
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# ANSI
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

from checker import validate_yaml_string

def run_test(name, func):
    print(f"{CYAN}▶ Running test:{RESET} {BOLD}{name}{RESET}...", end=" ", flush=True)
    try:
        func()
        print(f"{GREEN}PASS ✓{RESET}")
        return True
    except Exception as e:
        print(f"{RED}FAIL ✗{RESET}")
        print(f"  {RED}{e}{RESET}")
        return False

def test_syntax_error_detection():
    bad_yaml = "meta:\n  theme: academic\nslides:\n  - title: Broken: [Unclosed list"
    is_valid, diags = validate_yaml_string(bad_yaml, ROOT_DIR, "syntax.yaml")
    assert not is_valid, "Should have failed syntax validation"
    assert any("syntax" in d.message.lower() for d in diags), "Should have flagged YAML syntax error"

def test_type_safety_bullets_str():
    bad_yaml = """meta:
  theme: academic
slides:
  - layout: content
    title: String instead of list
    bullets: "This should be a list, not a string"
"""
    is_valid, diags = validate_yaml_string(bad_yaml, ROOT_DIR, "type.yaml")
    assert not is_valid, "Should have caught type error"
    assert any("expected list" in d.message for d in diags), "Should specifically report 'expected list'"

def test_missing_required_field():
    bad_yaml = """meta:
  theme: academic
slides:
  - layout: code
    title: Missing code snippet
    language: python
"""
    is_valid, diags = validate_yaml_string(bad_yaml, ROOT_DIR, "req.yaml")
    assert not is_valid, "Should fail when required 'code' field is absent"
    assert any("Missing required field 'code'" in d.message for d in diags)

def test_unbalanced_typst_math():
    bad_yaml = """meta:
  theme: academic
slides:
  - layout: content
    title: Unbalanced Math $alpha
    bullets:
      - Normal bullet
"""
    is_valid, diags = validate_yaml_string(bad_yaml, ROOT_DIR, "math.yaml")
    assert not is_valid, "Should detect unbalanced dollar signs"
    assert any("Unbalanced math delimiter" in d.message for d in diags)

def test_all_layouts_valid_pass():
    deck_yaml = """meta:
  theme: academic
  palette: indigo
  title: All Layouts Test Deck
  faculty: CS Department
slides:
  - layout: title
    title: Full Layout Test
    subtitle: Automated Test Suite

  - layout: content
    category: TEST
    title: Content Slide
    bullets:
      - "Bullet one with math: $x + y = z$"
      - "Bullet two with bold **keyword**"
    callout: "Takeaway note here"

  - layout: split-diagram
    category: TEST
    title: Split Slide
    image: assets/recipe-analogy.svg
    bullets:
      - "Left text column bullet"

  - layout: diagram
    category: TEST
    title: Full Diagram Slide
    image: assets/compiler-pipeline.svg
    takeaway: "Architecture takeaway"

  - layout: comparison
    category: TEST
    title: Comparison Test
    left_title: Alpha
    left_bullets:
      - "Feature A"
    right_title: Beta
    right_bullets:
      - "Feature B"
    conclusion: "Synthesis test"

  - layout: stat-grid
    category: TEST
    title: Stats Test
    stats:
      - value: "99.9"
        unit: "%"
        label: "Availability"
    summary: "Reliability summary"

  - layout: code
    category: TEST
    title: Code Test
    language: python
    code: |
      def hello():
          return 42
    bullets:
      - "Function implementation"
"""
    is_valid, diags = validate_yaml_string(deck_yaml, ROOT_DIR, "all_layouts.yaml")
    errors = [d for d in diags if d.severity == "error"]
    assert is_valid, f"All layouts should pass validation, but got errors: {[e.message for e in errors]}"
    assert len(errors) == 0

def test_pdf_compilation():
    out_pdf = ROOT_DIR / "dist" / "test_output.pdf"
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    res = subprocess.run(["typst", "compile", "slides.typ", str(out_pdf)], cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"Typst compilation failed: {res.stderr}"
    assert out_pdf.exists() and out_pdf.stat().st_size > 50000, "Output PDF was not generated or too small"

def test_png_export():
    out_dir = ROOT_DIR / "dist" / "test_slides"
    out_dir.mkdir(parents=True, exist_ok=True)
    res = subprocess.run(["typst", "compile", "--format", "png", "slides.typ", str(out_dir / "slide-{n}.png")], cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"PNG export failed: {res.stderr}"
    pngs = list(out_dir.glob("slide-*.png"))
    assert len(pngs) == 40, f"Expected 40 PNG slides, found {len(pngs)}"

def test_pptx_export():
    out_pptx = ROOT_DIR / "dist" / "test_presentation.pptx"
    py_cmd = str(ROOT_DIR / ".venv" / "bin" / "python") if (ROOT_DIR / ".venv" / "bin" / "python").exists() else "python3"
    res = subprocess.run([py_cmd, "scripts/export_pptx.py", str(out_pptx)], cwd=ROOT_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"PPTX export failed: {res.stderr}"
    assert out_pptx.exists() and out_pptx.stat().st_size > 100000, "Output PPTX was not generated or too small"

def test_paste_fence_sanitizer():
    from builder import extract_yaml_from_text
    chat_response = """Here is your complete slide deck:

```yaml
meta:
  theme: academic
slides:
  - layout: title
    title: Sanitized Deck
```

Hope this helps! Let me know if you need edits.
"""
    clean = extract_yaml_from_text(chat_response)
    assert clean.startswith("meta:") and "theme: academic" in clean
    assert not clean.startswith("```") and not clean.endswith("```")
    assert "Hope this helps" not in clean

def main():
    print(f"\n{BOLD}{CYAN}===================================================={RESET}")
    print(f"{BOLD}{CYAN}   SLIDE-MAKER COMPREHENSIVE TEST SUITE{RESET}")
    print(f"{BOLD}{CYAN}===================================================={RESET}\n")

    tests = [
        ("YAML Syntax Error Detection", test_syntax_error_detection),
        ("Strict Type Safety (Bullets Type Check)", test_type_safety_bullets_str),
        ("Schema Required Field Verification", test_missing_required_field),
        ("Unbalanced Math Delimiter Detection", test_unbalanced_typst_math),
        ("All 7 Semantic Layouts Schema Pass", test_all_layouts_valid_pass),
        ("Markdown Code Fence & Chatter Stripping", test_paste_fence_sanitizer),
        ("Typst PDF Compilation (40 Slides)", test_pdf_compilation),
        ("Slide Image PNG Export (40 Pages)", test_png_export),
        ("Native Editable PPTX Export", test_pptx_export),
    ]

    passed = 0
    for name, func in tests:
        if run_test(name, func):
            passed += 1

    print(f"\n{BOLD}Results:{RESET} {passed}/{len(tests)} tests passed.")
    if passed == len(tests):
        print(f"{BOLD}{GREEN}✓ ALL SYSTEMS FUNCTIONAL & VERIFIED.{RESET}\n")
        sys.exit(0)
    else:
        print(f"{BOLD}{RED}✗ SOME TESTS FAILED.{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
