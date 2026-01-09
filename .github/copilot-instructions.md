# AI Coding Instructions for propAMM Dataset Analysis

## Project Overview
This is a data analysis workspace for examining propAMM (Automated Market Maker) update data stored in Parquet format. The dataset covers block range 391876700-391976700 (approximately 100,000 blocks of blockchain data).

## Data Context
- **Primary Data File**: `pamm_updates_391876700_391976700.parquet`
- **Format**: Apache Parquet (columnar storage optimized for analytics)
- **Domain**: Blockchain/DeFi - Automated Market Maker pool updates and state changes

## Development Conventions

### Python Scripts for Data Analysis
When creating analysis scripts:
- Use **pandas** or **polars** for Parquet file reading (polars is faster for large datasets)
- Include initial schema exploration (columns, dtypes, row count)
- Add data profiling steps (missing values, unique counts, value distributions)
- Use descriptive variable names that reflect AMM domain concepts (e.g., `pool_updates`, `liquidity_changes`)

### Recommended Analysis Workflow
```python
import polars as pl  # or pandas as pd

# 1. Load with lazy evaluation for large files
df = pl.read_parquet('pamm_updates_391876700_391976700.parquet')

# 2. Schema inspection first
print(df.schema)
print(f"Rows: {len(df):,}")

# 3. Sample exploration
print(df.head())
print(df.describe())

# 4. Domain-specific analysis (AMM metrics)
# - Pool state changes
# - Liquidity events
# - Price impacts
# - Volume analysis
```

### Output Format
- Print summary statistics to console with clear labels
- Save processed results as CSV or new Parquet files
- Include timestamp-based filenames for outputs (e.g., `analysis_20260108.csv`)
- Document assumptions about the data structure in code comments

## Key Considerations
- **Memory**: Parquet files can be large; prefer lazy loading or chunked processing
- **Blockchain Data**: Block numbers are sequential identifiers; timestamps may be irregular
- **AMM Specifics**: Updates likely include price, liquidity, volume, or swap event data
- **No existing codebase**: This is a greenfield analysis project - establish clear patterns from the start

## File Organization
Keep analysis organized as the project grows:
- `scripts/` - Python analysis scripts
- `outputs/` - Generated CSV/Parquet files
- `notebooks/` - Jupyter notebooks for exploratory analysis (if created)
- Update README.md with findings and script usage instructions

## Dependencies
Ensure these are installed before running analysis:
```bash
pip install polars pandas pyarrow  # Core data libraries
pip install matplotlib seaborn      # For visualization
```

## Testing Data Scripts
- Validate on small samples first: `df.head(1000)` before full dataset processing
- Check for null/missing values in critical columns
- Verify block number ranges match expected dataset bounds
