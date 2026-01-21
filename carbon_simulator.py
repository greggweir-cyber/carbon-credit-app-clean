import pandas as pd
import numpy as np
import re

class CarbonCreditSimulator:
    def __init__(self, data_path="globallometree_equations.csv"):
        self.equations_df = pd.read_csv(data_path)
        self.coeff_cache = {}
        self._build_coeff_cache()

    def _build_coeff_cache(self):
        # Supports both:
        # - globallometree_equations.csv (simple schema)
        # - globallometree_raw_import.csv (expanded schema)
        for _, row in self.equations_df.iterrows():
            species = str(row.get("species_name", "")).strip()
            region = str(row.get("region", "")).strip()

            if not species or not region:
                continue

            component = str(row.get("component", "AGB")).strip().upper()
            eq_type = str(row.get("equation_type", "")).strip().upper()

            # Only handle AGB log-linear DBH for now (your current app feature)
            if component != "AGB" or eq_type != "LOG_LINEAR_DBH":
                continue

            formula = str(row.get("formula_text", ""))
            nums = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", formula)

            # Expect: intercept and slope somewhere in the formula string
            if len(nums) < 2:
                continue

            key = (species, region)
            self.coeff_cache[key] = {
                "equation_type": "LOG_LINEAR_DBH",
                "intercept": float(nums[0]),
                "slope": float(nums[1]),
                "wood_density": float(row.get("wood_density", 0.5) or 0.5),
            }


    def calculate_agb_kg(self, dbh_cm, species, region):
        coeffs = self.coeff_cache.get((species, region))
        if not coeffs:
            return 0.0

        if coeffs["equation_type"] == "LOG_LINEAR_DBH":
            intercept = coeffs["intercept"]
            slope = coeffs["slope"]
            biomass = np.exp(intercept + slope * np.log(max(dbh_cm, 0.01)))
            return float(biomass)

        return 0.0
