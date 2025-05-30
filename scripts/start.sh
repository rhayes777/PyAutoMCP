#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Script is running from: $DIR"

source ~/.zshrc
conda activate automcp
which python
python "$DIR/aggregator.py"

