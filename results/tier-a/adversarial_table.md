# Per-adversarial-attack robustness (measured — replaces the unbacked '94%→14%' line)

test_adversarial split: 11,254 records / 34,646 gold spans / 13 attack types. F2, strict-v1, recall with Wilson 95% CIs. ⚠ = underpowered (<150 records).

## F2 by attack type × detector

| Attack type | #recs | gliner | piiranha | presidio | regex | spacy | stanza | scrubadub |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base64_encoding | 3,379 | 0.731 | 0.386 | 0.638 | 0.397 | 0.358 | 0.356 | 0.384 |
| zero_width_char | 3,376 | 0.811 | 0.403 | 0.619 | 0.408 | 0.354 | 0.374 | 0.371 |
| ocr_artifact | 3,321 | 0.825 | 0.418 | 0.642 | 0.409 | 0.364 | 0.371 | 0.390 |
| unicode_homoglyph | 198 | 1.000 | 0.636 | 0.519 | 0.591 | 0.000 | 0.213 | 0.201 |
| context_ambiguous ⚠ | 124 | 0.449 | 0.499 | 0.416 | 0.440 | 0.149 | 0.223 | 0.271 |
| multi_token ⚠ | 122 | 1.000 | 0.520 | 0.654 | 0.789 | 0.128 | 0.227 | 0.437 |
| code_embedded ⚠ | 116 | 0.675 | 0.285 | 0.595 | 0.565 | 0.192 | 0.344 | 0.176 |
| bidi_attack ⚠ | 114 | 0.625 | 0.639 | 0.493 | 0.714 | 0.000 | 0.000 | 0.567 |
| negated_pii ⚠ | 114 | 0.994 | 0.539 | 0.857 | 0.689 | 0.385 | 0.394 | 0.315 |
| mixed_script ⚠ | 110 | 0.933 | 0.419 | 0.485 | 0.556 | 0.290 | 0.294 | 0.284 |
| url_embedded ⚠ | 97 | 0.952 | 0.607 | 0.361 | 0.789 | 0.000 | 0.000 | 0.155 |
| partial_redaction_advanced ⚠ | 92 | 0.655 | 0.535 | 0.444 | 0.714 | 0.000 | 0.000 | 0.548 |
| url_encoding ⚠ | 91 | 0.843 | 0.401 | 0.512 | 0.385 | 0.357 | 0.022 | 0.231 |

## Clean → adversarial recall (the reality of the '94%→14%' claim)

Detector recall on the CLEAN English test vs pooled adversarial vs its single WORST attack:

| Detector | clean recall | adversarial (all) | worst attack | worst recall |
|---|---:|---:|---|---:|
| gliner | 0.716 | 0.777 | context_ambiguous | 0.457 |
| piiranha | 0.327 | 0.402 | code_embedded | 0.266 |
| presidio | 0.562 | 0.658 | url_embedded | 0.394 |
| regex | 0.349 | 0.380 | url_encoding | 0.333 |
| spacy | 0.294 | 0.298 | bidi_attack | 0.000 |
| stanza | 0.308 | 0.306 | bidi_attack | 0.000 |
| scrubadub | 0.169 | 0.323 | url_embedded | 0.144 |

**Verdict on '94%→14%':** that figure was never measured and does not match any detector (no detector reaches 94% clean recall; gliner clean recall is ~0.72). The real picture is attack- and detector-specific — report this measured table, not the slogan. The English-tuned NER detectors degrade hardest on encoding/obfuscation attacks; gliner is the most robust.

