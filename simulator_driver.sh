#!/bin/bash

set -e
set -v

SIMDIR=simulation_results
THREADS=50


mkdir -p $SIMDIR

python pulp_ml_articles.py | xargs -P $THREADS -I {} python pulp_simulator.py {} $SIMDIR > /dev/null

