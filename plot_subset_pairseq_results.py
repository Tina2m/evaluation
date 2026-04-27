from pathlib import Path

import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent

R1_MATCH_LOG = SCRIPT_DIR / "subset_pairseq_R1_matches.log"
R1_MISSING_LOG = SCRIPT_DIR / "subset_pairseq_R1_missing_in_large.log"
R2_MATCH_LOG = SCRIPT_DIR / "subset_pairseq_R2_matches.log"
R2_MISSING_LOG = SCRIPT_DIR / "subset_pairseq_R2_missing_in_large.log"

OUTPUT_PLOT = SCRIPT_DIR / "subset_pairseq_match_missing_barplot.png"


def count_match_statuses(log_path: Path) -> dict[str, int]:
    counts = {
        "IDENTICAL": 0,
        "SAME_SEQUENCE": 0,
        "FOUND_DIFFERENT": 0,
    }
    with open(log_path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("STATUS: "):
                status = line.split("STATUS: ", 1)[1]
                if status in counts:
                    counts[status] += 1
    return counts


def count_missing(log_path: Path) -> int:
    with open(log_path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("Missing reads (count=") and line.endswith("):"):
                return int(line.split("count=")[1].split(")")[0])

    # Fallback if the summary line is missing.
    count = 0
    with open(log_path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("@"):
                count += 1
    return count


def add_labels(ax, bars):
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + max(1, height * 0.01),
            str(int(height)),
            ha="center",
            va="bottom",
            fontsize=10,
        )


def add_stacked_labels(ax, bars):
    for bar in bars:
        height = bar.get_height()
        if height <= 0:
            continue

        y = bar.get_y() + height / 2
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y,
            str(int(height)),
            ha="center",
            va="center",
            fontsize=9,
            color="black",
            fontweight="bold",
        )


def main():
    r1_status = count_match_statuses(R1_MATCH_LOG)
    r1_missing = count_missing(R1_MISSING_LOG)
    r2_status = count_match_statuses(R2_MATCH_LOG)
    r2_missing = count_missing(R2_MISSING_LOG)

    samples = ["R1", "R2"]
    missing = [r1_missing, r2_missing]
    identical = [r1_status["IDENTICAL"], r2_status["IDENTICAL"]]
    same_sequence = [r1_status["SAME_SEQUENCE"], r2_status["SAME_SEQUENCE"]]
    found_different = [r1_status["FOUND_DIFFERENT"], r2_status["FOUND_DIFFERENT"]]
    total_matches = [
        identical[0] + same_sequence[0] + found_different[0],
        identical[1] + same_sequence[1] + found_different[1],
    ]

    x = [0, 1]
    width = 0.36

    fig, ax = plt.subplots(figsize=(9, 6))

    identical_bars = ax.bar(
        [value - width / 2 for value in x],
        identical,
        width,
        label="IDENTICAL",
        color="#2a9d8f",
    )
    same_sequence_bars = ax.bar(
        [value - width / 2 for value in x],
        same_sequence,
        width,
        bottom=identical,
        label="SAME_SEQUENCE",
        color="#e9c46a",
    )
    found_different_bars = ax.bar(
        [value - width / 2 for value in x],
        found_different,
        width,
        bottom=[identical[i] + same_sequence[i] for i in range(len(x))],
        label="FOUND_DIFFERENT",
        color="#457b9d",
    )
    missing_bars = ax.bar(
        [value + width / 2 for value in x],
        missing,
        width,
        label="Missing",
        color="#e76f51",
    )

    ax.set_title("PairSeq Subset Check: Match Statuses and Missing Reads")
    ax.set_xlabel("Read Set")
    ax.set_ylabel("Number of Reads")
    ax.set_xticks(x)
    ax.set_xticklabels(samples)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    add_stacked_labels(ax, identical_bars)
    add_stacked_labels(ax, same_sequence_bars)
    add_stacked_labels(ax, found_different_bars)
    add_labels(ax, missing_bars)
    for idx, total in enumerate(total_matches):
        ax.text(
            x[idx] - width / 2,
            total + max(1, total * 0.01),
            str(int(total)),
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    fig.tight_layout()
    fig.savefig(OUTPUT_PLOT, dpi=300)
    plt.show()

    print(f"R1 IDENTICAL: {r1_status['IDENTICAL']}")
    print(f"R1 SAME_SEQUENCE: {r1_status['SAME_SEQUENCE']}")
    print(f"R1 FOUND_DIFFERENT: {r1_status['FOUND_DIFFERENT']}")
    print(f"R1 matches total: {total_matches[0]}")
    print(f"R1 missing: {r1_missing}")
    print(f"R2 IDENTICAL: {r2_status['IDENTICAL']}")
    print(f"R2 SAME_SEQUENCE: {r2_status['SAME_SEQUENCE']}")
    print(f"R2 FOUND_DIFFERENT: {r2_status['FOUND_DIFFERENT']}")
    print(f"R2 matches total: {total_matches[1]}")
    print(f"R2 missing: {r2_missing}")
    print(f"Plot saved to: {OUTPUT_PLOT}")


if __name__ == "__main__":
    main()
