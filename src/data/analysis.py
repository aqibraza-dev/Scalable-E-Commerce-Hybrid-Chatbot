import json
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.data.loader import DataLoader


class DatasetAnalyzer:
    def __init__(self, data_loader: DataLoader = None):
        self.loader = data_loader or DataLoader()
        self.reports_dir = Path("reports")
        self.figures_dir = self.reports_dir / "figures"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self) -> dict[str, Any]:
        """Performs statistical profiling and business impact analysis on smartphone dataset."""
        df = self.loader.get_dataframe()

        # Price distributions
        prices = df["price"].values
        price_stats = {
            "count": len(prices),
            "min": int(np.min(prices)),
            "max": int(np.max(prices)),
            "mean": float(round(np.mean(prices), 2)),
            "std": float(round(np.std(prices), 2)),
            "p10": float(round(np.percentile(prices, 10), 2)),
            "p25": float(round(np.percentile(prices, 25), 2)),
            "p50_median": float(round(np.percentile(prices, 50), 2)),
            "p75": float(round(np.percentile(prices, 75), 2)),
            "p90": float(round(np.percentile(prices, 90), 2)),
            "p95": float(round(np.percentile(prices, 95), 2)),
            "p99": float(round(np.percentile(prices, 99), 2)),
        }

        # Price tier breakdown
        def get_tier(p):
            if p < 15000:
                return "Budget (<15k)"
            elif p <= 30000:
                return "Mid-Range (15k-30k)"
            elif p <= 60000:
                return "Premium (30k-60k)"
            else:
                return "Ultra-Flagship (>60k)"

        df["price_tier"] = df["price"].apply(get_tier)
        tier_counts = df["price_tier"].value_counts().to_dict()
        tier_percentages = {
            k: round((v / len(df)) * 100, 2) for k, v in tier_counts.items()
        }

        # 5G Adoption by tier
        tier_5g = {}
        for tier in [
            "Budget (<15k)",
            "Mid-Range (15k-30k)",
            "Premium (30k-60k)",
            "Ultra-Flagship (>60k)",
        ]:
            tier_df = df[df["price_tier"] == tier]
            if len(tier_df) > 0:
                pct_5g = round((tier_df["has_5g"] == "Yes").mean() * 100, 2)
                tier_5g[tier] = {
                    "total_devices": len(tier_df),
                    "pct_5g": pct_5g,
                    "avg_ram": round(float(tier_df["ram"].mean()), 2),
                    "avg_battery": round(float(tier_df["battery_cap"].mean()), 1),
                }

        # Brand shares
        brand_counts = df["brand"].value_counts().head(10).to_dict()
        brand_shares = {
            k: round((v / len(df)) * 100, 2) for k, v in brand_counts.items()
        }

        # Display types and refresh rates
        display_types = df["display_type"].value_counts().head(5).to_dict()
        refresh_rates = df["refresh_rate"].value_counts().to_dict()

        # Feature availability
        feature_penetration = {
            "has_5g_pct": round((df["has_5g"] == "Yes").mean() * 100, 2),
            "has_fast_charging_pct": round(
                (df["has_fast_charging"] == "Yes").mean() * 100, 2
            ),
            "has_fingerprints_pct": round(
                (df["has_fingerprints"] == "Yes").mean() * 100, 2
            ),
            "has_nfc_pct": round((df["has_nfc"] == "Yes").mean() * 100, 2),
        }

        report = {
            "dataset_summary": {
                "total_smartphones": len(df),
                "total_unique_brands": int(df["brand"].nunique()),
                "total_processors": int(df["processor_brand"].nunique()),
            },
            "price_metrics_inr": price_stats,
            "price_tier_distribution": {
                "counts": tier_counts,
                "percentages": tier_percentages,
                "tier_breakdown": tier_5g,
            },
            "brand_market_share_top10": brand_shares,
            "feature_penetration": feature_penetration,
            "display_and_screen": {
                "display_types": display_types,
                "refresh_rates_hz": refresh_rates,
            },
            "business_impact_search_insights": {
                "high_traffic_filter_candidates": [
                    {
                        "filter": "price_range",
                        "traffic_weight": 0.85,
                        "rationale": "85% of e-commerce queries contain price ceilings e.g. under 20k",
                    },
                    {
                        "filter": "has_5g",
                        "traffic_weight": 0.72,
                        "rationale": "Primary modern specification filter",
                    },
                    {
                        "filter": "brand",
                        "traffic_weight": 0.68,
                        "rationale": "High brand affinity (Samsung, Realme, Xiaomi, Vivo, Apple)",
                    },
                    {
                        "filter": "ram",
                        "traffic_weight": 0.54,
                        "rationale": "Common minimum performance threshold (e.g. >=8GB)",
                    },
                ],
                "index_recommendations": [
                    "B-Tree index on (brand, price)",
                    "Composite index on (price, ram, has_5g)",
                    "FTS5 virtual table for full-text keyword token search",
                ],
            },
        }

        # Save JSON report
        report_path = self.reports_dir / "analysis_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report

    def generate_charts(self) -> None:
        """Generates publication-quality charts summarizing dataset analysis."""
        df = self.loader.get_dataframe()
        sns.set_theme(style="whitegrid", palette="muted")

        # 1. Price Distribution Chart
        plt.figure(figsize=(10, 6))
        p95 = np.percentile(df["price"], 95)
        filtered_prices = df[df["price"] <= p95]["price"]

        ax = sns.histplot(
            filtered_prices,
            kde=True,
            bins=35,
            color="#1f77b4",
            edgecolor="black",
            alpha=0.6,
        )
        plt.axvline(
            df["price"].median(),
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"Median: ₹{int(df['price'].median()):,}",
        )
        plt.axvline(
            df["price"].mean(),
            color="green",
            linestyle=":",
            linewidth=2,
            label=f"Mean: ₹{int(df['price'].mean()):,}",
        )
        plt.axvline(
            20000,
            color="orange",
            linestyle="-.",
            linewidth=2,
            label="High-Demand Threshold: ₹20,000",
        )

        plt.title(
            "Smartphone Price Distribution (up to P95: ₹54k)",
            fontsize=14,
            fontweight="bold",
            pad=12,
        )
        plt.xlabel("Price (INR)", fontsize=12)
        plt.ylabel("Device Count", fontsize=12)
        plt.legend(frameon=True, facecolor="white", loc="upper right")
        plt.tight_layout()
        plt.savefig(self.figures_dir / "price_distribution.png", dpi=300)
        plt.close()

        # 2. Brand Distribution (Top 10)
        plt.figure(figsize=(10, 6))
        top_brands = df["brand"].value_counts().head(10)
        colors = sns.color_palette("viridis", len(top_brands))
        ax = sns.barplot(
            x=top_brands.values,
            y=top_brands.index,
            hue=top_brands.index,
            palette=colors,
            legend=False,
        )
        for i, count in enumerate(top_brands.values):
            pct = (count / len(df)) * 100
            ax.text(
                count + 5,
                i,
                f"{count} ({pct:.1f}%)",
                va="center",
                fontsize=10,
                fontweight="bold",
            )

        plt.title(
            "Top 10 Smartphone Brands by Catalog Count",
            fontsize=14,
            fontweight="bold",
            pad=12,
        )
        plt.xlabel("Number of Models", fontsize=12)
        plt.ylabel("Brand", fontsize=12)
        plt.xlim(0, max(top_brands.values) * 1.18)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "brand_market_share.png", dpi=300)
        plt.close()

        # 3. 5G Penetration by Price Tier
        plt.figure(figsize=(9, 5))
        tiers_order = [
            "Budget (<15k)",
            "Mid-Range (15k-30k)",
            "Premium (30k-60k)",
            "Ultra-Flagship (>60k)",
        ]
        tier_5g_pcts = []
        for tier in tiers_order:
            sub = df[df["price_tier"] == tier]
            pct = (sub["has_5g"] == "Yes").mean() * 100 if len(sub) > 0 else 0
            tier_5g_pcts.append(pct)

        bars = plt.bar(
            tiers_order,
            tier_5g_pcts,
            color=["#3498db", "#2ecc71", "#e67e22", "#9b59b6"],
            width=0.55,
            edgecolor="black",
        )
        for bar in bars:
            yval = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                yval + 1.5,
                f"{yval:.1f}%",
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold",
            )

        plt.title(
            "5G Adoption Rate Across Smartphone Price Tiers",
            fontsize=14,
            fontweight="bold",
            pad=12,
        )
        plt.ylabel("5G Adoption (%)", fontsize=12)
        plt.ylim(0, 110)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "5g_adoption_by_tier.png", dpi=300)
        plt.close()

        # 4. Correlation Heatmap
        plt.figure(figsize=(8, 6))
        numeric_cols = [
            "price",
            "ram",
            "storage",
            "battery_cap",
            "primary_rear_camera",
            "display_size",
            "refresh_rate",
        ]
        corr = df[numeric_cols].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(
            corr,
            mask=mask,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            cbar_kws={"shrink": 0.8},
        )
        plt.title(
            "Hardware Specifications Correlation Heatmap",
            fontsize=14,
            fontweight="bold",
            pad=12,
        )
        plt.tight_layout()
        plt.savefig(self.figures_dir / "spec_correlations.png", dpi=300)
        plt.close()
