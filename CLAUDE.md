# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PropAMM Dataset Analysis - A data analysis and visualization toolkit for examining Automated Market Maker (AMM) blockchain transactions from Solana. The dataset contains 5.5M events across 8 AMM protocols (HumidiFi, ZeroFi, TesseraV, SolFiV2, GoonFi, BisonFi, SolFi, AlphaQ) covering ~100,000 blocks of blockchain data.

**Primary Dataset**: [pamm_updates_391876700_391976700.parquet](pamm_updates_391876700_391976700.parquet) (5,526,137 events, 3.2GB in memory)

**Goals of this project**: The goal of this project is to compare how the type of solana validator client (Agave, Jito-Solana, BAM) affects block production, chain output and other relevant metrics. This is to be done via generating meaningful data visualisations.

## Commands

**Note**: Ensure before executing any python-related commands, such as running a script, the virtual environment is activated.

- If the python virtual env is not activated in the current terminal session, activate it via source venv/bin/activate

### Environment Setup

```bash
# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

### Running Analysis Scripts

```bash
# Create interactive dashboard (main visualization tool)
python create_dashboard.py

# Extract top validators by slots/blocks processed
python extract_unique_validators.py

# Fetch validator client information from API (ranks 21-100)
python scripts/fetch_validator_clients.py

# Aggregate validators by client type
python scripts/aggregate_top20_by_client.py
```

## Code Architecture

### Data Loading Pattern

All scripts use a common pattern for loading the Parquet dataset:

- **Pandas** for main analysis ([create_dashboard.py](create_dashboard.py:32), [extract_unique_validators.py](extract_unique_validators.py:32))
- **Polars** recommended for large-scale analysis (faster, mentioned in Copilot instructions)
- Always verify columns exist before analysis (see [extract_unique_validators.py](extract_unique_validators.py:38-41))

### Script Organization

**Root-level scripts** (user-facing analysis):

- [create_dashboard.py](create_dashboard.py) - Main interactive dashboard generator using Plotly
- [extract_unique_validators.py](extract_unique_validators.py) - Validator ranking by slots/events

**scripts/ directory** (supporting data fetching/processing):

- [scripts/fetch_validator_clients.py](scripts/fetch_validator_clients.py) - API integration with validators.app
- [scripts/aggregate_top20_by_client.py](scripts/aggregate_top20_by_client.py) - Groups validators by client type

**outputs/ directory** - Generated files (JSON, CSV, logs from API fetches)

### Validator Analysis Workflow

The codebase follows a multi-stage validator analysis pipeline:

1. **Extract validators** from Parquet → `extract_unique_validators.py` → `top100_validators_by_slots.txt`
2. **Fetch client info** from API → `fetch_validator_clients.py` → `outputs/validator_*.json`
3. **Aggregate by client** → `aggregate_top20_by_client.py` → `outputs/top20_by_client_*.txt`

This pipeline identifies which validator software clients (Jito-solana, Harmonic, etc.) are processing the most blocks.

### API Integration Details

- **Endpoint**: validators.app API (`https://www.validators.app/api/v1/validators/mainnet/{id}.json`)
- **Authentication**: Token-based (see [scripts/fetch_validator_clients.py](scripts/fetch_validator_clients.py:46-47))
- **Rate limiting**: 7-second delay between requests ([scripts/fetch_validator_clients.py](scripts/fetch_validator_clients.py:106))
- **Caching**: Skips existing JSON files to avoid re-fetching ([scripts/fetch_validator_clients.py](scripts/fetch_validator_clients.py:61-62))
- **Error handling**: Logs all operations to `outputs/fetch_log.txt`

### Dashboard Architecture ([create_dashboard.py](create_dashboard.py))

Uses Plotly `make_subplots` for 5-panel layout:

1. **Time Series** (row=1, col=1, colspan=2) - Stacked area chart of AMM activity by 5-min bins
2. **Market Share** (row=2, col=1) - Donut pie chart of protocol distribution
3. **Event Types** (row=2, col=2) - Bar chart comparing ORACLE vs TRADE events
4. **Block Throughput** (row=3, col=1) - Line chart with 100-block rolling average
5. **Top Validators** (row=3, col=2) - Horizontal bar chart of top 10 validators

All visualizations include custom hover templates for interactivity.

## Dataset Schema

Key columns from Parquet file:

- `slot` (uint64) - Block number identifier
- `time` (uint32) - Unix timestamp
- `validator` (string) - Node identifier (base58 encoded)
- `tx_idx` (int64) - Transaction position in block
- `sig` (string) - Transaction signature
- `signer` (string) - Wallet address
- `kind` (string) - Event type: "ORACLE" (87.6%) or "TRADE" (12.4%)
- `amm` (string) - Protocol name (HumidiFi, ZeroFi, etc.)
- `account_updates` (nested list) - State changes with pool information
- `trades` (nested list) - Trade details (amm, pool, from_token, to_token)
- `us_since_first_shred` (int64) - Timing metric

**Note**: ~87.6% of events are ORACLE updates (price/state changes), only 12.4% are actual TRADE events.

## Development Conventions

### Data Analysis Best Practices

When creating new analysis scripts:

- Use lazy loading or chunked processing for the 3.2GB dataset
- Include schema exploration first (`df.schema`, `df.columns`, `len(df)`)
- Add data profiling (missing values, unique counts)
- Use AMM domain names (e.g., `pool_updates`, `trade_events`, not generic names)
- Sample data first (`df.head(1000)`) before full processing
- Verify block number ranges (391876700-391976700)

### Output Naming Convention

- Timestamp-based filenames: `analysis_20260108.csv`
- Validator files: `validator_{id}.json`
- Aggregated reports: `top20_by_client_{date}.txt`
- CSV exports: `validator_clients_21_100_{date}.csv`

### Client Type Classification

Validators are grouped by software client ([scripts/aggregate_top20_by_client.py](scripts/aggregate_top20_by_client.py:42-53)):

- **Jito-solana**: `software_client = "JitoLabs"` AND `software_client_id = 1`
- **Harmonic**: `software_client = "Unknown"` or `None` AND `software_client_id = 10`
- **Other**: All remaining validators

This classification is critical for understanding validator diversity and client distribution on Solana.
