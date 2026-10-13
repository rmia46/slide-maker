#!/usr/bin/env python3
"""
Native editable PPTX exporter for slide-maker.
Preserves exact academic layouts, dimensions (16:9 widescreen), typography,
colors, callout blocks, code styling, and diagrams/images.
"""

import sys
import os
import re
import shutil
import tempfile
import subprocess
from pathlib import Path

import yaml
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# 16:9 Widescreen dimensions
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Academic Color Palettes
PALETTES = {
    "oxford": {
        "primary": RGBColor(15, 23, 42),
        "accent": RGBColor(30, 64, 175),
        "muted": RGBColor(71, 85, 105),
        "border": RGBColor(203, 213, 225),
        "bg": RGBColor(255, 255, 255),
    },
    "crimson": {
        "primary": RGBColor(26, 5, 5),
        "accent": RGBColor(153, 27, 27),
        "muted": RGBColor(87, 83, 78),
        "border": RGBColor(214, 211, 209),
        "bg": RGBColor(255, 255, 255),
    },
    "emerald": {
        "primary": RGBColor(2, 44, 34),
        "accent": RGBColor(6, 95, 70),
        "muted": RGBColor(71, 85, 105),
        "border": RGBColor(203, 213, 225),
        "bg": RGBColor(255, 255, 255),
    },
    "amber": {
        "primary": RGBColor(28, 25, 23),
        "accent": RGBColor(146, 64, 14),
        "muted": RGBColor(87, 83, 78),
        "border": RGBColor(214, 211, 209),
        "bg": RGBColor(255, 255, 255),
    },
    "slate": {
        "primary": RGBColor(15, 23, 42),
        "accent": RGBColor(51, 65, 85),
        "muted": RGBColor(100, 116, 139),
        "border": RGBColor(226, 232, 240),
        "bg": RGBColor(255, 255, 255),
    },
    "indigo": {
        "primary": RGBColor(15, 23, 42),
        "accent": RGBColor(67, 56, 202),
        "muted": RGBColor(71, 85, 105),
        "border": RGBColor(203, 213, 225),
        "bg": RGBColor(255, 255, 255),
    },
}

FONT_SERIF = "Georgia"
FONT_MONO = "Courier New"

def hex_to_rgb(hex_str: str) -> RGBColor:
    hex_str = hex_str.lstrip("#")
    return RGBColor(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

def get_colors(meta: dict) -> dict:
    pal_name = meta.get("palette", "crimson")
    base = PALETTES.get(pal_name, PALETTES["oxford"]).copy()
    custom = meta.get("colors", {})
    if "primary" in custom:
        base["primary"] = hex_to_rgb(custom["primary"])
    if "accent" in custom:
        base["accent"] = hex_to_rgb(custom["accent"])
    if "muted" in custom:
        base["muted"] = hex_to_rgb(custom["muted"])
    if "border" in custom:
        base["border"] = hex_to_rgb(custom["border"])
    return base

def parse_inline_formatting(text: str):
    """
    Parses **bold**, *italic*, and `code` into a list of tuples:
    (content, is_bold, is_italic, is_code)
    """
    if not text:
        return []
    
    # Clean latex math delimiters for editable text
    clean = re.sub(r"\$([^\$]+)\$", r"\1", str(text))
    # Replace common typst math symbols
    clean = clean.replace("\\Delta", "Δ").replace("\\alpha", "α").replace("\\beta", "β").replace("\\gamma", "γ")
    clean = clean.replace("->", "→").replace("=>", "⇒").replace("<=", "≤").replace(">=", "≥")

    # Simple tokenizer regex for **bold**, *italic*, `code`
    token_pattern = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")
    parts = token_pattern.split(clean)
    runs = []
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) >= 4:
            runs.append((part[2:-2], True, False, False))
        elif part.startswith("*") and part.endswith("*") and len(part) >= 2:
            runs.append((part[1:-1], False, True, False))
        elif part.startswith("`") and part.endswith("`") and len(part) >= 2:
            runs.append((part[1:-1], False, False, True))
        else:
            runs.append((part, False, False, False))
    return runs

def add_formatted_text(paragraph, text: str, default_font: str, default_size: Pt, default_color: RGBColor, default_bold=False, default_italic=False):
    runs = parse_inline_formatting(text)
    if not runs:
        return
    for content, is_bold, is_italic, is_code in runs:
        r = paragraph.add_run()
        r.text = content
        r.font.name = FONT_MONO if is_code else default_font
        r.font.size = default_size
        r.font.color.rgb = default_color
        r.font.bold = default_bold or is_bold
        r.font.italic = default_italic or is_italic

def prepare_image(img_path_str: str, project_root: Path, temp_dir: Path) -> str:
    """Resolve image path and convert SVG to PNG if necessary for python-pptx."""
    if not img_path_str:
        return None
    p = Path(img_path_str)
    if not p.is_absolute():
        p = project_root / p
    if not p.exists():
        return None
    
    # If SVG, rasterize to high-res PNG for PPTX compatibility
    if p.suffix.lower() == ".svg":
        png_out = temp_dir / f"{p.stem}_{os.urandom(4).hex()}.png"
        try:
            subprocess.run(["rsvg-convert", "-z", "2.0", str(p), "-o", str(png_out)], check=True, capture_output=True)
            return str(png_out)
        except Exception:
            try:
                subprocess.run(["inkscape", str(p), "--export-filename=" + str(png_out), "--export-dpi=192"], check=True, capture_output=True)
                return str(png_out)
            except Exception:
                return None
    return str(p)

class PPTXExporter:
    def __init__(self, root_dir: Path, yaml_path: Path):
        self.root_dir = root_dir
        self.yaml_path = yaml_path
        self.prs = Presentation()
        self.prs.slide_width = SLIDE_WIDTH
        self.prs.slide_height = SLIDE_HEIGHT
        self.blank_layout = self.prs.slide_layouts[6] # Blank
        self.temp_dir = Path(tempfile.mkdtemp(prefix="pptx_export_"))

    def cleanup(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def add_academic_decorations(self, slide_obj, meta: dict, colors: dict, page_num: int, total_pages: int):
        """Header & footer matching the exact Typst academic theme."""
        faculty = meta.get("faculty", "")
        title = meta.get("title", "")

        # Top Header
        header_box = slide_obj.shapes.add_textbox(Inches(0.86), Inches(0.40), Inches(11.61), Inches(0.4))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        
        # Left faculty, right title via tab or separate boxes
        p.text = faculty.upper()
        p.font.name = FONT_SERIF
        p.font.size = Pt(9.5)
        p.font.color.rgb = colors["muted"]
        p.font.bold = True

        r_box = slide_obj.shapes.add_textbox(Inches(6.0), Inches(0.40), Inches(6.47), Inches(0.4))
        rtf = r_box.text_frame
        rtf.margin_left = rtf.margin_top = rtf.margin_right = rtf.margin_bottom = 0
        rp = rtf.paragraphs[0]
        rp.alignment = PP_ALIGN.RIGHT
        rp.text = title
        rp.font.name = FONT_SERIF
        rp.font.size = Pt(9.5)
        rp.font.color.rgb = colors["muted"]

        # Top Thin Rule
        rule = slide_obj.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.86), Inches(0.72), Inches(11.61), Inches(0.01))
        rule.fill.solid()
        rule.fill.fore_color.rgb = colors["border"]
        rule.line.color.rgb = colors["border"]

        # Bottom Thin Rule
        b_rule = slide_obj.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.86), Inches(6.92), Inches(11.61), Inches(0.01))
        b_rule.fill.solid()
        b_rule.fill.fore_color.rgb = colors["border"]
        b_rule.line.color.rgb = colors["border"]

        # Footer text
        f_box = slide_obj.shapes.add_textbox(Inches(0.86), Inches(7.02), Inches(5.0), Inches(0.35))
        ftf = f_box.text_frame
        ftf.margin_left = ftf.margin_top = ftf.margin_right = ftf.margin_bottom = 0
        fp = ftf.paragraphs[0]
        fp.text = "Lecture Series"
        fp.font.name = FONT_SERIF
        fp.font.size = Pt(8.5)
        fp.font.italic = True
        fp.font.color.rgb = colors["muted"]

        # Slide Number
        n_box = slide_obj.shapes.add_textbox(Inches(10.0), Inches(7.02), Inches(2.47), Inches(0.35))
        ntf = n_box.text_frame
        ntf.margin_left = ntf.margin_top = ntf.margin_right = ntf.margin_bottom = 0
        np = ntf.paragraphs[0]
        np.alignment = PP_ALIGN.RIGHT
        np.text = f"{page_num}"
        np.font.name = FONT_SERIF
        np.font.size = Pt(9.5)
        np.font.bold = True
        np.font.color.rgb = colors["primary"]

    def add_slide_header(self, slide_obj, slide: dict, colors: dict) -> float:
        """Renders category, title, subtitle and red divider line. Returns bottom Y in Inches."""
        category = slide.get("category")
        title = slide.get("title", "Slide Title")
        subtitle = slide.get("subtitle")

        top_y = 0.88

        # Category
        if category:
            cat_box = slide_obj.shapes.add_textbox(Inches(0.86), Inches(top_y), Inches(11.61), Inches(0.28))
            ctf = cat_box.text_frame
            ctf.margin_left = ctf.margin_top = ctf.margin_right = ctf.margin_bottom = 0
            cp = ctf.paragraphs[0]
            cp.text = category.upper()
            cp.font.name = FONT_SERIF
            cp.font.size = Pt(9)
            cp.font.bold = True
            cp.font.color.rgb = colors["accent"]
            top_y += 0.28

        # Title
        t_box = slide_obj.shapes.add_textbox(Inches(0.86), Inches(top_y), Inches(11.61), Inches(0.55))
        ttf = t_box.text_frame
        ttf.word_wrap = True
        ttf.margin_left = ttf.margin_top = ttf.margin_right = ttf.margin_bottom = 0
        tp = ttf.paragraphs[0]
        tp.text = title
        tp.font.name = FONT_SERIF
        tp.font.size = Pt(22)
        tp.font.bold = True
        tp.font.color.rgb = colors["primary"]
        top_y += 0.52

        # Subtitle
        if subtitle:
            s_box = slide_obj.shapes.add_textbox(Inches(0.86), Inches(top_y), Inches(11.61), Inches(0.35))
            stf = s_box.text_frame
            stf.word_wrap = True
            stf.margin_left = stf.margin_top = stf.margin_right = stf.margin_bottom = 0
            sp = stf.paragraphs[0]
            sp.text = subtitle
            sp.font.name = FONT_SERIF
            sp.font.size = Pt(11.5)
            sp.font.color.rgb = colors["muted"]
            top_y += 0.35

        # Divider line
        div = slide_obj.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.86), Inches(top_y + 0.05), Inches(11.61), Inches(0.018))
        div.fill.solid()
        div.fill.fore_color.rgb = colors["accent"]
        div.line.color.rgb = colors["accent"]

        return top_y + 0.25

    def add_callout(self, slide_obj, text: str, colors: dict, top_y: float = 6.05, height: float = 0.72):
        """Adds standard key takeaway callout bar."""
        # Vertical left accent bar
        bar = slide_obj.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.86), Inches(top_y), Inches(0.04), Inches(height))
        bar.fill.solid()
        bar.fill.fore_color.rgb = colors["accent"]
        bar.line.color.rgb = colors["accent"]

        # Text container
        c_box = slide_obj.shapes.add_textbox(Inches(1.02), Inches(top_y + 0.02), Inches(11.45), Inches(height - 0.04))
        ctf = c_box.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_top = ctf.margin_right = ctf.margin_bottom = 0

        p1 = ctf.paragraphs[0]
        p1.text = "KEY TAKEAWAY"
        p1.font.name = FONT_SERIF
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = colors["accent"]

        p2 = ctf.add_paragraph()
        add_formatted_text(p2, text, FONT_SERIF, Pt(11.5), colors["primary"], default_italic=True)

    def render_title_slide(self, slide: dict, meta: dict, colors: dict):
        slide_obj = self.prs.slides.add_slide(self.blank_layout)
        title = slide.get("title", meta.get("title", "Lecture Title"))
        subtitle = slide.get("subtitle", meta.get("subtitle", ""))
        faculty = slide.get("faculty", meta.get("faculty", "Department of Computer Science"))
        presenter = slide.get("presenter", meta.get("presenter", ""))
        date = slide.get("date", meta.get("date", ""))

        y = 1.8

        if faculty:
            f_box = slide_obj.shapes.add_textbox(Inches(1.2), Inches(y), Inches(10.9), Inches(0.35))
            ftf = f_box.text_frame
            fp = ftf.paragraphs[0]
            fp.text = faculty.upper()
            fp.font.name = FONT_SERIF
            fp.font.size = Pt(11)
            fp.font.bold = True
            fp.font.color.rgb = colors["accent"]
            y += 0.45

        # Title
        t_box = slide_obj.shapes.add_textbox(Inches(1.2), Inches(y), Inches(10.9), Inches(1.2))
        ttf = t_box.text_frame
        ttf.word_wrap = True
        tp = ttf.paragraphs[0]
        tp.text = title
        tp.font.name = FONT_SERIF
        tp.font.size = Pt(32)
        tp.font.bold = True
        tp.font.color.rgb = colors["primary"]
        y += 1.3

        if subtitle:
            s_box = slide_obj.shapes.add_textbox(Inches(1.2), Inches(y), Inches(10.9), Inches(0.6))
            stf = s_box.text_frame
            stf.word_wrap = True
            sp = stf.paragraphs[0]
            sp.text = subtitle
            sp.font.name = FONT_SERIF
            sp.font.size = Pt(15)
            sp.font.color.rgb = colors["muted"]
            y += 0.8

        # Divider
        div = slide_obj.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(y), Inches(10.9), Inches(0.025))
        div.fill.solid()
        div.fill.fore_color.rgb = colors["accent"]
        div.line.color.rgb = colors["accent"]
        y += 0.35

        # Metadata columns
        if presenter:
            p_box = slide_obj.shapes.add_textbox(Inches(1.2), Inches(y), Inches(4.5), Inches(0.8))
            ptf = p_box.text_frame
            p1 = ptf.paragraphs[0]
            p1.text = "PRESENTER"
            p1.font.name = FONT_SERIF
            p1.font.size = Pt(9)
            p1.font.bold = True
            p1.font.color.rgb = colors["muted"]
            p2 = ptf.add_paragraph()
            p2.text = presenter
            p2.font.name = FONT_SERIF
            p2.font.size = Pt(13)
            p2.font.bold = True
            p2.font.color.rgb = colors["primary"]

        if date:
            d_box = slide_obj.shapes.add_textbox(Inches(5.0), Inches(y), Inches(4.5), Inches(0.8))
            dtf = d_box.text_frame
            d1 = dtf.paragraphs[0]
            d1.text = "DATE"
            d1.font.name = FONT_SERIF
            d1.font.size = Pt(9)
            d1.font.bold = True
            d1.font.color.rgb = colors["muted"]
            d2 = dtf.add_paragraph()
            d2.text = date
            d2.font.name = FONT_SERIF
            d2.font.size = Pt(13)
            d2.font.bold = True
            d2.font.color.rgb = colors["primary"]

    def render_content_slide(self, slide: dict, meta: dict, colors: dict, page_num: int, total_pages: int):
        slide_obj = self.prs.slides.add_slide(self.blank_layout)
        self.add_academic_decorations(slide_obj, meta, colors, page_num, total_pages)
        content_top = self.add_slide_header(slide_obj, slide, colors)

        bullets = slide.get("bullets", [])
        callout = slide.get("callout")

        # Bullet block
        b_box = slide_obj.shapes.add_textbox(Inches(0.86), Inches(content_top), Inches(11.61), Inches(3.8))
        btf = b_box.text_frame
        btf.word_wrap = True
        btf.margin_left = btf.margin_top = btf.margin_right = btf.margin_bottom = 0

        for i, b_text in enumerate(bullets):
            p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
            p.space_after = Pt(12)
            # Custom bullet point run
            bullet_run = p.add_run()
            bullet_run.text = "•  "
            bullet_run.font.name = FONT_SERIF
            bullet_run.font.size = Pt(13.5)
            bullet_run.font.bold = True
            bullet_run.font.color.rgb = colors["accent"]
            add_formatted_text(p, b_text, FONT_SERIF, Pt(13), colors["primary"])

        if callout:
            self.add_callout(slide_obj, callout, colors)

    def render_split_slide(self, slide: dict, meta: dict, colors: dict, page_num: int, total_pages: int):
        slide_obj = self.prs.slides.add_slide(self.blank_layout)
        self.add_academic_decorations(slide_obj, meta, colors, page_num, total_pages)
        content_top = self.add_slide_header(slide_obj, slide, colors)

        img_pos = slide.get("image_position", "right")
        img_raw = slide.get("image")
        caption = slide.get("caption")
        bullets = slide.get("bullets", [])

        # Dimensions: 50/50 split
        col_width = Inches(5.45)
        gutter = Inches(0.7)
        left_x = Inches(0.86)
        right_x = left_x + col_width + gutter

        text_x = left_x if img_pos == "right" else right_x
        img_x = right_x if img_pos == "right" else left_x

        # Text Column
        b_box = slide_obj.shapes.add_textbox(text_x, Inches(content_top), col_width, Inches(4.3))
        btf = b_box.text_frame
        btf.word_wrap = True
        btf.margin_left = btf.margin_top = btf.margin_right = btf.margin_bottom = 0

        for i, b_text in enumerate(bullets):
            p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
            p.space_after = Pt(11)
            bullet_run = p.add_run()
            bullet_run.text = "•  "
            bullet_run.font.name = FONT_SERIF
            bullet_run.font.size = Pt(13)
            bullet_run.font.bold = True
            bullet_run.font.color.rgb = colors["accent"]
            add_formatted_text(p, b_text, FONT_SERIF, Pt(12.5), colors["primary"])

        # Image Column
        resolved_img = prepare_image(img_raw, self.root_dir, self.temp_dir)
        if resolved_img:
            # Place image centered vertically
            slide_obj.shapes.add_picture(resolved_img, img_x, Inches(content_top), width=col_width)
            if caption:
                c_box = slide_obj.shapes.add_textbox(img_x, Inches(content_top + 4.1), col_width, Inches(0.4))
                ctf = c_box.text_frame
                ctf.word_wrap = True
                cp = ctf.paragraphs[0]
                cp.alignment = PP_ALIGN.CENTER
                cp.text = caption
                cp.font.name = FONT_SERIF
                cp.font.size = Pt(9.5)
                cp.font.italic = True
                cp.font.color.rgb = colors["muted"]

        callout = slide.get("callout")
        if callout:
            self.add_callout(slide_obj, callout, colors, top_y=6.15, height=0.65)

    def render_diagram_slide(self, slide: dict, meta: dict, colors: dict, page_num: int, total_pages: int):
        slide_obj = self.prs.slides.add_slide(self.blank_layout)
        self.add_academic_decorations(slide_obj, meta, colors, page_num, total_pages)
        content_top = self.add_slide_header(slide_obj, slide, colors)

        img_raw = slide.get("image")
        caption = slide.get("caption")
        takeaway = slide.get("takeaway", slide.get("callout"))

        resolved_img = prepare_image(img_raw, self.root_dir, self.temp_dir)
        if resolved_img:
            slide_obj.shapes.add_picture(resolved_img, Inches(1.8), Inches(content_top), width=Inches(9.7))
            if caption:
                c_box = slide_obj.shapes.add_textbox(Inches(1.8), Inches(content_top + 4.1), Inches(9.7), Inches(0.35))
                ctf = c_box.text_frame
                ctf.word_wrap = True
                cp = ctf.paragraphs[0]
                cp.alignment = PP_ALIGN.CENTER
                cp.text = caption
                cp.font.name = FONT_SERIF
                cp.font.size = Pt(9.5)
                cp.font.italic = True
                cp.font.color.rgb = colors["muted"]

        if takeaway:
            self.add_callout(slide_obj, takeaway, colors, top_y=6.15, height=0.65)

    def render_comparison_slide(self, slide: dict, meta: dict, colors: dict, page_num: int, total_pages: int):
        slide_obj = self.prs.slides.add_slide(self.blank_layout)
        self.add_academic_decorations(slide_obj, meta, colors, page_num, total_pages)
        content_top = self.add_slide_header(slide_obj, slide, colors)

        col_w = Inches(5.5)
        gutter = Inches(0.6)
        c1_x = Inches(0.86)
        c2_x = c1_x + col_w + gutter

        left_title = slide.get("left_title", "Option A")
        right_title = slide.get("right_title", "Option B")
        left_bullets = slide.get("left_bullets", [])
        right_bullets = slide.get("right_bullets", [])

        # Column 1 Header
        c1_box = slide_obj.shapes.add_textbox(c1_x, Inches(content_top), col_w, Inches(0.4))
        c1_p = c1_box.text_frame.paragraphs[0]
        c1_p.text = left_title
        c1_p.font.name = FONT_SERIF
        c1_p.font.size = Pt(14)
        c1_p.font.bold = True
        c1_p.font.color.rgb = colors["primary"]

        div1 = slide_obj.shapes.add_shape(MSO_SHAPE.RECTANGLE, c1_x, Inches(content_top + 0.38), col_w, Inches(0.02))
        div1.fill.solid()
        div1.fill.fore_color.rgb = colors["accent"]
        div1.line.color.rgb = colors["accent"]

        # Column 1 Bullets
        b1_box = slide_obj.shapes.add_textbox(c1_x, Inches(content_top + 0.45), col_w, Inches(3.6))
        b1_tf = b1_box.text_frame
        b1_tf.word_wrap = True
        for i, b_text in enumerate(left_bullets):
            p = b1_tf.paragraphs[0] if i == 0 else b1_tf.add_paragraph()
            p.space_after = Pt(8)
            br = p.add_run()
            br.text = "•  "
            br.font.size = Pt(12)
            br.font.bold = True
            br.font.color.rgb = colors["accent"]
            add_formatted_text(p, b_text, FONT_SERIF, Pt(12), colors["primary"])

        # Column 2 Header
        c2_box = slide_obj.shapes.add_textbox(c2_x, Inches(content_top), col_w, Inches(0.4))
        c2_p = c2_box.text_frame.paragraphs[0]
        c2_p.text = right_title
        c2_p.font.name = FONT_SERIF
        c2_p.font.size = Pt(14)
        c2_p.font.bold = True
        c2_p.font.color.rgb = colors["primary"]

        div2 = slide_obj.shapes.add_shape(MSO_SHAPE.RECTANGLE, c2_x, Inches(content_top + 0.38), col_w, Inches(0.02))
        div2.fill.solid()
        div2.fill.fore_color.rgb = colors["accent"]
        div2.line.color.rgb = colors["accent"]

        # Column 2 Bullets
        b2_box = slide_obj.shapes.add_textbox(c2_x, Inches(content_top + 0.45), col_w, Inches(3.6))
        b2_tf = b2_box.text_frame
        b2_tf.word_wrap = True
        for i, b_text in enumerate(right_bullets):
            p = b2_tf.paragraphs[0] if i == 0 else b2_tf.add_paragraph()
            p.space_after = Pt(8)
            br = p.add_run()
            br.text = "•  "
            br.font.size = Pt(12)
            br.font.bold = True
            br.font.color.rgb = colors["accent"]
            add_formatted_text(p, b_text, FONT_SERIF, Pt(12), colors["primary"])

        conclusion = slide.get("conclusion")
        if conclusion:
            self.add_callout(slide_obj, conclusion, colors, top_y=6.15, height=0.65)

    def render_stat_grid_slide(self, slide: dict, meta: dict, colors: dict, page_num: int, total_pages: int):
        slide_obj = self.prs.slides.add_slide(self.blank_layout)
        self.add_academic_decorations(slide_obj, meta, colors, page_num, total_pages)
        content_top = self.add_slide_header(slide_obj, slide, colors)

        stats = slide.get("stats", [])
        if not stats:
            return

        cols = len(stats)
        gutter = 0.5
        total_w = 11.61
        col_w = (total_w - (cols - 1) * gutter) / cols

        for idx, s in enumerate(stats):
            x = 0.86 + idx * (col_w + gutter)
            box = slide_obj.shapes.add_textbox(Inches(x), Inches(content_top + 0.5), Inches(col_w), Inches(2.8))
            tf = box.text_frame
            tf.word_wrap = True

            p1 = tf.paragraphs[0]
            r1 = p1.add_run()
            r1.text = str(s.get("value", "0"))
            r1.font.name = FONT_SERIF
            r1.font.size = Pt(36)
            r1.font.bold = True
            r1.font.color.rgb = colors["accent"]

            if "unit" in s:
                r1_unit = p1.add_run()
                r1_unit.text = f" {s['unit']}"
                r1_unit.font.name = FONT_SERIF
                r1_unit.font.size = Pt(15)
                r1_unit.font.bold = True
                r1_unit.font.color.rgb = colors["muted"]

            p2 = tf.add_paragraph()
            p2.space_before = Pt(6)
            p2.text = s.get("label", "")
            p2.font.name = FONT_SERIF
            p2.font.size = Pt(13)
            p2.font.bold = True
            p2.font.color.rgb = colors["primary"]

            if "description" in s:
                p3 = tf.add_paragraph()
                p3.space_before = Pt(4)
                p3.text = s["description"]
                p3.font.name = FONT_SERIF
                p3.font.size = Pt(10)
                p3.font.color.rgb = colors["muted"]

        summary = slide.get("summary")
        if summary:
            self.add_callout(slide_obj, summary, colors, top_y=6.15, height=0.65)

    def render_code_slide(self, slide: dict, meta: dict, colors: dict, page_num: int, total_pages: int):
        slide_obj = self.prs.slides.add_slide(self.blank_layout)
        self.add_academic_decorations(slide_obj, meta, colors, page_num, total_pages)
        content_top = self.add_slide_header(slide_obj, slide, colors)

        code_text = slide.get("code", "").strip()
        bullets = slide.get("bullets", [])

        code_w = Inches(6.8)
        bullets_w = Inches(4.5)
        gutter = Inches(0.3)
        code_x = Inches(0.86)
        bullets_x = code_x + code_w + gutter

        # Dark code container card
        code_bg = slide_obj.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, code_x, Inches(content_top), code_w, Inches(4.3))
        code_bg.fill.solid()
        code_bg.fill.fore_color.rgb = RGBColor(30, 41, 59) # Slate 800
        code_bg.line.color.rgb = RGBColor(51, 65, 85)

        # Monospace code text
        lines = code_text.splitlines()
        code_font_size = Pt(11) if len(lines) <= 12 else (Pt(9.5) if len(lines) <= 18 else Pt(8.5))

        code_box = slide_obj.shapes.add_textbox(code_x + Inches(0.15), Inches(content_top + 0.12), code_w - Inches(0.3), Inches(4.0))
        ctf = code_box.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_top = ctf.margin_right = ctf.margin_bottom = 0
        for idx, line in enumerate(lines):
            p = ctf.paragraphs[0] if idx == 0 else ctf.add_paragraph()
            p.text = line
            p.font.name = FONT_MONO
            p.font.size = code_font_size
            p.font.color.rgb = RGBColor(248, 250, 252)

        # Bullets explaining code
        b_box = slide_obj.shapes.add_textbox(bullets_x, Inches(content_top), bullets_w, Inches(4.3))
        btf = b_box.text_frame
        btf.word_wrap = True
        btf.margin_left = btf.margin_top = btf.margin_right = btf.margin_bottom = 0

        for i, b_text in enumerate(bullets):
            p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
            p.space_after = Pt(10)
            br = p.add_run()
            br.text = "•  "
            br.font.size = Pt(12)
            br.font.bold = True
            br.font.color.rgb = colors["accent"]
            add_formatted_text(p, b_text, FONT_SERIF, Pt(12), colors["primary"])

    def export(self, output_pptx_path: Path):
        with open(self.yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        meta = data.get("meta", {})
        colors = get_colors(meta)
        slides = data.get("slides", [])
        total_pages = len(slides)

        for idx, s in enumerate(slides, start=1):
            layout = s.get("layout", s.get("type", "content"))
            if layout == "title":
                self.render_title_slide(s, meta, colors)
            elif layout in ("split-diagram", "split-image", "split"):
                self.render_split_slide(s, meta, colors, idx, total_pages)
            elif layout in ("diagram", "image", "full_diagram"):
                self.render_diagram_slide(s, meta, colors, idx, total_pages)
            elif layout == "comparison":
                self.render_comparison_slide(s, meta, colors, idx, total_pages)
            elif layout == "stat-grid":
                self.render_stat_grid_slide(s, meta, colors, idx, total_pages)
            elif layout == "code":
                self.render_code_slide(s, meta, colors, idx, total_pages)
            else:
                self.render_content_slide(s, meta, colors, idx, total_pages)

        self.prs.save(str(output_pptx_path))
        self.cleanup()

def main():
    root = Path(__file__).resolve().parent.parent
    yaml_path = root / "slides.yaml"
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "slides.pptx"

    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"⚡ Exporting editable PPTX -> {out_path}...")
    exporter = PPTXExporter(root, yaml_path)
    exporter.export(out_path)
    print(f"✓ Created {out_path} ({os.path.getsize(out_path) // 1024} KB)")

if __name__ == "__main__":
    main()
