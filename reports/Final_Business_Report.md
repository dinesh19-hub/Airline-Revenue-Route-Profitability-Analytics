# Final Business Recommendations & Report
**Prepared for:** Bain BCN Intern Analyst Case Study
**Project:** Airline Revenue & Route Profitability Analytics

## 1. Executive Summary
This analytical project evaluated one year of simulated commercial airline operations (Jan–Dec 2025) comprising over 100,000 passenger bookings. The objective was to identify the core drivers of route profitability, optimize capacity allocation, and generate data-driven pricing strategies. 

By restructuring the data pipeline via a robust SQL integration, conducting Exploratory Data Analysis (EDA) in Python, and deploying interactive Power BI and Streamlit dashboards, we uncovered highly actionable strategic insights.

## 2. Key Findings & Quantified Insights

### A. Route Profitability & Cost Structures
- **Transcontinental Dominance:** Long-haul domestic routes (e.g., LAX-JFK, SFO-ORD) generate the highest gross profit margins (averaging **~78%**). Despite higher fuel and crew costs, the elevated ticket prices on these routes easily absorb the variable costs.
- **Underperforming Short-Hauls:** Certain short-haul regional flights suffer from compressed margins. Fixed airport operational costs consume a disproportionately large share of revenue on these segments.

### B. Capacity Utilization
- **High Operational Efficiency:** The overall passenger load factor sits at an impressive **83%**. This indicates a highly efficient match of aircraft gauge (Total Capacity) to underlying route demand.
- **Seasonality Stability:** The month-over-month variance in load factor is exceptionally low, suggesting that the current scheduling algorithms are highly effective at scaling capacity up and down in response to macroeconomic travel cycles.

### C. Customer Segmentation
- **The Value of the Corporate Traveler:** Business class passengers in the 'Gold' or 'Platinum' loyalty tiers are the most valuable asset. The average Lifetime Value (LTV) of a Gold Business passenger is **$9,125**, which is **2.3x higher** than a comparable Gold Leisure passenger ($3,969).
- **Ancillary Revenue Sensitivity:** Leisure travelers exhibit high price elasticity on base fares but drive significant volume in ancillary revenues (baggage, seat selection).

### D. Yield Management (Pricing vs. Demand)
- **Classic Booking Curves:** The data proves the efficacy of the airline’s yield management engine. Base ticket prices remain flat and affordable during the 30–90 day booking window, incentivizing volume.
- **Last-Minute Premium:** Prices increase sharply for bookings made less than 14 days prior to departure, effectively capturing the inelastic demand of last-minute corporate travelers.

---

## 3. Actionable Business Recommendations

Based on the quantified insights, I propose the following strategic initiatives:

1. **Re-Gauge Underperforming Routes:**
   - *Action:* Swap mainline narrow-body aircraft with smaller regional jets on short-haul routes where fixed airport costs are eroding margins. 
   - *Impact:* Reduces variable fuel/crew costs while maintaining the 83% load factor, immediately lifting the gross margin on underperforming segments.

2. **Aggressive Corporate Retention:**
   - *Action:* Reroute marketing spend from general brand awareness into targeted B2B loyalty programs aimed at Gold and Platinum Business travelers. Offer accelerated status matches for competitor airlines.
   - *Impact:* Securing the $9,000+ LTV segment protects the core profitability engine against macroeconomic downturns.

3. **Dynamic Ancillary Pricing for Leisure:**
   - *Action:* Maintain highly competitive base fares for Economy/Leisure tickets made 60+ days in advance, but dynamically price ancillary products (bags, priority boarding) based on real-time flight demand.
   - *Impact:* Increases total revenue per available seat mile (TRASM) without damaging the airline's optical price competitiveness on flight search engines.

4. **Yield Curve Steepenening:**
   - *Action:* Increase the pricing algorithms' sensitivity at the 14-day and 7-day marks on heavily corporate routes (like LAX-JFK).
   - *Impact:* Captures additional yield from highly inelastic last-minute business demand, directly flowing to the bottom line since the variable cost of that seat is near zero.
