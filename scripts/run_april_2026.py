#!/usr/bin/env python3
"""Run the MasterThesis pipeline on resumable local-time date chunks."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import resource
import shutil
import sys
import tempfile
import time
import traceback
from datetime import date, datetime, time as dt_time, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.dataset as ds
import pyarrow.parquet as pq
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MASTER_THESIS_ROOT = Path("/home/ita/MasterThesis")
if str(MASTER_THESIS_ROOT) not in sys.path:
    sys.path.insert(0, str(MASTER_THESIS_ROOT))
from src.pipeline import PipelineConfig, run_pipeline  # noqa: E402

LOGGER = logging.getLogger("run_april_2026")
LOCAL_TZ = "Europe/Berlin"
OVERLAP = timedelta(minutes=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("/home/ita/data/ERA/D63_Nr7_8"))
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "config/example_pipeline_stage8.yaml")
    parser.add_argument("--date-from", type=date.fromisoformat, default=date(2026, 4, 3))
    parser.add_argument("--date-to", type=date.fromisoformat, default=date(2026, 4, 3))
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "outputs")
    parser.add_argument("--state", type=Path, default=PROJECT_ROOT / "outputs/april_2026/run_state.json")
    parser.add_argument("--keep-slices", action="store_true")
    parser.add_argument("--chunk-days", type=int, default=1)
    return parser.parse_args()


def local_timestamp(day: date, at: dt_time) -> pd.Timestamp:
    return pd.Timestamp(datetime.combine(day, at))


def day_window(day: date, chunk_days: int = 1) -> tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    nominal_start = local_timestamp(day, dt_time.min)
    nominal_end = local_timestamp(day + timedelta(days=chunk_days), dt_time.min)
    return nominal_start, nominal_end, nominal_start - OVERLAP, nominal_end + OVERLAP


def config_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_config(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Pipeline config must be a mapping: {path}")
    return value


def copy_metadata(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for path in source.glob("*.parquet"):
        if not path.is_file():
            continue
        shutil.copy2(path, target / path.name)


def write_filtered_dataset(source_root: Path, target_root: Path, start: pd.Timestamp, end: pd.Timestamp, table_name: str) -> int:
    source = source_root / table_name
    if not source.exists():
        return 0
    target = target_root / table_name
    target.mkdir(parents=True, exist_ok=True)
    partitioning = None if table_name == "vibration.parquet" else "hive"
    dataset = ds.dataset(source, format="parquet", partitioning=partitioning)
    expression = (ds.field("time") >= start.to_pydatetime()) & (ds.field("time") < end.to_pydatetime())
    table = dataset.to_table(filter=expression)
    if table.num_rows == 0:
        return 0
    for signal_id in sorted({str(value) for value in table.column("signal_id")}):
        part = table.filter(pc.equal(table.column("signal_id"), pa.scalar(signal_id)))
        part_dir = target / f"signal_id={signal_id}"
        part_dir.mkdir(parents=True, exist_ok=True)
        pq.write_table(part, part_dir / "filtered.parquet", compression="zstd")
    return table.num_rows


def make_slice(source: Path, start: pd.Timestamp, end: pd.Timestamp) -> tuple[Path, int]:
    temporary = Path(tempfile.mkdtemp(prefix="april_slice_"))
    copy_metadata(source, temporary)
    rows = write_filtered_dataset(source, temporary, start, end, "signal_data_point.parquet")
    rows += write_filtered_dataset(source, temporary, start, end, "vibration.parquet")
    return temporary, rows


def add_cycle_keys(cycles_path: Path, chunk_id: str, nominal_start: pd.Timestamp, nominal_end: pd.Timestamp) -> dict[str, int]:
    if not cycles_path.exists():
        return {"cycles": 0, "boundary_cycles": 0}
    frame = pd.read_parquet(cycles_path)
    frame["chunk_id"] = chunk_id
    frame["is_boundary_cycle"] = (
        (pd.to_datetime(frame["start_time"]) < nominal_start + OVERLAP)
        | (pd.to_datetime(frame["end_time"]) > nominal_end - OVERLAP)
    )
    frame["global_cycle_key"] = frame["chunk_id"].astype(str) + ":" + frame["session_id"].astype(str) + ":" + frame["cycle_id"].astype(str)
    frame.to_parquet(cycles_path, index=False)
    return {"cycles": len(frame), "boundary_cycles": int(frame["is_boundary_cycle"].sum())}


def measurement_stats(run_dir: Path, cycles_path: Path) -> dict[str, Any]:
    batches = list((run_dir / "multi_sensor/measurements").rglob("batch_*.parquet"))
    rows = sum(pq.ParquetFile(path).metadata.num_rows for path in batches)
    size = sum(path.stat().st_size for path in batches)
    cycles = pd.read_parquet(cycles_path) if cycles_path.exists() else pd.DataFrame()
    rates: dict[str, Any] = {}
    if batches and not cycles.empty:
        measurements = pd.concat((pd.read_parquet(path, columns=["cycle_id", "signal_name"]) for path in batches), ignore_index=True)
        durations = cycles[["cycle_id", "duration_seconds"]].drop_duplicates("cycle_id")
        counts = measurements.groupby(["signal_name", "cycle_id"], as_index=False).size().rename(columns={"size": "number_of_samples"})
        joined = counts.merge(durations, on="cycle_id", how="inner")
        joined["sample_rate_hz"] = joined["number_of_samples"] / joined["duration_seconds"].where(joined["duration_seconds"] > 0)
        for signal, group in joined.groupby("signal_name"):
            rates[str(signal)] = {"cycles": int(len(group)), "median_hz": round(float(group["sample_rate_hz"].median()), 4), "p05_hz": round(float(group["sample_rate_hz"].quantile(0.05)), 4), "p95_hz": round(float(group["sample_rate_hz"].quantile(0.95)), 4)}
    return {"batch_count": len(batches), "rows": rows, "bytes": size, "signal_rates_hz": rates}


def run_day(day: date, args: argparse.Namespace, yaml_config: dict[str, Any], state: dict[str, Any]) -> None:
    chunk_id = f"{day.isoformat()}__{(day + timedelta(days=args.chunk_days - 1)).isoformat()}"
    nominal_start, nominal_end, slice_start, slice_end = day_window(day, args.chunk_days)
    log_path = PROJECT_ROOT / "logs/april_2026" / f"{chunk_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    LOGGER.addHandler(handler)
    started = time.perf_counter()
    slice_dir: Path | None = None
    try:
        state[chunk_id] = {"status": "running", "started_at": datetime.now().isoformat()}
        args.state.parent.mkdir(parents=True, exist_ok=True)
        args.state.write_text(json.dumps(state, indent=2), encoding="utf-8")
        slice_started = time.perf_counter()
        slice_dir, source_rows = make_slice(args.dataset, slice_start, slice_end)
        slice_seconds = time.perf_counter() - slice_started
        run_config = dict(yaml_config)
        run_config.update({"dataset_path": str(slice_dir), "output_root": str(args.output_root), "stop_after": yaml_config.get("stop_after", "cycle_quality_profiling")})
        config = PipelineConfig(dataset_path=slice_dir, experiment=str(run_config.get("experiment", "Versuch1")), stop_after=str(run_config["stop_after"]), reference_signal=str(run_config.get("reference_signal", "position")), session_gap_seconds=run_config.get("session_gap_seconds"), movement_threshold=float(run_config.get("movement_threshold", 1.0)), output_root=args.output_root, max_cycles_to_extract=int(run_config.get("max_cycles_to_extract", 3)), extract_all_cycles=bool(run_config.get("extract_all_cycles", False)), cycle_batch_size=int(run_config.get("cycle_batch_size", 500)), resume_extraction=bool(run_config.get("resume_extraction", True)), overwrite_existing=bool(run_config.get("overwrite_existing", False)), selected_extraction_signals=tuple(run_config.get("selected_extraction_signals", ()) or ()), validation_cycle_count=int(run_config.get("validation_cycle_count", 3)), required_validation_signals=tuple(run_config.get("required_validation_signals", ()) or ()), minimum_samples_per_validation_cycle=run_config.get("minimum_samples_per_validation_cycle"), require_consecutive_validation_cycles=bool(run_config.get("require_consecutive_validation_cycles", True)), max_cycles_to_scan_for_validation=run_config.get("max_cycles_to_scan_for_validation", 10_000), generate_validation_html=bool(run_config.get("generate_validation_html", True)), generate_cycle_features=bool(run_config.get("generate_cycle_features", False)), parquet_compression=str(run_config.get("parquet_compression", "zstd")), quality_profiling_batch_size=int(run_config.get("quality_profiling_batch_size", 1000)), signal_roles=run_config.get("signal_roles"), validation_rule_generation=run_config.get("validation_rule_generation"), dataset_validation=run_config.get("dataset_validation"), cycle_tensor_generation=run_config.get("cycle_tensor_generation"))
        pipeline_started = time.perf_counter()
        result = run_pipeline(config)
        pipeline_seconds = time.perf_counter() - pipeline_started
        run_dir = Path(result["run"]["run_directory"])
        cycles_path = run_dir / "cycles/cycles.parquet"
        cycle_info = add_cycle_keys(cycles_path, chunk_id, nominal_start, nominal_end)
        measurements = measurement_stats(run_dir, cycles_path)
        feature_files = list((run_dir / "features").glob("**/*")) if (run_dir / "features").exists() else []
        quality_files = list((run_dir / "quality_profiling").glob("**/*")) if (run_dir / "quality_profiling").exists() else []
        state[chunk_id] = {"status": "done", "run_dir": str(run_dir), "source_rows": source_rows, "slice_seconds": slice_seconds, "pipeline_seconds": pipeline_seconds, "peak_rss_kb": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss), "cycle_info": cycle_info, "measurements": measurements, "features_populated": bool(feature_files), "quality_profiling_populated": bool(quality_files), "stop_after": config.stop_after}
    except Exception:
        state[chunk_id] = {"status": "failed", "traceback": traceback.format_exc()}
        LOGGER.exception("Chunk %s failed", chunk_id)
    finally:
        args.state.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
        if slice_dir is not None and not args.keep_slices:
            shutil.rmtree(slice_dir, ignore_errors=True)
        LOGGER.removeHandler(handler)
        handler.close()
        LOGGER.info("Chunk %s elapsed %.2fs", chunk_id, time.perf_counter() - started)


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    yaml_config = load_config(args.config)
    state = json.loads(args.state.read_text(encoding="utf-8")) if args.state.exists() else {"meta": {"timezone": LOCAL_TZ, "config_hash": config_hash(args.config)}}
    day = args.date_from
    while day <= args.date_to:
        chunk_end = day + timedelta(days=args.chunk_days - 1)
        if state.get(f"{day.isoformat()}__{chunk_end.isoformat()}", {}).get("status") == "done":
            day += timedelta(days=args.chunk_days)
            continue
        run_day(day, args, yaml_config, state)
        day += timedelta(days=args.chunk_days)
    print(json.dumps(state, indent=2, default=str))


if __name__ == "__main__":
    main()
