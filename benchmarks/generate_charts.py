import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def generate_benchmark_charts():
    reports_dir = Path("reports")
    figures_dir = reports_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    json_path = reports_dir / "benchmark_results.json"
    if not json_path.exists():
        print(f"Error: {json_path} not found. Run run_benchmarks.py first.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pure = data["pure_llm_baseline"]
    hybrid = data["hybrid_architecture"]
    search = data["search_engine_performance"]
    fin = data["one_million_user_financial_impact"]

    sns.set_theme(style="whitegrid", palette="muted")

    # ============================================================
    # Chart 1: P50, P90, P95, P99 Latency Comparison
    # ============================================================
    plt.figure(figsize=(10, 6))
    percentiles = ["P50", "P90", "P95", "P99", "Mean"]
    pure_vals = [
        pure["latency_p50_ms"],
        pure["latency_p90_ms"],
        pure["latency_p95_ms"],
        pure["latency_p99_ms"],
        pure["latency_mean_ms"],
    ]
    hybrid_vals = [
        hybrid["latency_p50_ms"],
        hybrid["latency_p90_ms"],
        hybrid["latency_p95_ms"],
        hybrid["latency_p99_ms"],
        hybrid["latency_mean_ms"],
    ]

    x = np.arange(len(percentiles))
    width = 0.35

    rects1 = plt.bar(
        x - width / 2,
        pure_vals,
        width,
        label="Pure LLM Pipeline",
        color="#e74c3c",
        edgecolor="black",
        alpha=0.85,
    )
    rects2 = plt.bar(
        x + width / 2,
        hybrid_vals,
        width,
        label="Hybrid Architecture",
        color="#2ecc71",
        edgecolor="black",
        alpha=0.85,
    )

    for rect in rects1:
        h = rect.get_height()
        plt.text(
            rect.get_x() + rect.get_width() / 2.0,
            h + 0.5,
            f"{h:.1f}ms",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    for rect in rects2:
        h = rect.get_height()
        plt.text(
            rect.get_x() + rect.get_width() / 2.0,
            h + 0.5,
            f"{h:.1f}ms",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#1b4f72",
        )

    plt.ylabel(
        "Latency (Milliseconds - lower is better)", fontsize=12, fontweight="bold"
    )
    plt.title(
        f"Latency Distribution: Pure LLM vs Hybrid Architecture (P95 Speedup: {pure['latency_p95_ms'] / max(0.1, hybrid['latency_p95_ms']):.1f}x)",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    plt.xticks(x, percentiles, fontsize=11, fontweight="bold")
    plt.ylim(0, max(pure_vals) * 1.22)
    plt.legend(frameon=True, facecolor="white", loc="upper left", fontsize=11)
    plt.tight_layout()
    plt.savefig(figures_dir / "latency_p95_comparison.png", dpi=300)
    plt.close()
    print("  -> Saved latency_p95_comparison.png")

    # ============================================================
    # Chart 2: 1M User Scale: Cost & Token Savings Curve
    # ============================================================
    plt.figure(figsize=(10, 6))
    user_scales = np.array(
        [10_000, 50_000, 100_000, 250_000, 500_000, 750_000, 1_000_000]
    )
    scale_labels = ["10k", "50k", "100k", "250k", "500k", "750k", "1M"]

    # Cost in USD
    cost_per_query_pure = pure["cost_usd"] / pure["total_queries"]
    cost_per_query_hybrid = hybrid["cost_usd"] / hybrid["total_queries"]

    pure_costs = user_scales * cost_per_query_pure
    hybrid_costs = user_scales * cost_per_query_hybrid
    savings = pure_costs - hybrid_costs

    plt.plot(
        scale_labels,
        pure_costs,
        marker="o",
        linewidth=2.5,
        color="#c0392b",
        label="Pure LLM Monthly Spend ($)",
    )
    plt.plot(
        scale_labels,
        hybrid_costs,
        marker="s",
        linewidth=2.5,
        color="#27ae60",
        label="Hybrid System Spend ($)",
    )
    plt.fill_between(
        scale_labels,
        hybrid_costs,
        pure_costs,
        color="#2ecc71",
        alpha=0.25,
        label=f"Net Savings: ₹{fin['net_monthly_savings_inr']:,.0f}/mo ($ {fin['net_monthly_savings_usd']:,.0f})",
    )

    for i, txt in enumerate(savings):
        if i in [2, 4, 6]:
            plt.annotate(
                f"+${txt:,.0f} saved",
                (scale_labels[i], hybrid_costs[i]),
                textcoords="offset points",
                xytext=(0, 20),
                ha="center",
                fontsize=9,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.6),
            )

    plt.title(
        "Cost Scaling Comparison Across Monthly Active Users",
        fontsize=14,
        fontweight="bold",
        pad=12,
    )
    plt.xlabel("Monthly Active Queries / Users", fontsize=12, fontweight="bold")
    plt.ylabel("Monthly Operating Spend (USD)", fontsize=12, fontweight="bold")
    plt.legend(frameon=True, facecolor="white", loc="upper left", fontsize=11)
    plt.tight_layout()
    plt.savefig(figures_dir / "token_and_cost_savings.png", dpi=300)
    plt.close()
    print("  -> Saved token_and_cost_savings.png")

    # ============================================================
    # Chart 3: Query Routing Breakdown (Donut Chart)
    # ============================================================
    plt.figure(figsize=(9, 7))
    tier_counts = hybrid.get("tier_breakdown", {})
    labels = []
    sizes = []
    colors_map = {
        "TIER_0_GUARDRAIL_BLOCKED": ("Security Blocked (Tier 0)", "#e74c3c"),
        "TIER_1_EXACT_CACHE": ("Exact Cache Hit (Tier 1)", "#2ecc71"),
        "TIER_2_SEMANTIC_CACHE": ("Semantic Cache Hit (Tier 2)", "#3498db"),
        "TIER_3_TYPICAL_BOT": ("Typical Deterministic Bot (Tier 3)", "#f39c12"),
        "TIER_4_LLM_RAG": ("LLM RAG Engine (Tier 4)", "#9b59b6"),
    }

    tier_labels = []
    tier_sizes = []
    tier_colors = []

    for k, count in tier_counts.items():
        if count > 0:
            name, col = colors_map.get(k, (k, "#95a5a6"))
            tier_labels.append(name)
            tier_sizes.append(count)
            tier_colors.append(col)

    explode = [0.03] * len(tier_sizes)

    wedges, texts, autotexts = plt.pie(
        tier_sizes,
        explode=explode,
        labels=tier_labels,
        colors=tier_colors,
        autopct="%1.1f%%",
        pctdistance=0.75,
        startangle=140,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
    )

    for autotext in autotexts:
        autotext.set_color("black")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(10)

    for text in texts:
        text.set_fontsize(10)
        text.set_fontweight("bold")

    zero_token_pct = hybrid["token_reduction_pct"]
    plt.title(
        f"Hybrid Architecture Traffic Routing Breakdown\n(Zero-Token Queries: {zero_token_pct}%)",
        fontsize=14,
        fontweight="bold",
        pad=14,
    )
    plt.tight_layout()
    plt.savefig(figures_dir / "query_routing_breakdown.png", dpi=300)
    plt.close()
    print("  -> Saved query_routing_breakdown.png")

    # ============================================================
    # Chart 4: Search Engine Scalability & Throughput (QPS)
    # ============================================================
    plt.figure(figsize=(9, 5))
    metrics_names = ["P50 (Median)", "P90", "P95", "P99", "Mean"]
    lat_vals = [
        search["latency_p50_ms"],
        search["latency_p90_ms"],
        search["latency_p95_ms"],
        search["latency_p99_ms"],
        search["latency_mean_ms"],
    ]

    bars = plt.bar(
        metrics_names,
        lat_vals,
        color=["#1abc9c", "#16a085", "#2980b9", "#8e44ad", "#34495e"],
        width=0.55,
        edgecolor="black",
    )
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 0.05,
            f"{yval:.2f}ms",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.ylabel("Latency (Milliseconds)", fontsize=12, fontweight="bold")
    plt.title(
        f"Product Search Engine Latency Profile (Throughput: {search['qps']} QPS)",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    plt.ylim(0, max(lat_vals) * 1.3)
    plt.tight_layout()
    plt.savefig(figures_dir / "cache_efficiency_curve.png", dpi=300)
    plt.close()
    print("  -> Saved cache_efficiency_curve.png")


if __name__ == "__main__":
    generate_benchmark_charts()
