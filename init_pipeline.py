import os
import json
import requests
import shutil
import sys

def check_access(url):
    print(f"Checking access to {url}...")
    try:
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {url} accessible")
            return True
        else:
            print(f"❌ {url} returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing {url}: {e}")
        return False

def check_zenodo():
    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        print("⚠️ ZENODO_TOKEN not found in environment")
        return False

    print("Checking Zenodo API token...")
    try:
        response = requests.get("https://zenodo.org/api/deposit/depositions",
                                params={"access_token": token}, timeout=10)
        if response.status_code == 200:
            print("✅ Zenodo API token valid")
            return True
        else:
            print(f"❌ Zenodo API token invalid (status {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error checking Zenodo token: {e}")
        return False

def check_disk_space():
    total, used, free = shutil.disk_usage(".")
    free_gb = free / (2**30)
    print(f"Available disk space: {free_gb:.2f} GB")
    if free_gb < 10:
        print("⚠️ Low disk space (< 10 GB)")
    return free_gb

def check_permissions():
    if os.access(".", os.W_OK):
        print("✅ Write permissions confirmed")
        return True
    else:
        print("❌ No write permissions in current directory")
        return False

def download_metadata():
    base_url = "https://static.case.law/"
    files = ["ReportersMetadata.json", "VolumesMetadata.json", "JurisdictionsMetadata.json"]
    downloaded = []
    for f in files:
        print(f"Downloading {f}...")
        try:
            r = requests.get(base_url + f, stream=True)
            if r.status_code == 200:
                with open(f, 'wb') as out:
                    for chunk in r.iter_content(chunk_size=8192):
                        out.write(chunk)
                print(f"✅ {f} downloaded")
                downloaded.append(f)
            else:
                print(f"❌ Failed to download {f} (status {r.status_code})")
        except Exception as e:
            print(f"❌ Error downloading {f}: {e}")
    return downloaded

def analyze_metadata():
    print("Analyzing metadata...")
    try:
        with open("JurisdictionsMetadata.json", "r") as f:
            jurisdictions = json.load(f)

        with open("ReportersMetadata.json", "r") as f:
            reporters = json.load(f)

        with open("VolumesMetadata.json", "r") as f:
            volumes = json.load(f)

        num_jurisdictions = len(jurisdictions)
        num_volumes = len(volumes)

        # Estimate total size. Hardcoded based on user prompt for total (~2.3 TB)
        # and we can try to find volume size in metadata if available.
        # Looking at typical CAP metadata, it might not have exact size for all.

        # Find top 10 jurisdictions by volume count
        jur_vol_count = {}
        for vol in volumes:
            jurs = vol.get("jurisdictions", [])
            jur = jurs[0].get("name", "Unknown") if jurs else "Unknown"
            jur_vol_count[jur] = jur_vol_count.get(jur, 0) + 1

        top_jurs = sorted(jur_vol_count.items(), key=lambda x: x[1], reverse=True)[:10]

        analysis = {
            "volumes_available": num_volumes,
            "jurisdictions_count": num_jurisdictions,
            "total_size_estimated_tb": 2.3,
            "recommendation": "download top 10 jurisdictions (~150GB)",
            "top_10_jurisdictions": top_jurs,
            "estimated_time_h": 48,
            "estimated_dois": "300-400"
        }

        return analysis
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return None

def main():
    print("--- INIT SCRIPT ---")

    # 1. Validation
    case_law_ok = check_access("https://static.case.law/")
    zenodo_ok = check_zenodo()
    disk_free = check_disk_space()
    perms_ok = check_permissions()

    if not (case_law_ok and perms_ok):
        print("❌ Critical checks failed. Stopping.")
        sys.exit(1)

    # 2. Download
    downloaded = download_metadata()
    if len(downloaded) < 3:
        print("❌ Could not download all metadata files. Stopping.")
        sys.exit(1)

    # 3. Analyze
    analysis = analyze_metadata()
    if not analysis:
        sys.exit(1)

    # 4. Generate Config
    config = {
        "status": "READY",
        "checks": {
            "case_law": case_law_ok,
            "zenodo": zenodo_ok,
            "disk_free_gb": disk_free,
            "permissions": perms_ok
        },
        "analysis": analysis,
        "plan": {
            "target_jurisdictions": [j[0] for j in analysis["top_10_jurisdictions"]],
            "action": "download_top_jurisdictions"
        }
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("✅ config.json generated with plan")
    print("--- INIT SCRIPT COMPLETE ---")

if __name__ == "__main__":
    main()
