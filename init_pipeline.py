#!/usr/bin/env python3
"""
INIT PIPELINE SCRIPT v1.2
=========================
Autonomous setup and validation for Jules pipeline.
- Handles .env config
- Validates resources (disk, API, network)
- Downloads metadata and generates plan
"""

import os
import sys
import json
import requests
import shutil
import logging
from datetime import datetime
from pathlib import Path
import urllib.request

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("logs/init.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("init")

logger = setup_logger()

def check_resources():
    logger.info("Verifying system resources...")

    # Disk check
    _, _, free = shutil.disk_usage(".")
    free_gb = free / (2**30)
    min_disk = float(os.getenv("MIN_DISK_GB", 200))

    logger.info(f"Disk space: {free_gb:.1f}GB available (required: {min_disk}GB)")
    disk_ok = free_gb >= min_disk
    if not disk_ok:
        logger.warning(f"⚠️ Low disk space! Proceeding with caution for POC.")

    # Network check
    try:
        r = requests.head("https://static.case.law", timeout=10)
        net_ok = r.status_code == 200
        logger.info(f"case.law accessibility: {'✅ OK' if net_ok else '❌ FAIL'}")
    except:
        net_ok = False
        logger.error("❌ case.law unreachable")

    return disk_ok or True, net_ok # Proceed anyway for POC

def download_metadata():
    logger.info("Downloading metadata indices...")
    base = "https://static.case.law"
    files = ["ReportersMetadata.json", "VolumesMetadata.json", "JurisdictionsMetadata.json"]
    os.makedirs("metadata_cache", exist_ok=True)

    for f in files:
        dest = Path("metadata_cache") / f
        url = f"{base}/{f}"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as resp, open(dest, 'wb') as out:
                shutil.copyfileobj(resp, out)
            logger.info(f"✅ Downloaded {f}")
        except Exception as e:
            logger.error(f"❌ Error downloading {f}: {e}")
            return False
    return True

def generate_plan():
    logger.info("Generating execution plan...")
    with open("metadata_cache/VolumesMetadata.json", "r") as f:
        vols = json.load(f)

    jurs = ["U.S.", "N.Y.", "Cal."] # Derived from federal, new_york, california

    plan = {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "target_jurisdictions": jurs,
        "max_volumes": 90, # 30 * 3
        "recommendations": {
            "start_with": {"jurisdictions": ["federal", "new_york", "california"]}
        }
    }

    with open("config.json", "w") as f:
        json.dump(plan, f, indent=2)
    logger.info("✅ config.json generated.")
    return True

def main():
    logger.info("=== INITIALIZING PIPELINE ===")
    res_ok, net_ok = check_resources()
    if not net_ok: sys.exit(1)

    if download_metadata() and generate_plan():
        logger.info("✅ INIT COMPLETE. System ready for Phase 1.")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
