#!/bin/bash

set -e
set -v

TOPLEVELDIR=results_mallet_sim
SIMDIR=results2
THREADS=30

#for RATE in 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 ; do
#for RATE in 0.0 0.2 0.4 0.6 0.8 1.0 ; do
for RATE in 2 4 8 16 32 ; do
    date
    echo "RATE = $RATE"
    DIR=${TOPLEVELDIR}/${SIMDIR}_${RATE}
    mkdir -p $DIR
    python parse_mallet.py mallet/dorota_curated_topics.txt mallet/80000composition.txt 500 | xargs -P $THREADS -I {} nice python pulp_simulator2.py $DIR $RATE {} #&> /dev/null
done

