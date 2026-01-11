"""
Validator Client Performance Analysis - Block Packing Efficiency

Compares Jito-solana vs Harmonic validators using PROPERLY NORMALIZED metrics.

Key Metric: Events per Slot (block packing efficiency)
- Independent of stake distribution
- Independent of slot assignment
- Measures actual performance when validators produce blocks

Note: Metrics like "total events" or "events per validator" are misleading
because they conflate performance with stake-weighted slot assignment.

Outputs a 4-panel interactive Plotly dashboard focused on normalized performance.
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

    # Extract Harmonic validators (lines 28-42, accounting for 0-indexing: lines[27:42])
    for i in range(27, 42):  # Lines 28-42 (15 validators)
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
    Filters to only include the 35 mapped validators.

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
    Compute properly normalized performance metrics.

    Focus: Metrics that measure actual performance (events per slot),
    not stake-dependent metrics (total events, slots per validator).

    Args:
        df: Enriched DataFrame
        validator_counts: dict with validator counts per client type

    Returns:
        dict: All calculated metrics
    """
    print("Calculating properly normalized metrics...")
    metrics = {}

    # PRIMARY METRIC: Events per slot (performance when producing blocks)
    events_per_slot = df.groupby(['client_type', 'slot']).size()
    efficiency_stats = events_per_slot.groupby('client_type').agg(['mean', 'median', 'std', 'count'])

    # Add coefficient of variation (std/mean) - measures consistency
    efficiency_stats['cv'] = efficiency_stats['std'] / efficiency_stats['mean']
    metrics['efficiency_stats'] = efficiency_stats

    # Distribution for box plots
    efficiency_distribution = events_per_slot.reset_index(name='events')
    metrics['efficiency_distribution'] = efficiency_distribution

    # Scatter plot data (raw events per slot by slot number)
    scatter_data = events_per_slot.reset_index()
    scatter_data.columns = ['client_type', 'slot', 'events']
    metrics['scatter_data'] = scatter_data

    # Events per slot over time (5-minute bins) - normalized time series
    time_efficiency = df.groupby(['time_bin_5min', 'client_type', 'slot']).size()
    time_efficiency_avg = time_efficiency.groupby(['time_bin_5min', 'client_type']).mean().unstack()
    metrics['time_efficiency'] = time_efficiency_avg

    # Events per slot by event type (ORACLE vs TRADE efficiency)
    events_per_slot_by_type = df.groupby(['client_type', 'slot', 'kind']).size()
    efficiency_by_type = events_per_slot_by_type.groupby(['client_type', 'kind']).mean().unstack(fill_value=0)
    metrics['efficiency_by_type'] = efficiency_by_type

    # Event type proportions (for context)
    event_breakdown = df.groupby(['client_type', 'kind']).size().unstack(fill_value=0)
    event_breakdown_pct = event_breakdown.div(event_breakdown.sum(axis=1), axis=0) * 100
    metrics['event_breakdown_pct'] = event_breakdown_pct

    # Store validator counts and total blocks for context
    metrics['validator_counts'] = validator_counts
    metrics['total_blocks'] = df.groupby('client_type')['slot'].nunique()
    metrics['total_events'] = df.groupby('client_type').size()

    # SPIKE WINDOW ANALYSIS: Prepare data for Panel 4
    # Define spike window constants
    SPIKE_START = pd.Timestamp('2026-01-07 16:20:00')
    SPIKE_END = pd.Timestamp('2026-01-07 16:24:59')
    SPIKE_CONTEXT_START = pd.Timestamp('2026-01-07 16:00:00')
    SPIKE_CONTEXT_END = pd.Timestamp('2026-01-07 16:40:00')
    PEAK_SLOTS = [391948792, 391948795]

    # Filter to context window (40 minutes around spike)
    df_context = df[
        (df['datetime'] >= SPIKE_CONTEXT_START) &
        (df['datetime'] < SPIKE_CONTEXT_END)
    ].copy()

    # Calculate events per slot in context window
    context_scatter = df_context.groupby(['client_type', 'slot']).size().reset_index()
    context_scatter.columns = ['client_type', 'slot', 'events']

    # Mark which slots are in spike window
    df_context['in_spike_window'] = (
        (df_context['datetime'] >= SPIKE_START) &
        (df_context['datetime'] < SPIKE_END)
    )

    # Calculate spike window metrics
    spike_window_metrics = {}
    for client_type in ['Jito-solana', 'Harmonic']:
        df_client_spike = df_context[
            (df_context['client_type'] == client_type) &
            (df_context['in_spike_window'] == True)
        ]

        if len(df_client_spike) > 0:
            events_by_slot = df_client_spike.groupby('slot').size()
            spike_window_metrics[client_type] = {
                'avg': events_by_slot.mean(),
                'total_events': len(df_client_spike),
                'blocks': df_client_spike['slot'].nunique()
            }

    # Store in metrics dict
    metrics['spike_context_scatter'] = context_scatter
    metrics['spike_window_metrics'] = spike_window_metrics
    metrics['spike_peak_slots'] = PEAK_SLOTS

    print("  ✓ Block packing efficiency calculated (events per slot)")
    print("  ✓ Performance consistency metrics computed")
    print("  ✓ Time-based efficiency patterns analyzed")
    print("  ✓ Event type efficiency breakdown completed")
    print("  ✓ Spike window analysis data prepared\n")

    return metrics


def create_visualization(metrics):
    """
    Generate 4-panel Plotly dashboard with properly normalized metrics.

    All panels focus on events per slot (block packing efficiency),
    which is the only meaningful performance comparison.

    Args:
        metrics: dict of calculated metrics
    """
    print("Creating 4-panel visualization dashboard...")

    # Color scheme
    colors = {
        'Jito-solana': "#009DFF",  # Blue
        'Harmonic': "#227B52"       # Green
    }

    # Create subplot layout
    fig = make_subplots(
        rows=4, cols=1,
        specs=[
            [{"type": "scatter"}],
            [{"type": "box"}],
            [{"type": "scatter"}],
            [{"type": "scatter"}]  # New spike analysis panel
        ],
        subplot_titles=(
            "Raw Data: Block Packing Efficiency by Slot (All Data Points)",
            "Statistical Comparison: Events per Slot with Key Percentiles",
            "Time Series: Average Events per Slot (5-minute bins)",
            "Spike Analysis: 16:20-16:24 Window (Harmonic 169.25 vs Jito 65.69 avg)"
        ),
        row_heights=[0.25, 0.20, 0.25, 0.30],  # Give more space to spike panel
        vertical_spacing=0.10
    )

    # Panel 1: Raw events per slot scatter plot
    scatter_data = metrics['scatter_data']
    for client_type in ['Jito-solana', 'Harmonic']:
        client_data = scatter_data[scatter_data['client_type'] == client_type]
        fig.add_trace(
            go.Scatter(
                x=client_data['slot'],
                y=client_data['events'],
                name=client_type,
                mode='markers',
                marker=dict(
                    size=4,
                    color=colors[client_type],
                    opacity=0.6
                ),
                hovertemplate='<b>%{fullData.name}</b><br>Slot: %{x}<br>Events: %{y}<extra></extra>'
            ),
            row=1, col=1
        )

    # Panel 2: Box plot with percentile annotations
    for client_type in ['Jito-solana', 'Harmonic']:
        client_data = scatter_data[scatter_data['client_type'] == client_type]

        fig.add_trace(
            go.Box(
                y=client_data['events'],
                name=client_type,
                marker_color=colors[client_type],
                boxmean='sd',  # Show mean line and standard deviation
                boxpoints='outliers',  # Show outlier points
                hovertemplate='<b>%{fullData.name}</b><br>Value: %{y}<extra></extra>'
            ),
            row=2, col=1
        )

    # Calculate and add text annotations with percentiles
    annotations = []
    for i, client_type in enumerate(['Jito-solana', 'Harmonic']):
        client_data = scatter_data[scatter_data['client_type'] == client_type]['events']

        # Calculate all key percentiles
        p25 = client_data.quantile(0.25)
        p50 = client_data.median()
        p75 = client_data.quantile(0.75)
        p95 = client_data.quantile(0.95)
        p99 = client_data.quantile(0.99)
        mean_val = client_data.mean()

        # Create annotation text
        annotation_text = (
            f"<b>{client_type}</b><br>"
            f"p99: {p99:.1f}<br>"
            f"p95: {p95:.1f}<br>"
            f"p75: {p75:.1f}<br>"
            f"p50: {p50:.1f}<br>"
            f"p25: {p25:.1f}<br>"
            f"mean: {mean_val:.1f}"
        )

        # Position annotation to the right of each box
        annotations.append(
            dict(
                x=i,  # 0 for Jito-solana, 1 for Harmonic
                y=p99 + 10,  # Position above the p99 value
                xref='x2',  # Reference to Panel 2's x-axis
                yref='y2',  # Reference to Panel 2's y-axis
                text=annotation_text,
                showarrow=False,
                font=dict(size=10, family='monospace'),
                align='left',
                xanchor='left',
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor=colors[client_type],
                borderwidth=2,
                borderpad=6
            )
        )

    # Add annotations to figure layout
    current_annotations = list(fig.layout.annotations) if fig.layout.annotations else []
    current_annotations.extend(annotations)
    fig.update_layout(annotations=current_annotations)

    # Panel 3: Time series with 5-minute bins (shows spike clearly)
    time_efficiency = metrics['time_efficiency']
    for client_type in ['Jito-solana', 'Harmonic']:
        if client_type in time_efficiency.columns:
            fig.add_trace(
                go.Scatter(
                    x=time_efficiency.index,
                    y=time_efficiency[client_type],
                    name=client_type,
                    mode='lines',
                    line=dict(width=2, color=colors[client_type]),
                    connectgaps=False,  # Show gaps where data is missing (NaN)
                    hovertemplate='<b>%{fullData.name}</b><br>Time: %{x}<br>Avg Events/Slot: %{y:.2f}<extra></extra>'
                ),
                row=3, col=1
            )

    # Panel 4: Spike window analysis with highlighted peaks
    context_scatter = metrics['spike_context_scatter']
    spike_metrics = metrics['spike_window_metrics']
    peak_slots = metrics['spike_peak_slots']

    # Plot regular Jito-solana points
    jito_context = context_scatter[context_scatter['client_type'] == 'Jito-solana']
    fig.add_trace(
        go.Scatter(
            x=jito_context['slot'],
            y=jito_context['events'],
            name='Jito-solana',
            mode='markers',
            marker=dict(size=4, color=colors['Jito-solana']),
            hovertemplate='<b>Jito-solana</b><br>Slot: %{x}<br>Events: %{y}<extra></extra>',
            showlegend=False
        ),
        row=4, col=1
    )

    # Plot regular Harmonic points (non-peak)
    harmonic_context = context_scatter[context_scatter['client_type'] == 'Harmonic']
    harmonic_regular = harmonic_context[~harmonic_context['slot'].isin(peak_slots)]
    fig.add_trace(
        go.Scatter(
            x=harmonic_regular['slot'],
            y=harmonic_regular['events'],
            name='Harmonic',
            mode='markers',
            marker=dict(size=4, color=colors['Harmonic']),
            hovertemplate='<b>Harmonic</b><br>Slot: %{x}<br>Events: %{y}<extra></extra>',
            showlegend=False
        ),
        row=4, col=1
    )

    # Highlight peak slots with special markers
    harmonic_peaks = harmonic_context[harmonic_context['slot'].isin(peak_slots)]
    fig.add_trace(
        go.Scatter(
            x=harmonic_peaks['slot'],
            y=harmonic_peaks['events'],
            name='Peak Slots',
            mode='markers+text',
            marker=dict(
                size=4,
                color=colors['Harmonic'],
            ),
            text=[f"{int(row['events'])}" for _, row in harmonic_peaks.iterrows()],
            textposition='top center',
            textfont=dict(size=10, color='#8B0000', family='monospace'),
            hovertemplate='<b>PEAK SLOT</b><br>Slot: %{x}<br>Events: %{y}<extra></extra>'
        ),
        row=4, col=1
    )

    # Add horizontal baseline reference lines
    fig.add_hline(
        y=54.37, line_dash="dash", line_color=colors['Harmonic'],
        line_width=1.5, opacity=0.5,
        annotation_text="Harmonic baseline: 54.37",
        annotation_position="right",
        row=4, col=1
    )
    fig.add_hline(
        y=57.26, line_dash="dash", line_color=colors['Jito-solana'],
        line_width=1.5, opacity=0.5,
        annotation_text="Jito baseline: 57.26",
        annotation_position="right",
        row=4, col=1
    )

    # Add shaded region for spike window (16:20-16:24)
    # Note: Need to convert timestamps to slot numbers for shading
    spike_start_slot = 391948700  # Approximate slot at 16:20
    spike_end_slot = 391948800    # Approximate slot at 16:24

    fig.add_vrect(
        x0=spike_start_slot, x1=spike_end_slot,
        fillcolor="rgba(255, 0, 0, 0.1)",  # Light red shading
        layer="below", line_width=0,
        annotation_text="Spike Window",
        annotation_position="top left",
        row=4, col=1
    )

    # Add spike window statistics annotations
    spike_annotations = []

    # Harmonic spike annotation
    if 'Harmonic' in spike_metrics:
        harmonic_spike_text = (
            f"<b>Harmonic Spike</b><br>"
            f"Avg: {spike_metrics['Harmonic']['avg']:.1f}<br>"
            f"Blocks: {spike_metrics['Harmonic']['blocks']}<br>"
            f"vs baseline: +{(spike_metrics['Harmonic']['avg'] - 54.37) / 54.37 * 100:.0f}%"
        )

        spike_annotations.append(
            dict(
                x=0.25, y=0.95,
                xref='x4 domain', yref='y4 domain',  # Reference to Panel 4
                text=harmonic_spike_text,
                showarrow=False,
                font=dict(size=10, family='monospace'),
                align='left',
                bgcolor='rgba(34, 123, 82, 0.9)',  # Harmonic green
                bordercolor='#227B52',
                borderwidth=2,
                borderpad=6
            )
        )

    # Jito spike annotation
    if 'Jito-solana' in spike_metrics:
        jito_spike_text = (
            f"<b>Jito-solana Spike</b><br>"
            f"Avg: {spike_metrics['Jito-solana']['avg']:.1f}<br>"
            f"Blocks: {spike_metrics['Jito-solana']['blocks']}<br>"
            f"vs baseline: +{(spike_metrics['Jito-solana']['avg'] - 57.26) / 57.26 * 100:.0f}%"
        )

        spike_annotations.append(
            dict(
                x=0.75, y=0.95,
                xref='x4 domain', yref='y4 domain',
                text=jito_spike_text,
                showarrow=False,
                font=dict(size=10, family='monospace'),
                align='left',
                bgcolor='rgba(0, 157, 255, 0.9)',  # Jito blue
                bordercolor='#009DFF',
                borderwidth=2,
                borderpad=6
            )
        )

    # Add to existing annotations
    current_annotations_with_spike = list(fig.layout.annotations) if fig.layout.annotations else []
    current_annotations_with_spike.extend(spike_annotations)
    fig.update_layout(annotations=current_annotations_with_spike)

    # Update layout
    # Panel 1 axes
    fig.update_xaxes(title_text="Slot Number", row=1, col=1)
    fig.update_yaxes(title_text="Events per Slot", row=1, col=1)

    # Panel 2 axes
    fig.update_xaxes(title_text="Client Type", row=2, col=1)
    fig.update_yaxes(title_text="Events per Slot", row=2, col=1)

    # Panel 3 axes
    fig.update_xaxes(
        title_text="Time (5-min bins)",
        tickformat="%H:%M<br>%b %d",  # Format: HH:MM with date on second line
        row=3, col=1
    )
    fig.update_yaxes(title_text="Avg Events per Slot", row=3, col=1)

    # Overall layout
    fig.update_layout(
        height=1400,  # Increased for 3 panels
        showlegend=True,
        title_text="<b>Validator Client Performance: Jito-solana vs Harmonic</b><br>" +
                   "<sub>Panel 1: Raw data | Panel 2: Statistical comparison | Panel 3: Time series (spike visible)</sub>",
        title_font_size=18,
        barmode='overlay',
        hovermode='closest'
    )

    # Save to HTML
    output_path = 'validator_client_analysis_20260110.html'
    fig.write_html(output_path)
    print(f"  ✓ Dashboard saved to: {output_path}\n")

    return output_path


def print_summary(metrics):
    """
    Print summary of properly normalized performance metrics.

    Focus: Block packing efficiency (events per slot) - the only meaningful
    performance comparison independent of stake distribution.

    Args:
        metrics: dict of calculated metrics
    """
    efficiency_stats = metrics['efficiency_stats']
    validator_counts = metrics['validator_counts']
    total_blocks = metrics['total_blocks']
    total_events = metrics['total_events']
    event_breakdown_pct = metrics['event_breakdown_pct']

    print("=" * 120)
    print("=== Validator Client Performance Analysis: Block Packing Efficiency ===")
    print("=" * 120)
    print()
    print("FOCUS: Events per Slot (properly normalized performance metric)")
    print("Note: This metric is independent of stake distribution and slot assignment")
    print()
    print("-" * 120)

    # Table header
    print(f"{'Client Type':<15} | {'Validators':>10} | {'Total Blocks':>12} | "
          f"{'Mean ±Std':>18} | {'Median':>10} | {'CV':>8} | {'Performance':>15}")
    print("-" * 120)

    # Table rows
    for client_type in ['Jito-solana', 'Harmonic']:
        mean_val = efficiency_stats.loc[client_type, 'mean']
        std_val = efficiency_stats.loc[client_type, 'std']
        median_val = efficiency_stats.loc[client_type, 'median']
        cv_val = efficiency_stats.loc[client_type, 'cv']

        print(f"{client_type:<15} | {validator_counts[client_type]:>10} | "
              f"{total_blocks[client_type]:>12,} | "
              f"{mean_val:>7.2f} ± {std_val:<7.2f} | {median_val:>10.2f} | "
              f"{cv_val:>8.3f} | {'events/slot':>15}")

    print()
    print("=" * 120)
    print("=== Performance Comparison ===")
    print("=" * 120)

    # Calculate ratios and differences
    jito_mean = efficiency_stats.loc['Jito-solana', 'mean']
    harmonic_mean = efficiency_stats.loc['Harmonic', 'mean']
    efficiency_ratio = jito_mean / harmonic_mean if harmonic_mean > 0 else 0
    efficiency_diff = jito_mean - harmonic_mean
    efficiency_diff_pct = (efficiency_diff / harmonic_mean * 100) if harmonic_mean > 0 else 0

    jito_cv = efficiency_stats.loc['Jito-solana', 'cv']
    harmonic_cv = efficiency_stats.loc['Harmonic', 'cv']

    print(f"Block Packing Efficiency (Mean Events/Slot):")
    print(f"  Jito-solana:  {jito_mean:.2f} events/slot")
    print(f"  Harmonic:     {harmonic_mean:.2f} events/slot")
    print(f"  Difference:   {efficiency_diff:+.2f} events/slot ({efficiency_diff_pct:+.1f}%)")
    print(f"  Ratio:        {efficiency_ratio:.2f}x")
    print()
    print(f"Consistency (Coefficient of Variation):")
    print(f"  Jito-solana:  {jito_cv:.3f} (lower = more consistent)")
    print(f"  Harmonic:     {harmonic_cv:.3f}")
    print()

    print("=" * 120)
    print("=== Interpretation ===")
    print("=" * 120)
    print()
    if abs(efficiency_diff_pct) < 10:
        print(f"✓ Both clients show SIMILAR block packing efficiency (difference < 10%)")
        print(f"  The {efficiency_diff_pct:.1f}% difference is relatively small.")
    elif jito_mean > harmonic_mean:
        print(f"✓ Jito-solana packs {efficiency_diff_pct:.1f}% more events per block")
    else:
        print(f"✓ Harmonic packs {-efficiency_diff_pct:.1f}% more events per block")
    print()
    print("IMPORTANT: Any difference in total transaction volume between client types")
    print("is primarily due to stake-weighted slot assignment, NOT performance differences.")
    print()
    print(f"Context: These 35 validators processed {total_events.sum():,} total events")
    print(f"         across {total_blocks.sum():,} unique blocks (~{total_blocks.sum() / 100:.1f}k blocks)")
    print("=" * 120)
    print()


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("  VALIDATOR CLIENT PERFORMANCE ANALYSIS")
    print("  Block Packing Efficiency: Jito-solana vs Harmonic")
    print("  (Properly Normalized Metrics)")
    print("=" * 80 + "\n")

    # Step 1: Parse mapping
    mapping, validator_counts = parse_client_mapping()

    # Step 2: Load and enrich data
    df = load_and_enrich_data(mapping)

    # Step 3: Calculate metrics
    metrics = calculate_metrics(df, validator_counts)

    # Step 4: Create visualization
    output_path = create_visualization(metrics)

    print(f"\n{'='*80}")
    print(f"Analysis complete! Dashboard saved to: {output_path}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
