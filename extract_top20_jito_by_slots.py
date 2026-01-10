#!/usr/bin/env python3
"""
Extract the top 20 validators running Jito-solana (by slots processed)
Reads from top100_validators_by_slots.txt and checks client info in outputs folder
"""

import json
import os
import re
from datetime import datetime

def parse_top100_file(filename):
    """Parse the top100 validators file and return list of (rank, validator_id, slots, events)"""
    validators = []

    with open(filename, 'r') as f:
        for line in f:
            # Skip comments and headers
            if line.startswith('#') or line.startswith('Rank') or line.startswith('---') or line.startswith('=') or not line.strip():
                continue

            # Parse the data line - format: "Rank   Validator_ID   Slots   Events"
            # Example: "1      HEL1USMZKAL2odpNBj2oCjffnFGaYwmbGmyewGv1e2TU          3,778        210,865"
            parts = line.split()
            if len(parts) >= 4:
                try:
                    rank = int(parts[0])
                    validator_id = parts[1]
                    slots = parts[2].replace(',', '')
                    events = parts[3].replace(',', '')
                    validators.append((rank, validator_id, slots, events))
                except (ValueError, IndexError):
                    continue

    return validators

def get_validator_client_info(validator_id, outputs_dir='outputs'):
    """Check if validator JSON exists and return client info"""
    json_path = os.path.join(outputs_dir, f'validator_{validator_id}.json')

    if not os.path.exists(json_path):
        return None

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            return {
                'software_client': data.get('software_client'),
                'software_client_id': data.get('software_client_id'),
                'name': data.get('name', 'Unknown'),
                'vote_account': data.get('vote_account', validator_id)
            }
    except (json.JSONDecodeError, FileNotFoundError):
        return None

def main():
    print("=" * 100)
    print("EXTRACTING TOP 20 JITO-SOLANA VALIDATORS (BY SLOTS PROCESSED)")
    print("=" * 100)
    print()

    # Parse the top 100 validators file
    top100_file = 'top100_validators_by_slots.txt'
    validators = parse_top100_file(top100_file)

    print(f"Parsed {len(validators)} validators from {top100_file}")
    print()

    # Find top 20 Jito validators
    jito_validators = []
    checked_count = 0
    missing_json = []

    for rank, validator_id, slots, events in validators:
        checked_count += 1

        # Get client info from JSON file
        client_info = get_validator_client_info(validator_id)

        if client_info is None:
            missing_json.append((rank, validator_id))
            print(f"Rank {rank:3d}: {validator_id} - JSON NOT FOUND")
            continue

        software_client = client_info.get('software_client')
        software_client_id = client_info.get('software_client_id')

        # Check if it's Jito-solana (JitoLabs with client_id = 1)
        if software_client == 'JitoLabs' and software_client_id == 1:
            jito_validators.append({
                'rank': rank,
                'validator_id': validator_id,
                'slots': slots,
                'events': events,
                'name': client_info.get('name'),
                'software_client': software_client,
                'software_client_id': software_client_id
            })
            print(f"Rank {rank:3d}: {validator_id} - JITO ✓ ({client_info.get('name')})")

            # Stop when we have 20
            if len(jito_validators) >= 20:
                print()
                print(f"Found 20 Jito validators after checking {checked_count} validators")
                break
        else:
            print(f"Rank {rank:3d}: {validator_id} - {software_client or 'Unknown'} (ID: {software_client_id})")

    print()
    print("=" * 100)
    print(f"TOP 20 JITO-SOLANA VALIDATORS (BY SLOTS)")
    print("=" * 100)
    print()
    print(f"{'Rank':<6} {'Validator ID':<45} {'Slots':<12} {'Events':<12} {'Name':<30}")
    print("-" * 100)

    for v in jito_validators:
        name = v['name'] if v['name'] else 'Unknown'
        print(f"{v['rank']:<6} {v['validator_id']:<45} {v['slots']:<12} {v['events']:<12} {name[:30]:<30}")

    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"Total validators checked: {checked_count}")
    print(f"Jito-solana validators found: {len(jito_validators)}")
    print(f"Missing JSON files: {len(missing_json)}")

    # Save to output file
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = f'outputs/top20_jito_by_slots_{timestamp}.txt'

    with open(output_file, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write(f"TOP 20 JITO-SOLANA VALIDATORS (BY SLOTS PROCESSED)\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source: top100_validators_by_slots.txt\n")
        f.write(f"Criteria: software_client = 'JitoLabs' AND software_client_id = 1\n")
        f.write("=" * 100 + "\n\n")

        f.write(f"{'Rank':<6} {'Validator ID':<45} {'Slots':<12} {'Events':<12} {'Name':<30}\n")
        f.write("-" * 100 + "\n")

        for v in jito_validators:
            name = v['name'] if v['name'] else 'Unknown'
            f.write(f"{v['rank']:<6} {v['validator_id']:<45} {v['slots']:<12} {v['events']:<12} {name[:30]:<30}\n")

        f.write("\n" + "=" * 100 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 100 + "\n")
        f.write(f"Total validators checked: {checked_count}\n")
        f.write(f"Jito-solana validators found: {len(jito_validators)}\n")
        f.write(f"Missing JSON files: {len(missing_json)}\n")

        if missing_json:
            f.write("\nValidators with missing JSON files:\n")
            for rank, vid in missing_json:
                f.write(f"  Rank {rank}: {vid}\n")

    print(f"\nResults saved to: {output_file}")

    # Also save as CSV for easy analysis
    csv_file = f'outputs/top20_jito_by_slots_{timestamp}.csv'
    with open(csv_file, 'w') as f:
        f.write("rank,validator_id,slots,events,name,software_client,software_client_id\n")
        for v in jito_validators:
            name = v['name'] if v['name'] else 'Unknown'
            f.write(f"{v['rank']},{v['validator_id']},{v['slots']},{v['events']},\"{name}\",{v['software_client']},{v['software_client_id']}\n")

    print(f"CSV saved to: {csv_file}")

if __name__ == '__main__':
    main()
