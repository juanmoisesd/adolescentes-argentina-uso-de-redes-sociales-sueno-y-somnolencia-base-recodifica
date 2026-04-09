import os
import json
import requests
import logging
import time
from pathlib import Path
from pipeline_utils import setup_logger, get_config

logger = setup_logger("phase_1")

def download_volume(url, dest_path):
    if dest_path.exists():
        logger.info(f"Skipping {dest_path.name}, already exists.")
        return True

    logger.info(f"Downloading {url} to {dest_path}...")
    headers = {'User-Agent': 'Mozilla/5.0'}

    for attempt in range(5):
        try:
            r = requests.get(url, headers=headers, stream=True, timeout=60)
            if r.status_code == 200:
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        f.write(chunk)
                logger.info(f"✅ Successfully downloaded {dest_path.name}")
                return True
            elif r.status_code == 404:
                logger.error(f"❌ 404 Not Found: {url}")
                return False
            else:
                logger.warning(f"⚠️ Attempt {attempt+1}: Status {r.status_code} for {url}")
        except Exception as e:
            logger.error(f"❌ Attempt {attempt+1}: Error downloading {url}: {e}")

        time.sleep(2 ** attempt) # Exponential backoff

    return False

def main():
    logger.info("--- PHASE 1: DOWNLOAD STARTED ---")
    config = get_config()
    if not config:
        logger.error("config.json not found. Run init_pipeline.py first.")
        return

    # Extract target jurisdictions from recommendations
    plan = config.get("plan", {})
    recommendations = plan.get("recommendations", {})
    target_jurs = recommendations.get("start_with", {}).get("jurisdictions", [])

    if not target_jurs:
        logger.error("No target jurisdictions found in plan.")
        return

    logger.info(f"Targeting jurisdictions: {target_jurs}")

    metadata_path = Path("metadata_cache/VolumesMetadata.json")
    if not metadata_path.exists():
        logger.error("VolumesMetadata.json not found in metadata_cache/")
        return

    with open(metadata_path, "r") as f:
        volumes = json.load(f)

    # Standardize jurisdiction names for matching
    # Map friendly names from plan to metadata names
    # Note: Real CAP metadata uses names like "United States", "New York", "California"
    jur_map = {
        "federal": ["U.S.", "United States", "U. S."],
        "new_york": ["N.Y.", "New York"],
        "california": ["Cal.", "California"],
        "texas": ["Tex.", "Texas"],
        "florida": ["Fla.", "Florida"]
    }

    accepted_names = []
    for tj in target_jurs:
        accepted_names.extend(jur_map.get(tj.lower(), [tj]))

    download_count = 0
    # In production, we'd remove the limit or use a large one
    max_volumes_per_poc = 10

    for vol in volumes:
        if download_count >= max_volumes_per_poc:
            break

        vol_jurs = [j.get("name") for j in vol.get("jurisdictions", [])]
        if any(j in accepted_names for j in vol_jurs):
            reporter_slug = vol.get("reporter_slug")
            vol_num = vol.get("volume_number")

            if not reporter_slug or not vol_num:
                continue

            url = f"https://static.case.law/{reporter_slug}/{vol_num}.zip"

            # Safe directory name
            safe_jur = vol_jurs[0].replace(".", "").replace(" ", "_").lower()
            jur_dir = Path("raw_data") / safe_jur
            jur_dir.mkdir(parents=True, exist_ok=True)
            dest = jur_dir / f"{vol_num}.zip"

            if download_volume(url, dest):
                download_count += 1

    logger.info(f"--- PHASE 1 COMPLETE ({download_count} volumes) ---")

if __name__ == "__main__":
    main()
