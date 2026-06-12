# calculate.py
# The function used to realize all calculation logic
import numpy as np

import parameters


def calculate_expected_cost(test_cost, p_severe, p_ecmo, c_mild, c_sev_no, c_sev_ecmo):
    # Calculate the expected cost for treating (does NOT include secondary infection)

    p_mild = 1 - p_severe
    p_no_ecmo = 1 - p_ecmo

    expected = test_cost \
               + p_mild * c_mild \
               + p_severe * p_no_ecmo * c_sev_no \
               + p_severe * p_ecmo * c_sev_ecmo

    return expected

def calculate_expected_life_years(p_severe, p_ecmo, mort_no_ecmo, mort_ecmo, ly_non_sev, ly_sev_no, ly_sev_ecmo, discount_rate):
    # Calculate the expected life years saved under a specific strategy

    p_mild = 1 - p_severe
    p_no_ecmo = 1 - p_ecmo
    p_survive_no_ecmo = 1 - mort_no_ecmo
    p_survive_ecmo = 1 - mort_ecmo

    ly_mild_d = discount_life_years(ly_non_sev, discount_rate)
    ly_sev_no_d = discount_life_years(ly_sev_no, discount_rate)
    ly_sev_ecmo_d = discount_life_years(ly_sev_ecmo, discount_rate)

    expected = p_mild * ly_mild_d \
               + p_severe * p_no_ecmo * p_survive_no_ecmo * ly_sev_no_d \
               + p_severe * p_ecmo * p_survive_ecmo * ly_sev_ecmo_d
    return expected

def discount_life_years(ly, rate):
    total = 0.0
    for t in range(1, int(ly) + 1):
        total += 1.0 / ((1 + rate) ** t)
    return total

def mid(x):
    if isinstance(x, list):
        return (x[0] + x[1]) / 2
    return x



def calculate_icer(cost_rapid, cost_delay, ly_rapid, ly_delayed):
    # Calculate ICER 增量成本效果比
    # ICER = (C_rapid - C_delayed) / (LY_rapid - LY_delayed)

    temp_cost = cost_rapid - cost_delay
    temp_ly = ly_rapid - ly_delayed
    if temp_ly == 0:
        return float('inf')
    return temp_cost / temp_ly


def monte_carlo_psa(sds_params, rds_params, cost_treatment, cost_test, ly_sds, ly_rds, population_size = parameters.DISPLAY["population_size"], n_iterations=10000, random_seed=42):
    # Return the incremental cost and incremental effect of each iteration
    np.random.seed(random_seed)
    delta_costs = []
    delta_lys = []
    icers = []

    for i in range(n_iterations):
        # 1. Random sampling in the interval
        # SDS
        p_severe_sds = np.random.uniform(*sds_params["p_severe"])
        mort_no_ecmo_sds = np.random.uniform(*sds_params["mortality_severe_no_ecmo"])
        mort_ecmo_sds = np.random.uniform(*sds_params["mortality_severe_ecmo"])

        #
        p_ecmo_sds = np.random.uniform(*sds_params["p_ecmo_if_severe"]) if isinstance(sds_params["p_ecmo_if_severe"],
                                                                                      list) else sds_params[
            "p_ecmo_if_severe"]

        # RDS
        p_severe_rds = np.random.uniform(*rds_params["p_severe"])
        mort_no_ecmo_rds = np.random.uniform(*rds_params["mortality_severe_no_ecmo"])
        mort_ecmo_rds = np.random.uniform(*rds_params["mortality_severe_ecmo"])

        #
        p_ecmo_rds = np.random.uniform(*rds_params["p_ecmo_if_severe"]) if isinstance(rds_params["p_ecmo_if_severe"],
                                                                                      list) else rds_params[
            "p_ecmo_if_severe"]

        # COST
        c_mild = np.random.uniform(*cost_treatment["mild"])
        c_sev_no = np.random.uniform(*cost_treatment["severe_no_ecmo"])
        c_sev_ecmo = np.random.uniform(*cost_treatment["severe_ecmo"])
        c_test_sds = np.random.uniform(*cost_test["SDS"])

        #
        if isinstance(cost_test["RDS"], list):
            c_test_rds = np.random.uniform(*cost_test["RDS"])
        else:
            c_test_rds = cost_test["RDS"]

        # 2. Calculate SDS
        sds_cost = calculate_expected_cost(
            test_cost = c_test_sds,
            p_severe = p_severe_sds,
            p_ecmo = p_ecmo_sds,
            c_mild = c_mild,
            c_sev_no = c_sev_no,
            c_sev_ecmo = c_sev_ecmo,
        )

        sds_ly = calculate_expected_life_years(
            p_severe = p_severe_sds,
            p_ecmo = p_ecmo_sds,
            mort_no_ecmo = mort_no_ecmo_sds,
            mort_ecmo = mort_ecmo_sds,
            ly_non_sev = ly_sds["non_severe"],
            ly_sev_no = ly_sds["severe_no_ecmo"],
            ly_sev_ecmo = ly_sds["severe_ecmo"],
            discount_rate = ly_sds["discount_rate"],
        )

        # 3. Calculate RDS
        rds_cost = calculate_expected_cost(
            test_cost=c_test_rds,
            p_severe=p_severe_rds,
            p_ecmo=p_ecmo_rds,
            c_mild=c_mild,
            c_sev_no=c_sev_no,
            c_sev_ecmo=c_sev_ecmo,
        )

        rds_ly = calculate_expected_life_years(
            p_severe=p_severe_rds,
            p_ecmo=p_ecmo_rds,
            mort_no_ecmo=mort_no_ecmo_rds,
            mort_ecmo=mort_ecmo_rds,
            ly_non_sev=ly_rds["non_severe"],
            ly_sev_no=ly_rds["severe_no_ecmo"],
            ly_sev_ecmo=ly_rds["severe_ecmo"],
            discount_rate=ly_rds["discount_rate"],
        )

        # 4. Record
        delta_c = (rds_cost - sds_cost) * population_size
        delta_ly = (rds_ly - sds_ly) * population_size
        icer = delta_c / delta_ly if delta_ly != 0 else np.inf

        delta_costs.append(delta_c)
        delta_lys.append(delta_ly)
        icers.append(icer)

    return np.array(delta_costs), np.array(delta_lys), np.array(icers)


def one_way_sensitivity(sds_params, rds_params, cost_treatment, cost_test,
                        ly_sds, ly_rds, population_size, param_name,
                        param_range, strategy="both"):

    icers = []
    for val in param_range:
        sds_copy = {k: v for k, v in sds_params.items()}
        rds_copy = {k: v for k, v in rds_params.items()}

        if strategy == "sds" or strategy == "both":
            sds_copy[param_name] = val
        if strategy == "rds" or strategy == "both":
            rds_copy[param_name] = val


    return icers