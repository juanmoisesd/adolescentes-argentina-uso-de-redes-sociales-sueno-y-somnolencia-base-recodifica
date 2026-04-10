#!/usr/bin/env python3
"""
INIT PIPELINE SCRIPT v1.3
=========================
Autonomous setup and validation for Jules pipeline.
- Handles .env config
- Validates resources (disk, API, network)
- Downloads metadata and generates plan
- Supports Full Scale (Opción B)
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
        logger.warning(f"⚠️ Low disk space! Scaling might be constrained.")

    # Network check
    try:
        r = requests.head("https://static.case.law", timeout=10)
        net_ok = r.status_code == 200
        logger.info(f"case.law accessibility: {'✅ OK' if net_ok else '❌ FAIL'}")
    except:
        net_ok = False
        logger.error("❌ case.law unreachable")

    return disk_ok, net_ok

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

    with open("metadata_cache/JurisdictionsMetadata.json", "r") as f:
        jurs_data = json.load(f)

    # Identify if we want all or specific
    target_env = os.getenv("JURISDICTIONS", "all")

    if target_env == "all":
        target_jurs = [j.get("name") for j in jurs_data]
        logger.info(f"Full scale selected: All {len(target_jurs)} jurisdictions.")
    else:
        # Expecting JSON list format
        try:
            target_jurs = json.loads(target_env)
        except:
            target_jurs = ["U.S.", "N.Y.", "Cal."]

    plan = {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "target_jurisdictions": target_jurs,
        "mode": "full" if target_env == "all" else "partial",
        "recommendations": {
            "start_with": {"jurisdictions": target_jurs}
        }
    }

    with open("config.json", "w") as f:
        json.dump(plan, f, indent=2)
    logger.info("✅ config.json generated.")
    return True

def main():
    logger.info("=== INITIALIZING PIPELINE (v1.3) ===")
    res_ok, net_ok = check_resources()
    if not net_ok:
        logger.error("Network check failed. Aborting.")
        sys.exit(1)

    if download_metadata() and generate_plan():
        logger.info("✅ INIT COMPLETE. System ready for Scaling.")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
