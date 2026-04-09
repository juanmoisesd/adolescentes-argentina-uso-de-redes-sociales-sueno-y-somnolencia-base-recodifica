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

### Step 2: Get Files
You need 4 files:
1. ✅ `init_pipeline.py` (provided)
2. ✅ `PHASE_-1_INIT_GUIDE.docx` (read this)
3. ✅ `PIPELINE_MAESTRO_v2.docx` (reference for Phases 1-10)
4. ✅ This README

Place them in `~/pipeline_project/`

### Step 3: Initialize System
```bash
python3 init_pipeline.py
```

This will:
- ✅ Validate case.law connectivity
- ✅ Validate Zenodo API token
- ✅ Check disk space (200GB minimum)
- ✅ Download metadata indices
- ✅ Generate `config.json` (your execution plan)
- ✅ Print detailed report

### Step 4: Review Output
After init completes, check:
- `logs/init_report.txt` — Human-readable summary
- `config.json` — Machine-readable plan (Jules reads this)
- `logs/init.log` — Detailed execution trace

**If status = "ready"** → Proceed to Step 5
**If status = "warnings"** → Fix issues, re-run init

### Step 5: Execute Pipeline (Phases 1-10)
```bash
# Option A: Run one phase at a time
python3 phase_1_download.py    # Download from case.law
python3 phase_2_extract.py     # Parse JSON
python3 phase_3_features.py    # Calculate metrics
# ... (phases 4-10)

# Option B: Run full pipeline (RECOMMENDED)
bash run_full_pipeline.sh       # Executes 1-10 sequentially
```

**Monitor progress:**
```bash
tail -f ~/pipeline_project/logs/execution.log
```

---

## 📋 FILE STRUCTURE

```
~/pipeline_project/
├── .env                          # Credentials (KEEP PRIVATE)
├── init_pipeline.py              # Initialization script
├── config.json                   # Auto-generated plan (after Phase -1)
│
├── /raw_data/                    # Downloaded ZIPs (Phase 1)
│   └── {jurisdiction}/{reporter}/{volume}.zip
│
├── /processed_data/              # Parsed Parquets (Phase 2)
│   └── {volume}.parquet
│
├── /datasets/                    # Publishable datasets (Phase 4)
│   └── dataset_{name}_{version}.csv
│
├── /papers/                      # Auto-generated papers (Phase 5)
│   ├── {dataset_name}.md
│   └── {dataset_name}.pdf
│
├── /outputs/                     # Zenodo-ready deposits (Phase 7)
│   └── deposit_{dataset}/
│       ├── dataset.csv
│       ├── paper.pdf
│       ├── README.md
│       ├── CITATION.cff
│       └── metadata.json
│
├── /metadata_cache/              # Downloaded indices (Phase -1)
│   ├── ReportersMetadata.json
│   ├── VolumesMetadata.json
│   └── JurisdictionsMetadata.json
│
├── /registry/                    # DOI tracking
│   ├── dois.csv                 # Published DOIs
│   ├── derived_dois.csv         # Derived publication DOIs
│   └── meta_dois.csv            # Meta-paper DOIs
│
└── /logs/
    ├── init.log                 # Initialization trace
    ├── init_report.txt          # Initialization summary
    └── execution.log            # Full pipeline trace
```

---

## 🔐 CREDENTIALS (.env)

```bash
# Zenodo Production (real, permanent records)
ZENODO_TOKEN=your_zenodo_api_token_here

# OR Zenodo Sandbox (testing, temporary)
ZENODO_SANDBOX_TOKEN=your_sandbox_token_here

# Both optional. If neither exists, init will warn you.
```

**How to get token:**
- Production: https://zenodo.org/account/settings/applications/
- Sandbox: https://sandbox.zenodo.org/account/settings/applications/

---

## 📊 EXPECTED OUTPUTS (by phase)

| Phase | Input | Output | Example Volume |
|-------|-------|--------|---|
| 1 | case.law URLs | Downloaded ZIPs | 50-500GB |
| 2 | ZIPs | Parsed Parquets | 1-10GB each |
| 3 | Parquets | Features CSV | 45K rows/metrics |
| 4 | Features | Datasets | 4-5 datasets |
| 5 | Datasets | Papers | 4-5 .md/.pdf |
| 6 | Papers | Optimized metadata | Updated papers |
| 7 | Papers + Data | Zenodo deposits | Ready to upload |
| 8 | Deposits | DOIs | 4-5 DOIs |
| 9 | DOIs | Meta-papers | 4-5 meta-papers |
| 10 | All | Validation report | Complete audit |

**Multiplier effect (per 10 volumes):**
- 30-40 datasets
- 60-80 papers (base + derived)
- 4-5 meta-papers
- **120+ DOIs**

---

## 🧠 HOW JULES WORKS

1. **Phase -1 (init_pipeline.py)**
   - Validates system
   - Downloads metadata
   - Generates config.json
   - Reports blockers BEFORE starting

2. **Phases 1-10 (automated)**
   - Reads config.json
   - Executes pipeline sequentially
   - Logs every step with timestamp
   - Auto-resumes if interrupted
   - No manual intervention needed

3. **Monitoring**
   - Check `logs/execution.log` in real-time
   - Each phase writes progress markers
   - DOIs registered in `/registry/dois.csv`

---

## ⚠️ IMPORTANT NOTES

### Before Starting Phase 1:
- ✅ Run Phase -1 and verify status = "ready"
- ✅ Review config.json recommendations
- ✅ Ensure 200GB+ free disk space
- ✅ Zenodo token is valid and has write permissions

### During Execution:
- Jules automatically retries failed downloads
- Skips already-processed volumes
- Logs all timestamps and errors
- Can resume from checkpoint if interrupted

### Common Issues:

**Error: "case.law not accessible"**
- Check internet connection
- case.law may be temporarily down (try again later)

**Error: "Zenodo API token invalid"**
- Generate new token at zenodo.org/account/settings/applications/
- Update .env file
- Re-run init_pipeline.py

**Error: "Disk space low (<200GB)"**
- Free up space or
- Change `project_root` in init_pipeline.py to different location

**Pipeline hangs:**
- Check logs/execution.log for last activity
- Re-run stuck phase (auto-resumption enabled)
- Increase timeout in phase script if needed

---

## 📚 DOCUMENTATION FILES

1. **init_pipeline.py** — Initialization script (source code)
2. **PHASE_-1_INIT_GUIDE.docx** — Detailed guide for Phase -1 setup
3. **PIPELINE_MAESTRO_v2.docx** — Complete reference for Phases 1-10
4. **This README** — Quick start + troubleshooting

---

## 🚀 FULL EXECUTION COMMAND (ONE-LINER)

After initial setup:
```bash
# Run initialization
python3 init_pipeline.py && \

# Then run full pipeline (if status = ready)
bash run_full_pipeline.sh && \

# Monitor progress
tail -f ~/pipeline_project/logs/execution.log
```

---

## 📧 SUPPORT & DEBUGGING

Check these in order:
1. `logs/init.log` — Initialization details
2. `logs/execution.log` — Phase-by-phase trace
3. `logs/init_report.txt` — Summary of checks
4. `config.json` — Current execution plan
5. PIPELINE_MAESTRO_v2.docx — Detailed reference

---

## 🎯 METRICS & SUCCESS CRITERIA

**Phase -1 Success:**
- All 4 checks pass (✅)
- config.json generated
- status = "ready"

**Phase 1-10 Success:**
- All volumes processed
- Datasets generated
- Papers created
- DOIs published to Zenodo
- Citation network built
- QA validation passed

**Final Output:**
- `/registry/dois.csv` populated with 100+ DOIs
- `/outputs/` contains all Zenodo deposits
- `/logs/execution.log` shows complete trace
- Meta-papers generated and published

---

## 💡 TIPS FOR OPTIMAL RESULTS

1. **Start small**: Download top 2-3 jurisdictions first (proof of concept)
2. **Monitor closely**: Check logs regularly for errors
3. **Parallel downloads**: Use config.json recommendation (5 concurrent max)
4. **Storage strategy**: Use separate SSD for raw_data if possible
5. **Backup**:  Keep copies of /registry/*.csv (critical DOI tracking)

---

**Version:** 1.0
**Last Updated:** April 2025
**Author:** Juan Moisés de la Serna
**Status:** Production Ready
