# plot.py
import matplotlib.pyplot as plt
import numpy as np


def plot_icer_scatter(delta_costs, delta_lys, wtp_threshold=50000):
    """ICER Scatter Plot — Cost-Effectiveness Plane"""
    fig, ax = plt.subplots(figsize=(8, 6))

    # Draw a scatter plot
    ax.scatter(delta_lys, delta_costs, alpha=0.3, s=10, c='steelblue')

    # Draw reference line
    ax.axhline(y=0, color='black', linewidth=0.8)
    ax.axvline(x=0, color='black', linewidth=0.8)

    # Draw the WTP line (with a slope of wtp_threshold, only draw the first quadrant part)
    x_wtp = np.linspace(0, max(delta_lys) * 1.1, 100)
    ax.plot(x_wtp, wtp_threshold * x_wtp, 'r--', linewidth=1.5,
            label=f'WTP = {wtp_threshold:,} CNY/Life Year')

    # Label Quadrant
    ax.text(max(delta_lys) * 0.7, max(delta_costs) * 0.7, 'Higher cost\nBetter results', alpha=0.5)
    ax.text(min(delta_lys) * 0.7, max(delta_costs) * 0.7, 'Higher cost\nWorse results\n(Disadvantage)', alpha=0.5)
    ax.text(min(delta_lys) * 0.7, min(delta_costs) * 0.7, 'Lower cost\nWorse results', alpha=0.5)
    ax.text(max(delta_lys) * 0.7, min(delta_costs) * 0.7, 'Lower cost\nBetter results\n(Absolute Advantage)',
            alpha=0.5, fontweight='bold', color='darkgreen')

    # Absolute Advantage Ratio
    dominant = np.sum((delta_costs < 0) & (delta_lys > 0)) / len(delta_costs)

    ax.set_xlabel('Incremental Life Years (delta LY)')
    ax.set_ylabel('Incremental cost (delta C, CNY)')
    ax.set_title(f'ICER Scatter Plot (n={len(delta_costs)})\nAbsolute Advantage Ratio: {dominant:.1%}')
    ax.legend()

    plt.tight_layout()
    return fig


def plot_ceac(icers, wtp_range=None, threshold=50000):
    """Cost-Effectiveness Acceptability Curve"""
    if wtp_range is None:
        wtp_range = np.linspace(0, 200000, 200)

    # Remove inf
    finite_icers = icers[np.isfinite(icers)]

    probabilities = []
    for wtp in wtp_range:
        prob = np.mean(finite_icers < wtp)
        probabilities.append(prob)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(wtp_range, probabilities, 'b-', linewidth=2)
    ax.axvline(x=threshold, color='red', linestyle='--',
               label=f'Current WTP = {threshold:,} CNY')
    ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)

    ax.set_xlabel('Willingness-to-pay threshold (CNY/Life Year)')
    ax.set_ylabel('The Probability of RDS Being Accepted')
    ax.set_title('Cost-Effectiveness Acceptability Curve (CEAC)')
    ax.legend()
    ax.grid(alpha=0.3)

    # Indicate the probability under the current WTP
    prob_at_threshold = np.mean(finite_icers < threshold)
    ax.annotate(f'{prob_at_threshold:.1%}',
                xy=(threshold, prob_at_threshold),
                xytext=(threshold + 10000, prob_at_threshold + 0.05),
                arrowprops=dict(arrowstyle='->'))

    plt.tight_layout()
    return fig
