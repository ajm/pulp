#!/bin/bash

set -e
set -v

TOPLEVELDIR=results_mallet_sim
SIMDIR=results3
THREADS=1
NUMDOCS=200
NUMSHOWN=20
NUMITER=10

for RATE in 1.0 0.8 0.6 0.4 0.2 0.0 ; do 
    date
    echo "RATE = $RATE"
    DIR=${TOPLEVELDIR}/${SIMDIR}_${RATE}
    mkdir -p $DIR
    python parse_mallet.py mallet/dorota_curated_topics.txt mallet/80000composition.txt $NUMDOCS \
        | xargs -P $THREADS -I {} nice python pulp_simulator3.py $DIR $RATE $NUMSHOWN $NUMITER {} #&> /dev/null
done

