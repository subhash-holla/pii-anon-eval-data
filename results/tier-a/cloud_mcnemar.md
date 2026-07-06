# GLINER vs AWS — paired McNemar (the 'free local ties best cloud' test)

Over **201,880** English gold spans. gliner micro-F2 0.7337 (recall 0.7163) vs aws micro-F2 0.7360 (recall 0.7282).

| Quantity | Value |
|---|---|
| Discordant: gliner✓ aws✗ (b) | 18,577 |
| Discordant: gliner✗ aws✓ (c) | 20,980 |
| Δrecall (gliner − aws) | **-0.0119** [95% CI -0.0138, -0.0100] |
| McNemar | mcnemar-chi2-continuity, statistic=145.9, **p=1.4e-33** |

## Verdict
**Significant difference** (McNemar p=1.4e-33): aws has higher recall (Δrecall=-0.0119). The near-tie in micro-F2 masks a paired-significant recall gap.

_Caveat: AWS Comprehend is a non-deterministic managed service scored in a SINGLE run; the p-value reflects that run. AX-001: synthetic-distribution precision, not external validity._
