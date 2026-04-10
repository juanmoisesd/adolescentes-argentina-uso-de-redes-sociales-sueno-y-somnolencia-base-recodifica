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
        return True

    logger.info(f"Downloading {url}...")
    headers = {'User-Agent': 'Mozilla/5.0'}

    for attempt in range(5):
        try:
            r = requests.get(url, headers=headers, stream=True, timeout=60)
            if r.status_code == 200:
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=131072):
                        f.write(chunk)
                logger.info(f"✅ Successfully downloaded {dest_path.name}")
                return True
            elif r.status_code == 404:
                logger.error(f"❌ 404 Not Found: {url}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Attempt {attempt+1} failed for {url}: {e}")

        time.sleep(2 ** attempt)
    return False

def main():
    logger.info("--- PHASE 1: DOWNLOAD STARTED ---")
    config = get_config()
    target_jurs = config.get("target_jurisdictions", [])
    mode = config.get("mode", "partial")

    # Respect user's executive order parameters
    max_per_jur = int(os.getenv("MAX_VOLUMES_PER_JURISDICTION", 999999))
    checkpoint_interval = int(os.getenv("CHECKPOINT_INTERVAL", 50))

    logger.info(f"Targeting {len(target_jurs)} jurisdictions. Mode: {mode}")

    metadata_path = Path("metadata_cache/VolumesMetadata.json")
    if not metadata_path.exists():
        logger.error("Metadata not found. Run init_pipeline.py first.")
        return

    with open(metadata_path, "r") as f:
        volumes = json.load(f)

    jur_counts = {j: 0 for j in target_jurs}
    total_downloaded = 0

    for vol in volumes:
        vol_jurs = [j.get("name") for j in vol.get("jurisdictions", [])]
        for vj in vol_jurs:
            if vj in jur_counts and (mode == "full" or jur_counts[vj] < max_per_jur):
                reporter_slug = vol.get('reporter_slug')
                vol_num = vol.get('volume_number')
                url = f"https://static.case.law/{reporter_slug}/{vol_num}.zip"

                safe_jur = vj.replace(".", "").replace(" ", "_").lower()
                jur_dir = Path("raw_data") / safe_jur
                jur_dir.mkdir(parents=True, exist_ok=True)
                dest = jur_dir / f"{vol_num}.zip"

                if download_volume(url, dest):
                    jur_counts[vj] += 1
                    total_downloaded += 1

                    if total_downloaded % checkpoint_interval == 0:
                        logger.info(f"📊 Checkpoint reached: {total_downloaded} volumes downloaded.")
                break

        if mode != "full" and all(count >= max_per_jur for count in jur_counts.values()):
            break

    logger.info(f"--- PHASE 1 COMPLETE ({total_downloaded} total volumes) ---")

if __name__ == "__main__":
    main()
