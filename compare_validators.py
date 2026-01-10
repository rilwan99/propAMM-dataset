#!/usr/bin/env python3
"""
Compare validator IDs between top_by_client_20260109.txt and outputs folder
"""

import os
import re

# Extract validators from top_by_client_20260109.txt
top_by_client_validators = set()

with open('top_by_client_20260109.txt', 'r') as f:
    content = f.read()
    # Extract all base58 validator IDs (43-44 character alphanumeric strings)
    validators = re.findall(r'\b[1-9A-HJ-NP-Za-km-z]{43,44}\b', content)
    top_by_client_validators.update(validators)

print(f"Found {len(top_by_client_validators)} unique validators in top_by_client_20260109.txt")
print("Validators in top_by_client_20260109.txt:")
for v in sorted(top_by_client_validators):
    print(f"  {v}")

print("\n" + "="*80 + "\n")

# Extract validators from outputs folder
outputs_validators = set()
outputs_dir = 'outputs'

for filename in os.listdir(outputs_dir):
    if filename.startswith('validator_') and filename.endswith('.json'):
        validator_id = filename.replace('validator_', '').replace('.json', '')
        outputs_validators.add(validator_id)

print(f"Found {len(outputs_validators)} validators in outputs folder")

print("\n" + "="*80 + "\n")

# Find validators in outputs but NOT in top_by_client
in_outputs_not_in_top = outputs_validators - top_by_client_validators

print(f"Validators in outputs folder but NOT in top_by_client_20260109.txt ({len(in_outputs_not_in_top)}):")
for v in sorted(in_outputs_not_in_top):
    print(f"  {v}")

print("\n" + "="*80 + "\n")

# Find validators in top_by_client but NOT in outputs
in_top_not_in_outputs = top_by_client_validators - outputs_validators

print(f"Validators in top_by_client_20260109.txt but NOT in outputs folder ({len(in_top_not_in_outputs)}):")
for v in sorted(in_top_not_in_outputs):
    print(f"  {v}")

print("\n" + "="*80 + "\n")

# Summary
print("SUMMARY:")
print(f"  Total in top_by_client_20260109.txt: {len(top_by_client_validators)}")
print(f"  Total in outputs folder: {len(outputs_validators)}")
print(f"  In outputs but NOT in top_by_client: {len(in_outputs_not_in_top)}")
print(f"  In top_by_client but NOT in outputs: {len(in_top_not_in_outputs)}")
print(f"  Intersection (in both): {len(top_by_client_validators & outputs_validators)}")
