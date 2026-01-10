"""
Validator Client Type Comparison Analysis

Compares Jito-solana vs Harmonic validators on:
1. Transaction volume per validator (normalized)
2. Block production efficiency (events per slot)

Outputs a 4-panel interactive Plotly dashboard.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime


def parse_client_mapping():
    """
    Parse top_by_client_20260109.txt to create validator-to-client mapping.

    Returns:
        tuple: (validator_mapping dict, validator_counts dict)
    """
    validator_mapping = {}
    validator_counts = {'Jito-solana': 0, 'Harmonic': 0}

    print("Parsing validator client mapping from top_by_client_20260109.txt...")

    with open('top_by_client_20260109.txt', 'r') as f:
        lines = f.readlines()

    # Extract Jito-solana validators (lines 4-23, accounting for 0-indexing: lines[3:23])
    for i in range(3, 23):  # Lines 4-23 (20 validators)
        line = lines[i].strip()
        if line:
            # Parse line format: "1     22rU5yUmdVThrkoPieVNphqEyAtMQKmZxjwcD8v4bJDU          -          -"
            parts = line.split()
            if len(parts) >= 2:
                validator_id = parts[1]  # Second column is validator ID
                validator_mapping[validator_id] = 'Jito-solana'
                validator_counts['Jito-solana'] += 1

    # Extract Harmonic validators (lines 28-37, accounting for 0-indexing: lines[27:37])
    for i in range(27, 37):  # Lines 28-37 (10 validators)
        line = lines[i].strip()
        if line:
            parts = line.split()
            if len(parts) >= 2:
                validator_id = parts[1]
                validator_mapping[validator_id] = 'Harmonic'
                validator_counts['Harmonic'] += 1

    print(f"  Loaded {validator_counts['Jito-solana']} Jito-solana validators")
    print(f"  Loaded {validator_counts['Harmonic']} Harmonic validators")
    print(f"  Total: {len(validator_mapping)} validators\n")

    return validator_mapping, validator_counts


def load_and_enrich_data(validator_mapping):
    """
    Load parquet dataset and enrich with client_type column.
    Filters to only include the 30 mapped validators.

    Args:
        validator_mapping: dict mapping validator ID to client type

    Returns:
        pandas.DataFrame: Enriched dataset
    """
    print("Loading parquet dataset...")
    df = pd.read_parquet('pamm_updates_391876700_391976700.parquet')
    print(f"  Loaded {len(df):,} total events\n")

    print("Filtering to mapped validators only...")
    df_filtered = df[df['validator'].isin(validator_mapping.keys())].copy()
    print(f"  Filtered to {len(df_filtered):,} events ({len(df_filtered)/len(df)*100:.1f}% of dataset)\n")

    print("Enriching data with client_type and time features...")
    df_filtered['client_type'] = df_filtered['validator'].map(validator_mapping)
    df_filtered['datetime'] = pd.to_datetime(df_filtered['time'], unit='s')
    df_filtered['time_bin_5min'] = df_filtered['datetime'].dt.floor('5min')

    # Verify only 2 client types
    unique_clients = df_filtered['client_type'].unique()
    print(f"  Client types present: {list(unique_clients)}")
    assert len(unique_clients) == 2, f"Expected 2 client types, found {len(unique_clients)}"

    print(f"  Time range: {df_filtered['datetime'].min()} to {df_filtered['datetime'].max()}")
    print(f"  Duration: {(df_filtered['datetime'].max() - df_filtered['datetime'].min()).total_seconds() / 3600:.1f} hours\n")

    return df_filtered


def calculate_metrics(df, validator_counts):
    """
    Compute all comparison metrics with normalization.

    Args:
        df: Enriched DataFrame
        validator_counts: dict with validator counts per client type

    Returns:
        dict: All calculated metrics
    """
    print("Calculating metrics...")
    metrics = {}

    # Volume metrics (with normalization)
    client_volume = df.groupby('client_type').size()
    metrics['client_volume'] = client_volume

    # Average events per validator (NORMALIZED)
    avg_events_per_validator = client_volume / client_volume.index.map(validator_counts)
    metrics['avg_events_per_validator'] = avg_events_per_validator

    # Unique slots processed per client type
    slot_counts = df.groupby('client_type')['slot'].nunique()
    metrics['slot_counts'] = slot_counts

    # Average slots per validator (NORMALIZED)
    avg_slots_per_validator = slot_counts / slot_counts.index.map(validator_counts)
    metrics['avg_slots_per_validator'] = avg_slots_per_validator

    # Market share percentages
    volume_pct = (client_volume / client_volume.sum()) * 100
    metrics['volume_pct'] = volume_pct

    # Efficiency metrics
    events_per_slot = df.groupby(['client_type', 'slot']).size()
    efficiency_stats = events_per_slot.groupby('client_type').agg(['mean', 'median', 'std'])
    metrics['efficiency_stats'] = efficiency_stats

    # Distribution for box plots
    efficiency_distribution = events_per_slot.reset_index(name='events')
    metrics['efficiency_distribution'] = efficiency_distribution

    # Time series (5-minute bins)
    time_series = df.groupby(['time_bin_5min', 'client_type']).size().unstack(fill_value=0)
    metrics['time_series'] = time_series

    # Event type breakdown
    event_breakdown = df.groupby(['client_type', 'kind']).size().unstack(fill_value=0)
    metrics['event_breakdown'] = event_breakdown

    # Store validator counts for later use
    metrics['validator_counts'] = validator_counts

    print("  ✓ Volume metrics calculated")
    print("  ✓ Efficiency metrics calculated")
    print("  ✓ Time series generated")
    print("  ✓ Event breakdown computed\n")

    return metrics


def create_visualization(metrics):
    """
    Generate 4-panel Plotly dashboard comparing Jito-solana vs Harmonic.

    Args:
        metrics: dict of calculated metrics
    """
    print("Creating 4-panel visualization dashboard...")

    # Color scheme
    colors = {
        'Jito-solana': '#457B9D',  # Blue
        'Harmonic': '#52B788'       # Green
    }

    # Create subplot layout
    fig = make_subplots(
        rows=3, cols=2,
        specs=[
            [{"type": "scatter", "colspan": 2}, None],
            [{"type": "bar"}, {"type": "box"}],
            [{"type": "bar", "colspan": 2}, None]
        ],
        subplot_titles=(
            "Transaction Volume Over Time (Jito vs Harmonic)",
            "Normalized Per-Validator Metrics",
            "Block Efficiency Distribution",
            "Event Type Specialization"
        ),
        row_heights=[0.35, 0.35, 0.3],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    # Panel 1: Time Series Stacked Area Chart
    time_series = metrics['time_series']
    for client_type in ['Harmonic', 'Jito-solana']:  # Harmonic first so Jito is on top
        if client_type in time_series.columns:
            fig.add_trace(
                go.Scatter(
                    x=time_series.index,
                    y=time_series[client_type],
                    name=client_type,
                    mode='lines',
                    stackgroup='one',
                    fillcolor=colors[client_type],
                    line=dict(width=0.5, color=colors[client_type]),
                    hovertemplate='<b>%{fullData.name}</b><br>Time: %{x}<br>Events: %{y:,}<extra></extra>'
                ),
                row=1, col=1
            )

    # Panel 2: Grouped Bar Chart - Normalized Multi-Metric
    client_types = ['Jito-solana', 'Harmonic']

    # Prepare data for grouped bars
    avg_events = metrics['avg_events_per_validator'].reindex(client_types)
    mean_efficiency = metrics['efficiency_stats']['mean'].reindex(client_types)
    avg_slots = metrics['avg_slots_per_validator'].reindex(client_types)

    x_pos = [0, 1]  # Positions for Jito and Harmonic

    # Add three sets of bars
    fig.add_trace(
        go.Bar(
            x=client_types,
            y=avg_events,
            name='Avg Events/Validator',
            marker_color='#1D3557',
            hovertemplate='<b>%{x}</b><br>Avg Events per Validator: %{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )

    # Panel 3: Box Plot - Efficiency Distribution
    for client_type in client_types:
        client_data = metrics['efficiency_distribution'][
            metrics['efficiency_distribution']['client_type'] == client_type
        ]
        fig.add_trace(
            go.Box(
                y=client_data['events'],
                name=client_type,
                marker_color=colors[client_type],
                hovertemplate='<b>%{fullData.name}</b><br>Events/Slot: %{y}<extra></extra>'
            ),
            row=2, col=2
        )

    # Panel 4: Stacked Bar - Event Type Breakdown
    event_breakdown = metrics['event_breakdown']

    for event_type in ['ORACLE', 'TRADE']:
        if event_type in event_breakdown.columns:
            fig.add_trace(
                go.Bar(
                    x=client_types,
                    y=[event_breakdown.loc[ct, event_type] if ct in event_breakdown.index else 0
                       for ct in client_types],
                    name=event_type,
                    hovertemplate='<b>%{fullData.name}</b><br>%{x}: %{y:,} events<extra></extra>'
                ),
                row=3, col=1
            )

    # Update layout
    fig.update_xaxes(title_text="Time (5-min bins)", row=1, col=1)
    fig.update_yaxes(title_text="Number of Events", row=1, col=1)

    fig.update_xaxes(title_text="Client Type", row=2, col=1)
    fig.update_yaxes(title_text="Avg Events per Validator", row=2, col=1)

    fig.update_xaxes(title_text="Client Type", row=2, col=2)
    fig.update_yaxes(title_text="Events per Slot", row=2, col=2)

    fig.update_xaxes(title_text="Client Type", row=3, col=1)
    fig.update_yaxes(title_text="Number of Events", row=3, col=1)

    # Overall layout
    fig.update_layout(
        height=1200,
        showlegend=True,
        title_text="<b>Validator Client Type Comparison: Jito-solana vs Harmonic</b>",
        title_font_size=20,
        barmode='stack',
        hovermode='closest'
    )

    # Save to HTML
    output_path = 'outputs/validator_client_analysis_20260110.html'
    fig.write_html(output_path)
    print(f"  ✓ Dashboard saved to: {output_path}\n")

    return output_path


def print_summary(metrics):
    """
    Print summary statistics to console.

    Args:
        metrics: dict of calculated metrics
    """
    client_volume = metrics['client_volume']
    avg_events_per_validator = metrics['avg_events_per_validator']
    slot_counts = metrics['slot_counts']
    avg_slots_per_validator = metrics['avg_slots_per_validator']
    efficiency_stats = metrics['efficiency_stats']
    volume_pct = metrics['volume_pct']
    validator_counts = metrics['validator_counts']

    print("=" * 130)
    print("=== Validator Client Analysis Summary (Jito-solana vs Harmonic) ===")
    print("=" * 130)
    print()

    # Table header
    print(f"{'Client Type':<15} | {'Validators':>10} | {'Total Events':>13} | {'Avg Events/Val':>15} | "
          f"{'Unique Slots':>12} | {'Avg Slots/Val':>14} | {'Mean Events/Slot':>17} | {'Market Share %':>14}")
    print("-" * 130)

    # Table rows
    for client_type in ['Jito-solana', 'Harmonic']:
        print(f"{client_type:<15} | {validator_counts[client_type]:>10} | "
              f"{client_volume[client_type]:>13,} | {avg_events_per_validator[client_type]:>15,.0f} | "
              f"{slot_counts[client_type]:>12,} | {avg_slots_per_validator[client_type]:>14,.1f} | "
              f"{efficiency_stats.loc[client_type, 'mean']:>17,.2f} | {volume_pct[client_type]:>13.1f}%")

    print()
    print("=" * 130)
    print("=== Key Comparisons (Jito-solana / Harmonic Ratios) ===")
    print("=" * 130)

    # Calculate ratios
    jito_events = avg_events_per_validator['Jito-solana']
    harmonic_events = avg_events_per_validator['Harmonic']
    events_ratio = jito_events / harmonic_events if harmonic_events > 0 else 0

    jito_efficiency = efficiency_stats.loc['Jito-solana', 'mean']
    harmonic_efficiency = efficiency_stats.loc['Harmonic', 'mean']
    efficiency_ratio = jito_efficiency / harmonic_efficiency if harmonic_efficiency > 0 else 0

    print(f"Avg Events per Validator:  {events_ratio:.2f}x   (Jito: {jito_events:,.0f}, Harmonic: {harmonic_events:,.0f})")
    print(f"Avg Events per Slot:       {efficiency_ratio:.2f}x   (Jito: {jito_efficiency:.2f}, Harmonic: {harmonic_efficiency:.2f})")
    print("=" * 130)
    print()


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("  VALIDATOR CLIENT TYPE COMPARISON ANALYSIS")
    print("  Jito-solana vs Harmonic")
    print("=" * 80 + "\n")

    # Step 1: Parse mapping
    mapping, validator_counts = parse_client_mapping()

    # Step 2: Load and enrich data
    df = load_and_enrich_data(mapping)

    # Step 3: Calculate metrics
    metrics = calculate_metrics(df, validator_counts)

    # Step 4: Create visualization
    output_path = create_visualization(metrics)

    # Step 5: Print summary
    print_summary(metrics)

    print(f"\n{'='*80}")
    print(f"Analysis complete! Dashboard saved to: {output_path}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
