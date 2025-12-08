#!/usr/bin/env python3
"""
Master script to extract all seven tables from 'FY2022 Asset Reports.pdf'
into separate CSV files by combining the logic of all individual parsers.
"""
import re
import csv
import subprocess
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta
import numpy as np # Added for numpy functions used in parser 3

# ============================= CONFIGURATION =============================
from pathlib import Path

# Project root = top-level repo folder (fa25-team-b)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Input PDF location (relative path)
PDF_PATH = PROJECT_ROOT / "pdf" / "FY2022 Asset Reports.pdf"

# Output directory (CSVs/FY2022 Asset Report Final)
OUT_DIR = PROJECT_ROOT / "output" / "FY2022 Asset Report Final"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Output CSV file paths
OUT_CSV_REGION_SERVICE = OUT_DIR / "assets_by_region_service_FY2022.csv"
OUT_CSV_FIELD_OFFICE = OUT_DIR / "assets_by_field_office_FY2022.csv"
OUT_CSV_INSTALLED_MANUFACTURER = OUT_DIR / "installed_assets_by_location_manufacturer_FY2022.csv"
OUT_CSV_ASSET_DETAILS = OUT_DIR / "asset_details_FY2022.csv"
OUT_CSV_YEARS_STORAGE = OUT_DIR / "years_in_storage_FY2022.csv"
OUT_CSV_SITE_STATUS = OUT_DIR / "site_operational_status_FY2022.csv"
OUT_CSV_FLOOR_ASSET_DETAILS = OUT_DIR / "floor_asset_details_FY2022.csv"


# --- Common Regex & Constants ---
RE_MONTH = re.compile(r"for\s+month\s+of\s+([A-Za-z]+)\s+(\d{4})", re.I)
RE_MONTH_WORD = re.compile(
    r"(Assets|EGMs)\s+by\s+Region,?\s*Service\s+for month of\s+([A-Za-z]+\s+\d{4})",
    re.IGNORECASE,
)
MONTH_MAP = {
    'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
    'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug', 'September': 'Sep',
    'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
}

MONTH_NAME_TO_ABBR = { # Added for Parser 3
    "January": "Jan", "February": "Feb", "March": "Mar",
    "April": "Apr", "May": "May", "June": "Jun",
    "July": "Jul", "August": "Aug", "September": "Sep",
    "October": "Oct", "November": "Nov", "December": "Dec",
}


# =============================== COMMON/SHARED HELPERS ==============================
def load_text_from_pdf(pdf_path: Path) -> str:
    """Run pdftotext in layout mode and return the normalized text."""
    print(f"🔍 Extracting text from {pdf_path.name}...")
    try:
        # Use an in-memory output for the full text extraction
        raw = subprocess.check_output(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            universal_newlines=True,
            errors="ignore",
            stderr=subprocess.STDOUT
        )
        return raw.replace("\r", "")
    except FileNotFoundError:
        print("🚨 Error: 'pdftotext' command not found. Ensure Poppler is installed and on your PATH.")
        raise
    except Exception as e:
        print(f"🚨 Error during PDF text extraction: {e}")
        raise

def load_pages_from_pdf(pdf_path: str) -> List[str]:
    """Extract text from PDF, split by form-feed character to get pages."""
    text = subprocess.check_output(['pdftotext', '-layout', pdf_path, '-'], text=True)
    return text.split('\f')

def fmt_month(mon: str, yr: str) -> str:
    """Formats month/year to 'Mon-YY' tag."""
    return f"{mon[:3].title()}-{yr[-2:]}"

def month_tag(mon_str: str, year_str: str) -> str:
    """Formats month/year using MONTH_MAP to 'Mon-YY' tag."""
    mon = MONTH_MAP.get(mon_str.strip().title(), mon_str.strip()[:3].title())
    yy = year_str[-2:]
    return f"{mon}-{yy}"

def mon_abbr_from_number(n: int) -> str:
    return ["Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"][n-1]

def month_labels_from_report_date(s: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        dt = datetime.strptime(s.strip(), "%m/%d/%Y")
        return f"{mon_abbr_from_number(dt.month)}-{str(dt.year)[-2:]}", \
               f"{mon_abbr_from_number(dt.month)}-{dt.year}"
    except Exception:
        return None, None

def detect_month_map(pages: List[str]) -> Dict[int, str]:
    """Detects the month for each page, skipping duplicates/repeats."""
    month_start_pages: List[tuple[int, str]] = []
    seen_months: List[str] = []
    for i, page in enumerate(pages, start=1):
        m = RE_MONTH_WORD.search(page)
        if m:
            month = m.group(2).strip()
            if month not in seen_months:
                month_start_pages.append((i, month))
                seen_months.append(month)
    
    month_map: Dict[int, str] = {}
    last_end = len(pages)
    for idx, (start, month) in reversed(list(enumerate(month_start_pages))):
        end = last_end
        last_end = start - 1
        for p in range(start, end + 1):
            month_map[p] = month
    return month_map


# =============================== PARSER 1: EGMs by Region, Service ===============================
def parse_region_line(region, tail):
    """Corrected parsing function for T1 data row."""
    mloc = re.search(r"\d+", tail)
    if not mloc: return None
    loc = mloc.group(0)
    rest = tail[mloc.end():]
    nums = re.findall(r"\d+(?:\.\d+)?%?", rest)
    if not nums: return None
    values = [n for n in nums if not n.endswith('%')]
    percents = [n for n in nums if n.endswith('%')]
    percent = percents[-1].replace('%', '') if percents else ""
    army = navy = marine = air = total = ""
    if len(values) == 3:
        army, navy, total = values
    elif len(values) == 4:
        army, navy, marine, total = values
    elif len(values) >= 5:
        army, navy, marine, air, total = values[:5]
    return {
        "Region": region, "#Location": loc,
        "Army": army, "Navy": navy, "Marine_Corps": marine,
        "Airforce": air, "Total": total, "Percent": percent
    }

def extract_egms_by_region_service(text: str) -> pd.DataFrame:
    print("Parsing [1/7] 'EGMs by Region, Service'...")
    RE_T1_HDR = re.compile(r"^EGMs\s+by\s+Region,\s*Service", re.I)
    RE_T2_HDR = re.compile(r"^EGMs\s+by\s+Field\s+Office", re.I)
    RE_SKIP = re.compile(r"^(Slots|Army|Navy|Marine|Airforce|#\s*Locations)$", re.I)

    def detect_month_from_text(line):
        m = RE_MONTH.search(line)
        return fmt_month(m.group(1), m.group(2)) if m else None

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    rows = []
    block = []
    current_month = ""
    seen_months = set()

    def flush_block(month):
        if month in seen_months: return
        seen_months.add(month)
        for ln in block:
            if RE_SKIP.match(ln): continue
            if "Locations by Service" in ln and re.search(r"\d", ln):
                nums = re.findall(r"\d+", ln)
                rows.append({
                    "Region": "Locations by Service", "#Location": "",
                    "Army": nums[0] if len(nums) > 0 else "",
                    "Navy": nums[1] if len(nums) > 1 else "",
                    "Marine_Corps": nums[2] if len(nums) > 2 else "",
                    "Airforce": nums[3] if len(nums) > 3 else "",
                    "Total": nums[4] if len(nums) > 4 else "",
                    "Percent": "", "Month": month
                })
                continue
            if re.search(r"\d+\.?\d*\s*%(?:\s+\d+\.?\d*\s*%){2,}", ln):
                pcts = re.findall(r"\d+\.?\d*\s*%", ln)
                rows.append({
                    "Region": "% by Service", "#Location": "",
                    "Army": pcts[0] if len(pcts) > 0 else "",
                    "Navy": pcts[1] if len(pcts) > 1 else "",
                    "Marine_Corps": pcts[2] if len(pcts) > 2 else "",
                    "Airforce": pcts[3] if len(pcts) > 3 else "",
                    "Total": "", "Percent": "", "Month": month
                })
                continue
            r = re.match(r"^(Europe|Japan|Korea|Total)\b(.*)$", ln)
            if r:
                rec = parse_region_line(r.group(1), r.group(2).replace("–", " ").replace("-", " "))
                if rec:
                    rec["Month"] = month
                    rows.append(rec)

    in_block = False
    for ln in lines:
        m = detect_month_from_text(ln)
        if m: current_month = m
        if RE_T1_HDR.search(ln):
            in_block = True
            block = []
            continue
        if in_block and RE_T2_HDR.search(ln):
            flush_block(current_month)
            in_block = False
            block = []
            continue
        if in_block:
            block.append(ln)

    if in_block: flush_block(current_month)
    return pd.DataFrame(rows, columns=[
        "Region", "#Location", "Army", "Navy",
        "Marine_Corps", "Airforce", "Total", "Percent", "Month"
    ])


# =============================== PARSER 2: EGMs by Field Office ===============================
def parse_egm_by_field_office(all_text: str) -> pd.DataFrame:
    print("Parsing [2/7] 'EGMs by Field Office'...")
    RE_EGM_FO_HDR = re.compile(r"^\s*EGMs\s+by\s+Field\s+Office\b", re.I)
    RE_MONTH_LINE = re.compile(r"for\s+month\s+of\s+([A-Za-z]+)\s+(\d{4})", re.I)
    RE_REGION_LINE = re.compile(r"^\s*(Europe|Japan|Korea)\s*(?:\s+Slots\s+ACM\s+ITC\s+FRS\s+Total)?\s*$", re.I)
    RE_FO_ROW = re.compile(r"^\s*(\d{1,3})\s+([A-Z0-9'&\.\-\/ ]*?[A-Z0-9])\s+"
        r"(\d{1,4})\s+(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})\s+(\d{1,4})\s*$"
    )
    RE_REGION_TOTAL = re.compile(r"^\s*(Europe|Japan|Korea)\s+Total\s+(\d{1,5})\s+(\d{1,5})\s+(\d{1,5})\s+(\d{1,5})\s+(\d{1,5})\s*$", re.I)
    RE_PCT_LINE = re.compile(r"^\s*(\d{1,3})%\s+(\d{1,3})%\s+(\d{1,3})%\s+(\d{1,3})%\s+(\d{1,3})%\s*$")
    RE_ARMP_TOTAL = re.compile(r"^\s*ARMP\s+Total\s+(\d{1,5})\s+(\d{1,5})\s+(\d{1,5})\s+(\d{1,5})\s+(\d{1,5})\s*$", re.I)
    RE_NEXT_SECTION = re.compile(r"^\s*(Installed\s+Assets|EGMs\s+by\s+Region|REGION\s+FONUM|Years\s+in\s+Storage|Site\s+Operational\s+Status)\b", re.I)

    lines = all_text.split("\n")
    rows = []
    in_section = False
    cur_month = None
    cur_region = None
    just_saw_region = False
    seen_months = set()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not in_section and RE_EGM_FO_HDR.search(line):
            found_month = None
            for j in range(i, min(i + 7, len(lines))):
                m = RE_MONTH_LINE.search(lines[j])
                if m:
                    found_month = month_tag(m.group(1), m.group(2))
                    break
            if found_month:
                if found_month in seen_months:
                    while i < len(lines) and not RE_NEXT_SECTION.search(lines[i]): i += 1
                    continue
                seen_months.add(found_month)
                in_section = True
                cur_month = found_month
                cur_region = None
                just_saw_region = False
                i += 1
                continue

        if in_section:
            if RE_NEXT_SECTION.search(line):
                in_section = False
                cur_month = None
                i += 1
                continue
            mreg = RE_REGION_LINE.match(line)
            if mreg:
                cur_region = mreg.group(1).title()
                just_saw_region = True
                i += 1
                continue
            if just_saw_region:
                if re.search(r"\bSlots\b.*\bTotal\b", line):
                    i += 1
                    just_saw_region = False
                    continue
                else:
                    just_saw_region = False
            mfo = RE_FO_ROW.match(line)
            if mfo and cur_region and cur_month:
                rows.append({
                    "Region": cur_region, "FO#": int(mfo.group(1)),
                    "FOSHORT": mfo.group(2).strip(), "Slots": int(mfo.group(3)),
                    "ACM_CountR": int(mfo.group(4)), "ITC": int(mfo.group(5)),
                    "FRS": int(mfo.group(6)), "Total": int(mfo.group(7)), "Month": cur_month
                })
                i += 1
                continue
            mtot = RE_REGION_TOTAL.match(line)
            if mtot and cur_month:
                reg_name = mtot.group(1).title()
                rows.append({
                    "Region": reg_name, "FO#": "", "FOSHORT": f"{reg_name} Total",
                    "Slots": int(mtot.group(2)), "ACM_CountR": int(mtot.group(3)),
                    "ITC": int(mtot.group(4)), "FRS": int(mtot.group(5)),
                    "Total": int(mtot.group(6)), "Month": cur_month
                })
                i += 1
                if i < len(lines):
                    mp = RE_PCT_LINE.match(lines[i].strip())
                    if mp:
                        rows.append({
                            "Region": reg_name, "FO#": "", "FOSHORT": "%",
                            "Slots": mp.group(1) + "%", "ACM_CountR": mp.group(2) + "%",
                            "ITC": mp.group(3) + "%", "FRS": mp.group(4) + "%",
                            "Total": mp.group(5) + "%", "Month": cur_month
                        })
                        i += 1
                continue
            m_armp = RE_ARMP_TOTAL.match(line)
            if m_armp and cur_month:
                rows.append({
                    "Region": "ARMP", "FO#": "", "FOSHORT": "ARMP Total",
                    "Slots": int(m_armp.group(1)), "ACM_CountR": int(m_armp.group(2)),
                    "ITC": int(m_armp.group(3)), "FRS": int(m_armp.group(4)),
                    "Total": int(m_armp.group(5)), "Month": cur_month
                })
                i += 1
                continue
        i += 1
    return pd.DataFrame(rows, columns=[
        "Region", "FO#", "FOSHORT", "Slots", "ACM_CountR", "ITC", "FRS", "Total", "Month"
    ])


# =============================== PARSER 3: Installed Assets by Location, Manufacture ===============================
def parse_installed_assets(all_text: str, pdf_path: Path) -> pd.DataFrame:
    print("Parsing [3/7] 'Installed Assets by Location, Manufacture'...")
    
    # -------------------------- Helpers ---------------------

    def normalize_spaces(line: str) -> str:
        return re.sub(r"\s+", " ", line.strip())

    def parse_int_token(tok: str) -> Optional[int]:
        tok = tok.strip()
        if tok in ("-", "--", ""):
            return None
        if re.fullmatch(r"\d+", tok):
            return int(tok)
        if re.fullmatch(r"\d+-", tok):
            return int(tok[:-1])
        return None

    def month_in_range(month_name: str, year: int) -> bool:
        month_order = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        m = month_order.get(month_name)
        if m is None:
            return False
        # Filter for FY2022 (Nov 2021 to Sep 2022)
        return (2021, 11) <= (year, m) <= (2022, 9) 

    def get_month_label(month_name: str, year: int) -> str:
        abbr = MONTH_NAME_TO_ABBR.get(month_name, month_name[:3])
        yy = str(year)[-2:]
        return f"{abbr}-{yy}"

    # ------------------ Build FO → Group mapping ------------------

    def build_fo_group_map(lines: List[str]) -> Dict[Tuple[str, int], str]:
        fo_to_group: Dict[Tuple[str, int], str] = {}
        in_field = False
        current_region: Optional[str] = None

        for raw in lines:
            line = raw.rstrip("\n")
            if "EGMs by Field Office" in line:
                in_field = True
                current_region = None
                continue

            if not in_field:
                continue

            norm = normalize_spaces(line)
            if not norm:
                continue

            # Assuming these region headers are unique enough within the block
            if norm.startswith("Europe ") and "ACM" in norm:
                current_region = "Europe"; continue
            if norm.startswith("Japan ") and "ACM" in norm:
                current_region = "Japan"; continue
            if norm.startswith("Korea ") and "ACM" in norm:
                current_region = "Korea"; continue

            if "Installed Assets by Location" in norm:
                in_field = False
                current_region = None
                continue

            if current_region is None:
                continue

            tokens = norm.split()
            if len(tokens) < 2:
                continue

            if tokens[0].isdigit():
                try:
                    fo = int(tokens[0])
                except ValueError:
                    continue
                name_tokens = []
                # Name is everything between FO# and the first count column (Slots)
                for t in tokens[1:]:
                    if re.fullmatch(r"\d+", t):
                        break
                    name_tokens.append(t)
                if name_tokens:
                    fo_to_group[(current_region, fo)] = " ".join(name_tokens)
        return fo_to_group

    # ------------------ Regex for site rows ------------------

    SITE_RE = re.compile(
        r"^(?P<site>.+?)\s+(?P<fo>\d+)\s+(?P<loc>\d+)\s+"
        r"(?P<svc>Army|Navy|Air Force|Marine Corps|Marine|Airforce)\s+(?P<rest>.*)$"
    )

    # ---------------------- Robust Subtotal Parser ----------------------

    def parse_subtotal_row(line: str, region: str, month_label: str) -> Optional[dict]:
        norm = normalize_spaces(line)

        # 1. Simple 'Subtotal' marker
        if "Subtotal" in norm:
            parts = norm.split("Subtotal")
            group = parts[0].strip()
            rest = parts[1].strip()
        # 2. Heuristic: group name (non-numeric tokens) followed by numbers
        else:
            tokens = norm.split()
            group_tokens = []
            rest_tokens = []

            for t in tokens:
                if re.fullmatch(r"\d+|-", t):
                    rest_tokens.append(t)
                else:
                    if rest_tokens: # Found a non-numeric token AFTER the first number
                        return None
                    group_tokens.append(t)

            if not group_tokens or not rest_tokens:
                return None

            group = " ".join(group_tokens)
            rest = " ".join(rest_tokens)

        nums = [parse_int_token(tok) for tok in rest.split()]
        if len(nums) < 13:
            nums += [None] * (13 - len(nums))
        nums = nums[:13]

        (NOV, AIN, IGT, WMS, BAL, KON, ITE,
         tot_egm, frs, acm, blank_col, itc, total) = nums

        return {
            "region": region,
            "group_location": group,
            "site_name": "Subtotal",
            "FO #": np.nan,
            "Loc": np.nan,
            "Svc": np.nan,
            "NOV": NOV, "AIN": AIN, "IGT": IGT, "WMS": WMS,
            "BAL": BAL, "KON": KON, "ITE": ITE,
            "Tot/EGMs": tot_egm, "FRS": frs, "ACM": acm,
            "ITC": itc, "Total": total,
            "Month": month_label,
        }


    # ---------------------- Site Row Parser ----------------------

    def parse_site_row(line: str, region: str, month_label: str,
                       fo_to_group: Dict[Tuple[str, int], str]):
        norm = normalize_spaces(line)
        m = SITE_RE.match(norm)
        if not m:
            return None

        site_name = m.group("site").strip()
        try:
            fo = int(m.group("fo"))
            loc = int(m.group("loc"))
        except ValueError:
            return None
            
        svc = m.group("svc")
        rest = m.group("rest")

        # Handle 'Marine Corps' becoming two tokens after SITE_RE match
        if svc == "Marine" and rest.startswith("Corps "):
            svc = "Marine Corps"
            rest = rest[len("Corps "):]

        nums = [parse_int_token(tok) for tok in rest.split()]
        if len(nums) < 13:
            nums += [None] * (13 - len(nums))
        nums = nums[:13]

        (NOV, AIN, IGT, WMS, BAL, KON, ITE,
         tot_egm, frs, acm, blank_col, itc, total) = nums

        # The FO is the key for the group_location (FOSHORT)
        group_loc = fo_to_group.get((region, fo), None)

        return {
            "region": region,
            "group_location": group_loc,
            "site_name": site_name,
            "FO #": float(fo),
            "Loc": float(loc),
            "Svc": svc,
            "NOV": NOV, "AIN": AIN, "IGT": IGT, "WMS": WMS,
            "BAL": BAL, "KON": KON, "ITE": ITE,
            "Tot/EGMs": tot_egm, "FRS": frs, "ACM": acm,
            "ITC": itc, "Total": total,
            "Month": month_label,
        }


    # ---------------------- ARMP Total Parser ----------------------

    def parse_armp_row(line: str, month_label: str):
        norm = normalize_spaces(line)
        if not norm.startswith("ARMP Total"):
            return None

        rest = norm[len("ARMP Total"):].strip()
        nums = [parse_int_token(tok) for tok in rest.split()]

        if len(nums) < 13:
            nums += [None] * (13 - len(nums))
        nums = nums[:13]

        (NOV, AIN, IGT, WMS, BAL, KON, ITE,
         tot_egm, frs, acm, blank_col, itc, total) = nums

        return {
            "region": np.nan,
            "group_location": np.nan,
            "site_name": "ARMP Total",
            "FO #": np.nan,
            "Loc": np.nan,
            "Svc": np.nan,
            "NOV": NOV, "AIN": AIN, "IGT": IGT, "WMS": WMS,
            "BAL": BAL, "KON": KON, "ITE": ITE,
            "Tot/EGMs": tot_egm, "FRS": frs, "ACM": acm,
            "ITC": itc, "Total": total,
            "Month": month_label,
        }


    # ---------------------- Parse Block ----------------------

    def parse_assets_block(lines, start_idx, month_label, fo_to_group):
        rows = []
        current_region = None
        seen_armp = False
        i = start_idx

        while i < len(lines):
            raw = lines[i]
            norm = normalize_spaces(raw)
            i += 1

            if not norm:
                continue

            # Region headers
            if norm.startswith("Europe ") and "FO #" in norm:
                current_region = "Europe"; continue
            if norm.startswith("Japan ") and "FO #" in norm:
                current_region = "Japan"; continue
            if norm.startswith("Korea ") and "FO #" in norm:
                current_region = "Korea"; continue

            if current_region is None:
                continue

            # ARMP TOTAL
            armp = parse_armp_row(norm, month_label)
            if armp:
                rows.append(armp)
                seen_armp = True
                continue

            # *** SKIP SPECIAL 'Converted / Location Count' LINE ***
            if "Converted" in norm and "Subtotal" in norm:
                continue
            if "Location Count" in norm:
                continue

            # Subtotal
            subtotal = parse_subtotal_row(norm, current_region, month_label)
            if subtotal:
                rows.append(subtotal)
                continue

            # Site rows
            # Check for a Service (Svc) marker to identify a site row
            if any(s in norm for s in
                   ["Army", "Navy", "Air Force", "Marine Corps", "Marine", "Airforce"]):
                site = parse_site_row(norm, current_region, month_label, fo_to_group)
                if site:
                    rows.append(site)
                continue

            # Stop when we hit the next big section *after* ARMP
            if seen_armp and (
                "EGMs by Region" in norm
                or "Installed Assets by Location" in norm
                or "Years in Storage" in norm
                or "Site Operational Status" in norm # Added for completeness
            ):
                break

        return rows, i

    # ---------------------- Main Extraction ----------------------

    lines = all_text.splitlines()

    # Need the FO to Group mapping first, which comes from Parser 2's data area
    fo_to_group = build_fo_group_map(lines)

    all_rows: List[dict] = []
    current_month_label: Optional[str] = None
    month_re = re.compile(r"for month of\s+([A-Za-z]+)\s+(\d{4})")

    # MONTH–REGION DEDUP MEMORY
    seen_month_region = set()

    i = 0
    while i < len(lines):
        norm = normalize_spaces(lines[i])

        # Always check for month to update context
        m = month_re.search(norm)
        if m:
            mn = m.group(1)
            yr = int(m.group(2))
            current_month_label = get_month_label(mn, yr) if month_in_range(mn, yr) else None

        # Start parsing when the title and a valid month are found
        if "Installed Assets by Location, Manufacture" in norm and current_month_label:
            rows, new_i = parse_assets_block(lines, i+1, current_month_label, fo_to_group)

            # Deduplication logic to handle repeated report sections
            # Use the region of the *first* data row found in the block as a key
            regions_in_block = {r["region"] for r in rows if isinstance(r.get("region"), str)}
            region = next(iter(regions_in_block)) if regions_in_block else None
            block_key = (current_month_label, region)

            if block_key in seen_month_region:
                i = new_i
                continue
            seen_month_region.add(block_key)

            all_rows.extend(rows)
            i = new_i
            continue

        i += 1

    if not all_rows:
        return pd.DataFrame(columns=[
            "region", "group_location", "site_name", "FO #", "Loc", "Svc",
            "NOV", "AIN", "IGT", "WMS", "BAL", "KON", "ITE",
            "Tot/EGMs", "FRS", "ACM", "ITC", "Total", "Month"
        ])

    df = pd.DataFrame(all_rows)
    df = df[
        ["region", "group_location", "site_name", "FO #", "Loc", "Svc",
         "NOV", "AIN", "IGT", "WMS", "BAL", "KON", "ITE",
         "Tot/EGMs", "FRS", "ACM", "ITC", "Total", "Month"]
    ]

    return df


# =============================== PARSER 4: Asset Details (Installed Assets by Location) ===============================
def extract_asset_details(all_text: str) -> pd.DataFrame:
    print("Parsing [4/7] 'Asset Details' ...")
    
    # --- Localized Regex and Helpers (to match user's standalone script exactly) ---
    RE_TITLE = re.compile(r"Installed\s+Assets\s+by\s+Location", re.I)
    RE_DETAIL_HEADER = re.compile(
        r"^\s*REGION\s+FONUM\s+FOSHORT\s+Loc\s+LNAME\s+Asset\s+Class\s+Desc\s+Type\s+"
        r"Aquire\s+Effective\s+SerialNum\s+PLACE\s+Age\s+Years\s+in\s+Storage\s+Months",
        re.I
    )
    RE_STOP = re.compile(r"^\s*Loc\s+PLACE\s+REGION\s+SVC", re.I)
    TYPE_RE = re.compile(r"^\d{3,5}$")
    DATE_SERIAL_RE = re.compile(r"^(\d{1,2}/\d{1,2}/\d{4})(?:\s+(.*))?$")
    
    def find_report_date_at_line_end(line):
        m = re.search(r"(\d{1,2}/\d{1,2}/\d{4})\s*$", line)
        return (line[:m.start()].rstrip(), m.group(1)) if m else (line.rstrip(), None)

    def clean_months(x):
        m = re.search(r"[-+]?\d+(?:\.\d+)?", x or "")
        return m.group(0) if m else ""

    def clean_split(raw):
        return [t.strip() for t in re.split(r"\s{2,}", raw.strip()) if t.strip()]

    def is_date_like(tok):
        return bool(re.match(r"^\d{1,2}/\d{1,2}/\d{2,4}$", tok) or
                    (tok.isdigit() and len(tok) >= 4))

    def is_excel_serial(tok):
        """Detect Excel serial dates (e.g., 48014, 48066) used in Dec-2021 rows."""
        return tok.isdigit() and 30000 <= int(tok) <= 60000

    def convert_excel_date(tok):
        if is_excel_serial(tok):
            dt = datetime(1899, 12, 30) + timedelta(days=int(tok))
            return dt.strftime("%m/%d/%Y")
        return tok
    # --- End Localized Helpers ---

    lines = all_text.splitlines()
    rows = []
    encountered_months = set()
    i = 0

    while i < len(lines):

        if RE_TITLE.search(lines[i]):
            j = i + 1
            header_line = None

            for k in range(j, min(j + 200, len(lines))):
                if RE_DETAIL_HEADER.search(lines[k]):
                    header_line = lines[k]
                    j = k + 1
                    break

            if not header_line:
                i += 1
                continue

            # This date extraction relies on the header line or a line nearby containing the report date
            header_pure, date_str = find_report_date_at_line_end(header_line)
            month_disp, month_full = month_labels_from_report_date(date_str)

            if month_disp is None:
                month_disp = "UNKNOWN"

            # avoid duplicate month blocks
            if month_disp in encountered_months:
                while j < len(lines) and not RE_STOP.search(lines[j]):
                    j += 1
                i = j
                continue

            encountered_months.add(month_disp)

            # ------------------ ROW PARSING ------------------
            while j < len(lines) and not RE_STOP.search(lines[j]):
                raw = lines[j].strip()
                j += 1
                if not raw:
                    continue

                tokens = clean_split(raw)

                # UPDATED SHORT-ROW ACCEPTANCE LOGIC (User's logic)
                if len(tokens) < 8:
                    if not (
                        len(tokens) >= 5
                        and re.match(r"[A-Za-z]+", tokens[0])  # REGION
                        and tokens[1].isdigit()                # FONUM
                    ):
                        continue
                
                try:
                    REGION, FONUM = tokens[0], tokens[1]
                    idx = 2
                    lname_parts = []

                    # FOSHORT/Loc Parsing
                    if re.match(r"^\d{3}\b", tokens[idx]):
                        FOSHORT = ""
                        loc_token = tokens[idx]
                        parts = loc_token.split(None, 1)
                        Loc = parts[0]
                        lname_parts.append(parts[1] if len(parts) > 1 else "")
                        idx += 1
                    else:
                        FOSHORT = tokens[idx]
                        idx += 1
                        Loc = tokens[idx]
                        idx += 1

                    # LNAME until first pure numeric (Asset code)
                    while idx < len(tokens) and not tokens[idx].isdigit():
                        lname_parts.append(tokens[idx])
                        idx += 1

                    LNAME = " ".join(lname_parts)
                    Asset, Class = tokens[idx], tokens[idx + 1]
                    idx += 2

                    # Desc until TYPE_RE (3–5 digits)
                    desc_parts = []
                    while idx < len(tokens) and not TYPE_RE.match(tokens[idx]):
                        desc_parts.append(tokens[idx])
                        idx += 1

                    Desc = " ".join(desc_parts)
                    Type = tokens[idx]
                    idx += 1

                    remaining = tokens[idx:]
                    Aquire = Effective = SerialNum = PLACE = Age = ""
                    Years = Months = ""

                    if remaining:
                        parts = remaining[0].split()

                        # Case 1: three-part first token (Acq, Eff, Serial)
                        if (len(parts) >= 3 and is_date_like(parts[0]) and
                            is_date_like(parts[1]) and '-' in parts[2]):
                            Aquire, Effective, SerialNum = parts[0], parts[1], parts[2]
                            PLACE = remaining[1] if len(remaining) > 1 else ""
                            Age   = remaining[2] if len(remaining) > 2 else ""
                            Years = clean_months(remaining[3]) if len(remaining) > 3 else ""
                            Months= clean_months(" ".join(remaining[4:])) if len(remaining) > 4 else ""

                        # Case 2: Acq Eff Serial as separate tokens
                        elif (len(remaining) >= 3 and is_date_like(remaining[0])
                              and is_date_like(remaining[1]) and '-' in remaining[2]):
                            Aquire, Effective, SerialNum = remaining[0], remaining[1], remaining[2]
                            PLACE = remaining[3] if len(remaining) > 3 else ""
                            Age   = remaining[4] if len(remaining) > 4 else ""
                            Years = clean_months(remaining[5]) if len(remaining) > 5 else ""
                            Months= clean_months(" ".join(remaining[6:])) if len(remaining) > 6 else ""

                        # Case 3: Excel serial, or odd splits
                        else:
                            Aquire = remaining[0]
                            Effective_candidate = remaining[1] if len(remaining) > 1 else ""

                            if Effective_candidate:
                                m = DATE_SERIAL_RE.match(Effective_candidate)
                                if m and m.group(2):
                                    Effective = m.group(1)
                                    SerialNum = m.group(2)
                                else:
                                    Effective = Effective_candidate

                            place_idx = 2
                            PLACE = remaining[place_idx] if len(remaining) > place_idx else ""
                            Age   = remaining[place_idx+1] if len(remaining) > place_idx+1 else ""
                            Years = clean_months(remaining[place_idx+2]) if len(remaining) > place_idx+2 else ""
                            Months= clean_months(" ".join(remaining[place_idx+3:])) if len(remaining) > place_idx+3 else ""

                        # Convert Excel serials if present
                        Aquire = convert_excel_date(Aquire)
                        Effective = convert_excel_date(Effective)

                        # FINAL fallback for SerialNum from Age/Years
                        if not SerialNum and Age.strip() and not Age.isdigit():
                            SerialNum = Age
                            Age = ""

                    rows.append([
                        REGION, FONUM, FOSHORT, Loc, LNAME, Asset, Class, Desc, Type,
                        Aquire, Effective, SerialNum, PLACE, Age, Years, Months, month_disp
                    ])

                except Exception:
                    # silently skip truly broken lines
                    pass

            i = j
            continue

        i += 1

    header = [
        "REGION","FONUM","FOSHORT","Loc","LNAME","Asset",
        "Class","Desc","Type","Aquire","Effective",
        "SerialNum","PLACE","Age","Years in Storage",
        "Months","Month"
    ]
    return pd.DataFrame(rows, columns=header)

# =============================== PARSER 5: Years in Storage (EGMs Only) ===============================
def extract_years_in_storage(pdf_path: Path) -> pd.DataFrame:
    print("Parsing [5/7] 'Years in Storage (EGMs Only)'...")
    
    def total_pages(pdf_path: Path) -> int:
        try:
            info = subprocess.check_output(["pdfinfo", str(pdf_path)]).decode()
            for line in info.splitlines():
                if line.strip().startswith("Pages:"):
                    return int(line.split(":")[1])
        except FileNotFoundError:
            print("🚨 Warning: 'pdfinfo' command not found. Cannot determine total pages. Assuming 100.")
            return 100
        return 0

    def run_pdftotext(pdf_path: Path, page: int) -> List[str]:
        out = subprocess.check_output(
            ["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(pdf_path), "-"]
        )
        return out.decode("utf-8", errors="ignore").splitlines()

    def find_grid_pages_with_months(pdf_path: Path):
        n = total_pages(pdf_path)
        month_pattern = RE_MONTH_WORD
        current_month = None
        seen_months = set()
        result = []
        for p in range(1, n + 1):
            txt = subprocess.check_output(
                ["pdftotext", "-f", str(p), "-l", str(p), str(pdf_path), "-"]
            ).decode(errors="ignore")
            m = month_pattern.search(txt)
            if m:
                month_full_name = m.group(2).strip()
                m_parts = re.search(r"([A-Za-z]+)\s+(\d{4})", month_full_name)
                if m_parts: current_month = fmt_month(m_parts.group(1), m_parts.group(2))
            
            if "Years in Storage (EGMs Only)" in txt:
                if not current_month: continue
                if current_month in seen_months: continue
                seen_months.add(current_month)
                result.append((p, current_month))
        return result

    def parse_grid_page(pdf_path: Path, page: int):
        lines = run_pdftotext(pdf_path, page)
        header_idx = None
        for i, line in enumerate(lines):
            if "Age" in line and "by Age" in line:
                header_idx = i
                header = line
                break
        if header_idx is None: raise ValueError(f"Grid header not found on page {page}")

        age_start = header.find("Age")
        tot_start = header.find("by Age")
        col_starts = []
        
        fixed_col_width = 5 
        for col in range(15):
            col_starts.append(age_start + len("Age") + 1 + col * fixed_col_width)
        
        col_starts.insert(0, age_start)
        col_starts.append(tot_start)

        
        pattern = re.compile(r"\b12\s+11\s+10\s+9\s+8\s+7\s+6\s+5\s+4\s+3\s+2\s+1\b")
        mini_header = None
        mini_values = None
        for i, line in enumerate(lines):
            if pattern.search(line):
                nums = [int(x) for x in re.findall(r"\d+", line)][-12:]
                nextline = lines[i + 1] if i + 1 < len(lines) else ""
                vals = [int(x) for x in re.findall(r"\d+", nextline)]
                if len(vals) >= 13:
                    mini_counts = vals[-13:-1]
                    mini_total = vals[-1]
                    mini_header = nums
                    mini_values = mini_counts + [mini_total]
                else:
                    mini_header = nums
                    mini_values = nums + [sum(nums)]
                break

        age_rows = [None] * 26
        totals_by = None

        for line in lines[header_idx + 1:]:
            if not line.strip(): continue
            age_cell = line[col_starts[0]:col_starts[1]].strip()
            total_str = line[tot_start:].strip()
            total_val = int(total_str) if total_str.isdigit() else None
            
            if not age_cell:
                if total_val and total_val > 100 and totals_by is None:
                    col_tot = []
                    for j in range(1, 15):
                        seg = line[col_starts[j]:col_starts[j + 1]].strip()
                        col_tot.append(int(seg) if seg.isdigit() else 0)
                    totals_by = col_tot + [total_val]
                continue
            
            if not age_cell.isdigit(): continue

            age = int(age_cell)
            counts = []
            for j in range(1, 16):
                seg = line[col_starts[j]:col_starts[j+1]].strip()
                counts.append(int(seg) if seg.isdigit() else 0)

            total_by_age = total_val if total_val else sum(counts)
            age_rows[age] = (age, counts, total_by_age)

        for a in range(26):
            if age_rows[a] is None: age_rows[a] = (a, [0]*15, 0)

        if totals_by is None:
            sums = [0]*15
            for _, cts, _ in age_rows:
                if len(cts) == 15:
                    for k in range(15): sums[k] += cts[k]
            totals_by = sums + [sum(sums)]

        return age_rows, totals_by, mini_header, mini_values

    pages_with_months = find_grid_pages_with_months(pdf_path)
    rows = []
    for page, month in pages_with_months:
        try:
            age_rows, totals_by, mini_header, mini_values = parse_grid_page(pdf_path, page)
        except ValueError as e:
            print(f"Skipping page {page}: {e}")
            continue

        for age, counts, total in age_rows:
            rows.append([str(age)] + [str(x) for x in counts] + [str(total)] + [month])
        
        if totals_by and len(totals_by) == 16:
             rows.append(["Totals_By"] + [str(x) for x in totals_by[:-1]] + [str(totals_by[-1])] + [month])
        else:
             rows.append(["Totals_By"] + [""] * 15 + ["0"] + [month])

        hdr12 = mini_header[:12] if mini_header else [0]*12
        pad = [""] * (15 - len(hdr12))
        rows.append(["Mini_Header"] + [str(x) for x in hdr12] + pad + ["", month])

        vals12 = mini_values[:-1] if mini_values and len(mini_values) > 1 else [0]*12
        tot12 = mini_values[-1] if mini_values else 0
        pad2 = [""] * (15 - len(vals12))
        rows.append(["Mini_Values"] + [str(x) for x in vals12] + pad2 + [str(tot12), month])

    headers = ["EGM Age"] + [str(i) for i in range(15)] + ["Total by Age", "Month"]
    return pd.DataFrame(rows, columns=headers)


# =============================== PARSER 6: Site Operational Status ===============================
def extract_site_operational_status(all_text: str) -> pd.DataFrame:
    print("Parsing [6/7] 'Site Operational Status'...")
    RE_MONTH = re.compile(r"for\s+month\s+of\s+([A-Za-z]+)\s+(\d{4})", re.I)
    RE_SITE_HDR = re.compile(
        r"^\s*Loc\s+LNAME\s+PLACE\s+Open\s+Closed\s+KSI\s+CmtyNum\s+SVC\s+FONUM\s+FOSHORT\s+FOM\s+EMAIL\s+REGNUM\s+Region\s+",
        re.I,
    )
    END_MARKERS = [
        re.compile(r"^EGMs\s+by\s+Region", re.I),
        re.compile(r"^EGMs\s+by\s+Field\s+Office", re.I),
        re.compile(r"^Installed\s+Assets\s+by\s+Location", re.I),
        re.compile(r"^REGION\s+FONUM\s+FOSHORT", re.I),
        re.compile(r"^EGM[s]?\s+Years\s+in\s+Storage", re.I),
        re.compile(r"\bby\s+Age\b", re.I),
    ]
    SPLIT2 = re.compile(r"\s{2,}")
    LOC_LETTER = re.compile(r"^(\d+)\s+([A-Za-z])$")
    LOC_VALID = re.compile(r"^\d{3,5}(?:\s*[A-Za-z])?$")
    REGION_WORD = re.compile(r"^(Europe|Korea|Japan)\b", re.I)
    SECTION_CODE = re.compile(r"^[A-Z]{2}\d{2}$")
    P_SPLIT_NUM = re.compile(r"^\d+$")
    P_PCT_PREFIX = re.compile(r"^%+\s*")
    
    # --- Local Helpers ---
    def deglitch(s: str) -> str:
        if s is None: return ""
        t = (s.replace("\u00A0", " ").replace("\u200B", "").replace("\uFEFF", "").replace("\u2011", "-"))
        t = re.sub(r"[ \t\r\f\v]+", " ", t)
        return t.strip()
    def month_label(m: str, y: str) -> str:
        mon_abbr_map = {m.lower(): abbr for m, abbr in zip(list(MONTH_MAP.keys()), list(MONTH_MAP.values()))}
        m_abbr = mon_abbr_map.get(m.strip().lower(), m.strip()[:3].title())
        return f"{m_abbr}-{y}"
    def is_block_end(line: str) -> bool:
        return any(p.search(line.strip()) for p in END_MARKERS)
    def compute_slices_from_header(hline: str):
        tokens = [t for t in SPLIT2.split(hline.strip()) if t]
        starts, pos = [], 0
        for tok in tokens:
            idx = hline.find(tok, pos)
            if idx == -1: return tokens, []
            starts.append(idx)
            pos = idx + len(tok)
        ends = starts[1:] + [None]
        return tokens, list(zip(starts, ends))
    def slice_line(line: str, ranges):
        return [(line[s:e] if e else line[s:]) for (s, e) in ranges]
    def trim_edges(fields):
        return [deglitch(f) for f in fields]
    def idx_like(header, pat, default=None):
        rx = re.compile(pat, re.I)
        for i, h in enumerate(header):
            if rx.search(h): return i
        return default
    def to_mdy_force(s: str) -> str:
        if not s: return ""
        t = "".join(ch if ch.isdigit() else "/" for ch in str(s))
        m = re.match(r"^\s*(\d{1,2})/(\d{1,2})/(\d{2,4})", t)
        if not m: return deglitch(s)
        mm, dd, yy = map(int, m.groups())
        if yy < 100: yy = 2000 + yy if yy < 70 else 1900 + yy
        return f"{mm}/{dd}/{yy}"
    def fix_loc_lname(f, h):
        li, ni = idx_like(h, "^loc$"), idx_like(h, "^lname$")
        if li is None or ni is None: return f
        m = LOC_LETTER.match(f[li])
        if not m: return f
        num, let = m.groups()
        f[li] = num
        lname = f[ni] or ""
        if lname and lname[0].isalpha():
            if lname[0].upper() != let: f[ni] = (let + lname).lstrip()
        else: f[ni] = (let + lname).lstrip()
        return f
    def fix_region_smssection(f, h):
        ri, si, bi = idx_like(h, "^region$"), idx_like(h, "^sms\s*sect"), idx_like(h, "^sms\s*bank")
        if ri is None or si is None or bi is None: return f
        region, sms, bank = deglitch(f[ri]), deglitch(f[si]), deglitch(f[bi])
        if re.fullmatch(r"\d+", region) and REGION_WORD.fullmatch(sms) and SECTION_CODE.fullmatch(bank):
            f[ri] = f"{region} {sms}"; f[si] = bank; f[bi] = ""; return f
        return f
    def fix_regnum_region(f, h):
        gi, ri = idx_like(h, "^regnum$"), idx_like(h, "^region$")
        if gi is None or ri is None: return f
        regnum, region = deglitch(f[gi]), deglitch(f[ri])
        mR = re.fullmatch(r"(\d+)\s+(Europe|Korea|Japan)\b", region, flags=re.I)
        if mR and (not regnum or not regnum.isdigit()): f[gi], f[ri] = mR.group(1), mR.group(2); return f
        return f
    def fix_split_cmmt(f, h):
        si = idx_like(h, "^split$")
        ci = idx_like(h, "^cmmty$") or idx_like(h, "^cm.*ty$")
        if si is None or ci is None: return f
        split, cm = deglitch(f[si]), deglitch(f[ci])
        if P_SPLIT_NUM.fullmatch(split) and cm.startswith("%"):
            cm = P_PCT_PREFIX.sub("", cm).strip()
            f[si] = f"{split}%"
            f[ci] = cm
            return f
        return f
    def empty_main(fields_list, loc_i, place_i, open_i, closed_i):
        return (
            (place_i is not None and not fields_list[place_i]) and
            (open_i is not None and not fields_list[open_i]) and
            (closed_i is not None and not fields_list[closed_i])
        )

    lines = all_text.splitlines()
    rows = []
    header, ranges = None, []
    cur_month = None
    loc_index = None
    i = 0

    while i < len(lines):
        line = lines[i]
        m = RE_MONTH.search(line)
        if m: cur_month = month_label(m.group(1), m.group(2))

        if RE_SITE_HDR.match(line):
            header, ranges = compute_slices_from_header(line)
            loc_i = idx_like(header, "^loc$")
            open_i = idx_like(header, "^open$")
            closed_i = idx_like(header, "^closed$")
            place_i = idx_like(header, "^place$")
            msg_i = idx_like(header, "^message$") or (len(header) - 1)
            loc_index = loc_i
            i += 1
            prev = None

            while i < len(lines):
                raw = lines[i]
                if not raw.strip() or is_block_end(raw) or RE_SITE_HDR.match(raw): break
                fields = trim_edges(slice_line(raw, ranges))
                raw_loc = fields[loc_i] if loc_i is not None else ""
                loc_ok = bool(LOC_VALID.fullmatch(raw_loc))

                if loc_ok and empty_main(fields, loc_i, place_i, open_i, closed_i):
                    pending_rows = []
                    current_fields = list(fields)
                    
                    for look_i in range(i, len(lines)):
                        look_raw = lines[look_i]
                        if not look_raw.strip(): continue
                        if is_block_end(look_raw) or RE_SITE_HDR.match(look_raw): break
                        
                        look_fields = trim_edges(slice_line(look_raw, ranges))
                        look_raw_loc = look_fields[loc_i] if loc_i is not None else ""
                        look_loc_ok = bool(LOC_VALID.fullmatch(look_raw_loc))
                        
                        if look_loc_ok and empty_main(look_fields, loc_i, place_i, open_i, closed_i):
                             pending_rows.append(current_fields)
                             current_fields = look_fields
                        elif look_loc_ok and not empty_main(look_fields, loc_i, place_i, open_i, closed_i):
                            pending_rows.append(current_fields)
                            break
                        else:
                            for col_idx in range(len(header)):
                                if not current_fields[col_idx] and look_fields[col_idx]: 
                                    current_fields[col_idx] = look_fields[col_idx]
                            
                    if current_fields not in pending_rows:
                        pending_rows.append(current_fields)

                    for row_data in pending_rows:
                        if len(row_data) < len(header): row_data += [""] * (len(header) - len(row_data))
                        elif len(row_data) > len(header):
                            extra = " ".join(row_data[len(header):]).strip()
                            row_data = row_data[: len(header)]
                            if extra: row_data[msg_i] = (row_data[msg_i] + " " + extra).strip()
                        
                        row_data = fix_loc_lname(row_data, header)
                        row_data = fix_region_smssection(row_data, header)
                        row_data = fix_regnum_region(row_data, header)
                        row_data = fix_split_cmmt(row_data, header)
                        
                        if open_i is not None and row_data[open_i]: row_data[open_i] = to_mdy_force(row_data[open_i])
                        if closed_i is not None and row_data[closed_i]: row_data[closed_i] = to_mdy_force(row_data[closed_i])
                        rows.append(row_data + [cur_month])

                    i += len(pending_rows)
                    prev = len(rows) - 1
                    continue

                if loc_ok:
                    if len(fields) < len(header): fields += [""] * (len(header) - len(fields))
                    elif len(fields) > len(header):
                        extra = " ".join(fields[len(header):]).strip()
                        fields = fields[: len(header)]
                        if extra: fields[msg_i] = (fields[msg_i] + " " + extra).strip()

                    fields = fix_loc_lname(fields, header)
                    fields = fix_region_smssection(fields, header)
                    fields = fix_regnum_region(fields, header)
                    fields = fix_split_cmmt(fields, header)

                    if open_i is not None and fields[open_i]: fields[open_i] = to_mdy_force(fields[open_i])
                    if closed_i is not None and fields[closed_i]: fields[closed_i] = to_mdy_force(fields[closed_i])

                    rows.append(fields + [cur_month])
                    prev = len(rows) - 1
                    i += 1
                    continue

                if not loc_ok:
                    if msg_i is not None and prev is not None and fields[msg_i]:
                        rows[prev][msg_i] = (rows[prev][msg_i] + " " + fields[msg_i]).strip()
                    i += 1
                    continue

            continue
        i += 1

    if rows and loc_index is not None:
        seen = set()
        dedup = []
        for r in rows:
            key = (r[loc_index], r[-1])
            if key in seen: continue
            seen.add(key)
            dedup.append(r)
        rows = dedup

    if not rows: return pd.DataFrame(columns=header + ["Month"])
    df = pd.DataFrame(rows, columns=header + ["Month"])
    
    drop_cols = [c for c in df.columns if c.strip().upper() in ("FOM", "EMAIL")]
    df = df.drop(columns=drop_cols, errors="ignore")
    
    return df


# =============================== PARSER 7: Floor Asset Details ===============================
def parse_floor_line(line: str) -> Optional[Dict[str, str]]:
    tokens = line.split()
    if len(tokens) < 15: return None
    
    if len(tokens) > 5 and tokens[3] == "Marine" and tokens[4] == "Corps":
        tokens[3] = "Marine Corps"
        del tokens[4]

    try:
        age, year, cat = tokens[-1], tokens[-2], tokens[-3]
        if not age.isdigit() or not year.isdigit(): return None

        idx = len(tokens) - 3
        foshort_tokens: List[str] = []
        fonum: Optional[str] = None
        fonum_idx: Optional[int] = None

        while idx > 0:
            token = tokens[idx - 1]
            if token.isdigit(): fonum = token; fonum_idx = idx - 1; idx -= 1; break
            else: foshort_tokens.insert(0, token); idx -= 1

        if fonum is None or fonum_idx is None: return None
        foshort = ' '.join(foshort_tokens)
        
        loc, place, region, svc, asset, serial, asset_type = tokens[0:7]

        date_pattern = re.compile(r'\d{1,2}/\d{1,2}/\d{2,4}')
        idx_desc_end: Optional[int] = None
        for i in range(7, len(tokens)):
            if date_pattern.fullmatch(tokens[i]): idx_desc_end = i; break

        if idx_desc_end is None or idx_desc_end + 6 >= len(tokens): return None

        desc = ' '.join(tokens[7:idx_desc_end])
        acquire, effective, disposed, class_num, mfg = tokens[idx_desc_end:idx_desc_end + 5]

        search_start = idx_desc_end + 5
        search_end = fonum_idx 
        
        lname_tokens = tokens[search_start:search_end]
        lname = ' '.join(lname_tokens)

    except Exception:
        return None

    return {
        'Loc': loc, 'Place': place, 'Region': region, 'SVC': svc, 'Asset': asset,
        'SerialNum': serial, 'Type': asset_type, 'Desc': desc, 'Acquire': acquire,
        'Effective': effective, 'Disposed': disposed, 'Class': class_num,
        'MFG': mfg, 'LNAME': lname, 'FONUM': fonum, 'FOSHORT': foshort,
        'Cat': cat, 'Year': year, 'Age': age,
    }

def parse_floor_details_page(page_text: str) -> List[Dict[str, str]]:
    data: List[Dict[str, str]] = []
    for line in page_text.split('\n'):
        if not line.strip(): continue
        if re.match(r'^\s*\d', line) and 'Floor' in line:
            parsed = parse_floor_line(line.strip())
            if parsed: data.append(parsed)
    return data

def extract_floor_asset_details(pdf_path: str) -> pd.DataFrame:
    print("Parsing [7/7] 'Floor Asset Details'...")
    pages = load_pages_from_pdf(pdf_path)
    month_map = detect_month_map(pages)

    floor_data: List[Dict[str, str]] = []
    for p_num, page_text in enumerate(pages, start=1):
        month_full = month_map.get(p_num)
        if not month_full: continue
        
        m = re.match(r"([A-Za-z]+)\s+(\d{4})", month_full)
        month_tag_val = fmt_month(m.group(1), m.group(2)) if m else month_full

        for rec in parse_floor_details_page(page_text):
            rec['Month'] = month_tag_val
            floor_data.append(rec)

    df = pd.DataFrame(floor_data)
    if not df.empty:
        df = df.drop_duplicates(subset=['Loc', 'Asset', 'SerialNum', 'Month'])
    return df

# =============================== MASTER EXECUTION ===============================
def run_all_parsers(pdf_path: Path):
    if not pdf_path.exists():
        print(f"🚨 Error: PDF file not found at {pdf_path}. Cannot proceed.")
        return

    # 1. Load full text once for parsers 1, 2, 3, 4, 6
    text_content = load_text_from_pdf(pdf_path)

    # 2. Execute Parsers and Save Results
    results = {}
    
    # [1] EGMs by Region, Service
    results[OUT_CSV_REGION_SERVICE] = extract_egms_by_region_service(text_content)
    
    # [2] EGMs by Field Office
    results[OUT_CSV_FIELD_OFFICE] = parse_egm_by_field_office(text_content)
    
    # [3] Installed Assets by Location, Manufacture 
    results[OUT_CSV_INSTALLED_MANUFACTURER] = parse_installed_assets(text_content, pdf_path)
    
    # [4] Asset Details (Installed Assets by Location) - Uses the corrected logic
    results[OUT_CSV_ASSET_DETAILS] = extract_asset_details(text_content)
    
    # [5] Years in Storage (EGMs Only) (Needs to re-read per page for specific detection)
    results[OUT_CSV_YEARS_STORAGE] = extract_years_in_storage(pdf_path)
    
    # [6] Site Operational Status
    results[OUT_CSV_SITE_STATUS] = extract_site_operational_status(text_content)

    # [7] Floor Asset Details (Needs page-by-page mapping)
    results[OUT_CSV_FLOOR_ASSET_DETAILS] = extract_floor_asset_details(str(pdf_path))
    
    # 3. Save all DataFrames to CSV
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total_files = 0
    total_rows = 0
    
    print("\n💾 Saving all output CSV files...")
    for out_path, df in results.items():
        if df.empty:
            print(f"⚠️  Skipped {out_path.name}: No rows extracted.")
            continue
        
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        total_files += 1
        total_rows += len(df)
        print(f"✅ Saved {len(df)} rows → {out_path.name}")

    print(f"\n🎉 ALL DONE. Successfully generated {total_files} CSV files with a total of {total_rows} rows.")

if __name__ == "__main__":
    run_all_parsers(PDF_PATH)

