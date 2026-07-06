#!/usr/bin/env bash
# provision_azure_gpu.sh — stand up an Azure spot GPU VM, run the full 11-detector leaderboard inside the
# reproducible Docker image, copy results back, and DEPROVISION. Run from your Mac (needs `az` + `ssh`).
#
# The GPU only accelerates the local transformer detectors (GLiNER/Piiranha/Flair); the cloud DLP calls
# are HTTPS and run from anywhere. A spot Standard_NC4as_T4_v3 (1× NVIDIA T4) is ~$0.20–0.50/hr; a full
# multilingual local run is a few GPU-hours ⇒ ~$2–8 — small next to the Azure DLP spend. The VM ALSO draws
# on the same Azure credits, so mind the combined budget (see EVAL_RUNBOOK.md).
#
#   az login                                  # once
#   export PII_ANON_CLOUD_ENV=~/.pii-anon-cloud.env   # your AWS/Azure/GCP creds (sourced into the container)
#   scripts/provision_azure_gpu.sh up         # create VM, build image, run, fetch results
#   scripts/provision_azure_gpu.sh down       # delete the resource group (also runs on trap/EXIT of `up`)
#
# Override anything via env: RG, LOCATION, VM_NAME, VM_SIZE, ADMIN, MAX_AZURE_USD, KEEP_VM=1 (skip teardown).
set -euo pipefail

RG="${RG:-pii-anon-eval-rg}"
LOCATION="${LOCATION:-eastus}"
VM_NAME="${VM_NAME:-pii-anon-eval-gpu}"
VM_SIZE="${VM_SIZE:-Standard_NC4as_T4_v3}"     # 1× NVIDIA T4, spot-friendly
ADMIN="${ADMIN:-azureuser}"
IMAGE_URN="${IMAGE_URN:-Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest}"
MAX_AZURE_USD="${MAX_AZURE_USD:-90}"
PII_ANON_CLOUD_ENV="${PII_ANON_CLOUD_ENV:-$HOME/.pii-anon-cloud.env}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

down() { echo ">>> deleting resource group $RG"; az group delete --name "$RG" --yes --no-wait || true; }

ssh_vm() { ssh -o StrictHostKeyChecking=accept-new "$ADMIN@$PUBLIC_IP" "$@"; }

up() {
  echo ">>> creating resource group $RG in $LOCATION"
  az group create --name "$RG" --location "$LOCATION" -o none

  echo ">>> creating spot GPU VM $VM_NAME ($VM_SIZE)"
  az vm create --resource-group "$RG" --name "$VM_NAME" --image "$IMAGE_URN" --size "$VM_SIZE" \
    --admin-username "$ADMIN" --generate-ssh-keys \
    --priority Spot --max-price -1 --eviction-policy Deallocate \
    --os-disk-size-gb 128 -o none
  [ "${KEEP_VM:-0}" = "1" ] || trap down EXIT     # auto-teardown unless KEEP_VM=1

  PUBLIC_IP="$(az vm show -d -g "$RG" -n "$VM_NAME" --query publicIps -o tsv)"
  echo ">>> VM public IP: $PUBLIC_IP"

  echo ">>> installing the NVIDIA GPU driver extension (this takes a few minutes)"
  az vm extension set --resource-group "$RG" --vm-name "$VM_NAME" \
    --name NvidiaGpuDriverLinux --publisher Microsoft.HpcCompute --version 1.6 -o none

  echo ">>> installing Docker + NVIDIA container toolkit on the VM"
  ssh_vm 'bash -s' <<'REMOTE'
set -e
sudo apt-get update -y
curl -fsSL https://get.docker.com | sudo sh
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -fsSL https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list >/dev/null
sudo apt-get update -y && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker
sudo usermod -aG docker $USER || true
nvidia-smi || echo "WARN: nvidia-smi not ready yet (driver extension may still be settling)"
REMOTE

  echo ">>> shipping the repo to the VM (excludes results/.git via rsync filter)"
  rsync -az --exclude '.git' --exclude 'results' --exclude 'logs' --exclude '.venv' \
    --exclude 'dist/*.parquet' "$REPO_ROOT/" "$ADMIN@$PUBLIC_IP:~/pii-anon-eval/"
  if [ -f "$PII_ANON_CLOUD_ENV" ]; then
    scp "$PII_ANON_CLOUD_ENV" "$ADMIN@$PUBLIC_IP:~/pii-anon-cloud.env"
  else
    echo "WARN: $PII_ANON_CLOUD_ENV not found — cloud detectors will be skipped (local lane still runs)."
  fi

  echo ">>> building the image + running the full leaderboard on the VM"
  ssh_vm "MAX_AZURE_USD=$MAX_AZURE_USD bash -s" <<'REMOTE'
set -e
cd ~/pii-anon-eval
sudo docker build -t pii-anon-eval .
ENVFILE=""; [ -f ~/pii-anon-cloud.env ] && ENVFILE="--env-file $HOME/pii-anon-cloud.env"
sudo docker run --rm --gpus all $ENVFILE \
  -v "$HOME/pii-anon-eval/results:/app/results" \
  -v "$HOME/pii-anon-eval/BASELINES.md:/app/BASELINES.md" \
  pii-anon-eval scripts/run_full_leaderboard.sh --max-azure-usd "$MAX_AZURE_USD" --yes
REMOTE

  echo ">>> fetching results back"
  rsync -az "$ADMIN@$PUBLIC_IP:~/pii-anon-eval/results/" "$REPO_ROOT/results/"
  rsync -az "$ADMIN@$PUBLIC_IP:~/pii-anon-eval/BASELINES.md" "$REPO_ROOT/BASELINES.md"
  echo ">>> done. Results in results/ ; multilingual card block updated in BASELINES.md"
  echo ">>> verifying resource group teardown..."
  az group delete --name "$RG" --yes --no-wait || true
  sleep 5
  if [ "$(az group exists --name "$RG" -o tsv 2>/dev/null)" = "true" ]; then
    echo "WARNING: resource group $RG still exists — deletion is async, but VERIFY it completes."
    echo "  MANUAL ACTION REQUIRED if it lingers: az group delete --name \"$RG\" --yes"
  else
    echo ">>> resource group $RG deleted (no lingering spot VM)."
  fi
}

case "${1:-up}" in
  up) up ;;
  down) down ;;
  *) echo "usage: $0 [up|down]"; exit 2 ;;
esac
