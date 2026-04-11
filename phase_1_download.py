import os
import json
import requests
import logging
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from pipeline_utils import setup_logger, get_config

logger = setup_logger("phase_1")

def download_volume(url, dest_path):
    if dest_path.exists():
        return True

    headers = {'User-Agent': 'Mozilla/5.0'}
    for attempt in range(5):
        try:
            r = requests.get(url, headers=headers, stream=True, timeout=60)
            if r.status_code == 200:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=131072):
                        f.write(chunk)
                return True
            elif r.status_code == 404:
                return False
        except:
            pass
        time.sleep(2 ** attempt)
    return False

def main():
    logger.info("--- PHASE 1: DOWNLOAD STARTED (Multi-threaded) ---")
    config = get_config()
    target_jurs = config.get("target_jurisdictions", [])
    mode = config.get("mode", "partial")

    max_per_jur = int(os.getenv("MAX_VOLUMES_PER_JURISDICTION", 999999))
    max_workers = int(os.getenv("MAX_PARALLEL_DOWNLOADS", 5))
    checkpoint_interval = int(os.getenv("CHECKPOINT_INTERVAL", 50))

    logger.info(f"Targeting {len(target_jurs)} jurisdictions. Mode: {mode}, Workers: {max_workers}")

    metadata_path = Path("metadata_cache/VolumesMetadata.json")
    if not metadata_path.exists():
        logger.error("Metadata not found.")
        return

    with open(metadata_path, "r") as f:
        volumes = json.load(f)

    download_tasks = []
    jur_counts = {j: 0 for j in target_jurs}

    for vol in volumes:
        vol_jurs = [j.get("name") for j in vol.get("jurisdictions", [])]
        for vj in vol_jurs:
            if vj in jur_counts and (mode == "full" or jur_counts[vj] < max_per_jur):
                reporter_slug = vol.get('reporter_slug')
                vol_num = vol.get('volume_number')
                url = f"https://static.case.law/{reporter_slug}/{vol_num}.zip"
                safe_jur = vj.replace(".", "").replace(" ", "_").lower()
                dest = Path("raw_data") / safe_jur / f"{vol_num}.zip"

                download_tasks.append((url, dest))
                jur_counts[vj] += 1
                break

        if mode != "full" and all(count >= max_per_jur for count in jur_counts.values()):
            break

    total_tasks = len(download_tasks)
    logger.info(f"Queued {total_tasks} download tasks.")

    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(download_volume, url, dest): url for url, dest in download_tasks}
        for future in as_completed(future_to_url):
            completed += 1
            if future.result():
                if completed % checkpoint_interval == 0:
                    logger.info(f"📊 Progress: {completed}/{total_tasks} volumes processed.")
            else:
                url = future_to_url[future]
                logger.warning(f"Failed to download {url}")

    logger.info(f"--- PHASE 1 COMPLETE ({completed} total volumes processed) ---")

if __name__ == "__main__":
    main()
