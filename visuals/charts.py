import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def plot_trend(df):
    if df.empty:
        st.info("No data available for trend.")
        return

    pivot = df.pivot(index='month', columns='group', values='CRI')
    pivot = pivot.sort_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    pivot.plot(ax=ax, marker='o')
    ax.set_title("CRI Trend Over Time", fontsize=16)
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

def plot_group_bar(df):
    latest = df.sort_values('month').groupby('group').last().sort_values('CRI', ascending=True)

    fig, ax = plt.subplots(figsize=(8, max(4, len(latest) * 0.5)))
    colors = ['green' if x <= 39 else 'orange' if x <= 69 else 'red' for x in latest['CRI']]
    bars = ax.barh(latest.index, latest['CRI'], color=colors)

    ax.set_xlim(0, 100)
    ax.set_title(f"Current CRI by {df['group'].name.title() if hasattr(df['group'], 'name') else 'Group'}", fontsize=14)

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'{width:.1f}', va='center', ha='left', fontweight='bold')

    st.pyplot(fig)