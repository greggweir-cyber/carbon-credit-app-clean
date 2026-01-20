import streamlit as st
import pandas as pd
from carbon_simulator import CarbonCreditSimulator

st.set_page_config(page_title="Carbon Credit App (Clean)", layout="wide")
st.title("Carbon Credit App (Clean)")

# Simple ecoregion selector (your app currently uses simplified buckets)
ecoregion = st.selectbox("Ecoregion", ["temperate", "tropical", "boreal"], index=0)

native_df = pd.read_csv("native_species.csv")
native_species = native_df[native_df["ecoregion"].str.lower() == ecoregion.lower()]["species_name"].tolist()

if not native_species:
    st.error("No native species found for this ecoregion.")
    st.stop()

species = st.selectbox("Species", native_species, index=0)

dbh_cm = st.number_input("DBH (cm)", min_value=1.0, value=30.0, step=1.0)

sim = CarbonCreditSimulator("globallometree_equations.csv")
agb_kg = sim.calculate_agb_kg(dbh_cm, species, ecoregion)

st.write("### Result")
st.write(f"**AGB (kg/tree)**: {agb_kg:.4f}")
