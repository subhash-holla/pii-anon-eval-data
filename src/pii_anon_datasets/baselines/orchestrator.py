"""Baselines orchestrator — runs detectors over records, scores each via the AUDITED scorer, and
aggregates an **F2-ranked** leaderboard (micro + macro; per-entity-type / per-domain / per-language).

**Record-namespaced pooling (correctness):** each record's spans are offset into a disjoint coordinate
range before pooling, so a predicted span in record B can never spuriously match an identical gold span
in record A (the strict matcher keys only on ``(start, end, entity_type)``). Within a record gold and
pred share the same offset, so per-record matching is unchanged. This lets the AUDITED
:func:`pii_anon_datasets.scoring.detection.score_detection` do ALL the metric math + Wilson CIs + the
relaxed ``partial_f1`` in one call per slice — the orchestrator invents no statistics.

Pure-stdlib; detector libraries are reached only through each adapter's lazy ``build()`` (NFR-050).
A detector that is unavailable or raises is RECORDED (status unavailable/errored), never silently dropped.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from ..scoring.core import Span
from ..scoring.detection import DetectionScore, score_detection
from .contract import AdapterSpan, DetectorAdapter, lossiness, to_scoring_spans
from .results import BaselineResults

_Tagged = tuple[Span, str, str]  # (namespaced span, domain, language)
_PROGRESS_EVERY = 200  # emit a per-records progress event every N records (transparency on long runs)

# Optional progress sink: receives clock-free lifecycle event dicts (the CLI stamps time + renders).
Progress = Callable[[dict], None]


def _emit(progress: Progress | None, event: dict) -> None:
    if progress is not None:
        progress(event)


def score_detectors(
    records: Sequence[Mapping[str, object]],
    adapters: Sequence[DetectorAdapter],
    *,
    dataset_info: Mapping[str, object] | None = None,
    confidence: float = 0.95,
    progress: Progress | None = None,
) -> BaselineResults:
    """Run each adapter over ``records``, score via the audited scorer, F2-rank, and return results.

    ``progress`` (optional) receives clock-free lifecycle events — ``detector_start`` / ``records`` (with
    ``done``/``total``) / ``detector_done`` / ``detector_skipped`` / ``detector_error`` — so a caller can
    render a live view; the core emits no wall-clock and stays deterministic.
    """
    records = list(records)
    n_gold_total = sum(len(r.get("annotations", []) or []) for r in records)
    # The run's single language (cloud shards run one concrete code at a time). "all"/"" => multilingual or
    # unspecified: no per-language threading or gating (the historical behaviour). Only the cloud adapters
    # carry a ``language`` slot / ``supports_language`` hook, so local adapters are wholly unaffected.
    run_language = str((dataset_info or {}).get("language") or "")
    concrete_language = run_language if run_language and run_language != "all" else ""

    detectors: dict[str, dict] = {}
    ranking_rows: list[dict] = []
    for adapter in adapters:
        name = adapter.name
        if not adapter.available():
            detectors[name] = {
                "status": "unavailable",
                "model_id": getattr(adapter, "model_id", ""),
                "reason": f"{name}: detector library or credentials not available",
            }
            _emit(progress, {"event": "detector_skipped", "detector": name, "reason": "unavailable"})
            continue
        # A provider that does not support this run's language is RECORDED and skipped BEFORE the expensive
        # build()/detect() — never run as garbage en-on-Hindi, never a silent budget burn (cloud only;
        # local adapters expose no supports_language hook, so this is a no-op for them).
        supports = getattr(adapter, "supports_language", None)
        if concrete_language and callable(supports) and not supports(concrete_language):
            detectors[name] = {
                "status": "unsupported-language",
                "model_id": getattr(adapter, "model_id", ""),
                "reason": f"{name}: provider PII detection does not support language {concrete_language!r}",
            }
            _emit(progress, {"event": "detector_skipped", "detector": name, "reason": "unsupported-language"})
            continue
        # Thread the run language onto any adapter that carries the slot (the cloud adapters), so detect()
        # sends the right per-provider locale to the API.
        if concrete_language and hasattr(adapter, "language"):
            adapter.language = concrete_language
        _emit(progress, {"event": "detector_start", "detector": name, "total": len(records)})
        try:
            detectors[name] = _score_one(adapter, records, confidence, progress=progress)
        except Exception as exc:  # a single detector blowing up must not crash the whole run
            detectors[name] = {
                "status": "errored",
                "model_id": getattr(adapter, "model_id", ""),
                "reason": f"{type(exc).__name__}: {exc}",
            }
            _emit(progress, {"event": "detector_error", "detector": name, "error": f"{type(exc).__name__}: {exc}"})
            continue
        macro = detectors[name]["macro"] or {}
        ranking_rows.append(
            {"detector": name, "f2_micro": detectors[name]["micro"]["f2"], "f2_macro": macro.get("f2", 0.0)}
        )
        _emit(progress, {
            "event": "detector_done", "detector": name, "status": "scored",
            "record_errors": detectors[name]["record_errors"], "f2": detectors[name]["micro"]["f2"],
        })

    ranking_rows.sort(key=lambda row: row["f2_micro"], reverse=True)  # stable: ties keep insertion order
    ranking = [{"rank": i + 1, **row} for i, row in enumerate(ranking_rows)]

    dataset = dict(dataset_info or {})
    dataset["n_records"] = len(records)
    dataset["n_gold"] = n_gold_total
    return BaselineResults(dataset=dataset, confidence=confidence, ranking=ranking, detectors=detectors)


def merge_results(results: Sequence[BaselineResults]) -> BaselineResults:
    """Combine per-detector (or per-group) runs over the SAME records into one F2-ranked leaderboard.

    Unions the ``detectors`` blocks (last wins on a name collision), re-ranks the scored detectors by micro
    F2, and keeps the first result's dataset/confidence (all inputs are expected to be the same split/records).
    This is the restart-safe census pattern: run heavy detectors in separate processes, then merge.
    """
    results = list(results)
    if not results:
        raise ValueError("merge_results requires at least one result")
    # A merged leaderboard is only meaningful if every input scored the SAME
    # split + dataset version over the SAME record count — otherwise the rows
    # are not comparable and the leaderboard is a forgery (e.g. a detector's
    # easy-dev-split F2 ranked against everyone else's test-split F2). Fail
    # loud on a heterogeneous merge rather than silently keeping results[0].
    def _key(ds: dict) -> tuple:
        return (ds.get("split"), ds.get("dataset_version"), ds.get("language"), ds.get("n_records"))

    keys = {_key(r.dataset) for r in results}
    if len(keys) > 1:
        raise ValueError(
            "merge_results refuses a heterogeneous merge: inputs differ on "
            f"(split, dataset_version, language, n_records) — saw {sorted(map(str, keys))}. "
            "Re-run every detector on the same split/version before merging."
        )
    detectors: dict[str, dict] = {}
    for r in results:
        for name, det in r.detectors.items():
            detectors[name] = det
    ranking_rows = [
        {"detector": name, "f2_micro": det["micro"]["f2"], "f2_macro": (det.get("macro") or {}).get("f2", 0.0)}
        for name, det in detectors.items()
        if det.get("status") == "scored"
    ]
    ranking_rows.sort(key=lambda row: row["f2_micro"], reverse=True)
    ranking = [{"rank": i + 1, **row} for i, row in enumerate(ranking_rows)]
    return BaselineResults(
        dataset=dict(results[0].dataset), confidence=results[0].confidence, ranking=ranking, detectors=detectors
    )


def _trim_spans(spans: Sequence[AdapterSpan], text: str) -> list[AdapterSpan]:
    """Trim leading/trailing whitespace from each PREDICTED span to its entity boundary (dropping spans
    that are all whitespace). Tokenizer-based detectors often emit a leading sub-word space, which would
    otherwise fail strict (start, end) matching for a span they actually found — this makes matching fair.
    Gold is authoritative and never trimmed."""
    out: list[AdapterSpan] = []
    n = len(text)
    for s in spans:
        start, end = s.start, s.end
        while start < end and start < n and text[start].isspace():
            start += 1
        while end > start and end <= n and text[end - 1].isspace():
            end -= 1
        if end > start:
            out.append(AdapterSpan(start, end, s.entity_type, text[start:end]))
    return out


def _score_one(
    adapter: DetectorAdapter,
    records: Sequence[Mapping[str, object]],
    confidence: float,
    progress: Progress | None = None,
) -> dict:
    name = adapter.name
    model = adapter.build()
    _emit(progress, {"event": "built", "detector": name})
    pred_by_record: dict[str, list[AdapterSpan]] = {}
    record_errors = 0
    total = len(records)
    for i, rec in enumerate(records):
        text = str(rec.get("text", "") or "")
        try:
            if getattr(adapter, "wants_record", False):
                raw = adapter.detect(text, model, record=rec)
            else:
                raw = adapter.detect(text, model)
        except Exception:  # noqa: BLE001 - one pathological record must not zero out the whole detector
            raw = []
            record_errors += 1
        pred_by_record[str(rec["record_id"])] = _trim_spans(raw, text)
        if progress is not None and (i + 1) % _PROGRESS_EVERY == 0:
            _emit(progress, {"event": "records", "detector": name, "done": i + 1, "total": total})
    _emit(progress, {"event": "records", "detector": name, "done": total, "total": total})
    gold_tagged, pred_tagged = _namespace_and_tag(records, pred_by_record)

    micro = score_detection([s for s, _, _ in gold_tagged], [s for s, _, _ in pred_tagged], confidence)
    by_type = _slice(gold_tagged, pred_tagged, lambda s, dom, lang: s.entity_type, confidence)
    by_domain = _slice(gold_tagged, pred_tagged, lambda s, dom, lang: dom, confidence)
    by_language = _slice(gold_tagged, pred_tagged, lambda s, dom, lang: lang, confidence)

    macro = _macro([sc for sc in by_type.values() if sc.counts.n_gold > 0])
    return {
        "status": "scored",
        "model_id": getattr(adapter, "model_id", ""),
        "deterministic": bool(getattr(adapter, "deterministic", True)),
        "record_errors": record_errors,
        "n_records": len(records),
        "n_gold": micro.counts.n_gold,
        "n_pred": micro.counts.n_pred,
        "coverage": lossiness(adapter.label_map),
        "micro": micro.as_dict(),
        "macro": macro,
        "by_entity_type": {k: sc.as_dict() for k, sc in sorted(by_type.items())},
        "by_domain": {k: sc.as_dict() for k, sc in sorted(by_domain.items())},
        "by_language": {k: sc.as_dict() for k, sc in sorted(by_language.items())},
    }


def _namespace_and_tag(
    records: Sequence[Mapping[str, object]], pred_by_record: Mapping[str, Sequence[AdapterSpan]]
) -> tuple[list[_Tagged], list[_Tagged]]:
    """Offset each record's gold + predicted spans into a disjoint coordinate range (cumulative base)
    and tag every span with its record's domain + language for slicing."""
    gold_tagged: list[_Tagged] = []
    pred_tagged: list[_Tagged] = []
    base = 0
    for rec in records:
        dom = str(rec.get("domain", "unknown") or "unknown")
        lang = str(rec.get("language", "unknown") or "unknown")
        annotations = rec.get("annotations", []) or []
        gold = to_scoring_spans(
            AdapterSpan(int(a["start"]), int(a["end"]), str(a["entity_type"])) for a in annotations
        )
        pred = to_scoring_spans(pred_by_record.get(str(rec["record_id"]), []))
        max_end = 0
        for s in (*gold, *pred):
            max_end = max(max_end, s.end)
        for s in gold:
            gold_tagged.append((Span(s.start + base, s.end + base, s.entity_type), dom, lang))
        for s in pred:
            pred_tagged.append((Span(s.start + base, s.end + base, s.entity_type), dom, lang))
        base += max_end + 1
    return gold_tagged, pred_tagged


def _slice(
    gold_tagged: Sequence[_Tagged],
    pred_tagged: Sequence[_Tagged],
    key: Callable[[Span, str, str], str],
    confidence: float,
) -> dict[str, DetectionScore]:
    """Score one breakdown dimension: group gold + pred by ``key`` and run the audited scorer per group."""
    keys = {key(s, dom, lang) for s, dom, lang in gold_tagged}
    keys |= {key(s, dom, lang) for s, dom, lang in pred_tagged}
    out: dict[str, DetectionScore] = {}
    for k in keys:
        gold = [s for s, dom, lang in gold_tagged if key(s, dom, lang) == k]
        pred = [s for s, dom, lang in pred_tagged if key(s, dom, lang) == k]
        out[k] = score_detection(gold, pred, confidence)
    return out


def _macro(scores: Sequence[DetectionScore]) -> dict | None:
    """Unweighted mean of per-entity-type P/R/F1/F2 over the types actually present in gold (n_gold>0).

    A point estimate (mean of ratios) — deliberately NOT given a CI. Macro weights every PII type
    equally, so a detector cannot hide a missed rare-but-critical type (e.g. SSN) behind frequent ones.
    """
    if not scores:
        return None
    n = len(scores)
    return {
        "precision": sum(s.precision for s in scores) / n,
        "recall": sum(s.recall for s in scores) / n,
        "f1": sum(s.f1 for s in scores) / n,
        "f2": sum(s.f2 for s in scores) / n,
        "n_types": n,
        "_note": "unweighted mean over entity types with n_gold>0; point estimate (no CI).",
    }
