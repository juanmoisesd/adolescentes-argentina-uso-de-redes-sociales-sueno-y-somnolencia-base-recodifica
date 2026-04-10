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
                logger.info(f"✅ Downloaded {dest_path.name}")
                return True
            elif r.status_code == 404:
                return False
        except:
            pass
        time.sleep(2 ** attempt)
    return False

def main():
    logger.info("--- PHASE 1: DOWNLOAD STARTED ---")
    config = get_config()
    target_jurs = config.get("target_jurisdictions", [])

    # Handle 'all' or large sets efficiently
    is_full = config.get("mode") == "full"
    max_per_jur = int(os.getenv("MAX_VOLUMES_PER_JURISDICTION", 999999))

    logger.info(f"Targeting {len(target_jurs)} jurisdictions. Max {max_per_jur} per jur.")

    with open("metadata_cache/VolumesMetadata.json", "r") as f:
        volumes = json.load(f)

    jur_counts = {j: 0 for j in target_jurs}
    total_downloaded = 0

    for vol in volumes:
        vol_jurs = [j.get("name") for j in vol.get("jurisdictions", [])]
        for vj in vol_jurs:
            if vj in jur_counts and jur_counts[vj] < max_per_jur:
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
                break

        # Check if we should stop early for non-full mode
        if not is_full and all(count >= max_per_jur for count in jur_counts.values()):
            break

    logger.info(f"--- PHASE 1 COMPLETE ({total_downloaded} volumes) ---")

if __name__ == "__main__":
    main()
