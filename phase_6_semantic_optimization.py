import os
import logging
from pathlib import Path
from pipeline_utils import setup_logger

logger = setup_logger("phase_6")

def optimize_metadata(md_path):
    logger.info(f"Optimizing metadata for {md_path.name}...")
    with open(md_path, "r") as f:
        content = f.read()

    # Simulation: Ensure Academic SEO terms are present
    seo_terms = "\n\n<!-- SEO-Optimized-Metadata: computational law, large-scale legal analysis, nlp data science -->"
    if "SEO-Optimized-Metadata" not in content:
        content += seo_terms

    with open(md_path, "w") as f:
        f.write(content)
    logger.info(f"✅ Optimized {md_path.name}")

def main():
    logger.info("--- PHASE 6: SEMANTIC OPTIMIZATION STARTED ---")
    for md_file in Path("papers").glob("*.md"):
        optimize_metadata(md_file)
    logger.info("--- PHASE 6 COMPLETE ---")

if __name__ == "__main__":
    main()
