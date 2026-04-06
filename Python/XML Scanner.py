"""
Video Sitemap Tag Searcher
==========================
Reads Google Video Sitemap XML files, extracts each video's title,
page URL, direct file URL, category, and all tags, then writes the
results to a CSV. Parse errors are written to a configurable log file.
"""

import os
import csv
import logging
import importlib
ET = importlib.import_module('xml.etree.ElementTree')
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIG  –  edit these values before running
# ─────────────────────────────────────────────

# Folder containing your sitemap .xml files
XML_FOLDER = r"path/to/folder"

# Where the output CSV will be saved
OUTPUT_CSV = r"path/to/results.csv"

# Where errors and warnings are logged
LOG_FILE = r"path/to/error.log"

# Leave FILTER_TAGS empty ( [] ) to export ALL videos.
# Add strings to only include videos with at least one matching tag.
# e.g. FILTER_TAGS = ["Xbox", "MrBeast"]
FILTER_TAGS = [""]

# ─────────────────────────────────────────────
#  END OF CONFIG
# ─────────────────────────────────────────────

NS = {
    "sm":    "http://www.sitemaps.org/schemas/sitemap/0.9",
    "video": "http://www.google.com/schemas/sitemap-video/1.1",
}


def setup_logging(log_path: str) -> None:
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def tag_matches_filter(tags):
    if not FILTER_TAGS:
        return True
    lower_tags = [t.lower() for t in tags]
    for keyword in FILTER_TAGS:
        if any(keyword.lower() in t for t in lower_tags):
            return True
    return False


def cdata(element):
    return (element.text or "").strip()


def process_xml_file(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError as exc:
        logging.error("XML parse error in %s: %s", filepath, exc)
        return []
    except OSError as exc:
        logging.error("Cannot read %s: %s", filepath, exc)
        return []

    results = []
    filename = os.path.basename(filepath)

    for url_elem in root.findall("sm:url", NS):
        loc_elem = url_elem.find("sm:loc", NS)
        page_url = cdata(loc_elem) if loc_elem is not None else ""

        video_elem = url_elem.find("video:video", NS)
        if video_elem is None:
            logging.warning("No <video:video> in %s – skipped.", page_url)
            continue

        title_elem = video_elem.find("video:title", NS)
        title = cdata(title_elem) if title_elem is not None else "(no title)"

        content_elem = video_elem.find("video:content_loc", NS)
        content_url = cdata(content_elem) if content_elem is not None else ""

        cat_elem = video_elem.find("video:category", NS)
        category = cdata(cat_elem) if cat_elem is not None else ""

        tags = [cdata(t) for t in video_elem.findall("video:tag", NS) if cdata(t)]

        if not tag_matches_filter(tags):
            continue

        results.append({
            "source_file": filename,
            "title":       title,
            "page_url":    page_url,
            "content_url": content_url,
            "category":    category,
            "tags":        " | ".join(tags),
            "tag_count":   len(tags),
        })

    return results


def write_csv(rows, output_path):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fieldnames = ["source_file", "title", "page_url", "content_url", "category", "tags", "tag_count"]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    setup_logging(LOG_FILE)
    logging.info("=" * 60)
    logging.info("Sitemap Tag Searcher started – %s",
                 datetime.now().isoformat(sep=" ", timespec="seconds"))
    logging.info("XML folder : %s", XML_FOLDER)
    logging.info("Output CSV : %s", OUTPUT_CSV)
    logging.info("Tag filter : %s", ", ".join(FILTER_TAGS) if FILTER_TAGS else "(none)")
    logging.info("=" * 60)

    if not os.path.isdir(XML_FOLDER):
        logging.critical("XML_FOLDER does not exist: %s", XML_FOLDER)
        return

    xml_files = sorted(
        os.path.join(XML_FOLDER, f)
        for f in os.listdir(XML_FOLDER)
        if f.lower().endswith(".xml")
    )

    if not xml_files:
        logging.warning("No .xml files found in %s", XML_FOLDER)
        return

    logging.info("Found %d XML file(s) to process.", len(xml_files))

    all_rows = []
    file_errors = 0

    for i, filepath in enumerate(xml_files, start=1):
        fname = os.path.basename(filepath)
        logging.info("[%d/%d] %s", i, len(xml_files), fname)
        rows = process_xml_file(filepath)
        if rows:
            logging.info("  -> %d video(s) extracted.", len(rows))
            all_rows.extend(rows)
        else:
            file_errors += 1

    logging.info("-" * 60)
    logging.info("Files processed : %d", len(xml_files))
    logging.info("Total videos    : %d", len(all_rows))
    logging.info("File errors     : %d", file_errors)

    if all_rows:
        import re
        def page_number(row):
            m = re.search(r'(\d+)', row.get("source_file", ""))
            return int(m.group(1)) if m else 0
        all_rows.sort(key=page_number)
        if FILTER_TAGS:
            tag_name = "_".join(t.replace(" ", "-") for t in FILTER_TAGS)
            base, ext = os.path.splitext(OUTPUT_CSV)
            output_path = f"{base}_{tag_name}{ext}"
        else:
            output_path = OUTPUT_CSV
        write_csv(all_rows, output_path)
        logging.info("CSV written to  : %s", output_path)
    else:
        logging.warning("No rows to write – CSV not created.")

    logging.info("Done.")


if __name__ == "__main__":
    main()
