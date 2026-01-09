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

### Sample Data

Here are 10 representative rows from the dataset (5 ORACLE events, 5 TRADE events) with all columns:

| slot      | time       | validator                                    | tx_idx | sig                                                                                      | signer                                       | kind   | amm      | account_updates                                                                                                             | trades                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | us_since_first_shred |
| --------- | ---------- | -------------------------------------------- | ------ | ---------------------------------------------------------------------------------------- | -------------------------------------------- | ------ | -------- | --------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| 391879167 | 1767775317 | Awes4Tr6TX8JDzEhCZY2QVNimT6iD1zWHzf1vNyGvpLM | 1.0    | 4d1n2B6ATjFMbMXEbzQzpwpinFtuVCkYdKVE2E7GdfbjvfnLSZGp88WL83t3kYqMciQ5RsHQjny3reiNefGtV8hL | 9FmY4D6g7oeKqv15ETZGYNJzaCcWQDHbpWTdRGhXLEbm | TRADE  | None     | [{'amm_name': 'SolFiV2', 'account': '65ZHSArs5XxPseKQbB1B4r16vDxMWnCxHMzogDAqiDUc', 'is_pool': True, 'bytes_changed': 7}]   | [{'amm': 'SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF', 'pool': '65ZHSArs5XxPseKQbB1B4r16vDxMWnCxHMzogDAqiDUc', 'from_token': 'So11111111111111111111111111111111111111112', 'to_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'}]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 0.0                  |
| 391891609 | 1767780240 | EBoKqyT2kCabcHXgpF7ScwrHgGUsR821xkTJsHtP2JJi | 19.0   | 5BVrmjpyYS8LwkcAmkDakjLuqVhdrx8pejcD92C4QrLksG47avhUbCPKWG2gNSAt24Kb7jDPYceDzsc3XAKXUBPK | HhDzqB6RfK6ZdE6nQEQxRzd3BEDVVC1eiZA2UY1mkAsE | ORACLE | HumidiFi | [{'amm_name': 'HumidiFi', 'account': '8WFduUYU7iX94E3ZMejpTXi5TadKh9j5qp5ez5uSBJwa', 'is_pool': True, 'bytes_changed': 11}] | None                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 0.0                  |
| 391907812 | 1767786681 | DtdSSG8ZJRZVv5Jx7K1MeWp7Zxcu19GD5wQRGRpQ9uMF | 776.0  | 5cB9iMuKnHjMH9XYBKuMQ6RDxMaU3o3GxSbgjFW9jPqYpySMPfNNQebRNhT5UJ2Msdbymei6hP4fGBQNWJ1iRQD9 | AEB9dXBoxkrapNd59Kg29JefMMf3M1WLcNA12XjKSf4R | TRADE  | None     | [{'amm_name': 'TesseraV', 'account': 'FLckHLGMJy5gEoXWwcE68Nprde1D4araK4TGLw4pQq2n', 'is_pool': True, 'bytes_changed': 5}]  | [{'amm': 'TessVdML9pBGgG9yGks7o4HewRaXVAMuoVj4x83GLQH', 'pool': 'FLckHLGMJy5gEoXWwcE68Nprde1D4araK4TGLw4pQq2n', 'from_token': 'So11111111111111111111111111111111111111112', 'to_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'}]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 201875.0             |
| 391920538 | 1767791741 | HEL1USMZKAL2odpNBj2oCjffnFGaYwmbGmyewGv1e2TU | 125.0  | 4EYarmoWE1HrRHnCykEzQ1hzSJ4pkPjkrreNPWiAue3gZ676jsUvPwMBTvP1McTrRpWfGuqwypDxKS9ZZxxiZGhd | DNeVNvNMdP29KGWqdv3umqFAH9QVg5aw1RLNaKNy1Gow | TRADE  | None     | [{'amm_name': 'HumidiFi', 'account': 'FAYL7CoNENA6jGCWVJb5MZ7mjKuiiyYRkDTopdVticpp', 'is_pool': True, 'bytes_changed': 8}]  | [{'amm': '9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp', 'pool': 'FAYL7CoNENA6jGCWVJb5MZ7mjKuiiyYRkDTopdVticpp', 'from_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'to_token': '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump'} {'amm': 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc', 'pool': 'C9U2Ksk6KKWvLEeo5yUQ7Xu46X7NzeBJtd9PBfuXaUSM', 'from_token': '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump', 'to_token': 'So11111111111111111111111111111111111111112'} {'amm': 'HpNfyc2Saw7RKkQd8nEL4khUcuPhQ7WwY1B2qjx8jxFq', 'pool': 'DJNtGuBGEQiUCWE8F981M2C3ZghZt2XLD8f2sQdZ6rsZ', 'from_token': 'So11111111111111111111111111111111111111112', 'to_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'}]                                                                                                                                                                                                                                         | 79571.0              |
| 391923325 | 1767792842 | 2GUnfxZavKoPfS9s3VSEjaWDzB3vNf5RojUhprCS1rSx | 65.0   | 2Y6GxEjH6ciMYW2pBWTDoHNZE3Q54ugCfBNy73nZLsv6g6yPnS9DzV1kND58QvynxmMjkzeaC7EELkfLGKJpsrkE | 2xQ9Q25GsZG6Kd6iWpnrpRWNYmfqBwNPiuZ5J9HhTJut | TRADE  | None     | [{'amm_name': 'TesseraV', 'account': 'FLckHLGMJy5gEoXWwcE68Nprde1D4araK4TGLw4pQq2n', 'is_pool': True, 'bytes_changed': 3}]  | [{'amm': 'TessVdML9pBGgG9yGks7o4HewRaXVAMuoVj4x83GLQH', 'pool': 'FLckHLGMJy5gEoXWwcE68Nprde1D4araK4TGLw4pQq2n', 'from_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'to_token': 'So11111111111111111111111111111111111111112'}]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 40927.0              |
| 391926819 | 1767794230 | DNVZMSqeRH18Xa4MCTrb1MndNf3Npg4MEwqswo23eWkf | 645.0  | 5PD5vTBvy1qNkDheNCSNqmUGzqAgbAx5WJJAJANyouB6ueZjvPNGaymxWJwRyatsePQQBgKByxLrifoPYCKHoCNJ | GqXWUYiftFJddgSsEYx9vgsFeLe1ZqWb5vQZ2LKsmM5X | ORACLE | HumidiFi | [{'amm_name': 'HumidiFi', 'account': 'GAcKqojqgkRVDBihVAGvbqnuZdCiN9UGNrPCRG5DMGGA', 'is_pool': True, 'bytes_changed': 11}] | None                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 58126.0              |
| 391944934 | 1767801433 | BtsmiEEvnSuUnKxqXj2PZRYpPJAc7C34mGz8gtJ1DAaH | 717.0  | jd6J429o6BCTWvTKmCgUu4q7VQDyHj7ChH7UvcwheWx1wUCEmFqfxPJc67htnvbSQKvrShkKJxnDjC1jz3pTqbU  | updtkJ8HAhh3rSkBCd3p9Z1Q74yJW4rMhSbScRskDPM  | ORACLE | ZeroFi   | [{'amm_name': 'ZeroFi', 'account': '2h9hhu3gxY9kCdXEwdTHV8yPAMYVoHgKopRyG1HbDwfi', 'is_pool': True, 'bytes_changed': 5}]    | None                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 132864.0             |
| 391946174 | 1767801927 | G2TBEh2ahNGS9tGnuBNyDduNjyfUtGhMcssgRb8b6KfH | 1342.0 | 2T1gSMi5zjhqKcqaDgaaBQmLSpuYzgn9uN1hKgpeXLn7KNufcMpyNEq5bVjPLtmDqvta5EN5VcyCbgvZG8aZhsDg | DozaBETGtXLGAwHQy9Vj63LDWc3ewg8be2e4UvPvCn7n | TRADE  | None     | [{'amm_name': 'HumidiFi', 'account': '2866MvCKPGz9LdnPcmPueoV3mA2Ac1ceEQ8Xqb9VNefu', 'is_pool': True, 'bytes_changed': 44}] | [{'amm': 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc', 'pool': 'AhhoxZDmsg2snm85vPjqzYzEYESoKfb4KmTj4HrBBNwY', 'from_token': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'to_token': 'So11111111111111111111111111111111111111112'} {'amm': 'ALPHAQmeA7bjrVuccPsYPiCvsi428SNwte66Srvs4pHA', 'pool': 'Pi9nzTjPxD8DsRfRBGfKYzmefJoJM8TcXu2jyaQjSHm', 'from_token': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'to_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'} {'amm': 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc', 'pool': '8GsWExrRFeBj1Nh8gCuVQZo3f6yzd1YFofGbwebh7uFh', 'from_token': 'So11111111111111111111111111111111111111112', 'to_token': '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv'} {'amm': '9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp', 'pool': '2866MvCKPGz9LdnPcmPueoV3mA2Ac1ceEQ8Xqb9VNefu', 'from_token': '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv', 'to_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'}] | 279417.0             |
| 391953146 | 1767804702 | HEL1USMZKAL2odpNBj2oCjffnFGaYwmbGmyewGv1e2TU | 558.0  | 2tg2DbnbUuW5tUF1xip2Vjev5MiXhKWj2vxnCCftLAWQGS7wJPSEJViqmvSGkn6wzkFAHrXPN41b12qJ2hwadsA8 | updtkJ8HAhh3rSkBCd3p9Z1Q74yJW4rMhSbScRskDPM  | ORACLE | ZeroFi   | [{'amm_name': 'ZeroFi', 'account': '2h9hhu3gxY9kCdXEwdTHV8yPAMYVoHgKopRyG1HbDwfi', 'is_pool': True, 'bytes_changed': 7}]    | None                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 54998.0              |
| 391970901 | 1767811767 | Fudp7uPDYNYQRxoq1Q4JiwJnzyxhVz37bGqRki3PBzS  | 81.0   | 2yj8vyxgUDxUXPYWkBLLKjteYpdjHewaopdnZ3JfAomrjzcTSxRBWSivNt1fgYZcV8bMcB5RQhWgbTB9PrLoAwv1 | GUguMjDcAP6dv95z6cqG3cTmmPXJpYCGxDrPWv73tizL | ORACLE | HumidiFi | [{'amm_name': 'HumidiFi', 'account': 'hKgG7iEDRFNsJSwLYqz8ETHuZwzh6qMMLow8VXa8pLm', 'is_pool': True, 'bytes_changed': 10}]  | None                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 51522.0              |

_Note: Complex nested columns `account_updates` and `trades` are shown in their full representation._

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
