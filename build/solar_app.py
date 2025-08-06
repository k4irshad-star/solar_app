# %%
import streamlit as st
import pandas as pd
import math

# Load appliance specs from Excel
file_path = r"C:\Users\DELL\Downloads\Solar_System_Sizing_Calculator draft2SC.xlsx"
xls = pd.ExcelFile(file_path)
appliance_specs = xls.parse('ApplianceSpecs')  # Sheet with appliance data

# ---- User Inputs ----
st.title("Solar System Sizing App")

appliance_power = st.number_input("Appliance Power (W)", value=2000)
runtime = st.number_input("Runtime (hours/day)", value=8.0)
sun_hours = st.number_input("Sun Hours per Day", value=4.0)
panel_wattage = st.number_input("Panel Wattage (W)", value=500)

system_type = st.selectbox("System Type", ["AC", "DC"])
income_per_kg = st.number_input("Income per kg", value=0.1)
processing_speed = st.number_input("Processing Speed (kg/hr)", value=10)

# ---- Calculations ----
energy_per_day_kwh = (appliance_power * runtime) / 1000
solar_panel_kW_required = energy_per_day_kwh / sun_hours
solar_panel_kW_rounded = math.ceil(solar_panel_kW_required * 2) / 2  # round up to 0.5

# Solar panel cost
panel_cost_per_kw = 100 if system_type == "AC" else 50
capital_cost = solar_panel_kW_rounded * panel_cost_per_kw

# Income/day
kg_per_day = processing_speed * runtime
income_per_day = income_per_kg * kg_per_day

# ---- Output ----
st.subheader("Results")
st.write(f"Energy Required per Day: {energy_per_day_kwh:.2f} kWh")
st.write(f"Solar Panel Size Required: {solar_panel_kW_rounded:.1f} kWp")
st.write(f"Capital Cost: ${capital_cost:.2f}")
st.write(f"Income per Day: ${income_per_day:.2f}")





