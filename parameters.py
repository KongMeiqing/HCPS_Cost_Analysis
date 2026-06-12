# parameters.py

# Parameters for Display
DISPLAY = {
    "population_size": 1000,
    "wtp_threshold": 50000,
}
PATIENT_AGE_AT_INFECTION = 30

# Standard Diagnostic Strategy (SDS) diagnosed after 2 days
SDS = {
    "name": "Standard Diagnostic Strategy (5 days)",
    "p_severe": [0.55, 0.56],
    "p_ecmo_if_severe": [0.35, 0.45],
    "mortality_severe_ecmo": [0.3, 0.35],
    "mortality_severe_no_ecmo": [0.15, 0.2],
    "hospital_day": [10, 21],
}

# Rapid Diagnostic Strategy (RDS) diagnosed after 5 days
RDS = {
    "name": "Rapid Diagnostic Strategy (2 days)",
    "p_severe": [0.5, 0.6], # [0.35, 0.45]
    "p_ecmo_if_severe": [0.3, 0.4], #0.1
    "mortality_severe_ecmo": [0.25, 0.35],
    "mortality_severe_no_ecmo": [0.12, 0.18],
    "hospital_day": [5, 10],
}

# Costs for reference (in CNY)
COSTS = {
    "ward_per_day": [1000, 3000],        # General Ward (per day)
    "icu_per_day": [3000, 8000],        # ICU (per day)
    "vent_per_day": [1000, 3000],       # Mechanical ventilation (per day)（stacked on ICU）
    "ecmo_startup": [30000, 100000],      # ECMO startup fee
    "ecmo_per_day": [10000, 20000],      # ECMO (per day)
    "rapid_test": [800, 1700],           # Rapid test strip cost
    "conventional_dx": [110, 3900],     # Routine diagnosis
}

COST_TREATMENT = {
    "mild": [15000, 25000],
    "severe_no_ecmo": [80000, 120000],
    "severe_ecmo": [200000, 350000],
}


#EFFECT

LIFE_EXPECTANCY_RDS = {
    "non_severe": 35,
    "severe_no_ecmo": 32,
    "severe_ecmo": 28,
    "discount_rate": 0.03,
}

LIFE_EXPECTANCY_SDS = {
    "non_severe": 35,
    "severe_no_ecmo": 30,
    "severe_ecmo": 25,
    "discount_rate": 0.03,
}

SIMULATION = {
    "n_iterations": 10000,
    "random_seed": 42,
}

# Range for unilateral sensitivity analysis
SENSITIVITY = {
    "mortality_rds_severe_ecmo": [0.2, 0.3],
    "mortality_rds_severe_no_ecmo": [0.12, 0.18],
    "mortality_sds_severe_ecmo": [0.3, 0.35],
    "mortality_sds_severe_no_ecmo": [0.15, 0.2],
    "cost_ecmo": [150000, 350000],
}