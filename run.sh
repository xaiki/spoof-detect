#!/bin/sh

PY=python3
echo "🏛 fetching entities"
${PY} ./python/get_entities.py
echo "🌏 getting vendor data"
${PY} ./python/vendor.py --parallel $(cat /proc/cpuinfo | grep processor | wc -l)
echo "✨ augmenting data"
${PY} ./python/augment.py
echo "🖼 croping augmented data"
${PY} ./python/crop.py ./data/augmented/images
echo "TODO: 🧠 train model"
