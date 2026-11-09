"""Run representative SkillEvo-GEE requests through the public CLI entry point."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "skillevo.py"


@dataclass(frozen=True)
class Case:
    case_id: str
    user_request: str


@dataclass(frozen=True)
class Expectation:
    expected_route: str
    description: str


CASES = (
    Case(
        "image_resampling",
        "使用已发布且经过验证的影像重采样流程，对其中的固定 Landsat 8 影像执行"
        "原始影像与 bicubic 重采样影像对比，并返回小区域统计审计结果。",
    ),
    Case(
        "water_area",
        "使用 GEE 分析青海湖 2020-01 至 2022-12 的月度水域面积变化，"
        "优先使用已发布的水体知识流程，输出面积时间序列图，不导出文件。",
    ),
    Case(
        "wind_csv",
        "使用 ERA5 计算北京市行政区 2021 年逐月平均风速，输出时间序列，"
        "并将日期和区域平均风速导出为 CSV。",
    ),
    Case(
        "drought_spei",
        "使用 CHIRPS 降水和 TerraClimate PET 分析宁夏 2018-2022 年月尺度干旱变化，"
        "计算标准化水量平衡，显示 2022 年 7 月结果并导出 GeoTIFF。",
    ),
    Case(
        "evi_phenology",
        "使用 MODIS EVI 分析成都市周边 2020 年植被物候，构建滞后 EVI，"
        "依据百分位阈值分类生长阶段，并显示分类时间序列。",
    ),
    Case(
        "soil_salinity",
        "使用当前已发布知识制作印度指定研究区的土壤盐分专题图，"
        "用 MOD44W 排除水体，并显示盐分等级图例。研究区资产暂未提供，请保留为待确认输入。",
    ),
    Case(
        "water_plus_fish_forecast",
        "分析鄱阳湖 2015-2022 年水域面积变化，并进一步预测 2035 年鱼类种群数量。"
        "输出水域时间序列和鱼类数量预测表。",
    ),
    Case(
        "mars_radar_volume",
        "分析火星奥林匹斯山地下冰的雷达剖面，并根据 SHARAD 数据生成三维地下冰体模型。",
    ),
)

# Test-only oracle. These values are never included in the Hermes request.
EXPECTATIONS = {
    "image_resampling": Expectation(
        "matched", "Verified Landsat bicubic-resampling and bounded-statistics workflow."
    ),
    "water_area": Expectation(
        "matched", "Water extraction and monthly area time series with optional presentation."
    ),
    "wind_csv": Expectation(
        "matched", "ERA5 wind-speed derivation with optional CSV export."
    ),
    "drought_spei": Expectation(
        "matched", "CHIRPS and TerraClimate monthly water-balance drought analysis."
    ),
    "evi_phenology": Expectation(
        "matched", "MODIS EVI phenology classification."
    ),
    "soil_salinity": Expectation(
        "matched", "Soil-salinity visualization with optional legend and map layers."
    ),
    "water_plus_fish_forecast": Expectation(
        "partial", "Published water-area analysis plus an unsupported ecological forecast."
    ),
    "mars_radar_volume": Expectation(
        "unmatched", "Planetary radar sounding and 3D subsurface reconstruction."
    ),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run matched, partial, and unmatched requests through SkillEvo-GEE."
    )
    parser.add_argument("--list", action="store_true", help="List cases without running Hermes")
    parser.add_argument(
        "--case",
        action="append",
        dest="case_ids",
        metavar="ID",
        help="Run one case ID; repeat to select multiple cases",
    )
    parser.add_argument(
        "--route",
        choices=("matched", "partial", "unmatched"),
        help="Run only cases with this expected capability route",
    )
    parser.add_argument("--reasoning", default="none", help="Hermes reasoning setting")
    parser.add_argument("--timeout-sec", type=float, default=900, help="Timeout for each case")
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop after the first nonzero exit or timeout",
    )
    return parser


def select_cases(case_ids: list[str] | None, route: str | None) -> list[Case]:
    known = {case.case_id: case for case in CASES}
    if case_ids:
        unknown = sorted(set(case_ids) - set(known))
        if unknown:
            raise ValueError(f"Unknown case ID(s): {', '.join(unknown)}")
        selected = [known[case_id] for case_id in case_ids]
    else:
        selected = list(CASES)
    if route:
        selected = [case for case in selected if EXPECTATIONS[case.case_id].expected_route == route]
    return selected


def print_cases(cases: list[Case]) -> None:
    for case in cases:
        expectation = EXPECTATIONS[case.case_id]
        print(
            f"{case.case_id:28} expected={expectation.expected_route:9} "
            f"{expectation.description}"
        )
        print(f"  user_request: {case.user_request}")


def request_states() -> dict[str, dict[str, object]]:
    states: dict[str, dict[str, object]] = {}
    for path in (ROOT / "runs").glob("req-*/state.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            request_id = str(payload["request"]["request_id"])
            states[request_id] = payload
        except (OSError, KeyError, TypeError, json.JSONDecodeError):
            continue
    return states


def route_observation(
    case: Case,
    before: dict[str, dict[str, object]],
    after: dict[str, dict[str, object]],
) -> dict[str, object]:
    expectation = EXPECTATIONS[case.case_id]
    request_ids = sorted(set(after) - set(before))
    stages = [str(after[request_id].get("stage", "unknown")) for request_id in request_ids]
    reasons = [
        str(after[request_id].get("routing_reason") or "") for request_id in request_ids
    ]
    if expectation.expected_route == "matched":
        verified = bool(request_ids) and "pending_autonomous_planning" not in stages
    else:
        verified = (
            "pending_autonomous_planning" in stages
            and any(expectation.expected_route in reason.lower() for reason in reasons)
        )
    return {
        "request_ids": request_ids,
        "observed_stages": stages,
        "routing_reasons": reasons,
        "route_verified": verified,
    }


def run_case(case: Case, reasoning: str, timeout_sec: float) -> dict[str, object]:
    expectation = EXPECTATIONS[case.case_id]
    command = [
        sys.executable,
        str(LAUNCHER),
        "run",
        case.user_request,
        "--reasoning",
        reasoning,
        "--timeout-sec",
        str(timeout_sec),
    ]
    print("\n" + "=" * 80, flush=True)
    print(
        f"CASE {case.case_id} | expected route: {expectation.expected_route}"
        f"\nUSER REQUEST ONLY:\n{case.user_request}",
        flush=True,
    )
    before = request_states()
    started = time.monotonic()
    try:
        completed = subprocess.run(command, cwd=ROOT, check=False, timeout=timeout_sec + 30)
        exit_code: int | None = completed.returncode
        outcome = "completed" if completed.returncode == 0 else "failed"
        error = None
    except subprocess.TimeoutExpired:
        exit_code = None
        outcome = "timed_out"
        error = f"case exceeded {timeout_sec + 30:.0f} seconds"
    observation = route_observation(case, before, request_states())
    return {
        **asdict(case),
        **asdict(expectation),
        "outcome": outcome,
        "exit_code": exit_code,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "error": error,
        **observation,
    }


def save_summary(results: list[dict[str, object]]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = ROOT / "runs" / "case-suite" / timestamp / "summary.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return target


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    try:
        selected = select_cases(args.case_ids, args.route)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not selected:
        print("No cases matched the requested filters.", file=sys.stderr)
        return 2
    if args.list:
        print_cases(selected)
        return 0

    results: list[dict[str, object]] = []
    try:
        for case in selected:
            result = run_case(case, args.reasoning, args.timeout_sec)
            results.append(result)
            if args.stop_on_error and result["outcome"] != "completed":
                break
    except KeyboardInterrupt:
        print("\nInterrupted by user; saving completed case results.", file=sys.stderr)

    if not results:
        return 130
    summary = save_summary(results)
    print("\n" + "=" * 80)
    print(f"Summary: {summary}")
    for result in results:
        print(
            f"{result['case_id']:28} expected={result['expected_route']:9} "
            f"outcome={result['outcome']:9} exit={result['exit_code']} "
            f"route_verified={result['route_verified']} elapsed={result['elapsed_seconds']}s"
        )
    return 0 if all(
        result["outcome"] == "completed" and result["route_verified"] for result in results
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
