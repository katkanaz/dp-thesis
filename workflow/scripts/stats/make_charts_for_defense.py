import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

import plotly.graph_objects as go


SATURATED_COLORS = [
    "#E9C46A",
    "#F4A261",
    "#7EBDC2",
    "#94B2DB",
    "#C7D66D",
    "#D2B2CD",
    "#8DB580",
    "#A4B2B7"
]


def load_stats(json_path: str) -> Dict[str, Any]:
    """Load statistics from JSON file."""
    with open(json_path, "r") as f:
        return json.load(f)



def plot_motif_matches_per_sugar(
    motif_matches: Dict[str, int], output_dir: str
) -> None:
    """Doughnut chart: Number of motif matches per sugar."""
    sugars = list(motif_matches.keys())
    counts = list(motif_matches.values())

    # Create custom text labels with sugar name, percentage and count
    text_labels = [
        f"<b>{sugar}</b><br>{count}"
        for sugar, count in zip(sugars, counts)
    ]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=sugars,
                values=counts,
                hole=0.5,
                marker=dict(colors=SATURATED_COLORS[:len(sugars)], line=dict(color="white", width=2)),
                text=text_labels,
                textposition="auto",
                textfont=dict(size=27, color="black"),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
                showlegend=False,
            )
        ]
    )

    fig.update_layout(
        font=dict(size=18),
        height=800,
        width=800,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    fig.write_html(
        os.path.join(output_dir, "motif_matches_per_sugar.html")
    )

    fig.write_image(
        os.path.join(output_dir, "sugars.svg")
    )


def create_bar_graph(output_dir: str) -> None:
    fig = go.Figure(go.Bar(
        y = [ "After filtering", "W/o unsupported<br>alternative<br>conformations", "With ligands", "Containing sugars", "PDB mirror<sup>*</sup>" ],
        x = [ 7412, 11068, 11090, 23714, 250059 ],
        orientation="h",
        text = [ "<b>7 412</b>", "<b>11 068</b>", "<b>11 090</b>", "<b>23 714</b>", "<b>250 059</b>" ],
        textposition=["outside", "outside", "outside", "outside", "inside"],
        texttemplate="%{text}",
        textfont=dict(size=21),
        marker=dict(color="#F4A261")))
    fig.update_layout(
        yaxis = {
            "title": {
                "text": "Total structures",
                "font": dict(size=25, weight=600),
                "standoff": 30
            },
            "tickfont": dict(size=20),
            "ticklabelstandoff": 10
        },
        xaxis = {
            "tickfont": dict(size=17),
            "tickformat": " d"
        },
        font=dict(size=14),
        height=600,
        width=1300,
        margin=dict(l=50, r=0, t=0, b=0),
    )

    fig.write_html(
        os.path.join(output_dir, "funnel.html")
    )

    fig.write_image(
        os.path.join(output_dir, "pre-processed.svg")
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate statistics visualizations from JSON data"
    )
    parser.add_argument(
        "preproc_file", help="Path to the JSON file containing preprocessing statistics"
    )
    parser.add_argument(
        "results_file", help="Path to the JSON file containing results statistics"
    )
    parser.add_argument(
        "-o",
        "--output",
        default=".",
        help="Output directory for charts (default: current directory)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.preproc_file):
        print(f"Error: Preprocessing JSON file not found: {args.preproc_file}")
        return

    if not os.path.exists(args.results_file):
        print(f"Error: Results JSON file not found: {args.results_file}")
        return

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading results statistics from {args.results_file}...")
    results = load_stats(args.results_file)


    print("Generating charts...")


    if "motif_matches_per_sugar" in results:
        plot_motif_matches_per_sugar(
            results["motif_matches_per_sugar"], str(output_dir)
        )
        print("Motif matches per sugar chart saved")

    create_bar_graph(str(output_dir))


    print(f"\nAll charts saved to: {output_dir.absolute()}")


if __name__ == "__main__":
    main()

