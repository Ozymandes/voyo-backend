#!/usr/bin/env bash
# Download Egypt OSM extract for Valhalla tile processing.
# Run once before `docker-compose up` if you want to pre-seed the tiles.
#
# Usage:
#   bash config/valhalla/download_egypt_osm.sh
#
# If you skip this script, the Valhalla Docker container will download
# the extract automatically on first start (slower, but works).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_DIR="${SCRIPT_DIR}/custom_files"

mkdir -p "${DEST_DIR}"

OSM_URL="https://download.geofabrik.de/africa/egypt-latest.osm.pbf"
DEST_FILE="${DEST_DIR}/egypt-latest.osm.pbf"

if [ -f "${DEST_FILE}" ]; then
    echo "OSM extract already exists at ${DEST_FILE}"
    echo "Delete it and re-run to download a fresh copy."
    exit 0
fi

echo "Downloading Egypt OSM extract from Geofabrik..."
echo "  URL: ${OSM_URL}"
echo "  Destination: ${DEST_FILE}"
echo ""

curl -L --progress-bar -o "${DEST_FILE}" "${OSM_URL}"

FILE_SIZE=$(du -h "${DEST_FILE}" | cut -f1)
echo ""
echo "Download complete! File size: ${FILE_SIZE}"
echo ""
echo "Now run:  docker-compose up -d"
echo "Valhalla will process the PBF into routable tiles on first start (~5-10 min)."
