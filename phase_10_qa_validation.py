import os
import json
import logging
from pathlib import Path
from pipeline_utils import setup_logger

logger = setup_logger("phase_10")

def main():
    logger.info("--- PHASE 10: QA & VALIDATION STARTED ---")

    results = {
        "datasets": len(list(Path("datasets/aggregated").glob("*.csv"))),
        "papers": len(list(Path("papers").glob("*.md"))),
        "deposits": len(list(Path("outputs").glob("deposit_*"))),
        "dois": 0
    }

    # Count DOIs in registry
    registry = Path("registry/dois.csv")
    if registry.exists():
        with open(registry, "r") as f:
            results["dois"] = sum(1 for line in f) - 1

    # Check for empty files
    errors = []
    for csv in Path("datasets/aggregated").glob("*.csv"):
        if os.path.getsize(csv) < 50:
            errors.append(f"Empty dataset: {csv.name}")

    status = "SUCCESS" if not errors and results["dois"] >= 4 else "WARNING"

    qa_report = {
        "status": status,
        "metrics": results,
        "errors": errors,
        "timestamp": "2025-04-09"
    }

    with open("outputs/qa_metrics.json", "w") as f:
        json.dump(qa_report, f, indent=2)

    with open("outputs/FINAL_STATUS.txt", "w") as f:
        f.write(f"✅ FINAL STATUS: {status}\n")
        f.write(json.dumps(qa_report, indent=2))

    logger.info(f"✅ QA Complete. Status: {status}")
    logger.info("--- PHASE 10 COMPLETE ---")

if __name__ == "__main__":
    main()
