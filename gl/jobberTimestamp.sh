
time_ns=$1
time_s=$((time_ns / 1000000000)) # integer division
time_uct=$((time_s + 18000)) # add 5hrs for UCT
date -r $time_uct
