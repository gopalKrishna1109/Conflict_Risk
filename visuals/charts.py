import matplotlib.pyplot as plt
import streamlit as st

def plot_trend(df):
    if df.empty:
        st.info("No data available for trend view.")
        return

    # Pivot for line chart: months on x, groups on lines, CRI on y
    pivot = df.pivot(index='month', columns='group', values='CRI')
    pivot = pivot.sort_index()  # Ensure chronological order

    fig, ax = plt.subplots(figsize=(12, 6))

    pivot.plot(ax=ax, marker='o', linewidth=2.5)

    ax.set_title("Organization-Wide CRI Trend Over Time", fontsize=16, pad=20)
    ax.set_ylim(0, 100)
    ax.set_ylabel("CRI Score")
    ax.set_xlabel("Month")
    ax.grid(True, alpha=0.3, linestyle='--')

    # Optional: Add risk threshold bands
    ax.axhspan(0, 39, color='#16c961', alpha=0.2, label='Low Risk')
    ax.axhspan(39, 69, color='#f39c12', alpha=0.2, label='Medium Risk')
    ax.axhspan(69, 100, color='#e73825', alpha=0.2, label='High Risk')

    ax.legend(title="Group", bbox_to_anchor=(1.05, 1), loc='upper left')

    st.pyplot(fig)

def plot_group_bar(df):
    if df.empty:
        st.info("No data available for the selected filters.")
        return

    # Get unique groups in the current data
    groups = df['group'].unique()
    num_groups = len(groups)

    # Determine title
    agg_level = df['group'].name.title() if hasattr(df['group'], 'name') else 'Group'
    if num_groups == 1:
        title = f"Current CRI for {groups[0]}"
    else:
        title = f"Current Risk Levels by {agg_level}"

    # Use latest month per group, sorted by CRI descending for better visual hierarchy
    latest = df.sort_values('month').groupby('group').last()
    latest = latest.sort_values('CRI', ascending=True)  # Low to high for horizontal bar

    fig, ax = plt.subplots(figsize=(10, max(6, len(latest) * 0.7)))

    # Color by risk level
    colors = []
    for cri in latest['CRI']:
        if cri <= 39:
            colors.append("#16c961")  # Green
        elif cri <= 69:
            colors.append('#f39c12')  # Orange
        else:
            colors.append("#e73825")  # Red

    bars = ax.barh(latest.index, latest['CRI'], color=colors, height=0.8)

    ax.set_xlim(0, 100)
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_xlabel("CRI Score")

    # Add value labels on bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'{width:.1f}', va='center', ha='left', fontweight='bold')

    ax.grid(axis='x', alpha=0.3, linestyle='--')

    # Clean y-axis labels
    ax.tick_params(axis='y', labelsize=10)

    st.pyplot(fig)

def plot_radar(df):
    if df.empty:
        st.info("No data available for radar chart.")
        return

    # Get latest data and find highest-risk group
    latest = df.sort_values('month').groupby('group').last()
    high_risk_row = latest.sort_values('CRI', ascending=False).iloc[0]
    group_name = high_risk_row.name
    cri = high_risk_row['CRI']

    # Prepare data
    labels = [
        "Polarization &\nInstability",
        "Declining Trust &\nSafety",
        "Communication\nStrain",
        "HR Operational\nStress",
        "Rapid Change\nImpact"
    ]
    values = [
        high_risk_row['vol_score'],
        high_risk_row['trust_score'],
        high_risk_row['comm_score'],
        high_risk_row['hr_score'],
        high_risk_row['change_score']
    ]

    # Create radar chart
    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))

    angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
    angles += angles[:1]  # Close the circle
    values += values[:1]

    ax.plot(angles, values, 'o-', linewidth=1, color='#00d4ff')
    ax.fill(angles, values, alpha=0.25, color='#00d4ff')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=3, color='white')
    ax.set_yticklabels([])  # Hide radial numbers
    ax.set_ylim(0, 100)
    ax.grid(True, color='gray', alpha=0.3)

    # Title with group and CRI
    ax.set_title(f"\nComponent Drivers for {group_name}\n(CRI {cri:.1f})", 
                 size=5, color='white', pad=30)

    # Background
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')

    st.pyplot(fig)