import os
from dotenv import load_dotenv
import json
import time
import requests
from datetime import datetime


# Extract validator IDs for ranks 21-100 from top100_validators_by_slots.txt
def extract_validator_ids(filepath, start_rank=21, end_rank=100):
    ids = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('Rank') or line.startswith('-'):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                rank = int(parts[0])
            except ValueError:
                continue
            if start_rank <= rank <= end_rank:
                ids.append(parts[1])
    return ids

def get_top100_path():
    # Try both possible locations
    candidates = [
        os.path.join(os.path.dirname(__file__), "../top100_validators_by_slots.txt"),
        os.path.join(os.path.dirname(__file__), "../../top100_validators_by_slots.txt"),
        os.path.join(os.path.dirname(__file__), "top100_validators_by_slots.txt"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "top100_validators_by_slots.txt")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "top100_validators_by_slots.txt")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "top100_validators_by_slots.txt")),
        "top100_validators_by_slots.txt"
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Could not find top100_validators_by_slots.txt")

VALIDATOR_IDS = extract_validator_ids(get_top100_path(), 21, 100)

API_URL = "https://www.validators.app/api/v1/validators/mainnet/{}.json"
load_dotenv()
API_TOKEN = os.environ.get("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("API_TOKEN not set. Please define it in your .env file.")
HEADERS = {"Token": API_TOKEN}
OUTPUT_DIR = "outputs"
LOG_FILE = os.path.join(OUTPUT_DIR, "fetch_log.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def log(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {msg}\n")

def fetch_and_save(validator_id):
    url = API_URL.format(validator_id)
    out_path = os.path.join(OUTPUT_DIR, f"validator_{validator_id}.json")
    if os.path.exists(out_path):
        log(f"SKIP: {validator_id} | already exists")
        # Try to read existing file for aggregation
        try:
            with open(out_path) as f:
                data = json.load(f)
            return {
                "validator_id": validator_id,
                "software_client": data.get("software_client"),
                "software_client_id": data.get("software_client_id")
            }
        except Exception as e:
            log(f"ERROR: {validator_id} | failed to read existing file: {e}")
            return {
                "validator_id": validator_id,
                "software_client": None,
                "software_client_id": None,
                "error": f"read error: {e}"
            }
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        log(f"SUCCESS: {validator_id} | software_client: {data.get('software_client')} | software_client_id: {data.get('software_client_id')}")
        return {
            "validator_id": validator_id,
            "software_client": data.get("software_client"),
            "software_client_id": data.get("software_client_id")
        }
    except Exception as e:
        log(f"ERROR: {validator_id} | {e}")
        return {
            "validator_id": validator_id,
            "software_client": None,
            "software_client_id": None,
            "error": str(e)
        }

def main():
    results = []
    for vid in VALIDATOR_IDS:
        result = fetch_and_save(vid)
        results.append(result)
        time.sleep(7)  # increased delay to avoid rate limit
    # Save CSV for ranks 21-100
    csv_path = os.path.join(OUTPUT_DIR, f"validator_clients_21_100_{datetime.now().strftime('%Y%m%d')}.csv")
    with open(csv_path, "w") as f:
        f.write("validator_id,software_client,software_client_id,error\n")
        for r in results:
            f.write(f"{r['validator_id']},{r.get('software_client','')},{r.get('software_client_id','')},{r.get('error','')}\n")
    log(f"Saved CSV: {csv_path}")

if __name__ == "__main__":
    main()
