import pandas as pd
import numpy as np
import re

class CarbonCreditSimulator:
    def __init__(self, data_path="globallometree_equations.csv"):
        self.equations_df = pd.read_csv(data_path)
        self.coeff_cache = {}
        self._build_coeff_cache()

    def _build_coeff_cache(self):
        for _, row in self.equations_df.iterrows():
            key = (row["species_name"], row["region"])
            if row.get("equation_type") == "LOG_LINEAR_DBH":
                formula = str(row.get("formula_text", ""))
                nums = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", formula)
                if len(nums) >= 2:
                    self.coeff_cache[key] = {
                        "equation_type": "LOG_LINEAR_DBH",
                        "intercept": float(nums[0]),
                        "slope": float(nums[1]),
                        "wood_density": row.get("wood_density", 0.5)
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
