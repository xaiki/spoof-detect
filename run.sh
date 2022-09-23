#!/bin/sh
set -e

PY=python3
PARALLEL=$(cat /proc/cpuinfo | grep processor | wc -l)

echo "📊 detected ${PARALLEL} cores"
echo "🏛 fetching entities"
${PY} ./python/get_entities.py
echo "🌏 getting vendor data"
${PY} ./python/vendor.py --parallel $PARALLEL
echo "☠ getting extra backgrounds from OpenFish"
${PY} ./python/openfish.py --parallel $PARALLEL
echo "✨ augmenting data"
${PY} ./python/augment.py
echo "🖼 croping augmented data"
${PY} ./python/crop.py ./data/augmented/images
echo "🧠 train model"
sh train.sh
