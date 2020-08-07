#!/bin/bash

# 
# Usage: dump_db.sh <config file> <RSE> <nparts> <output file prefix>
#

config=$1
rse=$2
nparts=$3
out_prefix=$4

python db_dump.py -c $config -o $out_prefix -n $nparts $rse
