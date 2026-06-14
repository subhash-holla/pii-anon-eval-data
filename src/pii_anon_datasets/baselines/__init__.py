"""The ``pii-anon baselines`` detector-benchmark pipeline (the DETECTION metric family only — AX-004).

Runs the most-used PII detectors over a PII-Anon split, scores each through the AUDITED scorer
(:func:`pii_anon_datasets.scoring.detection.score_detection`: strict-v1 exact matching + Wilson 95% CIs +
the non-strippable synthetic-only caveat, AX-001), and aggregates an **F2-ranked** leaderboard with
per-entity-type / per-domain / per-language breakdowns (micro + macro). Pure-stdlib at import; every
detector library stays lazy (NFR-050) — importing this package pulls in no presidio/spacy/torch/etc.

This family is detection ONLY and is never fused with the anonymization / pseudonymization / Elo / RRS
families (AX-004): the results object exposes no merged ``overall``/``score`` field and is not numeric.
"""

from __future__ import annotations
