"""
Extract Top 100 Validators by Slots/Blocks Processed
Reads the parquet file and generates a ranked list of validators by block production

Author: AI Analysis System
Date: January 9, 2026
"""

import pandas as pd
from datetime import datetime

def extract_top_validators_by_slots(input_file='pamm_updates_391876700_391976700.parquet',
                                     output_file='top100_validators_by_slots.txt',
                                     csv_output='top100_validators_by_slots.csv',
                                     top_n=100):
    """
    Extract top N validators ranked by number of unique slots (blocks) processed
    
    Args:
        input_file: Path to the parquet data file
        output_file: Path to save the text report
        csv_output: Path to save the CSV file
        top_n: Number of top validators to extract (default: 20)
    """
    
    print("="*80)
    print(f"EXTRACTING TOP {top_n} VALIDATORS BY SLOTS/BLOCKS PROCESSED")
    print("="*80)
    
    # Load data
    print(f"\n📂 Loading data from: {input_file}")
    df = pd.read_parquet(input_file)
    
    print(f"✓ Loaded {len(df):,} rows")
    print(f"✓ Columns: {list(df.columns)}")
    
    # Check required columns
    if 'validator' not in df.columns or 'slot' not in df.columns:
        print("\n❌ Error: Required columns not found in dataset")
        print(f"Available columns: {', '.join(df.columns)}")
        return
    
    # Calculate validator metrics
    print(f"\n🔍 Calculating validator metrics...")
    print("  • Counting unique slots per validator...")
    print("  • Counting total events per validator...")
    
    validator_stats = df.groupby('validator').agg({
        'slot': 'nunique',      # Number of unique slots (blocks)
        'validator': 'count'    # Total number of events/appearances
    }).rename(columns={
        'slot': 'unique_slots',
        'validator': 'total_events'
    })
    
    # Sort by unique slots descending
    validator_stats = validator_stats.sort_values('unique_slots', ascending=False)
    
    # Get top N validators
    top_validators = validator_stats.head(top_n)
    
    print(f"\n✓ Analysis complete!")
    print(f"  • Total validators analyzed: {len(validator_stats):,}")
    print(f"  • Extracting top {top_n} validators")
    
    # Display results
    print(f"\n{'='*80}")
    print(f"TOP {top_n} VALIDATORS BY SLOTS/BLOCKS PROCESSED")
    print(f"{'='*80}")
    print(f"\n{'Rank':<6} {'Validator ID':<45} {'Slots':<12} {'Events':<12}")
    print("-" * 80)
    
    for rank, (validator_id, row) in enumerate(top_validators.iterrows(), 1):
        print(f"{rank:<6} {validator_id:<45} {row['unique_slots']:>10,}  {row['total_events']:>10,}")
    
    # Save to text file
    print(f"\n💾 Saving results to: {output_file}")
    with open(output_file, 'w') as f:
        f.write(f"# Top {top_n} Validators by Slots/Blocks Processed\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Source: {input_file}\n")
        f.write(f"# Block range: 391876700-391976700 (~100,000 blocks)\n")
        f.write(f"# Total validators in dataset: {len(validator_stats):,}\n")
        f.write("#" + "="*78 + "\n\n")
        
        f.write(f"{'Rank':<6} {'Validator ID':<45} {'Unique Slots':<15} {'Total Events':<15}\n")
        f.write("-" * 85 + "\n")
        
        for rank, (validator_id, row) in enumerate(top_validators.iterrows(), 1):
            f.write(f"{rank:<6} {validator_id:<45} {row['unique_slots']:>13,}  {row['total_events']:>13,}\n")
        
        # Add summary statistics
        f.write("\n" + "="*85 + "\n")
        f.write("SUMMARY STATISTICS\n")
        f.write("="*85 + "\n")
        f.write(f"Total unique validators: {len(validator_stats):,}\n")
        f.write(f"Total unique slots in dataset: {df['slot'].nunique():,}\n")
        f.write(f"Total events in dataset: {len(df):,}\n")
        f.write(f"\nTop {top_n} validators represent:\n")
        f.write(f"  • {top_validators['unique_slots'].sum():,} slots ({top_validators['unique_slots'].sum()/df['slot'].nunique()*100:.1f}% of total)\n")
        f.write(f"  • {top_validators['total_events'].sum():,} events ({top_validators['total_events'].sum()/len(df)*100:.1f}% of total)\n")
    
    print(f"✓ Saved text report")
    
    # Save to CSV
    print(f"💾 Saving CSV to: {csv_output}")
    csv_data = top_validators.reset_index()
    csv_data.insert(0, 'rank', range(1, len(csv_data) + 1))
    csv_data.columns = ['Rank', 'Validator_ID', 'Unique_Slots', 'Total_Events']
    csv_data.to_csv(csv_output, index=False)
    print(f"✓ Saved CSV file")
    
    # Additional insights
    print(f"\n📊 Key Insights:")
    print(f"  • Top validator processed {top_validators.iloc[0]['unique_slots']:,} unique slots")
    print(f"  • Top {top_n} validators control {top_validators['unique_slots'].sum()/df['slot'].nunique()*100:.1f}% of all slots")
    print(f"  • Average slots per top-{top_n} validator: {top_validators['unique_slots'].mean():.1f}")
    print(f"  • Average events per slot (top-{top_n}): {top_validators['total_events'].sum()/top_validators['unique_slots'].sum():.1f}")
    
    print("\n" + "="*80)
    print("✅ EXTRACTION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    extract_top_validators_by_slots()

    def extract_next80_validators_by_slots(input_file='pamm_updates_391876700_391976700.parquet',
                                           output_file='next80_validators_by_slots.txt'):
        """
        Extract validators ranked 21-100 by number of unique slots (blocks) processed
        Args:
            input_file: Path to the parquet data file
            output_file: Path to save the text report
        """
        print("="*80)
        print(f"EXTRACTING NEXT 80 VALIDATORS (RANKS 21-100) BY SLOTS/BLOCKS PROCESSED")
        print("="*80)
        print(f"\n📂 Loading data from: {input_file}")
        df = pd.read_parquet(input_file)
        print(f"✓ Loaded {len(df):,} rows")
        print(f"✓ Columns: {list(df.columns)}")
        if 'validator' not in df.columns or 'slot' not in df.columns:
            print("\n❌ Error: Required columns not found in dataset")
            print(f"Available columns: {', '.join(df.columns)}")
            return
        print(f"\n🔍 Calculating validator metrics...")
        validator_stats = df.groupby('validator').agg({
            'slot': 'nunique',
            'validator': 'count'
        }).rename(columns={
            'slot': 'unique_slots',
            'validator': 'total_events'
        })
        validator_stats = validator_stats.sort_values('unique_slots', ascending=False)
        # Select ranks 21-100 (skip first 20)
        next80_validators = validator_stats.iloc[20:100]
        print(f"\n✓ Analysis complete!")
        print(f"  • Total validators analyzed: {len(validator_stats):,}")
        print(f"  • Extracting validators ranked 21-100")
        print(f"\n{'='*80}")
        print(f"NEXT 80 VALIDATORS (RANKS 21-100) BY SLOTS/BLOCKS PROCESSED")
        print(f"{'='*80}")
        print(f"\n{'Rank':<6} {'Validator ID':<45} {'Slots':<12} {'Events':<12}")
        print("-" * 80)
        for rank, (validator_id, row) in enumerate(next80_validators.iterrows(), 21):
            print(f"{rank:<6} {validator_id:<45} {row['unique_slots']:>10,}  {row['total_events']:>10,}")
        print(f"\n💾 Saving results to: {output_file}")
        with open(output_file, 'w') as f:
            f.write(f"# Next 80 Validators by Slots/Blocks Processed (Ranks 21-100)\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Source: {input_file}\n")
            f.write(f"# Block range: 391876700-391976700 (~100,000 blocks)\n")
            f.write(f"# Total validators in dataset: {len(validator_stats):,}\n")
            f.write("#" + "="*78 + "\n\n")
            f.write(f"{'Rank':<6} {'Validator ID':<45} {'Unique Slots':<15} {'Total Events':<15}\n")
            f.write("-" * 85 + "\n")
            for rank, (validator_id, row) in enumerate(next80_validators.iterrows(), 21):
                f.write(f"{rank:<6} {validator_id:<45} {row['unique_slots']:>13,}  {row['total_events']:>13,}\n")
            # Add summary statistics
            f.write("\n" + "="*85 + "\n")
            f.write("SUMMARY STATISTICS\n")
            f.write("="*85 + "\n")
            f.write(f"Total unique validators: {len(validator_stats):,}\n")
            f.write(f"Total unique slots in dataset: {df['slot'].nunique():,}\n")
            f.write(f"Total events in dataset: {len(df):,}\n")
            f.write(f"\nRanks 21-100 represent:\n")
            f.write(f"  • {next80_validators['unique_slots'].sum():,} slots ({next80_validators['unique_slots'].sum()/df['slot'].nunique()*100:.1f}% of total)\n")
            f.write(f"  • {next80_validators['total_events'].sum():,} events ({next80_validators['total_events'].sum()/len(df)*100:.1f}% of total)\n")
        print(f"✓ Saved text report")
        print(f"\n📊 Key Insights:")
        print(f"  • Highest in this group processed {next80_validators.iloc[0]['unique_slots']:,} unique slots")
        print(f"  • Ranks 21-100 control {next80_validators['unique_slots'].sum()/df['slot'].nunique()*100:.1f}% of all slots")
        print(f"  • Average slots per validator (21-100): {next80_validators['unique_slots'].mean():.1f}")
        print(f"  • Average events per slot (21-100): {next80_validators['total_events'].sum()/next80_validators['unique_slots'].sum():.1f}")
        print("\n" + "="*80)
        print("✅ EXTRACTION COMPLETE (RANKS 21-100)")
        print("="*80)

    extract_next80_validators_by_slots()
