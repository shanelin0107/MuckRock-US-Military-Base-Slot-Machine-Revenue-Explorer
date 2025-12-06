#!/usr/bin/env python3
# =====================================================================
# Navy Report — One Script for:
#   1) Slot Machine Results – Navy         → <PDF stem>_slot_results.csv
#   2) NAFI Reimbursement from ARMP        → <PDF stem>_nafi_reimbursements.csv
#   3) Monthly Summary by Location  → monthly_summary_master.csv
#
# Works for both FY20–FY24-1 and FY20–FY24-2 PDFs.
# - Slot/NAFI
# - Monthly Summary
#
# Requirements:
#   - Poppler `pdftotext` on PATH
#   - pandas installed
# =====================================================================

import re
import subprocess
from pathlib import Path
from collections import defaultdict
import pandas as pd

# =========================================================
# CONFIG (edit PDF_PATH if needed)
# =========================================================
PDF_PATH = Path(r"D:\venv\ds701\Navy Report\Navy Revenue Report FY20-FY24-1.pdf")
OUT_DIR  = PDF_PATH.parent


def normalize_dashes(s: str) -> str:
    return s.replace("–", "-").replace("—", "-")

def extract_pdf_text(pdf_path: Path) -> str:
    return subprocess.check_output(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        universal_newlines=True, errors="ignore"
    )

def extract_pdf_lines_layout(pdf_path: Path):
    """Layout-preserving lines for table parsing."""
    text = extract_pdf_text(pdf_path)
    return normalize_dashes(text).split("\n")

# =========================================================
# -------------------- PART A: SLOT / NAFI -----------------
# =========================================================
SECTION_SLOT = "Slot Machine Results - Navy"
SECTION_NAFI = "NAFI Reimbursement from ARMP"
REPORT_TITLE = "ARMP Navy Slot Report"

FY_TOKEN = re.compile(r"(FY\d{2}\s+thru\s+SEP|ANNUALIZED\s+FY\d{2}|FY\d{2})", re.IGNORECASE)
NUM_TOKEN = re.compile(r"^\(?-?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\)?$")
MONEY_OR_DASH = re.compile(r"^\(?-?[\d,]+(?:\.\d{2})?\)?$|^-?$")

def parse_value(val: str):
    val = val.strip().replace("$", "")
    if not val or val == "-":
        return ""
    neg = val.startswith("(") and val.endswith(")")
    if neg:
        val = val[1:-1]
    try:
        num = float(val.replace(",", ""))
        return -num if neg else num
    except ValueError:
        return ""

def is_section_header(line: str) -> bool:
    s = line.strip()
    return (SECTION_SLOT in s) or (SECTION_NAFI in s) or (REPORT_TITLE in s)

def grab_header_columns(lines, start_idx):
    """Find header and extract FY columns dynamically."""
    header_idx = -1
    for k in range(start_idx, min(start_idx + 25, len(lines))):
        if "Country" in lines[k] and "Installation" in lines[k]:
            header_idx = k
            break
    if header_idx == -1:
        return -1, []

    # Merge header and continuation lines
    header_block = lines[header_idx]
    for off in (1, 2):
        if header_idx + off < len(lines):
            nxt = lines[header_idx + off]
            if any(x in nxt for x in ["FY", "SEP", "ANNUALIZED"]):
                header_block += "  " + nxt

    # Detect all FY-like tokens
    raw_cols = [m.group(0) for m in FY_TOKEN.finditer(header_block)]
    cleaned = []
    for c in raw_cols:
        c2 = re.sub(r"\s+", " ", c.strip().upper())
        if "THRU" in c2:
            m = re.search(r"FY(\d{2})", c2)
            if m:
                cleaned.append(f"FY{m.group(1)} thru SEP")
        elif "ANNUALIZED" in c2:
            m = re.search(r"FY(\d{2})", c2)
            if m:
                cleaned.append(f"ANNUALIZED FY{m.group(1)}")
        else:
            m = re.fullmatch(r"FY(\d{2})", c2)
            if m:
                cleaned.append(f"FY{m.group(1)}")

    seen = set()
    expected = []
    for c in cleaned:
        if c not in seen:
            seen.add(c)
            expected.append(c)
    return header_idx, expected

def parse_block_rows(lines, body_start, expected_cols):
    rows = []
    for k in range(body_start, len(lines)):
        row_line = lines[k]
        if not row_line.strip() or "Total" in row_line or is_section_header(row_line):
            break

        tokens = row_line.strip().split()
        if len(tokens) < 3:
            continue

        country = tokens[0]
        i = 1
        inst_parts = []
        while i < len(tokens):
            tok = tokens[i]
            if MONEY_OR_DASH.match(tok):
                break
            inst_parts.append(tok)
            i += 1

        installation = " ".join(inst_parts).strip()
        if not installation:
            continue

        number_tokens = tokens[i:]
        numbers = []
        for tok in number_tokens:
            clean = re.sub(r"[^\d,\.\(\)\-]", "", tok)
            if NUM_TOKEN.match(clean) or clean == "-":
                numbers.append(clean)

        values = [parse_value(x) for x in numbers]
        if len(values) < len(expected_cols):
            values += [""] * (len(expected_cols) - len(values))
        elif len(values) > len(expected_cols):
            values = values[:len(expected_cols)]

        row = {"Country": country, "Installation": installation}
        for c, v in zip(expected_cols, values):
            row[c] = v
        rows.append(row)
    return rows

def extract_section(lines, section_title):
    rows_all = []
    for i, line in enumerate(lines):
        if section_title in line:
            header_idx, expected_cols = grab_header_columns(lines, i)
            if header_idx == -1 or not expected_cols:
                continue
            rows = parse_block_rows(lines, header_idx + 1, expected_cols)
            if not rows:
                rows = parse_block_rows(lines, header_idx + 2, expected_cols)
            for r in rows:
                r["_cols"] = tuple(expected_cols)
            rows_all.extend(rows)
    return rows_all

def merge_blocks(rows):
    merged = defaultdict(dict)
    all_cols = set(["Country", "Installation"])
    for r in rows:
        key = (r["Country"], r["Installation"])
        merged[key]["Country"] = r["Country"]
        merged[key]["Installation"] = r["Installation"]
        for c in r.get("_cols", []):
            merged[key][c] = r.get(c, "")
            all_cols.add(c)
    return merged, all_cols

def ordered_columns(cols):
    cols = set(cols)
    base = ["Country", "Installation"]

    def year_of(label, kind):
        if kind == "bare":
            m = re.fullmatch(r"FY(\d{2})", label)
        elif kind == "sep":
            m = re.fullmatch(r"FY(\d{2}) thru SEP", label)
        else:
            m = re.fullmatch(r"ANNUALIZED FY(\d{2})", label)
        return int(m.group(1)) if m else None

    bare = sorted([c for c in cols if year_of(c, "bare")], key=lambda x: year_of(x, "bare"))
    sep  = sorted([c for c in cols if year_of(c, "sep")],  key=lambda x: year_of(x, "sep"))
    ann  = sorted([c for c in cols if year_of(c, "ann")],  key=lambda x: year_of(x, "ann"))

    wanted = base + bare + sep + ann
    leftovers = [c for c in cols if c not in wanted]
    return wanted + sorted(leftovers)

def run_slot_nafi(pdf_path: Path, out_dir: Path):
    lines = extract_pdf_lines_layout(pdf_path)

    slot_rows = extract_section(lines, SECTION_SLOT)
    nafi_rows = extract_section(lines, SECTION_NAFI)

    slot_merged, slot_cols = merge_blocks(slot_rows)
    nafi_merged, nafi_cols = merge_blocks(nafi_rows)

    slot_df = pd.DataFrame(slot_merged.values())
    nafi_df = pd.DataFrame(nafi_merged.values())

    slot_df = slot_df.reindex(columns=ordered_columns(slot_cols))
    nafi_df = nafi_df.reindex(columns=ordered_columns(nafi_cols))

    slot_out = out_dir / f"{pdf_path.stem}_slot_results.csv"
    nafi_out = out_dir / f"{pdf_path.stem}_nafi_reimbursements.csv"

    slot_df.to_csv(slot_out, index=False)
    nafi_df.to_csv(nafi_out, index=False)

    return slot_out, nafi_out

# =========================================================
# ------------ PART B: MONTHLY SUMMARY ------------
# =========================================================
re_hdr_main  = re.compile(r"^ARMP Navy Slot Report$")
re_hdr_sub   = re.compile(r"^Monthly Summary by Location$")
re_month     = re.compile(r"^[A-Za-z]{3}-\d{2}$")
re_code6     = re.compile(r"^\d{6}$")
re_loc4      = re.compile(r"^\d{4}$")
re_nums      = re.compile(r"\(?-?\d{1,3}(?:,\d{3})*(?:\.\d+)?\)?")
re_find_mon  = re.compile(r"([A-Za-z]{3}-\d{2})")
re_any_code6 = re.compile(r"\b\d{6}\b")

def clean_number(x):
    """Keep parentheses as printed; return numeric-looking fields as the same text (no commas)."""
    if pd.isna(x):
        return pd.NA
    s = str(x).strip().replace(",", "").replace("$", "")
    if re.fullmatch(r"\(?-?\d+(?:\.\d+)?\)?", s):
        return s
    try:
        return float(s)
    except:
        return s

def extract_number_tokens(tail):
    toks = re_nums.findall(tail)
    return [t.replace(",", "").replace("$", "").strip() for t in toks]

def month_to_date(m):
    try:
        mon, yr = m.split('-')
        yr = int(yr)
        yr = 2000 + yr if yr < 50 else 1900 + yr
        return pd.to_datetime(f"01-{mon}-{yr}", format="%d-%b-%Y", errors="coerce")
    except:
        return pd.NaT

def is_sep_month(m):
    try:
        return str(m).split("-")[0].lower().startswith("sep")
    except:
        return False

def map_tokens(month, toks):
    """v12.8 mapping rules (Sep-specific behavior)."""
    rev = nafi = annr = annn = pd.NA
    n = len(toks)
    if n >= 4:
        last4 = toks[-4:]
        rev, nafi, annr, annn = last4
    elif n == 3:
        if is_sep_month(month):
            rev, nafi, annr = toks[0], toks[1], toks[2]
        else:
            rev, nafi, annr = toks[0], toks[1], toks[2]
    elif n == 2:
        if is_sep_month(month):
            annr, annn = toks[0], toks[1]
        else:
            rev, nafi = toks[0], toks[1]
    elif n == 1:
        if is_sep_month(month):
            annr = toks[0]
        else:
            rev = toks[0]
    return rev, nafi, annr, annn

def run_monthly_summary(pdf_path: Path, out_dir: Path):
    print("🔍 Extracting Monthly Summary (v12.8) ...")
    txt = extract_pdf_text(pdf_path)
    lines = [ln.strip() for ln in txt.split("\n") if ln.strip()]

    rows = []
    installation = locno = location = site_code = full_loc = None
    last_month = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect new Installation block
        if re_hdr_main.match(line):
            for j in range(1, 6):
                if i + j < len(lines) and re_hdr_sub.match(lines[i + j]):
                    k = i + j + 1
                    while k < len(lines) and not lines[k].strip():
                        k += 1
                    if k < len(lines):
                        installation = lines[k].strip()
                        locno = location = site_code = full_loc = None
                        last_month = None
                    i = k
                    break
            i += 1
            continue

        # Skip headers and totals
        if "Loc #" in line or "Total for Current Period" in line:
            i += 1
            continue

        # Handle Temp Closed lines
        if "Temp Closed" in line:
            mmon = re_find_mon.search(line)
            month = mmon.group(1) if mmon else last_month
            rows.append({
                "Installation": installation, "Loc#": locno, "Location": full_loc,
                "Month": month, "Revenue": pd.NA, "NAFI Amt": pd.NA,
                "Annual Revenue": pd.NA, "Annual NAFI": pd.NA, "Status": "Temp Closed"
            })
            last_month = month
            i += 1
            continue

        parts = line.split()

        # New Loc# + Location
        if parts and re_loc4.match(parts[0]):
            locno = parts[0]
            loc_tokens, j = [], 1
            while j < len(parts) and not (re_month.match(parts[j]) or re_code6.match(parts[j])):
                loc_tokens.append(parts[j]); j += 1

            site_code = None
            if j < len(parts) and re_code6.match(parts[j]):
                site_code = parts[j]; j += 1

            location = " ".join(loc_tokens).strip()
            full_loc = f"{location} {site_code}".strip() if site_code else location

            if j < len(parts) and re_month.match(parts[j]):
                month = parts[j]; tail = " ".join(parts[j + 1:])
            else:
                i += 1; continue

            toks = extract_number_tokens(tail)
            rev, nafi, annr, annn = map_tokens(month, toks)

            rows.append({
                "Installation": installation, "Loc#": locno, "Location": full_loc,
                "Month": month, "Revenue": rev, "NAFI Amt": nafi,
                "Annual Revenue": annr, "Annual NAFI": annn, "Status": ""
            })
            last_month = month; i += 1; continue

        
        if parts and re_code6.match(parts[0]) and len(parts) > 1 and re_month.match(parts[1]):
            site_code = parts[0]
            full_loc = f"{location} {site_code}".strip()
            if rows and rows[-1]["Loc#"] == locno and site_code not in str(rows[-1]["Location"]):
                rows[-1]["Location"] = f"{rows[-1]['Location']} {site_code}".strip()
            month = parts[1]; tail = " ".join(parts[2:])

            toks = extract_number_tokens(tail)
            rev, nafi, annr, annn = map_tokens(month, toks)

            rows.append({
                "Installation": installation, "Loc#": locno, "Location": full_loc,
                "Month": month, "Revenue": rev, "NAFI Amt": nafi,
                "Annual Revenue": annr, "Annual NAFI": annn, "Status": ""
            })
            last_month = month; i += 1; continue

        if parts and re_month.match(parts[0]):
            month = parts[0]; tail = " ".join(parts[1:])
            toks = extract_number_tokens(tail)
            rev, nafi, annr, annn = map_tokens(month, toks)

            rows.append({
                "Installation": installation, "Loc#": locno, "Location": full_loc,
                "Month": month, "Revenue": rev, "NAFI Amt": nafi,
                "Annual Revenue": annr, "Annual NAFI": annn, "Status": ""
            })
            last_month = month; i += 1; continue

        i += 1

    df = pd.DataFrame(rows)
    df[["Installation", "Loc#", "Location"]] = df[["Installation", "Loc#", "Location"]].ffill()

    # Clean numerics (keep parentheses as-is)
    for c in ["Revenue", "NAFI Amt", "Annual Revenue", "Annual NAFI"]:
        df[c] = df[c].apply(clean_number)

    # Unique months
    df["MonthDate"] = df["Month"].apply(month_to_date)
    df = df.sort_values(["Installation", "Loc#", "Location", "MonthDate"])
    df = df.drop_duplicates(subset=["Installation", "Loc#", "Location", "Month"], keep="last")
    df = df.drop(columns=["MonthDate"])

    # ===================== YOKOSUKA CLEANUP =====================
    def yokosuka_row_is_bad(row) -> bool:
        if str(row["Installation"]).strip().lower() != "yokosuka":
            return False
        loc = str(row["Location"])
        if re_any_code6.search(loc):  # keep rows with site code
            return False
        return bool(re.search(r"(oct\s*15|o\s*t\s*15)", loc.lower()))

    df = df[~df.apply(yokosuka_row_is_bad, axis=1)].reset_index(drop=True)

    # ================= Souda Bay fix =================
    def is_souda_graffiti_no_code(row) -> bool:
        if str(row["Installation"]).strip().lower() != "souda bay":
            return False
        loc = str(row["Location"]).lower()
        return ("graffiti" in loc and "shipmate" in loc) and (re_any_code6.search(loc) is None)

    df = df[~df.apply(is_souda_graffiti_no_code, axis=1)].reset_index(drop=True)

    # ================= Sasebo fix =================
    def is_sasebo_bc_no_code(row) -> bool:
        if str(row["Installation"]).strip().lower() != "sasebo":
            return False
        loc = str(row["Location"]).lower()
        looks_bc = bool(re.search(r"sasebo\s+b\s*/?\s*c\b", loc))
        return looks_bc and (re_any_code6.search(loc) is None)

    df = df[~df.apply(is_sasebo_bc_no_code, axis=1)].reset_index(drop=True)

    # ================= Atsugi "None 401401" fix =================
    def is_atsugi_none_code(row) -> bool:
        if str(row["Installation"]).strip().lower() != "atsugi":
            return False
        if str(row["Loc#"]).strip() != "3079":
            return False
        loc = str(row["Location"]).strip().lower()
        return bool(re.match(r"^none\s+\d{6}$", loc))

    df = df[~df.apply(is_atsugi_none_code, axis=1)].reset_index(drop=True)

    # ================= Atsugi duplicate Club Trilogy fix =================
    mask_dup = df.apply(
        lambda r: (
            str(r["Installation"]).strip().lower() == "atsugi"
            and str(r["Loc#"]).strip() == "3079"
            and str(r["Location"]).strip().lower() == "club trilogy"
            and any(
                (df["Installation"].str.lower() == "atsugi")
                & (df["Loc#"].astype(str) == "3079")
                & (df["Month"] == r["Month"])
                & (df["Location"].str.lower().str.contains("club trilogy 401401"))
            )
        ),
        axis=1,
    )
    df = df[~mask_dup].reset_index(drop=True)

    out_csv = out_dir / f"{pdf_path.stem}_monthly_summary_master.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    return out_csv, len(df), df["Installation"].nunique()

# =========================================================
# ---------------------------- RUN ------------------------
# =========================================================
if __name__ == "__main__":
    # Part A: Slot + NAFI
    slot_out, nafi_out = run_slot_nafi(PDF_PATH, OUT_DIR)

    # Part B: Monthly Summary 
    monthly_out, n_rows, n_inst = run_monthly_summary(PDF_PATH, OUT_DIR)

    print("\n✅ CSV files created successfully!")
    print(f" - Slot Results:         {slot_out}")
    print(f" - NAFI Reimbursements:  {nafi_out}")
    print(f" - Monthly Summary:      {monthly_out}")
    print(f"   Rows: {n_rows} | Installations: {n_inst}")
