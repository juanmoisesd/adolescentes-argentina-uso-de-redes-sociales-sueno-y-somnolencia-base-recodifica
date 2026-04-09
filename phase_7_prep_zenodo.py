import os
import json
import logging
import shutil
from pathlib import Path
from pipeline_utils import setup_logger

logger = setup_logger("phase_7")

def main():
    logger.info("--- PHASE 7: ZENODO PREP STARTED ---")
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)

    for md_file in Path("papers").glob("*.md"):
        name = md_file.stem
        deposit_dir = outputs_dir / f"deposit_{name}"
        deposit_dir.mkdir(exist_ok=True)

        # Copy relevant files
        shutil.copy(md_file, deposit_dir / "paper.md")
        pdf_file = md_file.with_suffix(".pdf")
        if pdf_file.exists(): shutil.copy(pdf_file, deposit_dir / "paper.pdf")

        csv_file = Path(f"datasets/aggregated/dataset_{name}_v1.csv")
        if csv_file.exists(): shutil.copy(csv_file, deposit_dir / "dataset.csv")

        # Generate real metadata for Zenodo
        metadata = {
            "metadata": {
                "title": f"Large-Scale Computational Analysis: {name.replace('_', ' ').title()}",
                "upload_type": "dataset",
                "description": f"Extracted dataset and generated paper for {name} using CAP data.",
                "creators": [{"name": "de la Serna Tuya, Juan Moisés", "orcid": "0000-0002-8401-8018"}],
                "license": "CC-BY-4.0",
                "access_right": "open",
                "keywords": ["Legal Analytics", "Caselaw", "Data Science", name.replace('_', ' ')]
            }
        }
        with open(deposit_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"✅ Prepared deposit in {deposit_dir}")

    logger.info("--- PHASE 7 COMPLETE ---")

if __name__ == "__main__":
    main()
