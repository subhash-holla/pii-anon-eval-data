# Reproducible, reportable image for the full 11-detector PII-Anon leaderboard run.
#
# Bakes every local detector library + model weight and the three cloud DLP SDKs, so a run is offline,
# fast (GPU), and byte-for-byte reproducible — the portable unit you `docker run` identically on this Mac
# (CPU/MPS-less inside Linux containers) or, for speed, on an Azure NC-series (NVIDIA T4) GPU VM. The cloud
# DLP calls are plain HTTPS API calls that work from anywhere; the GPU only accelerates the local
# transformer detectors (GLiNER / Piiranha / Flair).
#
#   docker build -t pii-anon-eval .
#   # CPU:  docker run --rm -v "$PWD/results:/app/results" pii-anon-eval scripts/run_full_leaderboard.sh --dry-run
#   # GPU:  docker run --rm --gpus all -v "$PWD/results:/app/results" \
#   #         --env-file ~/.pii-anon-cloud.env pii-anon-eval scripts/run_full_leaderboard.sh --max-azure-usd 90
#
# Pin the digest in CI for full reproducibility; the tag below is a stable CUDA 12.1 / PyTorch 2.3 runtime.
FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        git build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    TOKENIZERS_PARALLELISM=false \
    HF_HOME=/opt/models/hf \
    PII_ANON_BIN=/opt/conda/bin/pii-anon \
    PYTHON_BIN=/opt/conda/bin/python

WORKDIR /app

# Install the package + every local-detector engine + cloud SDKs + distribution extras (editable so the
# repo-root `baselines/` adapter package and the scripts/ stay live). .dockerignore keeps the 309 MB
# dist/ parquet and results/ out of the build context — the eval reads the packaged splits/*.jsonl.gz.
COPY . /app
RUN pip install --no-cache-dir -e ".[baselines,engines,cloud,distribution]"

# Pre-bake the detector models so the run never downloads at eval time (reproducibility + speed):
#   spaCy en_core_web_lg · Stanza en · GLiNER urchade/gliner_multi_pii-v1 ·
#   Piiranha iiiorg/piiranha-v1-detect-personal-information · Flair "ner" (CoNLL-03 English).
RUN python -m spacy download en_core_web_lg \
    && python -c "import stanza; stanza.download('en')" \
    && python - <<'PY'
from gliner import GLiNER
GLiNER.from_pretrained("urchade/gliner_multi_pii-v1")
from transformers import pipeline
pipeline("token-classification", model="iiiorg/piiranha-v1-detect-personal-information", aggregation_strategy="simple")
from flair.models import SequenceTagger
SequenceTagger.load("ner")
print("models pre-baked OK")
PY

# Sanity: the CLI imports and lists detectors (cloud ones appear only with creds + --cloud at run time).
RUN pii-anon baselines --list || true

ENTRYPOINT ["/bin/bash"]
