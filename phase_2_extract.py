import os
import json
import logging
import zipfile
import pandas as pd
from pathlib import Path
from pipeline_utils import setup_logger

logger = setup_logger("phase_2")

def extract_case_data(zip_path):
    cases = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            json_files = [f for f in z.namelist() if f.startswith("json/") and f.endswith(".json")]
            for f in json_files:
                data = json.loads(z.read(f).decode('utf-8'))

                # Extract core metadata
                case_id = data.get("id")
                name = data.get("name_abbreviation")
                date = data.get("decision_date")
                court = data.get("court", {}).get("name")
                jurisdiction = data.get("jurisdiction", {}).get("name_long")

                # Extract text from opinions
                opinions = data.get("casebody", {}).get("opinions", [])
                full_text = " ".join([op.get("text", "") for op in opinions])

                # Count citations
                citations = data.get("citations", [])
                cite_count = len(citations)

                cases.append({
                    "id": case_id,
                    "name": name,
                    "date": date,
                    "court": court,
                    "jurisdiction": jurisdiction,
                    "text": full_text,
                    "citations_count": cite_count,
                    "volume": zip_path.stem
                })
    except Exception as e:
        logger.error(f"Error processing {zip_path.name}: {e}")

    return cases

def main():
    logger.info("--- PHASE 2: EXTRACTION STARTED ---")
    raw_dir = Path("raw_data")
    proc_dir = Path("processed_data")
    proc_dir.mkdir(exist_ok=True)

    total_cases = 0
    for zip_file in raw_dir.glob("**/*.zip"):
        logger.info(f"Processing {zip_file}...")
        cases = extract_case_data(zip_file)
        if cases:
            df = pd.DataFrame(cases)
            out_path = proc_dir / f"{zip_file.stem}.parquet"
            df.to_parquet(out_path, compression='snappy')
            logger.info(f"✅ Saved {len(cases)} cases to {out_path}")
            total_cases += len(cases)

    logger.info(f"--- PHASE 2 COMPLETE ({total_cases} total cases) ---")

if __name__ == "__main__":
    main()
