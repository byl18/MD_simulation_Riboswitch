import re
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = ['Nimbus Roman']  
mpl.rcParams['font.weight'] = 'bold'  
mpl.rcParams['font.size'] = 20

CYCLE_RE = re.compile(r"^cycle(\d+)$")
CV_LINE_RE = re.compile(r"\bcv\b\s+([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")


def parse_first_cv(cv_ranked_path: Path) -> float:
    """
    Read the first non-empty line of cv_ranked.log and extract the cv value.
    Expected line format like:
      replica 1 frame 195 cv 0.08154406048813752
    """
    with cv_ranked_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = CV_LINE_RE.search(line)
            if not m:
                raise ValueError(f"Cannot find 'cv <number>' in first line: {line}")
            return float(m.group(1))
    raise ValueError("cv_ranked.log has no non-empty lines")


def main():
    ap = argparse.ArgumentParser(
        description="Extract the first cv value from each cycle*/summary/cv_ranked.log and plot vs cycle."
    )
    ap.add_argument(
        "trial_dir",
        type=Path,
        help="Path to trial directory (contains cycle000, cycle001, ...), e.g. /.../trial001",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default='./cv_vs_cycle.png',
        help="Output image path (e.g. cv_vs_cycle.png). If not set, show interactively.",
    )
    ap.add_argument(
        "--title",
        default="First cv in cv_ranked.log vs cycle",
        help="Plot title",
    )
    args = ap.parse_args()

    trial_dir: Path = args.trial_dir
    if not trial_dir.is_dir():
        raise SystemExit(f"Not a directory: {trial_dir}")

    points = []  # list of (cycle_int, cv_float)

    for child in sorted(trial_dir.iterdir()):
        if not child.is_dir():
            continue
        m = CYCLE_RE.match(child.name)
        if not m:
            continue
        cycle_idx = int(m.group(1))
        cv_path = child / "summary" / "cv_ranked.log"
        if not cv_path.exists():
            # 没有就跳过（也可以改成报错）
            print(f"[WARN] missing: {cv_path}")
            continue

        try:
            cv_val = parse_first_cv(cv_path)
        except Exception as e:
            print(f"[WARN] failed to parse {cv_path}: {e}")
            continue

        points.append((cycle_idx, cv_val))

    if not points:
        raise SystemExit("No valid cv_ranked.log found / parsed.")

    # sort by cycle
    points.sort(key=lambda x: x[0])
    cycles = [p[0] for p in points]
    cvs = [p[1] for p in points]
    plt.figure()
    plt.plot(cycles, cvs, marker="o")
    plt.xlabel("Cycle", fontweight = 'bold')
    plt.ylabel("Top CV value", fontweight = 'bold')
    plt.title(args.title, fontweight = 'bold', pad = 20)
    plt.grid(True, alpha=0.3)
    if args.out is None:
        plt.show()
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(args.out, dpi=200, bbox_inches="tight")
        print(f"Saved: {args.out}")


if __name__ == "__main__":
    main()
