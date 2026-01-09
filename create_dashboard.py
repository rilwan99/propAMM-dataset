"""
Advanced Interactive Dashboard for PropAMM Dataset
Creates a comprehensive multi-panel dashboard using Plotly

Author: AI Analysis System
Date: January 9, 2026
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

def create_interactive_dashboard(file_path='pamm_updates_391876700_391976700.parquet',
                                  output_file='dashboard_propamm.html'):
    """
    Create a comprehensive interactive dashboard with multiple panels
    
    Dashboard includes:
    1. Time series of AMM activity
    2. Event type breakdown
    3. Protocol market share
    4. Block throughput metrics
    """
    
    print("="*70)
    print("CREATING INTERACTIVE PROPAMM DASHBOARD")
    print("="*70)
    
    # Load data
    print("\n📂 Loading data...")
    df = pd.read_parquet(file_path)
    
    # Preprocess
    print("🔧 Preprocessing...")
    df['datetime'] = pd.to_datetime(df['time'], unit='s')
    df['time_bin_5min'] = df['datetime'].dt.floor('5min')
    df['amm_clean'] = df['amm'].fillna('Unknown')
    
    # Create subplots with custom layout
    print("📊 Creating dashboard layout...")
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'AMM Activity Timeline (5-min intervals)',
            'Protocol Market Share',
            'Event Type Distribution',
            'Transactions Per Block (Rolling Avg)',
            'Hourly Activity Heatmap',
            'Top 10 Most Active Validators'
        ),
        specs=[
            [{"type": "scatter", "colspan": 2}, None],
            [{"type": "pie"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "bar"}]
        ],
        row_heights=[0.35, 0.35, 0.3],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )
    
    # ========================================================================
    # PANEL 1: Time Series - AMM Activity
    # ========================================================================
    print("  Adding Panel 1: Time Series...")
    activity_ts = df.groupby(['time_bin_5min', 'amm_clean']).size().reset_index(name='count')
    
    for amm in activity_ts['amm_clean'].unique():
        amm_data = activity_ts[activity_ts['amm_clean'] == amm]
        fig.add_trace(
            go.Scatter(
                x=amm_data['time_bin_5min'],
                y=amm_data['count'],
                mode='lines',
                name=amm,
                stackgroup='one',
                hovertemplate='<b>%{fullData.name}</b><br>Time: %{x}<br>Events: %{y}<extra></extra>'
            ),
            row=1, col=1
        )
    
    # ========================================================================
    # PANEL 2: Pie Chart - Protocol Market Share
    # ========================================================================
    print("  Adding Panel 2: Market Share...")
    amm_counts = df[df['amm_clean'] != 'Unknown']['amm_clean'].value_counts()
    
    fig.add_trace(
        go.Pie(
            labels=amm_counts.index,
            values=amm_counts.values,
            hole=0.4,
            textinfo='label+percent',
            showlegend=False,
            hovertemplate='<b>%{label}</b><br>Events: %{value:,}<br>Share: %{percent}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # ========================================================================
    # PANEL 3: Bar Chart - Event Types
    # ========================================================================
    print("  Adding Panel 3: Event Types...")
    event_counts = df['kind'].value_counts()
    
    fig.add_trace(
        go.Bar(
            x=event_counts.index,
            y=event_counts.values,
            marker_color=['#457B9D', '#E63946'],
            text=event_counts.values,
            texttemplate='%{text:,}',
            textposition='outside',
            showlegend=False,
            hovertemplate='<b>%{x}</b><br>Count: %{y:,}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # ========================================================================
    # PANEL 4: Line Chart - Blocks with Rolling Average
    # ========================================================================
    print("  Adding Panel 4: Block Throughput...")
    tx_per_block = df.groupby('slot').size().reset_index(name='tx_count')
    tx_per_block['tx_count_ma'] = tx_per_block['tx_count'].rolling(
        window=100, center=True
    ).mean()
    
    # Sample for performance (every 10th block)
    tx_sample = tx_per_block.iloc[::10]
    
    fig.add_trace(
        go.Scatter(
            x=tx_sample['slot'],
            y=tx_sample['tx_count_ma'],
            mode='lines',
            name='100-block MA',
            line=dict(color='#E63946', width=2),
            showlegend=False,
            hovertemplate='Block: %{x}<br>Avg Tx: %{y:.1f}<extra></extra>'
        ),
        row=3, col=1
    )
    
    # ========================================================================
    # PANEL 5: Bar Chart - Top Validators
    # ========================================================================
    print("  Adding Panel 5: Top Validators...")
    top_validators = df['validator'].value_counts().head(10)
    validator_labels = [v[:8] + '...' for v in top_validators.index]
    
    fig.add_trace(
        go.Bar(
            x=top_validators.values,
            y=validator_labels,
            orientation='h',
            marker_color='#06AED5',
            text=top_validators.values,
            texttemplate='%{text:,}',
            textposition='outside',
            showlegend=False,
            hovertemplate='<b>%{y}</b><br>Events: %{x:,}<extra></extra>'
        ),
        row=3, col=2
    )
    
    # ========================================================================
    # UPDATE LAYOUT
    # ========================================================================
    print("🎨 Finalizing layout...")
    
    # Update axes labels
    fig.update_xaxes(title_text="Time", row=1, col=1)
    fig.update_yaxes(title_text="Events", row=1, col=1)
    
    fig.update_yaxes(title_text="Count", row=2, col=2)
    
    fig.update_xaxes(title_text="Block Number", row=3, col=1)
    fig.update_yaxes(title_text="Tx Count", row=3, col=1)
    
    fig.update_xaxes(title_text="Event Count", row=3, col=2)
    
    # Overall layout
    fig.update_layout(
        title={
            'text': '<b>PropAMM Dataset Analysis Dashboard</b><br>' + 
                    f'<sub>Data Range: {df["datetime"].min()} to {df["datetime"].max()} | ' + 
                    f'Total Events: {len(df):,}</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        height=1400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        hovermode='closest'
    )
    
    # Save to HTML
    print(f"\n💾 Saving dashboard to {output_file}...")
    fig.write_html(output_file)
    
    print("="*70)
    print("✅ DASHBOARD CREATED SUCCESSFULLY!")
    print("="*70)
    print(f"\n📊 Dashboard saved to: {output_file}")
    print(f"📈 Total panels: 5")
    print(f"📉 Data points visualized: {len(df):,}")
    print(f"\n🌐 Open {output_file} in your web browser to explore the interactive dashboard")
    print("="*70)
    
    return fig

# ========================================================================
# MAIN
# ========================================================================

if __name__ == "__main__":
    # Create main dashboard
    create_interactive_dashboard()