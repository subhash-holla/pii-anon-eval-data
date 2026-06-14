# Claims Policy — what a result on this benchmark does (and does not) support

This dataset is a CC0 SYNTHETIC eval substrate. The following bounds what a published result computed on it may and may not claim.

WHAT A RESULT DOES SUPPORT: a reproducible, version-pinned (v2.0.0) measurement of a system's PII-detection / de-identification / re-identification-resistance behaviour on a controlled synthetic distribution, with stated confidence intervals on integer-count metrics. Cell-level power is statistical precision on THAT synthetic distribution.

WHAT A RESULT DOES NOT SUPPORT: Synthetic-only (AX-001): every record contains ONLY synthetic PII. A score on this corpus is statistical precision on the SYNTHETIC distribution, NOT external validity, and NOT a standalone recall claim absent the real-data correlation slice (FR-027). AX-003. A number here is therefore NOT a claim of real-world recall, NOT a claim of external validity, and NOT a compliance certification. Any real-world or regulatory claim requires the separate real-data correlation slice (FR-027), which is out of scope for this release.

DOI / PROVENANCE HONESTY: this release is archived on Zenodo at DOI 10.5281/zenodo.20690979 (minted by a human on deposit); no DOI was fabricated before minting. Cite the DOI or the version-pinned repository URL.
