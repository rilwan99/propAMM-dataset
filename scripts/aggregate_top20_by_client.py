import os
import json
from datetime import datetime
from glob import glob

def get_validator_files(outputs_dir):
    return glob(os.path.join(outputs_dir, "validator_*.json"))

def extract_validator_info(filepath):
    try:
        with open(filepath) as f:
            data = json.load(f)
        validator_id = os.path.basename(filepath).replace("validator_", "").replace(".json", "")
        client = data.get("software_client")
        client_id = data.get("software_client_id")
        # Try to extract slots/events if present
        slots = data.get("unique_slots") or data.get("slots")
        events = data.get("total_events") or data.get("events")
        return {
            "validator_id": validator_id,
            "software_client": client,
            "software_client_id": client_id,
            "slots": slots,
            "events": events
        }
    except Exception as e:
        return {"error": str(e), "filepath": filepath}

def main():
    outputs_dir = "outputs"
    files = get_validator_files(outputs_dir)
    validators = []
    errors = []
    for file in files:
        info = extract_validator_info(file)
        if "error" in info:
            errors.append(info)
        else:
            validators.append(info)

    # Group by client type
    client_groups = {
        "Jito-solana": [],
        "Harmonic": [],
        "Other": []
    }
    for v in validators:
        if v["software_client"] == "JitoLabs" and v["software_client_id"] == 1:
            client_groups["Jito-solana"].append(v)
        elif (v["software_client"] == "Unknown" or v["software_client"] is None) and v["software_client_id"] == 10:
            client_groups["Harmonic"].append(v)
        else:
            client_groups["Other"].append(v)

    # Sort by slots, then events, then validator_id
    def sort_key(v):
        slots = v["slots"] if v["slots"] is not None else 0
        events = v["events"] if v["events"] is not None else 0
        return (-int(slots), -int(events), v["validator_id"])

    for group in client_groups:
        client_groups[group] = sorted(client_groups[group], key=sort_key)[:20]

    # Write output
    today = datetime.now().strftime("%Y%m%d")
    out_path = os.path.join(outputs_dir, f"top20_by_client_{today}.txt")
    with open(out_path, "w") as f:
        for group in ["Jito-solana", "Harmonic", "Other"]:
            f.write(f"=== Top 20 Validators for {group} ===\n")
            f.write(f"{'Rank':<5} {'Validator ID':<44} {'Slots':>10} {'Events':>10}\n")
            f.write("-"*75 + "\n")
            for i, v in enumerate(client_groups[group], 1):
                f.write(f"{i:<5} {v['validator_id']:<44} {str(v['slots'] or '-'):>10} {str(v['events'] or '-'):>10}\n")
            f.write("\n")
        if errors:
            f.write("=== Errors/Incomplete Data ===\n")
            for err in errors:
                f.write(f"{err['filepath']}: {err['error']}\n")
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()
