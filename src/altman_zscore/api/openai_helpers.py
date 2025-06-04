import os
import json

def resolve_prompt_path(prompt_filename):
    prompt_path_new = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..", "prompts", prompt_filename
    )
    prompt_path_legacy = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "prompts", prompt_filename
    )
    if os.path.exists(prompt_path_new):
        return prompt_path_new
    elif os.path.exists(prompt_path_legacy):
        return prompt_path_legacy
    else:
        raise FileNotFoundError(
            f"Could not find {prompt_filename} in either src/prompts/ or src/altman_zscore/prompts/. Checked: {prompt_path_new}, {prompt_path_legacy}"
        )

def load_prompt_file(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def strip_code_block_markers(content):
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
    return content.strip()

def parse_llm_json_response(content):
    content = strip_code_block_markers(content)
    return json.loads(content)

def inject_company_context(ticker):
    company_officers_str = ""
    company_info_str = ""
    sec_info_str = ""
    if not ticker:
        return company_officers_str, company_info_str, sec_info_str
    from altman_zscore.utils.paths import get_output_dir
    company_officers_path = get_output_dir("company_officers.json", ticker=ticker)
    company_info_path = get_output_dir("company_info.json", ticker=ticker)
    sec_info_path = get_output_dir("sec_edgar_company_info.json", ticker=ticker)
    if os.path.exists(company_officers_path):
        try:
            with open(company_officers_path, "r", encoding="utf-8") as officers_file:
                officers_json = json.load(officers_file)
            import io, pprint
            buf = io.StringIO()
            pprint.pprint(officers_json, stream=buf, compact=True, width=120)
            company_officers_str = f"\n\n# Key Executives and Officers (from Yahoo Finance)\n{buf.getvalue()}\n"
        except Exception as e:
            company_officers_str = f"\n[Could not load company_officers.json: {e}]\n"
    if os.path.exists(company_info_path):
        try:
            with open(company_info_path, "r", encoding="utf-8") as info_file:
                company_info = json.load(info_file)
            trimmed_company = extract_trimmed_company_info(company_info)
            import io, pprint
            buf = io.StringIO()
            pprint.pprint(trimmed_company, stream=buf, compact=True, width=120)
            company_info_str = f"\n\n# Company Profile (from Yahoo Finance)\n{buf.getvalue()}\n"
        except Exception as e:
            company_info_str = f"\n[Could not load company_info.json: {e}]\n"
    if os.path.exists(sec_info_path):
        try:
            with open(sec_info_path, "r", encoding="utf-8") as sec_file:
                sec_info = json.load(sec_file)
                trimmed = extract_trimmed_sec_info(sec_info)
                trimmed = {k: v for k, v in trimmed.items() if v is not None}
                if "business_address" in trimmed:
                    trimmed["business_address"] = {k: v for k, v in trimmed["business_address"].items() if v is not None}
                    if not trimmed["business_address"]:
                        del trimmed["business_address"]
                import io, pprint
                buf = io.StringIO()
                pprint.pprint(trimmed, stream=buf, compact=True, width=120)
                sec_info_str = f"\n\n# Key SEC EDGAR Company Info (trimmed)\n{buf.getvalue()}\n"
        except Exception as e:
            sec_info_str = f"\n[Could not load sec_edgar_company_info.json: {e}]\n"
    return company_officers_str, company_info_str, sec_info_str

def extract_trimmed_sec_info(sec_info: dict) -> dict:
    base_info = {
        "name": sec_info.get("name"),
        "cik": sec_info.get("cik"),
        "sic": sec_info.get("sic"),
        "sicDescription": sec_info.get("sicDescription"),
        "stateOfIncorporation": sec_info.get("stateOfIncorporation"),
        "fiscalYearEnd": sec_info.get("fiscalYearEnd"),
        "category": sec_info.get("category"),
        "business_address": sec_info.get("addresses", {}).get("business", {}),
        "phone": sec_info.get("phone"),
        "tickers": sec_info.get("tickers"),
        "exchanges": sec_info.get("exchanges"),
        "ein": sec_info.get("ein"),
        "website": sec_info.get("website"),
    }
    try:
        filings = sec_info.get("filings", {}).get("recent", {})
        if not isinstance(filings, dict):
            return base_info
        accession_numbers = filings.get("accessionNumber", [])
        descriptions = filings.get("description", [])
        forms = filings.get("form", [])
        filing_dates = filings.get("filingDate", [])
        file_numbers = filings.get("fileNumber", [])
        num_filings = min(100, len(accession_numbers))
        exec_filings = []
        for i in range(num_filings):
            desc = descriptions[i] if i < len(descriptions) else ""
            form = forms[i] if i < len(forms) else ""
            date = filing_dates[i] if i < len(filing_dates) else ""
            acc_num = accession_numbers[i] if i < len(accession_numbers) else ""
            desc = str(desc).upper() if desc else ""
            form = str(form).upper() if form else ""
            is_exec_filing = (
                any(term in form for term in ["FORM 4", "FORM 3", "FORM 5"]) or
                any(term in desc for term in [
                    "RSU", "CEO", "CFO", "DIRECTOR", "EXECUTIVE", 
                    "BENEFICIAL OWNERSHIP", "STOCK AWARD", "OPTION"
                ])
            )
            if is_exec_filing:
                exec_filing = {
                    "date": date,
                    "description": desc,
                    "type": form,
                    "accessionNumber": acc_num
                }
                exec_filings.append(exec_filing)
        if exec_filings:
            base_info["recent_executive_filings"] = exec_filings[:20]
    except Exception as e:
        print(f"Error processing SEC filings: {str(e)}")
    return base_info

def extract_trimmed_company_info(company_info: dict) -> dict:
    filtered = {k: v for k, v in company_info.items() if k != "filings" and v is not None}
    exec_info = []
    exec_fields = [
        "officers", "executives", "management", "directors",
        "keyExecutives", "companyOfficers", "boardMembers",
        "insiderHolders", "institutionalHolders"
    ]
    for field in exec_fields:
        if field in company_info and company_info[field]:
            execs = company_info[field]
            if not isinstance(execs, list):
                continue
            for e in execs:
                if not isinstance(e, dict):
                    continue
                name = e.get("name", e.get("holderName", "Unknown"))
                title = e.get("title", e.get("position", e.get("relationship", "Unknown")))
                if "Unknown" in (name, title):
                    continue
                exec_data = {
                    "name": name,
                    "title": title
                }
                optional_fields = {
                    "age": e.get("age"),
                    "yearBorn": e.get("yearBorn"),
                    "since": e.get("since", e.get("yearsWithCompany")),
                    "compensation": e.get("totalCompensation"),
                    "shares": e.get("totalHolding", e.get("shares")),
                    "dateReported": e.get("latestTransDate", e.get("reportDate")),
                }
                exec_data.update({k: v for k, v in optional_fields.items() if v is not None})
                exec_info.append(exec_data)
    if exec_info:
        filtered["executive_information"] = exec_info
    for k, v in list(filtered.items()):
        if isinstance(v, dict):
            filtered[k] = {sk: sv for sk, sv in v.items() if sv is not None}
            if not filtered[k]:
                del filtered[k]
        elif isinstance(v, list):
            filtered[k] = [x for x in v if x is not None and (not isinstance(x, dict) or any(x.values()))]
    if "institutionalHolders" in company_info:
        inst_holders = company_info["institutionalHolders"]
        if isinstance(inst_holders, list):
            filtered["institutionalOwnership"] = [
                {k: v for k, v in holder.items() if v is not None}
                for holder in inst_holders
                if isinstance(holder, dict) and any(v is not None for v in holder.values())
            ]
    if "majorHolders" in company_info:
        major_holders = company_info["majorHolders"]
        if isinstance(major_holders, list):
            filtered["majorHolders"] = [
                {k: v for k, v in holder.items() if v is not None}
                for holder in major_holders
                if isinstance(holder, dict) and any(v is not None for v in holder.values())
            ]
    return filtered
