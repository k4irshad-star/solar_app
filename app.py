import streamlit as st
import pandas as pd
import math
import requests

# Configure page
st.set_page_config(
    page_title="Solar Productive Use Calculator",
    page_icon="☀️",
    layout="wide"
)

# Custom CSS for styling (same as before)
st.markdown("""
<style>
    :root {
        --primary: #4CAF50;
        --secondary: #2c3e50;
        --accent: #e74c3c;
        --background: #f5f5f5;
        --card: white;
        --text: #333333;
    }
    
    .stApp {
        background-color: var(--background);
    }
    
    .stSelectbox, .stNumberInput, .stTextInput {
        background-color: var(--card);
        border-radius: 8px;
    }
    
    .stButton>button {
        background-color: var(--primary);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background-color: var(--card);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 4px solid var(--primary);
    }
    
    .metric-title {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin-bottom: 5px;
    }
    
    .metric-value {
        font-size: 1.6rem;
        font-weight: bold;
        color: var(--secondary);
    }
    
    .metric-unit {
        font-size: 0.8rem;
        color: #7f8c8d;
    }
    
    .highlight {
        color: var(--accent);
        font-weight: bold;
    }
    
    .summary-card {
        background-color: var(--card);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .section-title {
        color: var(--secondary);
        border-bottom: 2px solid var(--primary);
        padding-bottom: 5px;
        margin-bottom: 15px;
    }
    
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4CAF50;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    
    .warning-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    
    .error-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    
    .dataframe {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        padding: 0 20px;
        border-radius: 8px 8px 0 0 !important;
        background-color: #e0e0e0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Custom metric card component
def metric_card(title, value, unit="", help_text=None):
    card = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-unit">{unit}</div>
    </div>
    """
    if help_text:
        with st.expander("ℹ️"):
            st.caption(help_text)
    st.markdown(card, unsafe_allow_html=True)

# Appliance & system options
appliances = ["Choose one", "Mill 2kW", "Mill 3kW"]
system_rating = ["Choose one", "AC", "DC"]

# Panel specs
panel_wattage_kw = 0.5  # 500W
panel_cost = 50  

# Maps
power_map = {"Mill 2kW": 2.0, "Mill 3kW": 3.0}
price_map_usd = {"Mill 2kW": 600, "Mill 3kW": 800}
processing_speed_map = {"Mill 2kW": 100, "Mill 3kW": 150}  # kg/hr

# --- CACHE EXCHANGE RATES ---
@st.cache_data(ttl=3600)  # cache for 1 hour
def get_exchange_rates():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()["rates"]
    else:
        return {}

# --- DETECT USER LOCATION & CURRENCY ---
def get_user_currency():
    try:
        ip_info = requests.get("https://ipapi.co/json/").json()
        country = ip_info.get("country_name", "Unknown")
        currency = ip_info.get("currency", "USD")
        return country, currency
    except:
        return "Unknown", "USD"

# Fetch exchange rates
rates = get_exchange_rates()
currencies = ["USD"] + sorted([c for c in rates.keys() if c != "USD"])

# Streamlit UI (same as before)
st.title("☀️ Solar Productive Use Calculator")
st.markdown("""
<span style="color: var(--secondary); font-size: 1.1rem;">
Calculate the financial viability of solar-powered productive use appliances with this comprehensive tool.
</span>
""", unsafe_allow_html=True)

with st.expander("ℹ️ About this calculator", expanded=False):
    st.write("""
    This calculator helps you:
    - Determine the solar system requirements for your productive use appliance
    - Calculate financial metrics including payback period and loan repayments
    - Evaluate the business viability of your solar-powered operation
    
    Simply fill in your parameters and click "Calculate" to see the results.
    """)

# Create columns for input layout (same as before)
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">Appliance Details</div>', unsafe_allow_html=True)
    selected_appliance = st.selectbox(
        "Productive Use Appliance:", 
        appliances,
        help="Select the appliance you want to power with solar"
    )
    selected_system = st.selectbox(
        "System Rating:", 
        system_rating,
        help="Select AC or DC system type"
    )
    
    runtime_per_day = st.number_input(
        "Runtime Per Day (hrs)", 
        min_value=1.0, 
        value=4.0, 
        step=0.5,
        help="Daily operating hours of the appliance"
    )
    
    operating_days = st.number_input(
        "Operating Days per Year", 
        min_value=1, 
        value=250,
        help="Number of days per year the business will operate"
    )
    
    income_per_kg = st.number_input(
        "Income per kg (USD)", 
        min_value=0.0, 
        value=5/140,
        help="Revenue generated per kg of processed material"
    )

with col2:
    st.markdown('<div class="section-title">Solar System Details</div>', unsafe_allow_html=True)
    sun_hours = st.number_input(
        "Sun Hours Per Day (hrs)", 
        min_value=1.0, 
        value=4.0, 
        step=0.5,
        help="Average daily peak sun hours at your location"
    )
    
    system_efficiency = st.number_input(
        "System Efficiency (%)", 
        min_value=1, 
        max_value=100, 
        value=80,
        help="Overall efficiency of the solar system (inverter + wiring losses)"
    )
    
    battery_hours = st.number_input(
        "Battery Storage (hrs)", 
        min_value=0, 
        value=1,
        help="Hours of battery backup required"
    )
    
    daily_operating_cost = st.number_input(
        "Daily Operating Cost (USD)", 
        value=10.0, 
        step=1.0,
        help="Daily expenses like labor, rent, etc."
    )

# Financial inputs (same as before)
st.markdown('<div class="section-title">Financing Options</div>', unsafe_allow_html=True)
col3, col4, col5, col6 = st.columns(4)

with col3:
    loan_term_years = st.number_input(
        "Loan Term (Years)", 
        value=3, 
        step=1, 
        min_value=1
    )

with col4:
    interest_rate = st.number_input(
        "Interest Rate (p.a. %)", 
        value=15.0, 
        step=0.1, 
        min_value=0.0, 
        format="%.2f"
    ) / 100

with col5:
    deposit = st.number_input(
        "Deposit (USD)", 
        value=0.0, 
        step=1.0, 
        min_value=0.0
    )

with col6:
    install_increase = st.number_input(
        "Import & Installation Cost Increase (%)", 
        value=100, 
        step=10, 
        min_value=0, 
        max_value=100
    )
    install_multiplier = 1 + (install_increase / 100)

# Currency selection (same as before)
st.markdown('<div class="section-title">Currency Settings</div>', unsafe_allow_html=True)
use_location = st.checkbox(
    "Use my location to set currency automatically", 
    value=False,
    help="Automatically detect your country and currency"
)

selected_currency = "USD"
if use_location:
    user_country, detected_currency = get_user_currency()
    if detected_currency in currencies:
        selected_currency = detected_currency
        st.success(f"Detected location: {user_country} - Using {detected_currency}")
    else:
        st.warning(f"Detected currency {detected_currency} not supported. Using USD instead.")
else:
    selected_currency = st.selectbox("Select Currency:", currencies)

# Calculate button (same as before)
st.markdown("<br>", unsafe_allow_html=True)
calculate_btn = st.button(
    "🚀 Calculate System Requirements", 
    use_container_width=True,
    type="primary"
)
st.markdown("<br>", unsafe_allow_html=True)

if calculate_btn:
    if selected_appliance != "Choose one" and selected_system != "Choose one":
        # Lookup values - keep everything in USD for calculations
        power = power_map[selected_appliance]
        price_usd = price_map_usd[selected_appliance]  # Keep in USD
        processing_speed = processing_speed_map[selected_appliance]

        # Get exchange rate but don't convert yet
        rate = rates.get(selected_currency, 1)

        # Calculations - all in USD
        specific_efficiency = processing_speed / power
        energy_required_per_day = runtime_per_day * power
        energy_production = energy_required_per_day / (system_efficiency / 100)
        production_per_day = specific_efficiency * energy_required_per_day
        income_per_hour = income_per_kg * processing_speed
        income_per_day = income_per_kg * production_per_day
        gross_income_per_year = income_per_day * operating_days
        net_income_per_day = income_per_day - daily_operating_cost
        panel_energy_per_day = panel_wattage_kw * sun_hours 
        panels_required = math.ceil(energy_production / panel_energy_per_day)
        solar_panel_cost = panels_required * panel_cost  # USD
        recommended_solar_size = math.ceil((energy_production / sun_hours) * 2) / 2
        battery_capacity = recommended_solar_size * battery_hours

        # Initialize both costs to 0 in USD
        inverter_cost = 0
        controller_cost = 0

        if selected_system == "AC":
            inverter_cost = recommended_solar_size * 100   # USD
        elif selected_system == "DC":
            controller_cost = recommended_solar_size * 50  # USD
            
        # Battery cost in USD
        battery_cost = battery_capacity * 300  # USD

        # Cost calculations in USD
        fob_subtotal_usd = price_usd + solar_panel_cost + inverter_cost + controller_cost + battery_cost
        total_with_import_usd = fob_subtotal_usd * install_multiplier
        loan_principal_usd = total_with_import_usd - deposit

        # Loan calculations in USD
        months = loan_term_years * 12
        monthly_rate = interest_rate / 12

        if monthly_rate > 0:
            monthly_repayment_usd = (loan_principal_usd * monthly_rate) / (1 - (1 + monthly_rate)**(-months))
        else:
            monthly_repayment_usd = loan_principal_usd / months

        total_repayment_usd = months * monthly_repayment_usd
        total_interest_paid_usd = total_repayment_usd - loan_principal_usd
        annual_repayment_usd = monthly_repayment_usd * 12
        daily_repayment_usd = annual_repayment_usd / 365

        if income_per_day > 0:
            repayment_percentage = (daily_repayment_usd / income_per_day) * 100
        else:
            repayment_percentage = 0
        
        # Business viability
        if net_income_per_day > 0 and daily_repayment_usd > 0:
            viable_business = net_income_per_day >= daily_repayment_usd
            viability_text = "Yes ✅" if viable_business else "No ❌"
            viability_class = "success-box" if viable_business else "error-box"
        else:
            viable_business = False
            viability_text = "N/A"
            viability_class = "warning-box"

        # Display results in tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💵 Financials", "⚡ Technical", "📈 Viability"])

        with tab1:
            st.subheader("Key Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric_card(
                    "Recommended Solar Size", 
                    f"{recommended_solar_size}", 
                    "kWp",
                    "Total solar capacity needed"
                )
            with col2:
                metric_card(
                    "Panels Required", 
                    f"{panels_required}", 
                    "500W panels",
                    "Number of solar panels needed"
                )
            with col3:
                metric_card(
                    "Daily Production", 
                    f"{round(production_per_day, 1)}", 
                    "kg/day",
                    "Estimated daily processing output"
                )
            with col4:
                # Convert to target currency only at display time
                metric_card(
                    "Daily Net Income", 
                    f"{round(net_income_per_day * rate, 1)}", 
                    selected_currency,
                    "Income after operating costs"
                )
            
            st.markdown("---")
            st.subheader("System Overview")
            st.markdown(f"""
            <div class="summary-card">
                <p><b>Appliance:</b> {selected_appliance} ({power}kW {selected_system} system)</p>
                <p><b>Daily Operation:</b> {runtime_per_day} hours/day, {operating_days} days/year</p>
                <p><b>Solar Requirements:</b> {panels_required} x 500W panels ({recommended_solar_size} kWp system)</p>
                <p><b>Battery Storage:</b> {battery_capacity} kWh ({battery_hours} hours backup)</p>
                <p><b>Location:</b> {sun_hours} peak sun hours per day</p>
            </div>
            """, unsafe_allow_html=True)

        with tab2:
            st.subheader("Cost Breakdown")
            
            col1, col2 = st.columns(2)
            with col1:
                # Convert to target currency only at display time
                metric_card(
                    "Appliance Cost", 
                    f"{round(price_usd * rate, 1)}", 
                    selected_currency,
                    "Cost of the productive use appliance"
                )
                metric_card(
                    "Solar Panel Cost", 
                    f"{round(solar_panel_cost * rate, 1)}", 
                    selected_currency,
                    f"Cost for {panels_required} panels"
                )
                
            with col2:
                if selected_system == "AC":
                    metric_card(
                        "Inverter Cost", 
                        f"{round(inverter_cost * rate, 1)}", 
                        selected_currency,
                        "Cost for AC system inverter"
                    )
                else:
                    metric_card(
                        "Controller Cost", 
                        f"{round(controller_cost * rate, 1)}", 
                        selected_currency,
                        "Cost for DC system controller"
                    )
                metric_card(
                    "Battery Cost", 
                    f"{round(battery_cost * rate, 1)}", 
                    selected_currency,
                    f"Cost for {battery_capacity} kWh battery"
                )
            
            st.markdown("---")
            st.subheader("Total Costs")
            
            col3, col4 = st.columns(2)
            with col3:
                metric_card(
                    "FOB Subtotal", 
                    f"{round(fob_subtotal_usd * rate, 1)}", 
                    selected_currency,
                    "Cost before import/installation"
                )
            with col4:
                metric_card(
                    "Installed Cost", 
                    f"{round(total_with_import_usd * rate, 1)}", 
                    selected_currency,
                    f"Total after {install_increase}% import/install costs"
                )
            
            st.markdown("---")
            st.subheader("Loan Details")
            
            col5, col6, col7 = st.columns(3)
            with col5:
                metric_card(
                    "Loan Principal", 
                    f"{round(loan_principal_usd * rate, 1)}", 
                    selected_currency,
                    "Amount being financed"
                )
            with col6:
                metric_card(
                    "Monthly Payment", 
                    f"{round(monthly_repayment_usd * rate, 1)}", 
                    selected_currency,
                    f"For {loan_term_years} years at {interest_rate*100}% p.a."
                )
            with col7:
                metric_card(
                    "Total Interest", 
                    f"{round(total_interest_paid_usd * rate, 1)}", 
                    selected_currency,
                    "Total interest over loan term"
                )

        with tab3:
            st.subheader("Technical Specifications")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                metric_card(
                    "Daily Energy Required", 
                    f"{round(energy_required_per_day, 1)}", 
                    "kWh",
                    "Energy needed to run appliance"
                )
            with col2:
                metric_card(
                    "Daily Energy Production", 
                    f"{round(energy_production, 1)}", 
                    "kWh",
                    "Energy system needs to generate"
                )
            with col3:
                metric_card(
                    "System Efficiency", 
                    f"{system_efficiency}", 
                    "%",
                    "Overall system efficiency"
                )
            
            st.markdown("---")
            st.subheader("Performance Metrics")
            
            col4, col5, col6 = st.columns(3)
            with col4:
                metric_card(
                    "Processing Speed", 
                    f"{processing_speed}", 
                    "kg/hour",
                    "Material processing rate"
                )
            with col5:
                metric_card(
                    "Specific Efficiency", 
                    f"{round(specific_efficiency, 2)}", 
                    "kg/kWh",
                    "Processing efficiency"
                )
            with col6:
                metric_card(
                    "Battery Backup", 
                    f"{battery_hours}", 
                    "hours",
                    "Battery storage duration"
                )
            
            st.markdown("---")
            st.subheader("Detailed Calculations")
            
            df_tech = pd.DataFrame([{
                "Parameter": "Appliance Power",
                "Value": f"{power}",
                "Unit": "kW"
            }, {
                "Parameter": "Daily Runtime",
                "Value": runtime_per_day,
                "Unit": "hours"
            }, {
                "Parameter": "Energy Required",
                "Value": round(energy_required_per_day, 2),
                "Unit": "kWh/day"
            }, {
                "Parameter": "Production Rate",
                "Value": processing_speed,
                "Unit": "kg/hour"
            }, {
                "Parameter": "Daily Production",
                "Value": round(production_per_day, 2),
                "Unit": "kg/day"
            }, {
                "Parameter": "Panel Requirement",
                "Value": panels_required,
                "Unit": "panels"
            }])
            
            st.dataframe(
                df_tech, 
                hide_index=True, 
                use_container_width=True,
                column_config={
                    "Parameter": st.column_config.Column(width="medium"),
                    "Value": st.column_config.Column(width="small"),
                    "Unit": st.column_config.Column(width="small")
                }
            )

        with tab4:
            st.subheader("Business Viability Analysis")
            
            st.markdown(f"""
            <div class="{viability_class}">
                <h3>Viable Business? {viability_text}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("Income vs. Repayments")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                metric_card(
                    "Daily Gross Income", 
                    f"{round(income_per_day * rate, 1)}", 
                    selected_currency,
                    "Income before expenses"
                )
            with col2:
                metric_card(
                    "Daily Net Income", 
                    f"{round(net_income_per_day * rate, 1)}", 
                    selected_currency,
                    "Income after operating costs"
                )
            with col3:
                metric_card(
                    "Daily Loan Repayment", 
                    f"{round(daily_repayment_usd * rate, 1)}", 
                    selected_currency,
                    "Daily loan repayment amount"
                )
            
            st.markdown("---")
            st.subheader("Financial Ratios")
            
            col4, col5 = st.columns(2)
            with col4:
                metric_card(
                    "Repayment % of Income", 
                    f"{round(repayment_percentage, 1)}", 
                    "%",
                    "Percentage of daily income needed for repayments"
                )
            with col5:
                if viable_business:
                    surplus = net_income_per_day - daily_repayment_usd
                    metric_card(
                        "Daily Surplus", 
                        f"{round(surplus * rate, 1)}", 
                        selected_currency,
                        "Daily profit after loan repayments"
                    )
            
            st.markdown("---")
            st.subheader("Payback Analysis")
            
            if viable_business and annual_repayment_usd > 0:
                payback_years = total_with_import_usd / (net_income_per_day * operating_days)
                st.markdown(f"""
                <div class="summary-card">
                    <p><b>Total System Cost:</b> {round(total_with_import_usd * rate, 1)} {selected_currency}</p>
                    <p><b>Annual Net Profit:</b> {round(net_income_per_day * operating_days * rate, 1)} {selected_currency}</p>
                    <p><b>Simple Payback Period:</b> {round(payback_years, 1)} years</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Payback analysis not available - business is not viable")

        st.caption(f"💱 Exchange rate used: 1 USD = {rate:.2f} {selected_currency}")
    else:
        st.error("⚠️ Please select both an Appliance and System type before calculating.")