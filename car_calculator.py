import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Car Value Calculator", layout="wide")

# --- HELPER FUNCTIONS ---
def calculate_monthly_payment(price, down_payment, trade_in, tax_rate, fees, interest_rate, term_months):
    tax_amount = price * (tax_rate / 100)
    loan_amount = price + tax_amount + fees - down_payment - trade_in
    
    if loan_amount <= 0:
        return 0, 0, 0, 0

    if interest_rate == 0:
        monthly_payment = loan_amount / term_months
        total_interest = 0
    else:
        monthly_rate = (interest_rate / 100) / 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** term_months) / ((1 + monthly_rate) ** term_months - 1)
        total_interest = (monthly_payment * term_months) - loan_amount

    return monthly_payment, total_interest, loan_amount, tax_amount

# --- APP TITLE ---
st.title("🏎️ The Ultimate Car Dilemma Calculator")
st.markdown("Compare the **Used 2023 Model Y** vs. **New Model Y (1.99%)** vs. **Lexus NX**.")

# --- SIDEBAR: GLOBAL SETTINGS ---
st.sidebar.header("🌍 Local Settings (Arkansas)")
tax_rate = st.sidebar.number_input("Sales Tax Rate (%)", value=6.5, step=0.1)
doc_fees = st.sidebar.number_input("Dealer/Reg Fees ($)", value=500, step=50)
down_payment_global = st.sidebar.number_input("Cash Down Payment ($)", value=20000, step=1000)

# --- MAIN COLUMNS ---
col1, col2, col3 = st.columns(3)

# --- CAR A: USED 2023 TESLA MODEL Y (Based on your AutoTrader Link) ---
with col1:
    st.subheader("Option A: Used 2023 Tesla Y")
    price_a = st.number_input("Price A ($)", value=31500)
    rate_a = st.number_input("Interest Rate A (%)", value=6.49)
    term_a = st.selectbox("Term A (Months)", (36, 48, 60, 72), index=2)
    ins_a = st.number_input("Monthly Insurance A ($)", value=155)
    fuel_a = st.number_input("Monthly Fuel/Electric A ($)", value=0, help="Enter 0 if using free charger")

# --- CAR B: NEW 2025 TESLA MODEL Y (Promo Rate) ---
with col2:
    st.subheader("Option B: New 2025 Tesla Y")
    price_b = st.number_input("Price B ($)", value=46000)
    rate_b = st.number_input("Interest Rate B (%)", value=1.99)
    term_b = st.selectbox("Term B (Months)", (36, 48, 60, 72), index=2)
    ins_b = st.number_input("Monthly Insurance B ($)", value=155)
    fuel_b = st.number_input("Monthly Fuel/Electric B ($)", value=0)

# --- CAR C: USED 2023 LEXUS NX (Comparison) ---
with col3:
    st.subheader("Option C: Used 2023 Lexus NX")
    price_c = st.number_input("Price C ($)", value=38000)
    rate_c = st.number_input("Interest Rate C (%)", value=6.49)
    term_c = st.selectbox("Term C (Months)", (36, 48, 60, 72), index=2)
    ins_c = st.number_input("Monthly Insurance C ($)", value=80)
    fuel_c = st.number_input("Monthly Fuel C ($)", value=96, help="Based on Premium Gas")

# --- CALCULATIONS ---
pay_a, int_a, loan_a, tax_a = calculate_monthly_payment(price_a, down_payment_global, 0, tax_rate, doc_fees, rate_a, term_a)
pay_b, int_b, loan_b, tax_b = calculate_monthly_payment(price_b, down_payment_global, 0, tax_rate, doc_fees, rate_b, term_b)
pay_c, int_c, loan_c, tax_c = calculate_monthly_payment(price_c, down_payment_global, 0, tax_rate, doc_fees, rate_c, term_c)

# Calculate Total Monthly Cost of Ownership
total_monthly_a = pay_a + ins_a + fuel_a
total_monthly_b = pay_b + ins_b + fuel_b
total_monthly_c = pay_c + ins_c + fuel_c

# Calculate 5-Year Total Cost (Loan Payments + Down Payment + Insurance + Fuel)
# Note: If loan term < 60, we assume 0 payments for remaining months
def get_5_year_cost(monthly_pay, term, down, ins, fuel):
    payments = monthly_pay * min(term, 60)
    running_costs = (ins + fuel) * 60
    return payments + down + running_costs

cost_5yr_a = get_5_year_cost(pay_a, term_a, down_payment_global, ins_a, fuel_a)
cost_5yr_b = get_5_year_cost(pay_b, term_b, down_payment_global, ins_b, fuel_b)
cost_5yr_c = get_5_year_cost(pay_c, term_c, down_payment_global, ins_c, fuel_c)

# --- DISPLAY RESULTS ---
st.divider()
st.header("💸 The Financial Showdown")

res_col1, res_col2, res_col3 = st.columns(3)

with res_col1:
    st.info(f"**Used Tesla Y**")
    st.metric(label="Monthly Loan Payment", value=f"${pay_a:,.2f}")
    st.metric(label="Total Monthly Out-of-Pocket", value=f"${total_monthly_a:,.2f}", delta_color="inverse")
    st.write(f"Total Interest Paid: ${int_a:,.2f}")

with res_col2:
    st.warning(f"**New Tesla Y (1.99%)**")
    st.metric(label="Monthly Loan Payment", value=f"${pay_b:,.2f}", delta=f"${pay_b - pay_a:,.2f}")
    st.metric(label="Total Monthly Out-of-Pocket", value=f"${total_monthly_b:,.2f}", delta=f"${total_monthly_b - total_monthly_a:,.2f}", delta_color="inverse")
    st.write(f"Total Interest Paid: ${int_b:,.2f}")

with res_col3:
    st.success(f"**Used Lexus NX**")
    st.metric(label="Monthly Loan Payment", value=f"${pay_c:,.2f}", delta=f"${pay_c - pay_a:,.2f}")
    st.metric(label="Total Monthly Out-of-Pocket", value=f"${total_monthly_c:,.2f}", delta=f"${total_monthly_c - total_monthly_a:,.2f}", delta_color="inverse")
    st.write(f"Total Interest Paid: ${int_c:,.2f}")

# --- CHARTS ---
st.divider()

# Chart 1: Total Cost Over 5 Years
st.subheader("Total Cost to Own (5 Years)")
st.caption("Includes: Down Payment + Monthly Payments + Insurance + Fuel")

fig_cost = go.Figure(data=[
    go.Bar(name='Loan/Purchase Cost', x=['Used Tesla Y', 'New Tesla Y', 'Lexus NX'], 
           y=[cost_5yr_a - (ins_a+fuel_a)*60, cost_5yr_b - (ins_b+fuel_b)*60, cost_5yr_c - (ins_c+fuel_c)*60], marker_color='royalblue'),
    go.Bar(name='Insurance & Fuel', x=['Used Tesla Y', 'New Tesla Y', 'Lexus NX'], 
           y=[(ins_a+fuel_a)*60, (ins_b+fuel_b)*60, (ins_c+fuel_c)*60], marker_color='firebrick')
])
fig_cost.update_layout(barmode='stack', height=400)
st.plotly_chart(fig_cost, use_container_width=True)

# Chart 2: Loan Balance Over Time (Equity Simulator)
st.subheader("Loan Balance vs. Estimated Value (Equity Check)")
st.caption("See when you break even. Assumes standard depreciation curves.")

# Generate Depreciation Curves
months = list(range(0, 61))
# Depreciation assumptions: New cars lose 20% year 1, then 10%. Used cars lose 10% per year.
def get_value_curve(start_price, is_new):
    values = []
    current = start_price
    for m in months:
        rate = 0.15/12 if is_new and m < 12 else 0.10/12
        current = current * (1 - rate)
        values.append(current)
    return values

def get_loan_curve(principal, rate, payment, term):
    balances = []
    balance = principal
    monthly_rate = (rate / 100) / 12
    for m in months:
        if m > term:
            balances.append(0)
        else:
            balances.append(max(0, balance))
            interest = balance * monthly_rate
            principal_pay = payment - interest
            balance -= principal_pay
    return balances

val_a = get_value_curve(price_a, False)
loan_curve_a = get_loan_curve(loan_a, rate_a, pay_a, term_a)

val_b = get_value_curve(price_b, True)
loan_curve_b = get_loan_curve(loan_b, rate_b, pay_b, term_b)

fig_equity = go.Figure()
# Car A
fig_equity.add_trace(go.Scatter(x=months, y=loan_curve_a, mode='lines', name='Loan Balance (Used Tesla)', line=dict(dash='dot', color='blue')))
fig_equity.add_trace(go.Scatter(x=months, y=val_a, mode='lines', name='Car Value (Used Tesla)', line=dict(color='blue')))
# Car B
fig_equity.add_trace(go.Scatter(x=months, y=loan_curve_b, mode='lines', name='Loan Balance (New Tesla)', line=dict(dash='dot', color='green')))
fig_equity.add_trace(go.Scatter(x=months, y=val_b, mode='lines', name='Car Value (New Tesla)', line=dict(color='green')))

fig_equity.update_layout(title="Will you be underwater?", xaxis_title="Months", yaxis_title="Dollars ($)")
st.plotly_chart(fig_equity, use_container_width=True)