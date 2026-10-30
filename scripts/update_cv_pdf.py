"""Insert the latest work-in-progress entry into the website's two-page CV PDF."""
from pathlib import Path
import re
import shutil
import subprocess
import fitz

CV = Path("public/CV_Hao_Huang.pdf")
TITLE = (
    "Stigmatizing Yourself: Emotional Labor and Privacy Disclosure in "
    "China’s Higher Education Financial Assistance (with Yitong Hao)"
)

def unique_block(page, phrase):
    blocks = [b for b in page.get_text("blocks") if phrase.lower() in b[4].lower()]
    if len(blocks) != 1:
        raise RuntimeError(f"Expected one block matching {phrase!r}, found {len(blocks)}")
    return blocks[0]

def main():
    original = fitz.open(str(CV))
    if len(original) != 2:
        raise RuntimeError("Expected the existing two-page CV PDF")
    if any("Stigmatizing Yourself" in p.get_text() for p in original):
        print("Entry is already present; leaving PDF unchanged")
        return
    first = original[0]
    existing = unique_block(first, "AI Federalism 2.0")
    heading = unique_block(first, "TEACHING & RESEARCH EXPERIENCES")
    final = unique_block(first, "Teaching Assistant")
    width, height = first.rect.width, first.rect.height
    cutoff = heading[1] - 2
    offset = 28
    top = existing[3] + 6.5
    if not (580 < existing[1] < heading[1] < 720):
        raise RuntimeError("Unexpected CV layout; manual editing required")
    if final[3] + offset > height - 62 or top + 21 > heading[1] + offset - 6:
        raise RuntimeError("Insufficient space on page 1")

    result = fitz.open()
    page = result.new_page(width=width, height=height)
    page.show_pdf_page(fitz.Rect(0, 0, width, cutoff), original, 0,
                       clip=fitz.Rect(0, 0, width, cutoff))
    page.show_pdf_page(fitz.Rect(0, cutoff + offset, width, height), original, 0,
                       clip=fitz.Rect(0, cutoff, width, height - offset))

    font = (subprocess.check_output(["fc-match", "Liberation Serif", "-f", "%{file}"], text=True).strip()
            if shutil.which("fc-match") else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
    if not Path(font).is_file():
        raise RuntimeError("Unicode serif font not found")
    page.insert_font(fontname="CVUnicode", fontfile=font)
    overflow = page.insert_textbox(
        fitz.Rect(72, top, width - 72, top + 25), TITLE,
        fontname="CVUnicode", fontsize=8.97, lineheight=1.13)
    if overflow < 0:
        raise RuntimeError("New title does not fit")

    for link in first.get_links():
        if link.get("kind") == fitz.LINK_URI:
            rect = fitz.Rect(link["from"])
            if rect.y0 >= cutoff:
                rect = rect + (0, offset, 0, offset)
            page.insert_link({"kind": fitz.LINK_URI, "from": rect, "uri": link["uri"]})
    second = result.new_page(width=original[1].rect.width, height=original[1].rect.height)
    second.show_pdf_page(second.rect, original, 1)
    for link in original[1].get_links():
        if link.get("kind") == fitz.LINK_URI:
            second.insert_link({"kind": fitz.LINK_URI, "from": link["from"], "uri": link["uri"]})

    if TITLE not in re.sub(r"\s+", " ", result[0].get_text()):
        raise RuntimeError("New title was not preserved as searchable PDF text")
    staged = CV.with_suffix(".new.pdf")
    result.save(str(staged), garbage=4, deflate=True)
    result.close()
    original.close()
    staged.replace(CV)
    print(f"Updated CV PDF: {TITLE}")

if __name__ == "__main__":
    main()
