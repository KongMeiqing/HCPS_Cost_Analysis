import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import parameters as p
import calculate as calc
import plot as pl

st.set_page_config(page_title="Cost-Effectiveness Analysis of Rapid Hantavirus Testing", layout="wide")

st.title("🦠 Hantavirus Diagnosis Strategy: Cost-Effectiveness Interaction Simulator")
st.markdown("Drag the slider below to observe the impact of different parameters on the economic efficiency of the diagnostic strategy.")

# --- 侧边栏：用户交互参数 ---
st.sidebar.header("🔧 Parameter Adjustment")

# 用户可调的三个核心参数
rds_cost = st.sidebar.slider(
    "Rapid Detection Cost (RDS Cost, CNY)",
    min_value=50, max_value=2000, value=800, step=10
)

sds_cost = st.sidebar.slider(
    "Routine Testing Cost (SDS Cost, CNY)",
    min_value=100, max_value=5000, value=2000, step=20
)

rds_severe_rate = st.sidebar.slider(
    "Rapid Detection of Severe Rate (RDS Severe Rate, %)",
    min_value=10, max_value=70, value=40, step=1
) / 100


def monte_carlo_psa(sds_params, rds_params, cost_treatment, cost_test, ly_sds, ly_rds, population_size,
                    n_iterations=10000, random_seed=42):
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
        p_ecmo_sds = np.random.uniform(*sds_params["p_ecmo_if_severe"]) if isinstance(sds_params["p_ecmo_if_severe"],
                                                                                      list) else sds_params[
            "p_ecmo_if_severe"]

        # RDS
        p_severe_rds = np.random.uniform(*rds_params["p_severe"])  # ✅ 这里会使用滑块传进来的值
        mort_no_ecmo_rds = np.random.uniform(*rds_params["mortality_severe_no_ecmo"])
        mort_ecmo_rds = np.random.uniform(*rds_params["mortality_severe_ecmo"])
        p_ecmo_rds = np.random.uniform(*rds_params["p_ecmo_if_severe"]) if isinstance(rds_params["p_ecmo_if_severe"],
                                                                                      list) else rds_params[
            "p_ecmo_if_severe"]

        # COST
        c_mild = np.random.uniform(*cost_treatment["mild"])
        c_sev_no = np.random.uniform(*cost_treatment["severe_no_ecmo"])
        c_sev_ecmo = np.random.uniform(*cost_treatment["severe_ecmo"])

        # ✅ 这里会使用滑块传进来的成本值
        c_test_sds = np.random.uniform(*cost_test["SDS"])
        c_test_rds = np.random.uniform(*cost_test["RDS"]) if isinstance(cost_test["RDS"], list) else cost_test["RDS"]

        # 计算 SDS 和 RDS 的成本、效果
        sds_cost = calc.calculate_expected_cost(c_test_sds, p_severe_sds, p_ecmo_sds, c_mild, c_sev_no, c_sev_ecmo)
        sds_ly = calc.calculate_expected_life_years(p_severe_sds, p_ecmo_sds, mort_no_ecmo_sds, mort_ecmo_sds,
                                                    ly_sds["non_severe"], ly_sds["severe_no_ecmo"],
                                                    ly_sds["severe_ecmo"], ly_sds["discount_rate"])

        rds_cost = calc.calculate_expected_cost(c_test_rds, p_severe_rds, p_ecmo_rds, c_mild, c_sev_no, c_sev_ecmo)
        rds_ly = calc.calculate_expected_life_years(p_severe_rds, p_ecmo_rds, mort_no_ecmo_rds, mort_ecmo_rds,
                                                    ly_rds["non_severe"], ly_rds["severe_no_ecmo"],
                                                    ly_rds["severe_ecmo"], ly_rds["discount_rate"])

        delta_c = (rds_cost - sds_cost) * population_size
        delta_ly = (rds_ly - sds_ly) * population_size
        icer = delta_c / delta_ly if delta_ly != 0 else np.inf

        delta_costs.append(delta_c)
        delta_lys.append(delta_ly)
        icers.append(icer)

    return np.array(delta_costs), np.array(delta_lys), np.array(icers)

# --- 核心逻辑：运行蒙特卡洛模拟 ---
@st.cache_data
def run_simulation(rds_cost, sds_cost, rds_severe_rate):
    # 创建动态参数
    rds_params_temp = {
        "p_severe": [rds_severe_rate - 0.05, rds_severe_rate + 0.05],
        "p_ecmo_if_severe": p.RDS["p_ecmo_if_severe"],
        "mortality_severe_ecmo": p.RDS["mortality_severe_ecmo"],
        "mortality_severe_no_ecmo": p.RDS["mortality_severe_no_ecmo"],
    }

    cost_test_temp = {
        "SDS": [sds_cost - 50, sds_cost + 50],
        "RDS": [rds_cost - 50, rds_cost + 50],
    }

    # 调用你的蒙特卡洛模拟函数
    delta_costs, delta_lys, icers = monte_carlo_psa(
        sds_params=p.SDS,
        rds_params=rds_params_temp,
        cost_treatment=p.COST_TREATMENT,
        cost_test=cost_test_temp,
        ly_sds=p.LIFE_EXPECTANCY_SDS,
        ly_rds=p.LIFE_EXPECTANCY_RDS,
        population_size=p.DISPLAY["population_size"],
        n_iterations=500,  # 设置 500 次足够交互快速响应
        random_seed=42
    )

    return delta_costs, delta_lys, icers

delta_c, delta_ly, icers = run_simulation(rds_cost, sds_cost, rds_severe_rate)

# --- 显示结果 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 ICER Scatter Plot")
    fig, ax = plt.subplots()
    ax.scatter(delta_ly, delta_c, alpha=0.3, s=5)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.set_xlabel("Incremental Life Years")
    ax.set_ylabel("Incremental Cost (CNY)")
    st.pyplot(fig)

with col2:
    st.subheader("📊 CEAC Curve")
    wtp_range = np.linspace(0, 200000, 100)
    probs = [np.mean(icers < wtp) for wtp in wtp_range]
    fig, ax = plt.subplots()
    ax.plot(wtp_range, probs, 'b-', linewidth=2)
    ax.axvline(50000, color='red', linestyle='--', label='WTP=50,000 CNY')
    ax.set_xlabel("Willingness-to-pay (CNY/Life Year)")
    ax.set_ylabel("Probability of RDS being cost-effective")
    ax.legend()
    st.pyplot(fig)

st.markdown(f"""
### 📌 Current Conclusion
- **Rapid testing cost**：{rds_cost} CNY
- **Routine testing cost**：{sds_cost} CNY
- **Absolute advantage ratio**：{np.mean((delta_c < 0) & (delta_ly > 0)):.1%}
""")

# ================= 新增的结论展示 =================

# 计算平均增量成本和增量效果
mean_delta_c = np.mean(delta_c)
mean_delta_ly = np.mean(delta_ly)

# 判断逻辑
if mean_delta_c < 0 and mean_delta_ly > 0:
    recommendation = f"✅ Rapid diagnostic tests (RDS) have more advantages: lower average cost and better effectiveness."
    color = "green"
elif mean_delta_c > 0 and mean_delta_ly > 0:
    # 计算平均 ICER
    mean_icer = mean_delta_c / mean_delta_ly
    if mean_icer < 50000:  # 假设 WTP 阈值是 50,000
        recommendation = f"✅ Rapid Diagnostic Tests (RDS) are cost-effective: Although the average cost is high, the average effectiveness is better, with an ICER of {mean_icer:,.0f} CNY/Life Year, below the WTP threshold."
        color = "green"
    else:
        recommendation = f"⚠️ Routine testing (SDS) may be more cost-effective: The average cost of rapid testing is too high, with an ICER of {mean_icer:,.0f} CNY/Life Year, exceeding the WTP threshold."
        color = "orange"
elif mean_delta_c < 0 and mean_delta_ly < 0:
    recommendation = "⚠️ Conventional testing (SDS) has more advantages: Rapid testing has a lower average cost, but the effectiveness is also worse."
    color = "orange"
else:
    recommendation = "⚠️ Results are unclear: Please refer to the chart for detailed analysis."
    color = "gray"

# 用带颜色的框显示推荐结论
st.markdown(
    f"""
    <div style="background-color: {color}; padding: 10px; border-radius: 5px; color: white; text-align: center; font-size: 1.2em;">
        {recommendation}
    </div>
    """,
    unsafe_allow_html=True
)

# ================= 新增的结论展示结束 =================