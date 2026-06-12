# main
import parameters as p
import calculate as calc
import plot as pl

def main():
    print("=== Economic Analysis of Diagnostic Strategies for Hantavirus Cardiopulmonary Syndrome (HCPS) ===\n")

    # ==================== 1. 点估计 ====================
    print("1. Point Estimate (Deterministic Analysis)")

    # get mid
    sds_cost_per = calc.calculate_expected_cost(
        test_cost=calc.mid(p.COSTS["conventional_dx"]),
        p_severe=calc.mid(p.SDS["p_severe"]),
        p_ecmo=calc.mid(p.SDS["p_ecmo_if_severe"]),
        c_mild=calc.mid(p.COST_TREATMENT["mild"]),
        c_sev_no=calc.mid(p.COST_TREATMENT["severe_no_ecmo"]),
        c_sev_ecmo=calc.mid(p.COST_TREATMENT["severe_ecmo"]),
    )
    sds_ly_per = calc.calculate_expected_life_years(
        p_severe=calc.mid(p.SDS["p_severe"]),
        p_ecmo=calc.mid(p.SDS["p_ecmo_if_severe"]),
        mort_no_ecmo=calc.mid(p.SDS["mortality_severe_no_ecmo"]),
        mort_ecmo=calc.mid(p.SDS["mortality_severe_ecmo"]),
        ly_non_sev=p.LIFE_EXPECTANCY_SDS["non_severe"],
        ly_sev_no=p.LIFE_EXPECTANCY_SDS["severe_no_ecmo"],
        ly_sev_ecmo=p.LIFE_EXPECTANCY_SDS["severe_ecmo"],
        discount_rate=p.LIFE_EXPECTANCY_SDS["discount_rate"],
    )

    rds_cost_per = calc.calculate_expected_cost(
        test_cost=calc.mid(p.COSTS["rapid_test"]),
        p_severe=calc.mid(p.RDS["p_severe"]),
        p_ecmo=calc.mid(p.RDS["p_ecmo_if_severe"]),
        c_mild=calc.mid(p.COST_TREATMENT["mild"]),
        c_sev_no=calc.mid(p.COST_TREATMENT["severe_no_ecmo"]),
        c_sev_ecmo=calc.mid(p.COST_TREATMENT["severe_ecmo"]),
    )
    rds_ly_per = calc.calculate_expected_life_years(
        p_severe=calc.mid(p.RDS["p_severe"]),
        p_ecmo=calc.mid(p.RDS["p_ecmo_if_severe"]),
        mort_no_ecmo=calc.mid(p.RDS["mortality_severe_no_ecmo"]),
        mort_ecmo=calc.mid(p.RDS["mortality_severe_ecmo"]),
        ly_non_sev=p.LIFE_EXPECTANCY_RDS["non_severe"],
        ly_sev_no=p.LIFE_EXPECTANCY_RDS["severe_no_ecmo"],
        ly_sev_ecmo=p.LIFE_EXPECTANCY_RDS["severe_ecmo"],
        discount_rate=p.LIFE_EXPECTANCY_RDS["discount_rate"],
    )

    pop = p.DISPLAY["population_size"]
    total_cost_sds = sds_cost_per * pop
    total_cost_rds = rds_cost_per * pop
    total_ly_sds = sds_ly_per * pop
    total_ly_rds = rds_ly_per * pop
    icer = calc.calculate_icer(total_cost_rds, total_cost_sds, total_ly_rds, total_ly_sds)

    print(f"   SDS — Cost per case: {sds_cost_per:,.0f} CNY, Discounted life years per case: {sds_ly_per:.2f}")
    print(f"   RDS — Cost per case: {rds_cost_per:,.0f} CNY, Discounted life years per case: {rds_ly_per:.2f}")
    print(f"   ICER = {icer:,.0f} CNY/Discounted Life Year")

    wtp = p.DISPLAY["wtp_threshold"]
    print(f"\n   WTP threshold: {wtp:,} CNY/Life Year")
    if icer < 0:
        print("   >>> Conclusion: Rapid testing strategy [absolute advantage] — both cost-saving and life-saving")
    elif icer < wtp:
        print("   >>> Conclusion: Rapid testing strategies are cost-effective")
    else:
        print("   >>> Conclusion: Rapid testing strategy is not cost-effective")

    # ==================== 2. 概率敏感性分析 ====================
    print(f"\n2. Probabilistic Sensitivity Analysis (PSA)")
    print(f"   Monte Carlo simulation: {p.SIMULATION['n_iterations']:,} iterations")

    delta_costs, delta_lys, icers = calc.monte_carlo_psa(
        sds_params=p.SDS,
        rds_params=p.RDS,
        cost_treatment=p.COST_TREATMENT,
        cost_test={
            "SDS": p.COSTS["conventional_dx"],
            "RDS": p.COSTS["rapid_test"],
        },
        ly_sds=p.LIFE_EXPECTANCY_SDS,
        ly_rds=p.LIFE_EXPECTANCY_RDS,
        population_size=pop,
        n_iterations=p.SIMULATION["n_iterations"],
        random_seed=p.SIMULATION["random_seed"],
    )

    # 统计
    finite_icers = icers[np.isfinite(icers)]
    ci_lower = np.percentile(finite_icers, 2.5)
    ci_upper = np.percentile(finite_icers, 97.5)
    dominant = np.sum((delta_costs < 0) & (delta_lys > 0)) / len(delta_costs)

    print(f"   ICER 95% CI: [{ci_lower:,.0f}, {ci_upper:,.0f}] CNY/Discounted Life Year")
    print(f"   Absolute Advantage Ratio: {dominant:.1%}")

    # ==================== 3. 绘图 ====================
    print(f"\n3. Generating figures...")

    fig1 = pl.plot_icer_scatter(delta_costs, delta_lys, wtp_threshold=wtp)
    pl.plt.show()
    fig1.savefig("icer_scatter.png", dpi=150)
    print("   → icer_scatter.png is saved")

    fig2 = pl.plot_ceac(icers, threshold=wtp)
    pl.plt.show()
    fig2.savefig("ceac_curve.png", dpi=150)
    print("   → ceac_curve.png is saved")

    print("\n=== Analysis Completed ===")


if __name__ == "__main__":
    import numpy as np  # main.py 自己也需要 numpy
    main()