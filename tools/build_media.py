from __future__ import annotations

import os
import sys
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
MEDIA = ROOT / "media"
WIDTH, HEIGHT = 1920, 1080
FPS = 30

BG = "#0b1118"
PANEL = "#151e29"
WHITE = "#f3f7fb"
MUTED = "#a8b7c7"
BLUE = "#2ca7ff"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    path = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / name
    return ImageFont.truetype(str(path), size)


def centered(draw: ImageDraw.ImageDraw, text: str, y: int, face, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=face)
    draw.text(((WIDTH - (box[2] - box[0])) / 2, y), text, font=face, fill=fill)


def title_card() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((160, 170, WIDTH - 160, HEIGHT - 170), 24, fill=PANEL)
    centered(draw, "RBG CAN INSIGHT", 305, font(76, True), WHITE)
    centered(draw, "Offline CAN and diagnostic investigation for Windows", 420, font(38), MUTED)
    centered(draw, "DBC decoding  |  ISO-TP/UDS  |  Findings  |  ECU evidence", 515, font(30), BLUE)
    centered(draw, "Synthetic demonstration - no vehicle or company data", 650, font(26), MUTED)
    return image


def screenshot_card(filename: str, heading: str, detail: str, zoom: float) -> Image.Image:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((100, 45), heading, font=font(48, True), fill=WHITE)
    draw.text((102, 108), detail, font=font(27), fill=MUTED)

    source = Image.open(SCREENSHOTS / filename).convert("RGB")
    max_w, max_h = 1720, 850
    base = min(max_w / source.width, max_h / source.height)
    scale = base * zoom
    resized = source.resize((int(source.width * scale), int(source.height * scale)), Image.Resampling.LANCZOS)
    left = (WIDTH - resized.width) // 2
    top = 175 + (max_h - resized.height) // 2
    canvas.paste(resized, (left, top))
    draw.rounded_rectangle((left - 3, top - 3, left + resized.width + 3, top + resized.height + 3), 8, outline="#33475b", width=3)
    return canvas


def outro_card() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    centered(draw, "Analyze recorded CAN traffic locally", 300, font(58, True), WHITE)
    centered(draw, "Paid Windows app with a free trial", 420, font(34), MUTED)
    centered(draw, "apps.microsoft.com/detail/9NTZXFCKR81D", 545, font(34, True), BLUE)
    centered(draw, "Version 2.3.0", 650, font(28), MUTED)
    return image


def hold(writer, image: Image.Image, seconds: float) -> None:
    frame = np.asarray(image)
    for _ in range(round(seconds * FPS)):
        writer.append_data(frame)


def build_video() -> None:
    MEDIA.mkdir(exist_ok=True)
    output = MEDIA / "rbg-can-insight-offline-can-uds-demo.mp4"
    writer = imageio.get_writer(
        output,
        fps=FPS,
        codec="libx264",
        quality=8,
        pixelformat="yuv420p",
        macro_block_size=None,
    )
    try:
        hold(writer, title_card(), 5)
        slides = [
            ("offline-findings.png", "Prioritize recorded diagnostic findings", "Review severity, evidence and source frames without sending requests to an ECU."),
            ("diagnostic-sequence.png", "Reconstruct the diagnostic sequence", "Follow recorded sessions, reads, DTC checks and routines in chronological order."),
            ("uds-analysis.png", "Reconstruct recorded ISO-TP and UDS traffic", "Pair requests and responses, inspect DIDs, DTCs, routines and negative responses."),
            ("signal-plot.png", "Decode and plot physical signals", "Use DBC definitions, mixed-unit scales, zoom, cursors and frame navigation."),
            ("byte-matrix-details.png", "Inspect Byte Matrix evidence", "Open decoded signal details directly from the selected message row."),
            ("diagnostic-catalog-coverage.png", "Measure diagnostic catalog coverage", "Compare recorded services, DIDs, DTCs and routines with local CDD or ODX data."),
        ]
        for filename, heading, detail in slides:
            for step in range(8):
                hold(writer, screenshot_card(filename, heading, detail, 1.0 + step * 0.002), 1)
        hold(writer, outro_card(), 6)
    finally:
        writer.close()


def build_gallery_gif() -> None:
    cards = [title_card()]
    cards.extend(
        screenshot_card(name, heading, detail, 1.0)
        for name, heading, detail in [
            ("uds-analysis.png", "Recorded UDS evidence", "Offline reconstruction from imported frames."),
            ("offline-findings.png", "Diagnostic findings", "Prioritized evidence linked to recorded source frames."),
            ("diagnostic-sequence.png", "Diagnostic sequence", "Chronological reconstruction of recorded operations."),
            ("signal-plot.png", "Physical signal plotting", "Separate scales keep mixed units readable."),
            ("byte-matrix-details.png", "Byte Matrix details", "Decoded signals expand under the selected row."),
        ]
    )
    cards.append(outro_card())
    small = [card.resize((640, 360), Image.Resampling.LANCZOS) for card in cards]
    small[0].save(
        MEDIA / "rbg-can-insight-gallery.gif",
        save_all=True,
        append_images=small[1:],
        duration=1800,
        loop=0,
        optimize=True,
    )


def build_thumbnail() -> None:
    thumb = Image.new("RGB", (1280, 720), BG)
    draw = ImageDraw.Draw(thumb)
    draw.rounded_rectangle((60, 60, 1220, 660), 24, fill=PANEL)
    draw.text((110, 150), "OFFLINE CAN + UDS", font=font(68, True), fill=WHITE)
    draw.text((110, 245), "INVESTIGATION SUITE", font=font(68, True), fill=BLUE)
    draw.text((115, 390), "Findings  |  DBC  |  ISO-TP  |  ECU evidence", font=font(30), fill=MUTED)
    draw.text((115, 485), "RBG CAN INSIGHT", font=font(43, True), fill=WHITE)
    thumb.save(MEDIA / "youtube-thumbnail.png", optimize=True)


if __name__ == "__main__":
    build_video()
    build_gallery_gif()
    build_thumbnail()
    title_card().save(MEDIA / "video-title.png", optimize=True)
    outro_card().save(MEDIA / "video-outro.png", optimize=True)
    for path in sorted(MEDIA.iterdir()):
        print(f"{path.name}: {path.stat().st_size} bytes")
