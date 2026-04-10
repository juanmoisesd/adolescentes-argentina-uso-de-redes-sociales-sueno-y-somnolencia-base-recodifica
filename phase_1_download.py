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

        time.sleep(2 ** attempt)

    return False

def main():
    logger.info("--- PHASE 1: DOWNLOAD STARTED ---")
    config = get_config()
    if not config:
        logger.error("config.json not found.")
        return

    target_jurs = config.get("target_jurisdictions", [])
    if not target_jurs:
        # Compatibility with older structure
        recommendations = config.get("plan", {}).get("recommendations", {})
        target_jurs = recommendations.get("start_with", {}).get("jurisdictions", [])

    if not target_jurs:
        logger.error("No target jurisdictions found in plan.")
        return

    logger.info(f"Targeting jurisdictions: {target_jurs}")

    with open("metadata_cache/VolumesMetadata.json", "r") as f:
        volumes = json.load(f)

    download_count = 0
    max_volumes_per_poc = 5

    for vol in volumes:
        if download_count >= max_volumes_per_poc:
            break

        vol_jurs = [j.get("name") for j in vol.get("jurisdictions", [])]
        if any(j in target_jurs for j in vol_jurs):
            url = f"https://static.case.law/{vol.get('reporter_slug')}/{vol.get('volume_number')}.zip"
            safe_jur = vol_jurs[0].replace(".", "").replace(" ", "_").lower()
            jur_dir = Path("raw_data") / safe_jur
            jur_dir.mkdir(parents=True, exist_ok=True)
            dest = jur_dir / f"{vol.get('volume_number')}.zip"

            if download_volume(url, dest):
                download_count += 1

    logger.info(f"--- PHASE 1 COMPLETE ({download_count} volumes) ---")

if __name__ == "__main__":
    main()
