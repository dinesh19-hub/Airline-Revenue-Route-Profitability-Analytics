# %% [markdown]
# # Customer Segmentation & Value Analysis
# This notebook analyzes passenger booking behaviors, customer lifetime value, and demographic segments.

# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# %%
base_dir = os.path.dirname(os.getcwd()) if os.path.basename(os.getcwd()) == 'notebooks' else os.getcwd()
processed_dir = os.path.join(base_dir, 'data', 'processed')
figures_dir = os.path.join(base_dir, 'reports', 'figures')

df_bookings = pd.read_pickle(os.path.join(processed_dir, 'bookings_clean.pkl'))

# %% [markdown]
# ### Customer Value Calculation

# %%
df_bookings['TotalSpend'] = df_bookings['TicketPrice'] + df_bookings['AncillaryRevenue']

customer_ltv = df_bookings.groupby('CustomerID').agg(
    TotalBookings=('BookingID', 'count'),
    TotalSpend=('TotalSpend', 'sum'),
    AvgAncillary=('AncillaryRevenue', 'mean'),
    PassengerType=('PassengerType', 'first'),
    LoyaltyTier=('LoyaltyTier', 'first')
).reset_index()

# Group by Passenger Type and Loyalty
segment_summary = customer_ltv.groupby(['PassengerType', 'LoyaltyTier'], dropna=False).agg(
    CustomerCount=('CustomerID', 'count'),
    AvgBookings=('TotalBookings', 'mean'),
    AvgSpend=('TotalSpend', 'mean')
).reset_index().fillna({'LoyaltyTier': 'None'})

segment_summary = segment_summary.sort_values('AvgSpend', ascending=False)
segment_summary

# %% [markdown]
# ### Visualizations

# %%
# Plot 1: Revenue by Passenger Type and Loyalty Tier
plt.figure(figsize=(12, 6))
sns.barplot(data=segment_summary, x='PassengerType', y='AvgSpend', hue='LoyaltyTier', palette='Set2')
plt.title('Average Customer Lifetime Value (LTV) by Segment', fontsize=16)
plt.ylabel('Average Spend ($)', fontsize=12)
plt.xlabel('Passenger Type', fontsize=12)
plt.legend(title='Loyalty Tier')
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, 'ltv_by_segment.png'))
plt.show()

# %%
# Plot 2: Scatter of Bookings vs Spend
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=customer_ltv.sample(n=min(5000, len(customer_ltv)), random_state=42), 
    x='TotalBookings', 
    y='TotalSpend', 
    hue='PassengerType',
    alpha=0.6,
    palette='Set1'
)
plt.title('Customer LTV vs Booking Frequency', fontsize=16)
plt.ylabel('Total Spend ($)', fontsize=12)
plt.xlabel('Total Bookings in Period', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, 'ltv_vs_frequency.png'))
plt.show()

print("Customer segmentation analysis complete and figures saved.")
