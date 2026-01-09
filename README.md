# PropAMM Dataset Visualization Project

## 📊 Overview

Comprehensive data analysis and visualization toolkit for the propAMM (Automated Market Maker) dataset. This project provides tools to analyze 5.5+ million blockchain transactions across 8 AMM protocols.

**Dataset:** `pamm_updates_391876700_391976700.parquet`  
**Size:** 5,526,137 events | 3.2 GB in memory  
**Time Period:** ~11 hours of blockchain activity (December 2024)  
**Protocols:** HumidiFi, ZeroFi, TesseraV, SolFiV2, GoonFi, BisonFi, SolFi, AlphaQ

---

## 🚀 Quick Start

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Visualizations

```bash
# Create interactive dashboard
python create_dashboard.py
```

### 3. View Results

- **Interactive charts** (.html): Open in web browser

### 4. Deactivate Environment (when done)

```bash
deactivate
```

---

## 📁 Project Files

| File                                         | Description                                   |
| -------------------------------------------- | --------------------------------------------- |
| **create_dashboard.py**                      | 📊 Creates interactive multi-panel dashboards |
| **requirements.txt**                         | 📦 Python dependencies                        |
| **pamm_updates_391876700_391976700.parquet** | 💾 PropAMM dataset (5.5M events)              |

---

## 📊 Available Visualizations

### Interactive Dashboards (create_dashboard.py)

- **Main Dashboard** - Multi-panel comprehensive overview
- **Protocol-Specific** - Focused dashboards for individual AMM protocols

---

## 📈 Key Dataset Insights

### Event Types

- **ORACLE updates:** 4,840,049 (87.6%) - Price/state updates
- **TRADE events:** 686,088 (12.4%) - Actual swaps

### Protocol Activity (Top 5)

1. **HumidiFi:** 2,228,674 events (40.3%)
2. **ZeroFi:** 957,190 events (17.3%)
3. **TesseraV:** 526,112 events (9.5%)
4. **SolFiV2:** 406,125 events (7.3%)
5. **GoonFi:** 387,330 events (7.0%)

### Data Schema

- `slot` - Block number (uint64)
- `time` - Unix timestamp (uint32)
- `validator` - Node identifier (string)
- `tx_idx` - Transaction position in block (int64)
- `sig` - Transaction signature (string)
- `signer` - Wallet address (string)
- `kind` - Event type: ORACLE or TRADE (string)
- `amm` - Protocol name (string)
- `account_updates` - State changes (nested list)
- `trades` - Trade details (nested list)
- `us_since_first_shred` - Timing metric (int64)

---

## 🛠️ Technology Stack

### Core Libraries

- **pandas** - Data manipulation
- **pyarrow** - Parquet file handling
- **polars** - High-performance data processing

### Visualization Libraries

- **Plotly** - Interactive charts (HTML output)
- **Matplotlib** - Static publication-quality charts
- **Seaborn** - Statistical visualizations

### Why These Libraries?

- **Plotly:** Best for interactive exploration and sharing (zoom, filter, hover)
- **Matplotlib:** Industry standard for static charts in reports
- **Seaborn:** Beautiful statistical plots with minimal code

---

## 💡 Usage Examples

### Example 1: Run Main Dashboard

```python
python create_dashboard.py
```

This will generate interactive HTML dashboards that you can open in your browser.

### Example 2: Custom Analysis

You can modify `create_dashboard.py` to create custom visualizations based on your specific analysis needs.

---

## 🎯 Recommended Workflow

1. **Set up environment** - Create and activate virtual environment, install dependencies
2. **Create dashboard** - Run `python create_dashboard.py`
3. **Explore visualizations** - Open generated HTML files in your browser
4. **Customize** - Modify the dashboard code for your specific analysis needs

---

## 🐛 Troubleshooting

### Virtual Environment Issues

```bash
# If activation fails, ensure you created the venv first
python3 -m venv venv
source venv/bin/activate
```

### "ModuleNotFoundError"

```bash
# Make sure virtual environment is activated (you should see (venv) in prompt)
source venv/bin/activate
pip install -r requirements.txt
```

### Out of Memory

The dataset is large (5.5M events). If you encounter memory issues, consider processing subsets of the data by modifying the dashboard script.

---

## 📊 Output Files

After running `create_dashboard.py`, you'll have interactive HTML dashboards ready to open in your browser.

---

## 🔬 Advanced Features

The dashboard provides:

- **Time series analysis** of AMM protocol activity
- **Protocol comparison** visualizations
- **Event type analysis** (ORACLE vs TRADE events)
- **Interactive exploration** with zoom, pan, and hover details

---

## 📝 Next Steps

- [ ] Run the dashboard generator
- [ ] Explore generated visualizations
- [ ] Customize dashboards for specific research questions
- [ ] Analyze nested trade data for deeper insights

---

## 📖 Additional Resources

- [Plotly Python Documentation](https://plotly.com/python/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Pandas Visualization Guide](https://pandas.pydata.org/docs/user_guide/visualization.html)

---

**Last Updated:** January 9, 2026  
**Status:** ✅ Fully Functional  
**Test Status:** ✅ All libraries verified working
