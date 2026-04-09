#!/usr/bin/env python3
"""
INIT PIPELINE SCRIPT
=====================
Validación inteligente + planificación automática para Jules
- Verifica accesos (case.law, Zenodo, disco)
- Descarga índices de metadata
- Genera plan de ejecución (config.json)
- Reporta bloqueadores ANTES de comenzar

Uso: python3 init_pipeline.py
"""

import os
import sys
import json
import requests
import shutil
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

# ==========================================
# CONFIGURACIÓN
# ==========================================

CONFIG = {
    "case_law_base": "https://static.case.law",
    "zenodo_api": "https://api.zenodo.org",
    "zenodo_sandbox": "https://sandbox.zenodo.org",
    "project_root": os.getcwd(),
    "min_free_space_gb": 200,
    "timeout_seconds": 30
}

# ==========================================
# SETUP DIRECTORIOS
# ==========================================

def setup_directories():
    """Crea estructura de directorios"""
    dirs = [
        "raw_data",
        "processed_data",
        "datasets",
        "papers",
        "meta_papers",
        "outputs",
        "registry",
        "logs",
        "metadata_cache"
    ]

    for d in dirs:
        path = Path(CONFIG["project_root"]) / d
        path.mkdir(parents=True, exist_ok=True)

    return True

# ==========================================
# LOGGING
# ==========================================

class Logger:
    def __init__(self):
        self.log_file = Path(CONFIG["project_root"]) / "logs" / "init.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {msg}"
        print(log_msg)
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")

    def success(self, msg):
        self.log(msg, "✅ SUCCESS")

    def warning(self, msg):
        self.log(msg, "⚠️  WARNING")

    def error(self, msg):
        self.log(msg, "❌ ERROR")

    def info(self, msg):
        self.log(msg, "ℹ️  INFO")

logger = Logger()

# ==========================================
# CHECK 1: CASO.LAW ACCESIBLE
# ==========================================

def check_caselaw():
    """Verifica conectividad a case.law"""
    logger.info("Checking case.law connectivity...")

    try:
        response = requests.head(
            f"{CONFIG['case_law_base']}/",
            timeout=CONFIG["timeout_seconds"]
        )
        if response.status_code == 200:
            logger.success("case.law is accessible")
            return True
        else:
            logger.error(f"case.law returned status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Cannot connect to case.law: {str(e)}")
        return False

# ==========================================
# CHECK 2: ZENODO ACCESIBLE
# ==========================================

def check_zenodo():
    """Verifica API de Zenodo (tanto production como sandbox)"""
    logger.info("Checking Zenodo API access...")

    zenodo_token = os.getenv("ZENODO_TOKEN")
    if not zenodo_token:
        logger.warning("ZENODO_TOKEN not found in .env")
        logger.info("Trying Zenodo Sandbox instead (for testing)")
        zenodo_token = os.getenv("ZENODO_SANDBOX_TOKEN")
        use_sandbox = True
    else:
        use_sandbox = False

    if not zenodo_token:
        logger.error("Neither ZENODO_TOKEN nor ZENODO_SANDBOX_TOKEN found")
        logger.error("Create .env file with: ZENODO_TOKEN=your_token_here")
        return False, use_sandbox

    api_url = CONFIG["zenodo_sandbox"] if use_sandbox else CONFIG["zenodo_api"]

    try:
        headers = {"Authorization": f"Bearer {zenodo_token}"}
        response = requests.get(
            f"{api_url}/user",
            headers=headers,
            timeout=CONFIG["timeout_seconds"]
        )

        if response.status_code == 200:
            user_data = response.json()
            logger.success(f"Zenodo authenticated as: {user_data.get('email', 'Unknown')}")
            logger.info(f"Using {'SANDBOX' if use_sandbox else 'PRODUCTION'} environment")
            return True, use_sandbox
        else:
            logger.error(f"Zenodo auth failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False, use_sandbox
    except Exception as e:
        logger.error(f"Cannot connect to Zenodo: {str(e)}")
        return False, use_sandbox

# ==========================================
# CHECK 3: ESPACIO EN DISCO
# ==========================================

def check_disk_space():
    """Verifica espacio disponible en disco"""
    logger.info(f"Checking disk space (minimum required: {CONFIG['min_free_space_gb']}GB)...")

    try:
        stat = shutil.disk_usage(CONFIG["project_root"])
        free_gb = stat.free / (1024**3)

        if free_gb >= CONFIG["min_free_space_gb"]:
            logger.success(f"Disk space OK: {free_gb:.1f}GB available")
            return True, free_gb
        else:
            logger.warning(f"Low disk space: {free_gb:.1f}GB available (need {CONFIG['min_free_space_gb']}GB)")
            return False, free_gb
    except Exception as e:
        logger.error(f"Cannot check disk space: {str(e)}")
        return False, 0

# ==========================================
# CHECK 4: PERMISOS DE ESCRITURA
# ==========================================

def check_write_permissions():
    """Verifica permisos de escritura en directorios"""
    logger.info("Checking write permissions...")

    try:
        test_file = Path(CONFIG["project_root"]) / "logs" / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        logger.success("Write permissions OK")
        return True
    except Exception as e:
        logger.error(f"Write permission denied: {str(e)}")
        return False

# ==========================================
# DESCARGA METADATA INDICES
# ==========================================

def download_metadata_indices():
    """Descarga índices de metadata de case.law"""
    logger.info("Downloading metadata indices from case.law...")

    metadata_files = {
        "ReportersMetadata.json": f"{CONFIG['case_law_base']}/ReportersMetadata.json",
        "VolumesMetadata.json": f"{CONFIG['case_law_base']}/VolumesMetadata.json",
        "JurisdictionsMetadata.json": f"{CONFIG['case_law_base']}/JurisdictionsMetadata.json"
    }

    cache_dir = Path(CONFIG["project_root"]) / "metadata_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    metadata = {}

    for filename, url in metadata_files.items():
        try:
            logger.info(f"  Downloading {filename}...")
            filepath = cache_dir / filename

            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

            with open(filepath, 'r') as f:
                metadata[filename.replace(".json", "")] = json.load(f)

            logger.success(f"  Downloaded {filename}")
        except Exception as e:
            logger.warning(f"Could not download {filename}: {str(e)}")
            return None

    return metadata

# ==========================================
# ANALIZAR METADATA Y GENERAR PLAN
# ==========================================

def analyze_metadata(metadata):
    """Analiza metadata y genera plan de ejecución"""
    logger.info("Analyzing metadata and generating execution plan...")

    if not metadata or not all(k in metadata for k in ["ReportersMetadata", "VolumesMetadata", "JurisdictionsMetadata"]):
        logger.error("Metadata incomplete")
        return None

    try:
        reporters = metadata["ReportersMetadata"]
        volumes = metadata["VolumesMetadata"]
        jurisdictions = metadata["JurisdictionsMetadata"]

        # Estadísticas
        num_reporters = len(reporters) if isinstance(reporters, list) else len(reporters.get("reporters", []))
        num_volumes = len(volumes) if isinstance(volumes, list) else len(volumes.get("volumes", []))
        num_jurisdictions = len(jurisdictions) if isinstance(jurisdictions, list) else len(jurisdictions.get("jurisdictions", []))

        # Estimaciones (aproximadas)
        avg_volume_size_mb = 150  # Promedio estimado
        total_size_gb = (num_volumes * avg_volume_size_mb) / 1024

        # Recomendación: top jurisdicciones por tamaño
        top_jurisdictions = ["federal", "new_york", "california", "texas", "florida"]

        plan = {
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "num_reporters": num_reporters,
                "num_volumes": num_volumes,
                "num_jurisdictions": num_jurisdictions
            },
            "estimates": {
                "total_size_gb": round(total_size_gb, 1),
                "avg_volume_size_mb": avg_volume_size_mb,
                "estimated_download_time_hours": round(total_size_gb / 10),  # 10GB/h promedio
                "estimated_dois_total": round(num_volumes * 0.5)  # ~0.5 DOI por volumen
            },
            "recommendations": {
                "start_with": {
                    "jurisdictions": top_jurisdictions,
                    "rationale": "largest_and_most_cited",
                    "estimated_volumes": "~500-800",
                    "estimated_size_gb": 100,
                    "estimated_downloads_hours": 10
                },
                "phases_recommended": 10,
                "parallelization": "recommended (up to 5 concurrent downloads)"
            },
            "blockers": [],
            "warnings": []
        }

        logger.success(f"Plan generated: {num_volumes} volumes, ~{round(total_size_gb, 1)}GB")
        return plan

    except Exception as e:
        logger.error(f"Error analyzing metadata: {str(e)}")
        return None

# ==========================================
# GENERAR CONFIG FINAL
# ==========================================

def generate_config(checks, plan):
    """Genera archivo config.json final"""
    logger.info("Generating final config.json...")

    config_data = {
        "generated_at": datetime.now().isoformat(),
        "status": "ready" if all(checks.values()) else "warnings",
        "checks": checks,
        "plan": plan,
        "environment": {
            "python_version": sys.version,
            "project_root": CONFIG["project_root"],
            "zenodo_environment": "sandbox" if os.getenv("ZENODO_SANDBOX_TOKEN") else "production"
        },
        "next_steps": [
            "1. Review config.json",
            "2. If status=ready, run: python3 pipeline_phase1.py",
            "3. Check /logs/execution.log for progress"
        ]
    }

    config_path = Path(CONFIG["project_root"]) / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)

    logger.success(f"Config saved to {config_path}")
    return config_path

# ==========================================
# GENERAR REPORTE
# ==========================================

def generate_report(checks, plan, disk_info):
    """Genera reporte legible para el usuario"""
    logger.info("Generating summary report...")

    report = f"""
╔════════════════════════════════════════════════════════════════╗
║                  INIT PIPELINE REPORT                          ║
║              Jules Case.Law → Zenodo Pipeline                  ║
╚════════════════════════════════════════════════════════════════╝

✓ SYSTEM CHECKS
─────────────────────────────────────────────────────────────────
  case.law connectivity:        {'✅ OK' if checks['case_law'] else '❌ FAILED'}
  Zenodo API access:            {'✅ OK' if checks['zenodo'] else '❌ FAILED'}
  Disk space (>{CONFIG['min_free_space_gb']}GB):     {'✅ OK' if checks['disk_space'] else '⚠️  LOW'}
  Write permissions:            {'✅ OK' if checks['permissions'] else '❌ FAILED'}

📊 METADATA ANALYSIS
─────────────────────────────────────────────────────────────────
  Reporters available:          {plan.get('metadata', {}).get('num_reporters', 'N/A')}
  Volumes available:            {plan.get('metadata', {}).get('num_volumes', 'N/A')}
  Jurisdictions:                {plan.get('metadata', {}).get('num_jurisdictions', 'N/A')}

📈 ESTIMATES (if downloading ALL data)
─────────────────────────────────────────────────────────────────
  Total size:                   {plan.get('estimates', {}).get('total_size_gb', 'N/A')}GB
  Download time:                {plan.get('estimates', {}).get('estimated_download_time_hours', 'N/A')}h
  Estimated DOIs:               {plan.get('estimates', {}).get('estimated_dois_total', 'N/A')}

💡 RECOMMENDATION
─────────────────────────────────────────────────────────────────
  Start with top jurisdictions (~100GB, ~10h):
    - federal
    - new_york
    - california
  This will generate ~200-300 DOIs as proof of concept

🚀 NEXT STEPS
─────────────────────────────────────────────────────────────────
  1. Review /config.json for detailed plan
  2. If all checks ✅, run: python3 phase_1_download.py
  3. Monitor progress in /logs/execution.log

✍️  Config file:  {CONFIG['project_root']}/config.json
📋 Log file:      {CONFIG['project_root']}/logs/init.log

"""

    report_path = Path(CONFIG["project_root"]) / "logs" / "init_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)

    print(report)
    logger.success(f"Report saved to {report_path}")

# ==========================================
# MAIN
# ==========================================

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║          INITIALIZING CASE.LAW → ZENODO PIPELINE               ║
║                 Jules Autonomous Agent                         ║
╚════════════════════════════════════════════════════════════════╝
""")

    logger.info("=== INIT PIPELINE STARTED ===")

    # Setup
    logger.info("Setting up directories...")
    setup_directories()
    logger.success("Directories ready")

    # Checks
    checks = {
        "case_law": check_caselaw(),
        "zenodo": check_zenodo()[0],
        "disk_space": check_disk_space()[0],
        "permissions": check_write_permissions()
    }

    disk_info = check_disk_space()[1]

    # Metadata
    logger.info("\n" + "="*60)
    metadata = download_metadata_indices()

    # Plan
    logger.info("\n" + "="*60)
    plan = analyze_metadata(metadata) if metadata else None

    # Config
    logger.info("\n" + "="*60)
    if plan:
        config_path = generate_config(checks, plan)
    else:
        logger.error("Could not generate plan")
        plan = {"error": "metadata_download_failed"}
        config_path = generate_config(checks, plan)

    # Report
    logger.info("\n" + "="*60)
    generate_report(checks, plan or {}, disk_info)

    # Status final
    all_ok = all(checks.values())
    if all_ok and metadata:
        logger.success("\n✅ INIT COMPLETE - All checks passed. Ready to proceed to Phase 1.")
        return 0
    else:
        logger.warning("\n⚠️  INIT COMPLETE - Some checks failed. Review report above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
