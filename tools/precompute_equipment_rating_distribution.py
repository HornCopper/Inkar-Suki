from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_JSON = ROOT / "src" / "assets" / "source" / "jx3" / "equipment_rating_distribution.json"
DEFAULT_OUTPUT_DIR = ROOT / "src" / "assets" / "image" / "jx3" / "equipment_rating" / "distribution"
DEFAULT_COLOR_JSON = ROOT / "src" / "assets" / "source" / "jx3" / "equipment_rating_distribution_colors.json"

EPSILON = 1e-8

KUNGFU_IDS = {
    "冰心诀": 10081,
    "毒经": 10175,
    "紫霞功": 10014,
    "山海心诀": 10756,
    "幽罗引": 10821,
    "花间游": 10021,
    "北傲诀": 10464,
    "孤锋诀": 10698,
    "问水诀/山居剑意": 10144,
    "太玄经": 10615,
    "傲血战意": 10026,
    "惊羽诀": 10224,
    "分山劲": 10390,
    "隐龙诀": 10585,
    "天罗诡道": 10225,
    "凌海诀": 10533,
    "周天功": 10786,
    "莫问": 10447,
    "太虚剑意": 10015,
    "焚影圣诀": 10242,
    "笑尘诀": 10268,
    "无方": 10627,
    "易筋经": 10003,
}

DEFAULT_QUANTILE_DATA = [
    {"name": "冰心诀", "xL": 277, "q1": 356, "q2": 422.0, "q3": 509, "xR": 641},
    {"name": "毒经", "xL": 333, "q1": 411, "q2": 479.5, "q3": 561, "xR": 686},
    {"name": "紫霞功", "xL": 268, "q1": 346, "q2": 412.5, "q3": 495, "xR": 642},
    {"name": "山海心诀", "xL": 317, "q1": 397, "q2": 465.5, "q3": 556, "xR": 691},
    {"name": "幽罗引", "xL": 308, "q1": 390, "q2": 460.0, "q3": 543, "xR": 672},
    {"name": "花间游", "xL": 337, "q1": 420, "q2": 494.5, "q3": 591, "xR": 729},
    {"name": "北傲诀", "xL": 314, "q1": 400, "q2": 477.6, "q3": 570, "xR": 706},
    {"name": "孤锋诀", "xL": 352, "q1": 445, "q2": 525.5, "q3": 627, "xR": 771},
    {"name": "问水诀/山居剑意", "xL": 283, "q1": 368, "q2": 450.5, "q3": 553, "xR": 684},
    {"name": "太玄经", "xL": 343, "q1": 428, "q2": 499.5, "q3": 593, "xR": 736},
    {"name": "傲血战意", "xL": 281, "q1": 365, "q2": 434.5, "q3": 527, "xR": 657},
    {"name": "惊羽诀", "xL": 252, "q1": 344, "q2": 420.5, "q3": 518, "xR": 658},
    {"name": "分山劲", "xL": 337, "q1": 420, "q2": 493.5, "q3": 586, "xR": 714},
    {"name": "隐龙诀", "xL": 333, "q1": 414, "q2": 485.5, "q3": 579, "xR": 718},
    {"name": "天罗诡道", "xL": 283, "q1": 379, "q2": 469.5, "q3": 577, "xR": 723},
    {"name": "凌海诀", "xL": 351, "q1": 447, "q2": 527.0, "q3": 630, "xR": 783},
    {"name": "周天功", "xL": 289, "q1": 366, "q2": 432.5, "q3": 516, "xR": 652},
    {"name": "莫问", "xL": 318, "q1": 406, "q2": 478.5, "q3": 582, "xR": 728},
    {"name": "太虚剑意", "xL": 276, "q1": 377, "q2": 491.9, "q3": 599, "xR": 772},
    {"name": "焚影圣诀", "xL": 284, "q1": 375, "q2": 452.5, "q3": 551, "xR": 718},
    {"name": "笑尘诀", "xL": 310, "q1": 400, "q2": 483.0, "q3": 586, "xR": 727},
    {"name": "无方", "xL": 281, "q1": 374, "q2": 444.2, "q3": 535, "xR": 687},
    {"name": "易筋经", "xL": 320, "q1": 433, "q2": 531.5, "q3": 647, "xR": 806},
]


@dataclass
class NormalizedItem:
    name: str
    kungfu_id: int
    color: str
    x_l: float
    q1: float
    q2: float
    q3: float
    x_r: float
    z_l: float
    z1: float
    z2: float
    z3: float
    z_r: float


@dataclass
class FitResult(NormalizedItem):
    alpha: float
    beta: float
    mean: float
    variance: float
    fit_error: float
    fitted_q1: float
    fitted_q2: float
    fitted_q3: float
    curve: list[tuple[float, float]]


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return min(max(value, minimum), maximum)


def _load_input(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return DEFAULT_QUANTILE_DATA
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("input json must be a list")
    return data


def _load_color_config(path: Path) -> dict[str, str]:
    """Load kungfu-id keyed display colors used by the generated SVG charts."""
    with path.open("r", encoding="utf-8") as file:
        raw = json.load(file)
    if not isinstance(raw, dict):
        raise ValueError("color json must be an object")
    colors: dict[str, str] = {}
    for kungfu_id, item in raw.items():
        if not isinstance(item, dict):
            continue
        color = str(item.get("color") or "").strip()
        if color:
            colors[str(kungfu_id)] = color
    return colors


def normalize_quantiles(data: list[dict[str, Any]], colors: dict[str, str]) -> tuple[float, float, list[NormalizedItem]]:
    """Normalize q1/q2/q3 to the global [L, U] interval shared by all kungfus."""
    global_l = min(float(item["xL"]) for item in data)
    global_u = max(float(item["xR"]) for item in data)
    width = global_u - global_l
    if width <= 0:
        raise ValueError("global interval width must be positive")

    results = []
    for item in data:
        name = str(item["name"])
        kungfu_id = int(item.get("kungfu_id") or KUNGFU_IDS[name])
        x_l = float(item["xL"])
        q1 = float(item["q1"])
        q2 = float(item["q2"])
        q3 = float(item["q3"])
        x_r = float(item["xR"])
        results.append(
            NormalizedItem(
                name=name,
                kungfu_id=kungfu_id,
                color=str(item.get("color") or colors.get(str(kungfu_id)) or "#5f89b7"),
                x_l=x_l,
                q1=q1,
                q2=q2,
                q3=q3,
                x_r=x_r,
                z_l=(x_l - global_l) / width,
                z1=(q1 - global_l) / width,
                z2=(q2 - global_l) / width,
                z3=(q3 - global_l) / width,
                z_r=(x_r - global_l) / width,
            )
        )
    return global_l, global_u, results


def _log_beta(alpha: float, beta: float) -> float:
    return math.lgamma(alpha) + math.lgamma(beta) - math.lgamma(alpha + beta)


def beta_pdf(x: float, alpha: float, beta: float) -> float:
    safe_x = _clamp(x, 1e-5, 1 - 1e-5)
    return math.exp((alpha - 1) * math.log(safe_x) + (beta - 1) * math.log(1 - safe_x) - _log_beta(alpha, beta))


def _beta_continued_fraction(alpha: float, beta: float, x: float) -> float:
    max_iterations = 180
    fp_min = 1e-30
    qab = alpha + beta
    qap = alpha + 1
    qam = alpha - 1
    c = 1.0
    d = 1 - qab * x / qap
    if abs(d) < fp_min:
        d = fp_min
    d = 1 / d
    h = d

    for m in range(1, max_iterations + 1):
        m2 = 2 * m
        aa = m * (beta - m) * x / ((qam + m2) * (alpha + m2))
        d = 1 + aa * d
        if abs(d) < fp_min:
            d = fp_min
        c = 1 + aa / c
        if abs(c) < fp_min:
            c = fp_min
        d = 1 / d
        h *= d * c

        aa = -(alpha + m) * (qab + m) * x / ((alpha + m2) * (qap + m2))
        d = 1 + aa * d
        if abs(d) < fp_min:
            d = fp_min
        c = 1 + aa / c
        if abs(c) < fp_min:
            c = fp_min
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 3e-12:
            break
    return h


def beta_cdf(x: float, alpha: float, beta: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(
        math.lgamma(alpha + beta)
        - math.lgamma(alpha)
        - math.lgamma(beta)
        + alpha * math.log(x)
        + beta * math.log(1 - x)
    )
    if x < (alpha + 1) / (alpha + beta + 2):
        return bt * _beta_continued_fraction(alpha, beta, x) / alpha
    return 1 - bt * _beta_continued_fraction(beta, alpha, 1 - x) / beta


def beta_ppf(probability: float, alpha: float, beta: float) -> float:
    low = 0.0
    high = 1.0
    for _ in range(72):
        mid = (low + high) / 2
        if beta_cdf(mid, alpha, beta) < probability:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def _quantile_loss(alpha: float, beta: float, z1: float, z2: float, z3: float) -> float:
    return (
        (beta_ppf(0.25, alpha, beta) - z1) ** 2
        + (beta_ppf(0.50, alpha, beta) - z2) ** 2
        + (beta_ppf(0.75, alpha, beta) - z3) ** 2
    )


def fit_beta_from_quantiles(z1: float, z2: float, z3: float) -> tuple[float, float, float, tuple[float, float, float]]:
    """Fit alpha/beta in log space so both parameters stay positive."""
    targets = [_clamp(value, EPSILON, 1 - EPSILON) for value in (z1, z2, z3)]
    median = targets[1]
    iqr = max(targets[2] - targets[0], 1e-4)
    rough_variance = _clamp((iqr / 1.349) ** 2, 1e-5, median * (1 - median) * 0.95)
    concentration = max(median * (1 - median) / rough_variance - 1, 0.2)
    initial_alpha = max(median * concentration, 0.2)
    initial_beta = max((1 - median) * concentration, 0.2)

    def loss_at(point: tuple[float, float]) -> float:
        alpha = math.exp(point[0])
        beta = math.exp(point[1])
        if not math.isfinite(alpha) or not math.isfinite(beta) or alpha <= 0 or beta <= 0:
            return math.inf
        return _quantile_loss(alpha, beta, targets[0], targets[1], targets[2])

    simplex = [
        (math.log(initial_alpha), math.log(initial_beta)),
        (math.log(initial_alpha) + 0.26, math.log(initial_beta)),
        (math.log(initial_alpha), math.log(initial_beta) + 0.26),
    ]
    scored = [(point, loss_at(point)) for point in simplex]

    for _ in range(140):
        scored.sort(key=lambda item: item[1])
        best, good, worst = scored
        if abs(worst[1] - best[1]) < 1e-12:
            break
        centroid = ((best[0][0] + good[0][0]) / 2, (best[0][1] + good[0][1]) / 2)
        reflected_point = (centroid[0] + centroid[0] - worst[0][0], centroid[1] + centroid[1] - worst[0][1])
        reflected = (reflected_point, loss_at(reflected_point))

        if reflected[1] < best[1]:
            expanded_point = (
                centroid[0] + 2 * (reflected_point[0] - centroid[0]),
                centroid[1] + 2 * (reflected_point[1] - centroid[1]),
            )
            expanded = (expanded_point, loss_at(expanded_point))
            scored[2] = expanded if expanded[1] < reflected[1] else reflected
            continue

        if reflected[1] < good[1]:
            scored[2] = reflected
            continue

        contracted_point = (
            centroid[0] + 0.5 * (worst[0][0] - centroid[0]),
            centroid[1] + 0.5 * (worst[0][1] - centroid[1]),
        )
        contracted = (contracted_point, loss_at(contracted_point))
        if contracted[1] < worst[1]:
            scored[2] = contracted
            continue

        scored = [
            best,
            (
                (
                    best[0][0] + 0.5 * (good[0][0] - best[0][0]),
                    best[0][1] + 0.5 * (good[0][1] - best[0][1]),
                ),
                0,
            ),
            (
                (
                    best[0][0] + 0.5 * (worst[0][0] - best[0][0]),
                    best[0][1] + 0.5 * (worst[0][1] - best[0][1]),
                ),
                0,
            ),
        ]
        scored[1] = (scored[1][0], loss_at(scored[1][0]))
        scored[2] = (scored[2][0], loss_at(scored[2][0]))

    scored.sort(key=lambda item: item[1])
    alpha = math.exp(scored[0][0][0])
    beta = math.exp(scored[0][0][1])
    fitted = (
        beta_ppf(0.25, alpha, beta),
        beta_ppf(0.50, alpha, beta),
        beta_ppf(0.75, alpha, beta),
    )
    return alpha, beta, scored[0][1], fitted


def compute_beta_stats(alpha: float, beta: float) -> tuple[float, float]:
    mean = alpha / (alpha + beta)
    variance = alpha * beta / ((alpha + beta) ** 2 * (alpha + beta + 1))
    return mean, variance


def build_beta_curves(items: list[NormalizedItem]) -> list[FitResult]:
    results = []
    for item in items:
        alpha, beta, fit_error, fitted = fit_beta_from_quantiles(item.z1, item.z2, item.z3)
        mean, variance = compute_beta_stats(alpha, beta)
        curve = [(index / 179, beta_pdf(index / 179, alpha, beta)) for index in range(180)]
        results.append(
            FitResult(
                **item.__dict__,
                alpha=alpha,
                beta=beta,
                mean=mean,
                variance=variance,
                fit_error=fit_error,
                fitted_q1=fitted[0],
                fitted_q2=fitted[1],
                fitted_q3=fitted[2],
                curve=curve,
            )
        )
    return results


def _path_from_curve(
    curve: list[tuple[float, float]],
    *,
    width: float,
    height: float,
    left: float,
    top: float,
    max_density: float,
) -> str:
    points = []
    for index, (x_value, density) in enumerate(curve):
        x = left + x_value * width
        y = top + height - density / max_density * height
        command = "M" if index == 0 else "L"
        points.append(f"{command}{x:.2f},{y:.2f}")
    return " ".join(points)


def render_beta_chart(fit_results: list[FitResult], selected: FitResult) -> str:
    """Render one static SVG where selected kungfu is highlighted and all others are muted."""
    svg_width = 228
    svg_height = 146
    margin_left = 22
    margin_top = 14
    chart_width = 190
    chart_height = 76
    max_density = max(max(point[1] for point in item.curve) for item in fit_results) * 1.08

    grid_lines = []
    for tick in (0, 0.5, 1):
        x = margin_left + tick * chart_width
        grid_lines.append(f'<line x1="{x:.1f}" y1="{margin_top}" x2="{x:.1f}" y2="{margin_top + chart_height}" stroke="#edf2f6" stroke-width="1"/>')
        grid_lines.append(f'<text x="{x:.1f}" y="107" text-anchor="middle" font-size="9" font-weight="700" fill="#87929e">{tick:g}</text>')
    for tick in (0.25, 0.5, 0.75):
        y = margin_top + chart_height * tick
        grid_lines.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{margin_left + chart_width}" y2="{y:.1f}" stroke="#f1f5f8" stroke-width="1"/>')

    muted_paths = []
    highlighted_path = ""
    for item in fit_results:
        path = _path_from_curve(
            item.curve,
            width=chart_width,
            height=chart_height,
            left=margin_left,
            top=margin_top,
            max_density=max_density,
        )
        if item.kungfu_id == selected.kungfu_id:
            highlighted_path = f'<path d="{path}" fill="none" stroke="{item.color}" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round"/>'
        else:
            muted_paths.append(
                f'<path d="{path}" fill="none" stroke="#8aa0b3" stroke-width="1.05" stroke-linecap="round" stroke-linejoin="round" opacity="0.22"/>'
            )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">
  <rect width="{svg_width}" height="{svg_height}" rx="10" fill="#ffffff"/>
  <rect x="0.5" y="0.5" width="{svg_width - 1}" height="{svg_height - 1}" rx="9.5" fill="none" stroke="#edf2f6"/>
  <text x="216" y="17" text-anchor="end" font-size="10" font-weight="800" fill="{selected.color}">{selected.name}</text>
  {''.join(grid_lines)}
  <line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{margin_left + chart_width}" y2="{margin_top + chart_height}" stroke="#ccd8e2" stroke-width="1"/>
  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" stroke="#ccd8e2" stroke-width="1"/>
  {''.join(muted_paths)}
  {highlighted_path}
  <text x="12" y="132" font-size="11" font-weight="900" fill="#7a8590">均值 {selected.mean:.3f} · 标准差 {math.sqrt(selected.variance):.3f}</text>
</svg>
'''


def render_fit_table(fit_results: list[FitResult]) -> list[dict[str, Any]]:
    """Return a sortable parameter table for metadata consumers."""
    return [
        {
            "kungfu_id": item.kungfu_id,
            "name": item.name,
            "alpha": round(item.alpha, 8),
            "beta": round(item.beta, 8),
            "mean": round(item.mean, 8),
            "variance": round(item.variance, 10),
            "fitError": round(item.fit_error, 12),
        }
        for item in sorted(fit_results, key=lambda value: value.mean, reverse=True)
    ]


def _result_to_json(item: FitResult, image_name: str) -> dict[str, Any]:
    return {
        "kungfu_id": item.kungfu_id,
        "name": item.name,
        "image": f"distribution/{image_name}",
        "color": item.color,
        "alpha": round(item.alpha, 8),
        "beta": round(item.beta, 8),
        "mean": round(item.mean, 8),
        "variance": round(item.variance, 10),
        "fitError": round(item.fit_error, 12),
        "quantiles": {
            "xL": item.x_l,
            "q1": item.q1,
            "q2": item.q2,
            "q3": item.q3,
            "xR": item.x_r,
        },
        "normalizedQuantiles": {
            "zL": round(item.z_l, 8),
            "z1": round(item.z1, 8),
            "z2": round(item.z2, 8),
            "z3": round(item.z3, 8),
            "zR": round(item.z_r, 8),
        },
        "fittedQuantiles": {
            "q1": round(item.fitted_q1, 8),
            "q2": round(item.fitted_q2, 8),
            "q3": round(item.fitted_q3, 8),
        },
    }


def precompute_distribution(
    data: list[dict[str, Any]],
    output_json: Path,
    output_dir: Path,
    color_json: Path,
) -> dict[str, Any]:
    global_l, global_u, normalized = normalize_quantiles(data, _load_color_config(color_json))
    fit_results = build_beta_curves(normalized)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    items: dict[str, dict[str, Any]] = {}
    for item in fit_results:
        image_name = f"{item.kungfu_id}.svg"
        (output_dir / image_name).write_text(render_beta_chart(fit_results, item), encoding="utf-8")
        items[str(item.kungfu_id)] = _result_to_json(item, image_name)

    payload = {
        "version": 1,
        "title": "四参数 Beta 拟合：全局公共上下界归一化分布",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "color_config": str(color_json.relative_to(ROOT)).replace("\\", "/"),
        "global": {
            "L": global_l,
            "U": global_u,
            "axis": "normalized_beta_pdf",
            "note": "0 表示全体心法共同观测区间下界，1 表示共同观测区间上界。",
        },
        "items": items,
        "fitTable": render_fit_table(fit_results),
    }
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Precompute equipment rating DPS beta distribution charts.")
    parser.add_argument("--input", type=Path, default=None, help="Optional quantile JSON input. Defaults to embedded data.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--color-json", type=Path, default=DEFAULT_COLOR_JSON)
    args = parser.parse_args()

    payload = precompute_distribution(_load_input(args.input), args.output_json, args.output_dir, args.color_json)
    print(
        f"generated {len(payload['items'])} distribution charts -> "
        f"{args.output_dir.relative_to(ROOT)}; metadata -> {args.output_json.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
