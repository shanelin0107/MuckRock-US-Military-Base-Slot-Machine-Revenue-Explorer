#!/usr/bin/env python3
# =============================================================================
# FY2022 Asset Reports — ALL EXTRACTORS (single script)
#
# Generates the following outputs from one PDF:
#   1) assets_by_region_service.csv
#   2) assets_by_field_office.csv
#   3) asset_details.csv
#   4) floor_asset_details.csv (+ floor_asset_details.xlsx if xlsxwriter available)
#   5) site_operational_status.csv
#
# Requirements:
#   - Poppler `pdftotext` on PATH
#   - Python 3.x
#   - pandas (for Table 1 + Field Office preview/DF handling)
#   - xlsxwriter (optional; for the XLSX export in Floor Asset Details)
# =============================================================================

import re
import csv
import subprocess
from pathlib import Path
from datetime import datetime

import pandas as pd

try:
    import xlsxwriter  # optional for XLSX export
except ImportError:
    xlsxwriter = None

# ---------- GLOBAL CONFIG ----------
PDF_PATH = Path(r"D:/venv/ds701/asset/FY2022 Asset Reports.pdf")
OUT_DIR  = Path(r"D:/venv/ds701/asset")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================ #
#                            SHARED SMALL HELPERS                              #
# ============================================================================ #

def pdftotext_layout_to_string(pdf_path: Path) -> str:
    """Return pdftotext -layout output for a PDF as a single string."""
    return subprocess.check_output(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        text=True, errors="ignore"
    ).replace("\r", "")

def mon_abbr(name: str) -> str:
    n = name.strip().lower()
    full = ["january","february","march","april","may","june","july",
            "august","september","october","november","december"]
    abbr = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for i, m in enumerate(full):
        if n.startswith(m[:3]):
            return abbr[i]
    return name[:3].title()

def to_mdy_force(s: str) -> str:
    """Force M/D/YYYY from a string containing a date; leave as trimmed if unparseable."""
    if not s:
        return ""
    t = "".join(ch if ch.isdigit() else "/" for ch in str(s))
    m = re.match(r"^\s*(\d{1,2})/(\d{1,2})/(\d{2,4})", t)
    if not m:
        # light clean
        return re.sub(r"[ \t\r\f\v]+"," ", str(s)).strip()
    mm, dd, yy = map(int, m.groups())
    if yy < 100:
        yy = 2000 + yy if yy < 70 else 1900 + yy
    return f"{mm}/{dd}/{yy}"

# ============================================================================ #
# 1) Table 1 — EGMs by Region, Service → assets_by_region_service.csv          #
# ============================================================================ #

def extract_table1_assets_by_region_service(pdf_path: Path, out_csv: Path):
    RE_T1_HDR = re.compile(r"^EGMs\s+by\s+Region,\s*Service", re.I)
    RE_T2_HDR = re.compile(r"^EGMs\s+by\s+Field\s+Office", re.I)
    RE_MONTH  = re.compile(r"for\s+month\s+of\s+([A-Za-z]+)\s+(\d{4})", re.I)
    RE_SKIP   = re.compile(r"^(Slots|Army|Navy|Marine|Airforce|#\s*Locations)$", re.I)

    def fmt_month(mon, yr): return f"{mon[:3].title()}-{yr[-2:]}"

    def parse_region_line(region, tail):
        mloc = re.search(r"\d+", tail)
        if not mloc:
            return None
        loc = mloc.group(0)
        rest = tail[mloc.end():]
        nums = re.findall(r"\d+(?:\.\d+)?%?", rest)
        if not nums:
            return None
        percent = nums[-1].replace("%", "")
        vals = nums[:-1]
        army = navy = marine = air = total = ""
        if len(vals) == 3:
            army, navy, total = vals
        elif len(vals) == 4:
            army, navy, marine, total = vals
        elif len(vals) >= 5:
            army, navy, marine, air, total = vals[:5]
        return {
            "Region": region, "#Location": loc,
            "Army": army, "Navy": navy, "Marine_Corps": marine,
            "Airforce": air, "Total": total, "Percent": percent
        }

    print("🔍 [1/5] Extracting: EGMs by Region, Service …")
    text = pdftotext_layout_to_string(pdf_path)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    rows, block = [], []
    current_month = ""

    def detect_month_from_text(line):
        m = RE_MONTH.search(line)
        return fmt_month(m.group(1), m.group(2)) if m else None

    def flush_block(month):
        for ln in block:
            if RE_SKIP.match(ln):
                continue
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
        if m:
            current_month = m
        if RE_T1_HDR.search(ln):
            in_block, block = True, []
            continue
        if in_block and RE_T2_HDR.search(ln):
            flush_block(current_month)
            in_block, block = False, []
            continue
        if in_block:
            block.append(ln)
    if in_block:
        flush_block(current_month)

    df = pd.DataFrame(rows, columns=[
        "Region", "#Location", "Army", "Navy",
        "Marine_Corps", "Airforce", "Total", "Percent", "Month"
    ])
    df.to_csv(out_csv, index=False)
    print(f"✅ Saved {out_csv}  Rows:{len(df)}")

# ============================================================================ #
# 2) EGMs by Field Office → assets_by_field_office.csv                          #
# ============================================================================ #

def extract_assets_by_field_office(pdf_path: Path, out_csv: Path):
    print("🔍 [2/5] Extracting: EGMs by Field Office …")
    RE_EGM_FO_HDR   = re.compile(r"^\s*EGMs\s+by\s+Field\s+Office\b", re.I)
    RE_MONTH_LINE   = re.compile(r"for\s+month\s+of\s+([A-Za-z]+)\s+(\d{4})", re.I)
    RE_REGION_LINE  = re.compile(r"^\s*(Europe|Japan|Korea)\s*(?:\s+Slots\s+ACM\s+ITC\s+FRS\s+Total)?\s*$", re.I)
    RE_FO_ROW       = re.compile(
        r"^\s*(\d{1,3})\s+([A-Z0-9'&\.\-\/ ]*?[A-Z0-9])\s+"
        r"(\d{1,4})\s+(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})\s+(\d{1,4})\s*$"
    )
    RE_REGION_TOTAL = re.compile(
        r"^\s*(Europe|Japan|Korea)\s+Total\s+(\d{1,4})\s+(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})\s+(\d{1,4})\s*$",
        re.I
    )
    RE_PCT_LINE     = re.compile(r"^\s*(\d{1,3})%\s+(\d{1,3})%\s+(\d{1,3})%\s+(\d{1,3})%\s+(\d{1,3})%\s*$")
    RE_NEXT_SECTION = re.compile(
        r"^\s*(Installed\s+Assets|EGMs\s+by\s+Region|REGION\s+FONUM|Years\s+in\s+Storage|Site\s+Operational\s+Status)\b",
        re.I
    )

    MONTH_MAP = {
        'January':'Jan','February':'Feb','March':'Mar','April':'Apr','May':'May','June':'Jun',
        'July':'Jul','August':'Aug','September':'Sep','October':'Oct','November':'Nov','December':'Dec'
    }
    def month_tag(mon_str, year_str):
        mon = MONTH_MAP.get(mon_str.strip().title(), mon_str.strip()[:3].title())
        yy  = year_str[-2:]
        return f"{mon}-{yy}"

    text = pdftotext_layout_to_string(pdf_path)
    lines = text.split("\n")

    rows = []
    in_section = False
    cur_month = None
    cur_region = None
    just_saw_region = False

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # header start
        if not in_section and RE_EGM_FO_HDR.search(line):
            found_month = None
            for j in range(i, min(i+6, len(lines))):
                m = RE_MONTH_LINE.search(lines[j])
                if m:
                    found_month = month_tag(m.group(1), m.group(2))
                    break
            if found_month:
                in_section = True
                cur_month = found_month
                cur_region = None
                i += 1
                continue

        if in_section:
            if RE_NEXT_SECTION.search(line):
                in_section = False
                cur_month = None
                cur_region = None
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
                    "Region": cur_region,
                    "FO#": int(mfo.group(1)),
                    "FOSHORT": mfo.group(2).strip(),
                    "Slots": int(mfo.group(3)),
                    "ACM_CountR": int(mfo.group(4)),
                    "ITC": int(mfo.group(5)),
                    "FRS": int(mfo.group(6)),
                    "Total": int(mfo.group(7)),
                    "Month": cur_month
                })
                i += 1
                continue

            mtot = RE_REGION_TOTAL.match(line)
            if mtot and cur_month:
                reg_name = mtot.group(1).title()
                rows.append({
                    "Region": reg_name,
                    "FO#": "",
                    "FOSHORT": f"{reg_name} Total",
                    "Slots": int(mtot.group(2)),
                    "ACM_CountR": int(mtot.group(3)),
                    "ITC": int(mtot.group(4)),
                    "FRS": int(mtot.group(5)),
                    "Total": int(mtot.group(6)),
                    "Month": cur_month
                })
                i += 1
                if i < len(lines):
                    mp = RE_PCT_LINE.match(lines[i].strip())
                    if mp:
                        rows.append({
                            "Region": reg_name,
                            "FO#": "",
                            "FOSHORT": "%",
                            "Slots": mp.group(1) + "%",
                            "ACM_CountR": mp.group(2) + "%",
                            "ITC": mp.group(3) + "%",
                            "FRS": mp.group(4) + "%",
                            "Total": mp.group(5) + "%",
                            "Month": cur_month
                        })
                        i += 1
                continue

        i += 1

    df = pd.DataFrame(rows, columns=[
        "Region","FO#","FOSHORT","Slots","ACM_CountR","ITC","FRS","Total","Month"
    ])
    df.to_csv(out_csv, index=False)
    print(f"✅ Saved {out_csv}  Rows:{len(df)}")

# ============================================================================ #
# 3) Installed Assets by Location, Manufacture → asset_details.csv              #
# ============================================================================ #

def extract_installed_assets_details(pdf_path: Path, out_csv: Path, keep_months=None):
    print("🔍 [3/5] Extracting: Installed Assets by Location, Manufacture …")

    RE_TITLE = re.compile(r"Installed\s+Assets\s+by\s+Location", re.I)
    RE_DETAIL_HEADER = re.compile(
        r"^\s*REGION\s+FONUM\s+FOSHORT\s+Loc\s+LNAME\s+Asset\s+Class\s+Desc\s+Type\s+Aquire\s+Effective\s+SerialNum\s+PLACE\s+Age\s+Years\s+in\s+Storage\s+Months",
        re.I,
    )
    HEADER_TOKENS = [
        "REGION","FONUM","FOSHORT","Loc","LNAME","Asset","Class","Desc","Type",
        "Aquire","Effective","SerialNum","PLACE","Age","Years in Storage","Months"
    ]
    RE_STOP = re.compile(
        r"^(?:\s*$|EGM\s+Years\s+in\s+Storage|Years\s+in\s+Storage|Site\s+Operational\s+Status|EGMs\s+by|Installed\s+Assets\s+by\s+Location)",
        re.I,
    )

    def mon_abbr_from_number(n): 
        return ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][n-1]

    def month_labels_from_report_date(s):
        try:
            dt = datetime.strptime(s.strip(), "%m/%d/%Y")
            return f"{mon_abbr_from_number(dt.month)}-{str(dt.year)[-2:]}", f"{mon_abbr_from_number(dt.month)}-{dt.year}"
        except:
            return None, None

    def find_report_date_at_line_end(line):
        m = re.search(r"(\d{1,2}/\d{1,2}/\d{4})\s*$", line)
        return (line[:m.start()].rstrip(), m.group(1)) if m else (line.rstrip("\n"), None)

    def compute_slices(header_line, tokens):
        starts, pos = [], 0
        for tok in tokens:
            idx = header_line.find(tok, pos)
            if idx == -1:
                width = max(1, len(header_line)//len(tokens))
                starts = [i*width for i in range(len(tokens))]
                break
            starts.append(idx); pos = idx + len(tok)
        ends = starts[1:] + [None]
        return list(zip(starts, ends))

    def slice_line(line, ranges): return [(line[s:e] if e is not None else line[s:]) for (s, e) in ranges]
    def trim_edges(fields): return [f.strip() for f in fields]

    NUM_F = re.compile(r"[-+]?\d+(?:\.\d+)?")
    def clean_months_cell(x: str) -> str:
        m = NUM_F.search(x or "")
        return m.group(0) if m else ""

    text = pdftotext_layout_to_string(pdf_path)
    lines = text.splitlines()

    rows, i = [], 0
    while i < len(lines):
        line = lines[i]
        if RE_TITLE.search(line):
            j, header_line = i + 1, None
            for k in range(j, min(j + 40, len(lines))):
                if RE_DETAIL_HEADER.search(lines[k]):
                    header_line, j = lines[k], k + 1
                    break
            if not header_line:
                i += 1; continue

            header_pure, date_str = find_report_date_at_line_end(header_line)
            month_disp, month_filt = month_labels_from_report_date(date_str) if date_str else (None, None)

            ranges = compute_slices(header_pure, HEADER_TOKENS)
            ncols = len(HEADER_TOKENS)

            while j < len(lines):
                raw, s = lines[j], lines[j].strip()
                if not s or RE_STOP.search(s): break

                fields = slice_line(raw, ranges)
                fields = trim_edges(fields)

                if len(fields) > ncols:
                    extra = " ".join(fields[ncols:])
                    fields = fields[:ncols]
                    fields[7] = (fields[7] + " " + extra).rstrip()
                elif len(fields) < ncols:
                    fields += [""] * (ncols - len(fields))

                fields[15] = clean_months_cell(fields[15])
                fields.append(month_filt if keep_months else month_disp)

                rows.append(fields)
                j += 1
            i = j; continue
        i += 1

    if keep_months:
        rows = [r for r in rows if r[-1] in keep_months]

    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(HEADER_TOKENS + ["Month"])
        w.writerows(rows)
    print(f"✅ Saved {out_csv}  Rows:{len(rows)}")

# ============================================================================ #
# 4) Floor Asset Details → floor_asset_details.csv (+ .xlsx)                    #
# ============================================================================ #

def extract_floor_asset_details(pdf_path: Path, out_csv: Path, out_xlsx: Path, keep_months):
    print("🔍 [4/5] Extracting: Floor Asset Details …")

    COLS = [
        "Loc","PLACE","REGION","SVC","Asset","SerialNum","Type","Desc","Aquire",
        "Effective","Disposed","Class","MFG","LNAME","FONUM","FOSHORT","Cat","Year","Age"
    ]
    HDR_TEXT = "Loc PLACE REGION SVC Asset SerialNum Type Desc Aquire Effective Disposed Class MFG LNAME FONUM FOSHORT Cat Year Age"

    RE_MONTH = re.compile(r"for\s+month\s+of\s+([A-Za-z]+)\s+(\d{4})", re.I)
    RE_HDR   = re.compile(
        r"^\s*Loc\s+PLACE\s+REGION\s+SVC\s+Asset\s+SerialNum\s+Type\s+Desc\s+Aquire\s+Effective\s+Disposed\s+Class\s+MFG\s+LNAME\s+FONUM\s+FOSHORT\s+Cat\s+Year\s+Age",
        re.I,
    )
    RE_END   = re.compile(
        r"^(?:\s*$|Years\s+in\s+Storage|EGMs\s+by|Installed\s+Assets\s+by|Site\s+Operational\s+Status|REGION\s+FONUM\s+FOSHORT)",
        re.I,
    )

    def month_label(m: str, y: str) -> str:
        return f"{mon_abbr(m)}-{y}"

    def compute_slices(header_line: str):
        tokens = HDR_TEXT.split()
        starts, pos = [], 0
        for tok in tokens:
            idx = header_line.find(tok, pos)
            if idx == -1:
                width = max(1, len(header_line)//len(tokens))
                starts = [i*width for i in range(len(tokens))]
                break
            starts.append(idx); pos = idx + len(tok)
        ends = starts[1:] + [None]
        return list(zip(starts, ends))

    def slice_line(line: str, ranges):
        return [(line[s:e] if e is not None else line[s:]) for (s, e) in ranges]

    def clean_edges(fields):
        return [f.lstrip().rstrip() for f in fields]

    def fix_mfg_splits(fields):
        if len(fields) < len(COLS):
            fields += [""] * (len(COLS) - len(fields))
        cls = fields[11].strip()
        mfg = fields[12].strip()
        lname = fields[13]

        m_tail = re.fullmatch(r"(\d+)\s+([A-Z])", cls)
        if m_tail and 1 <= len(mfg) <= 2 and mfg.isalpha() and mfg.isupper():
            digits, letter = m_tail.groups()
            fields[11] = digits
            fields[12] = letter + mfg
            return fields

        if len(mfg) == 1 and mfg.isalpha() and mfg.isupper():
            first = lname.split(" ", 1)[0].strip()
            if 1 <= len(first) <= 2 and first.isalpha() and first.isupper():
                fields[12] = mfg + first
                fields[13] = lname[len(first):].lstrip()
                return fields
        return fields

    text = pdftotext_layout_to_string(pdf_path)
    lines = text.splitlines()

    rows, cur_month = [], None
    i = 0
    while i < len(lines):
        line = lines[i]
        m = RE_MONTH.search(line)
        if m:
            cur_month = month_label(m.group(1), m.group(2))

        if RE_HDR.match(line):
            ranges = compute_slices(line)
            i += 1
            prev_row_idx = None
            while i < len(lines):
                raw = lines[i]
                s = raw.strip()
                if not s or RE_END.match(s) or RE_HDR.match(raw):
                    break

                fields = slice_line(raw.rstrip("\n"), ranges)

                if fields[0].strip() == "":
                    if prev_row_idx is not None:
                        rows[prev_row_idx][7] = (rows[prev_row_idx][7] + raw).rstrip("\n")
                    i += 1
                    continue

                fields = clean_edges(fields)

                if len(fields) < len(COLS):
                    fields += [""] * (len(COLS) - len(fields))
                elif len(fields) > len(COLS):
                    extra = " ".join(fields[len(COLS):])
                    fields = fields[:len(COLS)]
                    fields[7] = (fields[7] + " " + extra).rstrip()

                fields[8] = to_mdy_force(fields[8])    # Aquire
                fields[9] = to_mdy_force(fields[9])    # Effective

                fields = fix_mfg_splits(fields)

                fields.append(cur_month)

                rows.append(fields)
                prev_row_idx = len(rows) - 1
                i += 1
            continue
        i += 1

    if keep_months:
        rows = [r for r in rows if r[-1] in keep_months]

    # second pass date normalization
    for r in rows:
        r[8] = to_mdy_force(r[8])
        r[9] = to_mdy_force(r[9])

    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(COLS + ["Month"])
        w.writerows(rows)
    print(f"✅ Saved {out_csv}  Rows:{len(rows)}  Cols:{len(COLS)+1}")

    if xlsxwriter:
        wb = xlsxwriter.Workbook(str(out_xlsx))
        ws = wb.add_worksheet("floor_asset_details")
        text_fmt = wb.add_format({"num_format": "@"})
        for c, h in enumerate(COLS + ["Month"]):
            ws.write(0, c, h, text_fmt)
        for r, row in enumerate(rows, start=1):
            for c, val in enumerate(row):
                ws.write(r, c, str(val), text_fmt)
        widths = {"Asset":12, "SerialNum":20, "Desc":46, "Aquire":11, "Effective":11, "Disposed":11}
        idx = {name: i for i, name in enumerate(COLS + ["Month"])}
        for name, w in widths.items():
            if name in idx:
                ws.set_column(idx[name], idx[name], w)
        wb.close()
        print(f"✅ Saved {out_xlsx} (all cells TEXT)")
    else:
        print("ℹ️ xlsxwriter not installed — skipping XLSX (pip install xlsxwriter)")

# ============================================================================ #
# 5) Site Operational Status → site_operational_status.csv                      #
# ============================================================================ #

def extract_site_operational_status(pdf_path: Path, out_csv: Path, keep_months):
    print("🔍 [5/5] Extracting: Site Operational Status …")
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
    LOC_LETTER   = re.compile(r"^(\d+)\s+([A-Za-z])$")
    LOC_VALID    = re.compile(r"^\d{3,5}(?:\s*[A-Za-z])?$")
    REGION_WORD  = re.compile(r"^(Europe|Korea|Japan)\b", re.I)
    SECTION_CODE = re.compile(r"^[A-Z]{2}\d{2}$")
    P_SPLIT_NUM        = re.compile(r"^\d+$")
    P_PCT_PREFIX       = re.compile(r"^%+\s*")
    P_SPLIT_PCT_TAIL   = re.compile(r"^(\d+)\s*%+\s+(.+)$")
    P_CMMTY_PCT_BOTH   = re.compile(r"^(\d+)\s*%+\s+(.+)$")

    def deglitch(s: str) -> str:
        if s is None: return ""
        t = (s.replace("\u00A0"," ")
               .replace("\u200B","")
               .replace("\uFEFF","")
               .replace("\u2011","-"))
        t = re.sub(r"[ \t\r\f\v]+", " ", t)
        return t.strip()

    def month_label(m: str, y: str) -> str:
        return f"{mon_abbr(m)}-{y}"

    def is_block_end(line: str) -> bool:
        s = line.strip()
        return any(p.search(s) for p in END_MARKERS)

    def compute_slices_from_header(header_line: str):
        tokens = [t for t in SPLIT2.split(header_line.strip()) if t]
        starts, pos = [], 0
        for tok in tokens:
            idx = header_line.find(tok, pos)
            if idx == -1:
                width = max(1, len(header_line)//max(1, len(tokens)))
                starts = [i*width for i in range(len(tokens))]
                break
            starts.append(idx)
            pos = idx + len(tok)
        ends = starts[1:] + [None]
        return [t.strip() for t in tokens], list(zip(starts, ends))

    def slice_line(line: str, ranges):
        return [(line[s:e] if e is not None else line[s:]) for (s, e) in ranges]

    def trim_edges(fields):
        return [deglitch(f) for f in fields]

    def idx_like(header, pattern, default=None):
        rx = re.compile(pattern, re.I)
        for i, h in enumerate(header):
            if rx.search(h): return i
        return default

    def fix_loc_lname(fields, header):
        li = idx_like(header, r"^loc$")
        ni = idx_like(header, r"^lname$")
        if li is None or ni is None:
            return fields
        m = LOC_LETTER.match(fields[li])
        if not m:
            return fields
        num, letter = m.groups()
        fields[li] = num
        lname = fields[ni] or ""
        if lname and lname[0].isalpha():
            if lname[0].upper() != letter:
                fields[ni] = (letter + lname).lstrip()
        else:
            fields[ni] = (letter + lname).lstrip()
        return fields

    def fix_region_smssection(fields, header):
        ri = idx_like(header, r"^region$")
        si = idx_like(header, r"^sms\s*sect")
        bi = idx_like(header, r"^sms\s*bank")
        if ri is None or si is None or bi is None: return fields
        region = trim_edges([fields[ri]])[0]
        sms    = trim_edges([fields[si]])[0]
        bank   = trim_edges([fields[bi]])[0]
        if re.fullmatch(r"\d+", region) and REGION_WORD.fullmatch(sms) and SECTION_CODE.fullmatch(bank):
            fields[ri] = f"{region} {sms}"
            fields[si] = bank
            fields[bi] = ""
            return fields
        m = re.fullmatch(r"(\d+)\s+(Europe|Korea|Japan)\b", sms, flags=re.I)
        if not region and m and SECTION_CODE.fullmatch(bank):
            fields[ri] = f"{m.group(1)} {m.group(2)}"
            fields[si] = bank
            fields[bi] = ""
            return fields
        if not region and re.fullmatch(r"\d+\s+(Europe|Korea|Japan)\b", sms, flags=re.I):
            fields[ri] = sms
            fields[si] = ""
            return fields
        if re.fullmatch(r"\d+", region) and REGION_WORD.fullmatch(sms):
            fields[ri] = f"{region} {sms}"
            fields[si] = ""
            return fields
        m2 = re.fullmatch(r"(\d+)\s+(Europe|Korea|Japan)\s+([A-Z]{2}\d{2})", sms, flags=re.I)
        if not region and m2:
            fields[ri] = f"{m2.group(1)} {m2.group(2)}"
            fields[si] = m2.group(3)
            return fields
        return fields

    def fix_regnum_region(fields, header):
        gi = idx_like(header, r"^regnum$")
        ri = idx_like(header, r"^region$")
        if gi is None or ri is None: return fields
        regnum = trim_edges([fields[gi]])[0]
        region = trim_edges([fields[ri]])[0]
        mR = re.fullmatch(r"(\d+)\s+(Europe|Korea|Japan)\b", region, flags=re.I)
        if mR and (not regnum or not regnum.isdigit()):
            fields[gi] = mR.group(1)
            fields[ri] = mR.group(2)
            return fields
        mG = re.fullmatch(r"(\d+)\s+(Europe|Korea|Japan)\b", regnum, flags=re.I)
        if mG:
            fields[gi] = mG.group(1)
            fields[ri] = mG.group(2)
            return fields
        return fields

    def fix_split_cmmt(fields, header):
        si = idx_like(header, r"^split$")
        ci = idx_like(header, r"^cmmty$") or idx_like(header, r"^cm.*ty$")
        if si is None or ci is None: return fields
        split = trim_edges([fields[si]])[0]
        cm    = trim_edges([fields[ci]])[0]

        if P_SPLIT_NUM.fullmatch(split) and cm.startswith('%'):
            cm_clean = P_PCT_PREFIX.sub("", cm).strip()
            fields[si] = f"{split}%"
            fields[ci] = cm_clean
            return fields

        m = P_SPLIT_PCT_TAIL.fullmatch(split)
        if m and not cm:
            fields[si] = f"{m.group(1)}%"
            fields[ci] = m.group(2).strip()
            return fields

        m2 = P_CMMTY_PCT_BOTH.fullmatch(cm)
        if m2 and not split:
            fields[si] = f"{m2.group(1)}%"
            fields[ci] = m2.group(2).strip()
            return fields

        if P_SPLIT_NUM.fullmatch(split):
            fields[si] = f"{split}%"
            return fields

        return fields

    text = pdftotext_layout_to_string(pdf_path)
    lines = text.splitlines()

    rows, header, msg_i, cur_month = [], None, None, None
    i = 0
    while i < len(lines):
        line = lines[i]
        m = RE_MONTH.search(line)
        if m:
            cur_month = f"{mon_abbr(m.group(1))}-{m.group(2)}"

        if RE_SITE_HDR.match(line):
            # build header slices
            tokens = [t for t in re.split(r"\s{2,}", line.strip()) if t]
            starts, pos = [], 0
            for tok in tokens:
                idx = line.find(tok, pos)
                if idx == -1:
                    width = max(1, len(line)//max(1, len(tokens)))
                    starts = [i*width for i in range(len(tokens))]
                    break
                starts.append(idx); pos = idx + len(tok)
            ends = starts[1:] + [None]
            ranges = list(zip(starts, ends))
            header = [t.strip() for t in tokens]

            msg_i    = next((i for i,h in enumerate(header) if re.search(r"^message$", h, re.I)), len(header)-1)
            loc_i    = next((i for i,h in enumerate(header) if re.search(r"^loc$", h, re.I)), None)
            open_i   = next((i for i,h in enumerate(header) if re.search(r"^open$", h, re.I)), None)
            closed_i = next((i for i,h in enumerate(header) if re.search(r"^closed$", h, re.I)), None)

            i += 1
            prev = None
            while i < len(lines):
                raw = lines[i]
                if not raw.strip() or any(p.search(raw.strip()) for p in END_MARKERS) or RE_SITE_HDR.match(raw):
                    break

                fields = [(raw[s:e] if e is not None else raw[s:]) for (s, e) in ranges]
                fields = [re.sub(r"[ \t\r\f\v]+"," ", f.replace("\u00A0"," ").replace("\u200B","").replace("\uFEFF","").replace("\u2011","-")).strip() for f in fields]

                raw_loc = fields[loc_i] if loc_i is not None else ""
                loc_ok  = bool(LOC_VALID.fullmatch(raw_loc))

                if not loc_ok:
                    if fields[msg_i] and prev is not None:
                        rows[prev][msg_i] = (rows[prev][msg_i] + " " + fields[msg_i]).strip()
                    i += 1
                    continue

                if len(fields) < len(header):
                    fields += [""] * (len(header) - len(fields))
                elif len(fields) > len(header):
                    extra = " ".join(fields[len(header):]).strip()
                    fields = fields[:len(header)]
                    if extra:
                        fields[msg_i] = (fields[msg_i] + " " + extra).strip()

                fields = fix_loc_lname(fields, header)
                fields = fix_region_smssection(fields, header)
                fields = fix_regnum_region(fields, header)
                fields = fix_split_cmmt(fields, header)

                if open_i is not None and fields[open_i]:
                    fields[open_i] = to_mdy_force(fields[open_i])
                if closed_i is not None and fields[closed_i]:
                    fields[closed_i] = to_mdy_force(fields[closed_i])

                rows.append(fields + [cur_month])
                prev = len(rows) - 1
                i += 1
            continue
        i += 1

    if keep_months:
        rows = [r for r in rows if r[-1] in keep_months]

    if not rows:
        out_header = ["Loc","LNAME","PLACE","Open","Closed","KSI","CmtyNum","SVC",
                      "FONUM","FOSHORT","FOM","EMAIL","REGNUM","Region","SMSSection",
                      "SMSBank","MESSAGE","RptGrp","Shortname","Split","CMMTY","FOABRV","Month"]
        with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f, quoting=csv.QUOTE_ALL).writerow(out_header)
        print(f"✅ Saved {out_csv}  Rows:0  Cols:{len(out_header)}")
        return

    header_out = header + ["Month"]
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(header_out)
        w.writerows(rows)
    print(f"✅ Saved {out_csv}  Rows:{len(rows)}  Cols:{len(header_out)}")

# ============================================================================ #
#                                     MAIN                                     #
# ============================================================================ #

if __name__ == "__main__":
    # Outputs (same names you requested)
    OUT_REGION_SERVICE = OUT_DIR / "assets_by_region_service.csv"
    OUT_FIELD_OFFICE   = OUT_DIR / "assets_by_field_office.csv"
    OUT_ASSET_DETAILS  = OUT_DIR / "asset_details.csv"
    OUT_FLOOR_CSV      = OUT_DIR / "floor_asset_details.csv"
    OUT_FLOOR_XLSX     = OUT_DIR / "floor_asset_details.xlsx"
    OUT_SITE_STATUS    = OUT_DIR / "site_operational_status.csv"

    # Month filters (when applicable)
    KEEP_MONTHS_FLOOR = [
        "Nov-2021","Dec-2021","Jan-2022","Feb-2022","Mar-2022",
        "Apr-2022","May-2022","Jun-2022","Jul-2022","Aug-2022","Sep-2022"
    ]
    KEEP_MONTHS_SITE  = KEEP_MONTHS_FLOOR
    KEEP_MONTHS_ASSET_DETAILS = None  # or e.g., ["Nov-2021","Dec-2021"]

    # 1) Table 1 — EGMs by Region, Service
    extract_table1_assets_by_region_service(PDF_PATH, OUT_REGION_SERVICE)

    # 2) EGMs by Field Office
    extract_assets_by_field_office(PDF_PATH, OUT_FIELD_OFFICE)

    # 3) Installed Assets by Location, Manufacture
    extract_installed_assets_details(PDF_PATH, OUT_ASSET_DETAILS, keep_months=KEEP_MONTHS_ASSET_DETAILS)

    # 4) Floor Asset Details (CSV + optional XLSX)
    extract_floor_asset_details(PDF_PATH, OUT_FLOOR_CSV, OUT_FLOOR_XLSX, keep_months=KEEP_MONTHS_FLOOR)

    # 5) Site Operational Status
    extract_site_operational_status(PDF_PATH, OUT_SITE_STATUS, keep_months=KEEP_MONTHS_SITE)

    print("\n🎉 All done.")
