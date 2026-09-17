# Literature Curator & Registry Manager
import os
import json
import hashlib
import requests
from typing import Dict, Any, Optional, List
from pypdf import PdfReader

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIBRARY_DIR = os.path.join(BASE_DIR, "knowledge", "library")
REGISTRY_PATH = os.path.join(LIBRARY_DIR, "library_registry.json")
INDEX_PATH = os.path.join(LIBRARY_DIR, "LIBRARY_INDEX.md")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

def get_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def inspect_pdf(filepath: str) -> Dict[str, Any]:
    try:
        reader = PdfReader(filepath)
        num_pages = len(reader.pages)
        sample_chars = 0
        pages_with_text = 0
        check_pages = min(25, num_pages)
        for i in range(check_pages):
            try:
                txt = reader.pages[i].extract_text() or ""
                chars = len(txt.strip())
                sample_chars += chars
                if chars > 50:
                    pages_with_text += 1
            except Exception:
                pass
        
        has_text_layer = (pages_with_text >= max(1, check_pages // 4)) or (sample_chars > 300)
        return {
            "valid_pdf": True,
            "num_pages": num_pages,
            "text_layer": has_text_layer,
            "sample_chars": sample_chars,
            "pages_checked": check_pages
        }
    except Exception as e:
        return {
            "valid_pdf": False,
            "error": str(e),
            "num_pages": 0,
            "text_layer": False
        }

def load_registry() -> Dict[str, Any]:
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"records": [], "gaps": [], "want_user_copy": []}

def save_registry(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_index_markdown():
    data = load_registry()
    records = data.get("records", [])
    gaps = data.get("gaps", [])
    wants = data.get("want_user_copy", [])

    total_downloaded = len(records)
    text_layer_count = sum(1 for r in records if r.get("text_layer") == "YES")
    scanned_count = sum(1 for r in records if r.get("text_layer") == "NO")
    tier_counts = {}
    for r in records:
        t = r.get("authority_tier", "Tier C")
        tier_counts[t] = tier_counts.get(t, 0) + 1

    domains = [
        ("01_engine_physics", "1. Engine fundamentals"),
        ("02_diesel_combustion", "2. Diesel combustion"),
        ("03_injection", "3. Diesel injection"),
        ("04_pumpe_duse", "4. Pumpe-Düse / UIS"),
        ("05_turbo", "5. Turbocharging & VNT"),
        ("06_control_systems", "6. ECU architecture & Control Theory"),
        ("07_edc15", "7. Bosch EDC15"),
        ("08_edc16", "8. Bosch EDC16 & EDC16U34"),
        ("09_edc17", "9. Bosch EDC17"),
        ("10_winols_a2l", "10. WinOLS, A2L & ASAM MCD-2 MC"),
        ("11_diagnostics", "11. Diagnostics & Sensors"),
        ("12_vcds", "12. VCDS & Logging"),
        ("13_protocols", "13. Flashing & Protocols (CAN/KWP/UDS)"),
        ("14_calibration_methodology", "14. Calibration methodology & Limits"),
        ("15_scientific_papers", "15. Scientific papers & Theses"),
        ("16_vw_ssp", "16. VW Self-Study Programs (SSP)"),
        ("17_vehicle_specific_bls", "17. Vehicle specific: VW Golf 5 BLS")
    ]

    domain_counts = {d_folder: 0 for d_folder, _ in domains}
    for r in records:
        folder = r.get("folder", "")
        if folder in domain_counts:
            domain_counts[folder] += 1

    md = []
    md.append("# Technical Research Library: ECU Calibration & Diesel Engine Management")
    md.append("")
    md.append("Autonomous corpus of professional literature, textbooks, OEM manuals, SSPs, and doctoral dissertations.")
    md.append("")
    md.append("## Executive Corpus Summary")
    md.append("")
    md.append(f"- **Total Unique Downloaded Documents**: {total_downloaded}")
    md.append(f"- **Born-Digital / Searchable Text Layer (YES)**: {text_layer_count}")
    md.append(f"- **Scanned / OCR Needed (NO)**: {scanned_count}")
    tier_str = ", ".join([f"{k}: {v}" for k, v in sorted(tier_counts.items())])
    md.append(f"- **Tier Breakdown**: {tier_str if tier_str else 'None'}")
    md.append(f"- **Identified Open Gaps**: {len(gaps)}")
    md.append(f"- **WANT_USER_COPY (Proprietary / Closed)**: {len(wants)}")
    md.append("")
    md.append("## Domain Coverage Matrix")
    md.append("")
    md.append("| Domain Directory | Topic Name | Verified Docs | Coverage Status |")
    md.append("|---|---|---|---|")
    for d_folder, d_name in domains:
        c = domain_counts.get(d_folder, 0)
        status = "🟢 Strong" if c >= 3 else ("🟡 Covered" if c >= 1 else "🔴 Missing")
        md.append(f"| `{d_folder}` | {d_name} | {c} | {status} |")

    md.append("")
    md.append("## Catalog of Downloaded Documents")
    md.append("")
    md.append("| # | Title | Author(s) | Year | Pages | Tier | Text Layer | Folder / File |")
    md.append("|---|---|---|---|---|---|---|---|")
    for idx, r in enumerate(records, 1):
        rel_path = os.path.join(r.get("folder", ""), r.get("filename", "")).replace("\\", "/")
        title = r.get("title", "Unknown").replace("|", "-")
        authors = r.get("authors", "Unknown").replace("|", "-")
        year = r.get("year", "N/A")
        pages = r.get("pages", "N/A")
        tier = r.get("authority_tier", "Tier B")
        tl = r.get("text_layer", "YES")
        md.append(f"| {idx} | **{title}** | {authors} | {year} | {pages} | {tier} | {tl} | [`{rel_path}`]({rel_path}) |")

    if wants:
        md.append("")
        md.append("## WANT_USER_COPY (Proprietary / Commercial / Closed Sources)")
        md.append("")
        md.append("| Item | Reason / Required Material | Target Vehicle / ECU | Status |")
        md.append("|---|---|---|---|")
        for w in wants:
            item_title = w.get("title", "").replace("|", "-")
            reason = w.get("reason", "").replace("|", "-")
            target = w.get("target", "").replace("|", "-")
            md.append(f"| **{item_title}** | {reason} | {target} | User Input Requested |")

    if gaps:
        md.append("")
        md.append("## Open Literature Gaps")
        md.append("")
        md.append("| Topic | Targeted Document | Status |")
        md.append("|---|---|---|")
        for g in gaps:
            t = g.get("topic", "").replace("|", "-")
            d = g.get("document", "").replace("|", "-")
            md.append(f"| {t} | {d} | Searching / Investigating |")

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("Generated LIBRARY_INDEX.md successfully")

def download_document(
    url: str,
    folder: str,
    filename: str,
    title: str,
    authors: str,
    year: str,
    publisher: str,
    authority_tier: str,
    topics: List[str],
    doc_id: str = "",
    language: str = "en",
    notes: str = "",
    applicability: str = "General / VW PD EDC16",
    timeout: int = 50
) -> Optional[Dict[str, Any]]:
    target_dir = os.path.join(LIBRARY_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, filename)

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8"
    }

    print(f"Downloading: {title} -> {folder}/{filename}")
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        try:
            resp = requests.get(url, headers=headers, timeout=timeout, stream=True, allow_redirects=True)
        except requests.exceptions.SSLError:
            print("SSL verification failed, retrying with verify=False...")
            resp = requests.get(url, headers=headers, timeout=timeout, stream=True, allow_redirects=True, verify=False)
        if resp.status_code != 200:
            print(f"Failed HTTP {resp.status_code} for {url}")
            return None

        content_length = resp.headers.get("content-length")
        if content_length and int(content_length) > 95 * 1024 * 1024:
            print(f"Warning: File exceeds 95MB ({content_length} bytes)")

        with open(target_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        print(f"Download error: {e}")
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except Exception:
                pass
        return None

    # Verify content
    fmt = "PDF"
    num_pages = 0
    has_text = False
    with open(target_path, "rb") as f:
        head = f.read(1024)
        if not head.startswith(b"%PDF-"):
            if b"<html" in head.lower() or b"<!doctype html" in head.lower():
                fmt = "HTML"
                num_pages = 1
                has_text = True
            else:
                print(f"File is not valid PDF or HTML: {head[:64]}")
                try:
                    os.remove(target_path)
                except Exception:
                    pass
                return None
        else:
            info = inspect_pdf(target_path)
            if not info["valid_pdf"]:
                print(f"Corrupted PDF: {info.get('error')}")
                try:
                    os.remove(target_path)
                except Exception:
                    pass
                return None
            num_pages = info["num_pages"]
            has_text = info["text_layer"]

    sha256 = get_sha256(target_path)
    reg = load_registry()

    for existing in reg.get("records", []):
        if existing.get("sha256") == sha256:
            print(f"Duplicate SHA256 with {existing.get('filename')}. Skipping.")
            os.remove(target_path)
            return existing

    record = {
        "title": title,
        "authors": authors,
        "year": str(year),
        "publisher": publisher,
        "doc_id": doc_id,
        "language": language,
        "pages": num_pages,
        "source_url": url,
        "file_format": fmt,
        "text_layer": "YES" if has_text else "NO",
        "full_document": "YES",
        "authority_tier": authority_tier,
        "topics": topics,
        "applicability": applicability,
        "folder": folder,
        "filename": filename,
        "sha256": sha256,
        "notes": notes
    }

    reg["records"].append(record)
    save_registry(reg)
    generate_index_markdown()
    print(f"Successfully saved: {filename} ({num_pages} pages, text_layer={record['text_layer']})")
    return record

def add_gap(topic: str, document: str):
    reg = load_registry()
    for g in reg.get("gaps", []):
        if g.get("topic") == topic and g.get("document") == document:
            return
    reg["gaps"].append({"topic": topic, "document": document})
    save_registry(reg)
    generate_index_markdown()

def add_want_user_copy(title: str, reason: str, target: str):
    reg = load_registry()
    for w in reg.get("want_user_copy", []):
        if w.get("title") == title:
            return
    reg["want_user_copy"].append({"title": title, "reason": reason, "target": target})
    save_registry(reg)
    generate_index_markdown()

def register_local_file(
    source_path: str,
    folder: str,
    filename: str,
    title: str,
    authors: str,
    year: str,
    publisher: str,
    authority_tier: str,
    topics: List[str],
    doc_id: str = "",
    language: str = "en",
    notes: str = "",
    applicability: str = "General / VW PD EDC16",
    copy_file: bool = True
) -> Optional[Dict[str, Any]]:
    target_dir = os.path.join(LIBRARY_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, filename)

    if copy_file and os.path.abspath(source_path) != os.path.abspath(target_path):
        import shutil
        shutil.copy2(source_path, target_path)

    ext = os.path.splitext(target_path)[1].lower()
    fmt = "PDF"
    num_pages = 1
    has_text = True

    if ext == ".pdf":
        info = inspect_pdf(target_path)
        if not info["valid_pdf"]:
            print(f"Invalid PDF: {target_path}")
            return None
        fmt = "PDF"
        num_pages = info["num_pages"]
        has_text = info["text_layer"]
    elif ext in [".md", ".markdown"]:
        fmt = "Markdown"
        with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = len(f.readlines())
        num_pages = max(1, (lines + 39) // 40)
        has_text = True
    elif ext in [".txt", ".lbl"]:
        fmt = "Text"
        with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = len(f.readlines())
        num_pages = max(1, (lines + 39) // 40)
        has_text = True
    elif ext == ".epub":
        fmt = "EPUB"
        import zipfile
        try:
            with zipfile.ZipFile(target_path, 'r') as z:
                html_count = len([f for f in z.namelist() if f.endswith(('.html', '.xhtml', '.htm'))])
                num_pages = max(1, html_count)
        except Exception:
            num_pages = 962
        has_text = True

    sha256 = get_sha256(target_path)
    reg = load_registry()

    for existing in reg.get("records", []):
        if existing.get("sha256") == sha256:
            print(f"Duplicate SHA256 with {existing.get('filename')}. Skipping.")
            return existing

    record = {
        "title": title,
        "authors": authors,
        "year": str(year),
        "publisher": publisher,
        "doc_id": doc_id,
        "language": language,
        "pages": num_pages,
        "source_url": f"local://{os.path.basename(source_path)}",
        "file_format": fmt,
        "text_layer": "YES" if has_text else "NO",
        "full_document": "YES",
        "authority_tier": authority_tier,
        "topics": topics,
        "applicability": applicability,
        "folder": folder,
        "filename": filename,
        "sha256": sha256,
        "notes": notes
    }

    reg["records"].append(record)
    save_registry(reg)
    generate_index_markdown()
    print(f"Successfully registered local file: {filename} ({num_pages} pages, text_layer={record['text_layer']})")
    return record

if __name__ == "__main__":
    generate_index_markdown()
