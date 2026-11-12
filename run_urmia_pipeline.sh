#!/usr/bin/env bash
# =============================================================
# Urmia Lake Basin - LST & NDVI Analysis Pipeline
# Author : Javid Hojabri
# Repo   : satellite-geospatial-toolbox
# Purpose: Reproducible execution of the Urmia Lake Basin
#          Land Surface Temperature and NDVI workflows on Linux.
# Usage  : bash scripts/run_urmia_pipeline.sh
# =============================================================

# ---- Fail fast and safe -------------------------------------
# -e : exit on any error
# -u : treat unset variables as errors
# -o pipefail : catch errors inside pipes
set -euo pipefail

# ---- Paths --------------------------------------------------
# Resolve the repository root regardless of where the script is called from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

VENV_DIR="$REPO_ROOT/.venv"
OUTPUT_DIR="$REPO_ROOT/outputs"
LOG_DIR="$REPO_ROOT/logs"

# ---- Configuration ------------------------------------------
# Scripts to run (order matters: NDVI series first, then LST trend)
NDVI_SCRIPT="$REPO_ROOT/GEE_timeseries_analysis.py"
LST_SCRIPT="$REPO_ROOT/lst_trend_analysis_urmia.py"

# Study area: Lake Urmia Basin bounding box (WGS84)
export STUDY_AREA="Urmia Lake Basin"
export BBOX_MIN_LON="44.5"
export BBOX_MIN_LAT="36.5"
export BBOX_MAX_LON="47.5"
export BBOX_MAX_LAT="38.5"

echo "=============================================="
echo " Urmia Lake Basin Pipeline"
echo " Study area : $STUDY_AREA"
echo " BBOX       : [$BBOX_MIN_LON, $BBOX_MIN_LAT, $BBOX_MAX_LON, $BBOX_MAX_LAT]"
echo "=============================================="

# ---- 1. Prepare directories ---------------------------------
mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

# ---- 2. Check Python availability ---------------------------
if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] python3 not found. Install it with:"
    echo "        sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
    exit 1
fi

PYTHON_VERSION="$(python3 --version)"
echo "[OK] Found $PYTHON_VERSION"

# ---- 3. Create and activate a virtual environment -----------
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Creating virtual environment at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
echo "[OK] Virtual environment activated"

# ---- 4. Install dependencies --------------------------------
echo "[INFO] Installing Python dependencies..."
python -m pip install --upgrade pip >/dev/null
python -m pip install --quiet earthengine-api pandas numpy

# ---- 5. Verify Google Earth Engine authentication -----------
echo "[INFO] Checking Earth Engine authentication..."
if ! python -c "import ee; ee.Initialize()" >/dev/null 2>&1; then
    echo "[WARN] Earth Engine is not authenticated on this machine."
    echo "       Run the following command once, then re-run this script:"
    echo "         python -c \"import ee; ee.Authenticate()\""
    exit 1
fi
echo "[OK] Earth Engine authenticated"

# ---- 6. Run the NDVI time-series workflow -------------------
if [ -f "$NDVI_SCRIPT" ]; then
    echo "[INFO] Running NDVI time series: $(basename "$NDVI_SCRIPT")"
    python "$NDVI_SCRIPT" 2>&1 | tee "$LOG_DIR/ndvi_timeseries.log"
else
    echo "[WARN] Skipped: $NDVI_SCRIPT not found"
fi

# ---- 7. Run the LST trend workflow --------------------------
if [ -f "$LST_SCRIPT" ]; then
    echo "[INFO] Running LST trend analysis: $(basename "$LST_SCRIPT")"
    python "$LST_SCRIPT" 2>&1 | tee "$LOG_DIR/lst_trend.log"
else
    echo "[WARN] Skipped: $LST_SCRIPT not found"
fi

# ---- 8. Summary ---------------------------------------------
echo "=============================================="
echo "[DONE] Pipeline finished at $(date '+%Y-%m-%d %H:%M:%S')"
echo " Logs    : $LOG_DIR"
echo " Outputs : $OUTPUT_DIR"
echo "=============================================="

deactivate
