# PHASE -1
## SYSTEM VALIDATION & AUTO-PLANNING
### Quick Start Guide for Jules

#### WHAT PHASE -1 DOES
Phase -1 is an AUTONOMOUS INITIALIZATION script that Jules runs BEFORE anything else. It:
* ✅ Validates all system access (case.law, Zenodo, disk, permissions)
* ✅ Downloads metadata indices from case.law
* ✅ Analyzes available data (volume count, size, jurisdictions)
* ✅ Generates an AUTOMATIC EXECUTION PLAN (config.json)
* ✅ Creates a detailed report of blockers and recommendations
* ✅ Decides whether to PROCEED or PAUSE

#### HOW JULES EXECUTES THIS
**Step 1: Setup Environment**
Create project directory with .env file:
(See README_PIPELINE.md for details)

**Step 2: Copy Init Script**
Make sure `init_pipeline.py` is in your project root
* File: `init_pipeline.py` (provided)
* Location: `~/pipeline_project/init_pipeline.py`
* Permissions: `python3 init_pipeline.py`

**Step 3: EXECUTE INIT SCRIPT**
This is what Jules does (single command):
`python3 init_pipeline.py`

The script will:
1. Create all necessary directories
2. Test case.law connectivity (5s timeout)
3. Validate Zenodo API token
4. Check disk space (minimum 200GB required)
5. Download metadata indices from case.law
6. Analyze data and generate execution plan
7. Create `config.json` with recommendations
8. Print detailed report to console + save to `init_report.txt`

#### OUTPUT FILES GENERATED
After `init_pipeline.py` completes, you'll have:

| FILE | PURPOSE |
|------|---------|
| `config.json` | Auto-generated plan (Jules reads this) |
| `init_report.txt` | Human-readable summary (for Juan) |
| `logs/init.log` | Complete execution log (timestamps) |
| `metadata_cache/` | Downloaded JSON indices (reused later) |

#### IF CHECKS PASS ✅
Status = 'ready' in `config.json`
* Jules proceeds to Phase 1 automatically
* Reads `config.json` to understand the plan
* Executes: `python3 phase_1_download.py`
* Downloads data according to recommendations

#### IF CHECKS FAIL ❌
Status = 'warnings' or 'blocker' in `config.json`
Possible issues and solutions:

| CHECK FAILS | ERROR | SOLUTION |
|-------------|-------|----------|
| case.law | Network timeout | Check internet. case.law may be down. |
| Zenodo API | Invalid token | Generate new token at zenodo.org/account/settings/applications/ |
| Disk space | <200GB free | Increase disk or use different project_root |
| Permissions | Cannot write | Change permissions: `chmod 755 project_root` |

#### TECHNICAL NOTES FOR JULES
* `init_pipeline.py` requires: `requests`, `pathlib` (standard library)
* If `requests` not installed: `pip install requests`
* Script timeout is 30 seconds per API call
* All output is logged to `logs/init.log` with timestamps
* Metadata indices are cached for reuse in later phases
* `config.json` is JSON-parseable (no comments)
