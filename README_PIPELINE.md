# CASE.LAW → ZENODO AUTOMATED PIPELINE
## Jules Autonomous Agent System

**Juan Moisés de la Serna**
Doctor en Psicología | Neurocientífico | Investigador
ORCID: 0000-0002-8401-8018

---

## ⚡ QUICK START (5 MINUTES)

### Step 1: Setup Environment
```bash
# Create project directory
mkdir -p ~/pipeline_project
cd ~/pipeline_project

# Create .env file with your credentials
cat > .env << EOF
ZENODO_TOKEN=your_token_here
# OR for testing:
ZENODO_SANDBOX_TOKEN=your_sandbox_token_here
EOF

chmod 600 .env
```

### Step 2: Initialize System
```bash
python3 init_pipeline.py
```
This script validates connectivity, checks for 200GB+ space, and downloads `case.law` metadata indices into `metadata_cache/`.

### Step 3: Execute Pipeline (Phases 1-10)
```bash
# Individual phases
python3 phase_1_download.py    # Download volumes from case.law
python3 phase_2_extract.py     # Parse JSON to Parquet
python3 phase_3_features.py    # Calculate 15+ features per case
python3 phase_4_aggregate.py   # Generate 4 publishable datasets
python3 phase_5_generate_papers.py # Generate papers via Jinja2
# ... (phases 6-10)

# Full execution
bash run_full_pipeline.sh
```

---

## 📊 EXPECTED OUTPUTS

| Phase | Output | Location |
|-------|--------|----------|
| 1 | Raw ZIPs | `raw_data/` |
| 2 | Columnar Data | `processed_data/*.parquet` |
| 3 | Extended Features | `datasets/all_features.csv` |
| 4 | Aggregated Datasets | `datasets/aggregated/` |
| 5-6 | Generated Papers | `papers/` |
| 7-8 | Zenodo Deposits | `outputs/` |
| 9 | Meta-Papers | `meta_papers/` |
| 10 | Final QA | `outputs/qa_metrics.json` |

---

## 🔐 REQUIREMENTS
- Python 3.8+
- Packages: `pandas`, `numpy`, `requests`, `pyarrow`, `jinja2`
- Storage: 200GB (minimum for Option A)

---
**Version:** 1.1
**Status:** Refined Production Ready
