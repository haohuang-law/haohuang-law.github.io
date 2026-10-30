"""Insert a work in progress into the existing two-page CV without clipping."""
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

def unique_block(page, text):
    found = [b for b in page.get_text("blocks") if text.lower() in b[4].lower()]
    if len(found) != 1:
        raise RuntimeError(f"Cannot uniquely locate {text!r}: {len(found)} matches")
    return found[0]

def main():
    original = fitz.open(str(CV))
    if len(original) != 2:
        raise RuntimeError("Expected existing two-page PDF")
    if any("Stigmatizing Yourself" in pg.get_text() for pg in original):
        print("New title already present")
        return

    first, last = original[0], original[1]
    ai = unique_block(first, "AI Federalism 2.0")
    teaching = unique_block(first, "TEACHING & RESEARCH EXPERIENCES")
    last_teaching = unique_block(first, "Teaching Assistant")
    width, height = first.rect.width, first.rect.height
    cut = teaching[1] - 2
    teach_bottom = last_teaching[3] + 5
    if not 580 < ai[1] < teaching[1] < 740 or teach_bottom > height - 30:
        raise RuntimeError("Unexpected CV layout")
    new_top = ai[3] + 6.5
    if new_top + 25 > height - 72:
        raise RuntimeError("New title would exceed page 1")

    output = fitz.open()
    p1 = output.new_page(width=width, height=height)
    p1.show_pdf_page(fitz.Rect(0, 0, width, cut), original, 0,
                     clip=fitz.Rect(0, 0, width, cut))
    font = (subprocess.check_output(["fc-match", "Liberation Serif", "-f", "%{file}"], text=True).strip()
            if shutil.which("fc-match") else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
    if not Path(font).is_file():
        raise RuntimeError("Unicode serif font unavailable")
    p1.insert_font(fontname="CVUnicode", fontfile=font)
    rem = p1.insert_textbox(fitz.Rect(72, new_top, width - 72, new_top + 25),
                            TITLE, fontname="CVUnicode", fontsize=8.97,
                            lineheight=1.13)
    if rem < 0:
        raise RuntimeError("WIP entry does not fit on page 1")

    p2 = output.new_page(width=width, height=height)
    move_to = 72.0
    section_height = teach_bottom - cut
    p2.show_pdf_page(fitz.Rect(0, move_to, width, move_to + section_height),
                     original, 0, clip=fitz.Rect(0, cut, width, teach_bottom))
    shift = section_height + 21
    p2.show_pdf_page(fitz.Rect(0, shift, width, height),
                     original, 1, clip=fitz.Rect(0, 0, width, height - shift))

    # Reload page objects after new_page to avoid invalidated PyMuPDF references.
    p1, p2 = output[0], output[1]
    for link in first.get_links():
        if link.get("kind") != fitz.LINK_URI:
            continue
        rect = fitz.Rect(link["from"])
        if rect.y0 < cut:
            p1.insert_link({"kind": fitz.LINK_URI, "from": rect, "uri": link["uri"]})
        else:
            rect = rect + (0, move_to - cut, 0, move_to - cut)
            p2.insert_link({"kind": fitz.LINK_URI, "from": rect, "uri": link["uri"]})
    for link in last.get_links():
        if link.get("kind") == fitz.LINK_URI:
            rect = fitz.Rect(link["from"]) + (0, shift, 0, shift)
            p2.insert_link({"kind": fitz.LINK_URI, "from": rect, "uri": link["uri"]})

    if TITLE not in re.sub(r"\s+", " ", output[0].get_text()):
        raise RuntimeError("New WIP not searchable")
    for required in ["TEACHING & RESEARCH EXPERIENCES", "PROFESSIONAL EXPERIENCE"]:
        if required not in output[1].get_text():
            raise RuntimeError("Original CV section was lost: " + required)
    temp = CV.with_suffix(".new.pdf")
    output.save(str(temp), garbage=4, deflate=True)
    output.close()
    original.close()
    temp.replace(CV)
    print("Updated the two-page CV PDF with the new Works in Progress entry")

if __name__ == "__main__":
    main()
