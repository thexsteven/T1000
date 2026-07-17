#!/bin/bash
# Polls the Stage 8 MasterThesis pipeline run every 5 min and logs status.
LOG=/home/ita/t1000/session-handoffs/monitoring/stage8_run_status.log
RUNDIR_BASE=/home/ita/MasterThesis/outputs/D63_Nr7_8/Versuch1
while true; do
  LATEST=$(ls -t "$RUNDIR_BASE" | head -1)
  TS=$(date '+%Y-%m-%d %H:%M:%S')
  RUNNING=$(pgrep -f "run_pipeline.py --config" | head -1)
  if [ -f "$RUNDIR_BASE/$LATEST/run_manifest.json" ]; then
    STATUS=$(python3 -c "
import json
d=json.load(open('$RUNDIR_BASE/$LATEST/run_manifest.json'))
print('completed_stages=' + str(d.get('completed_stages')))
print('end_time=' + str(d.get('end_time')))
print('error=' + str(d.get('error_message')))
" 2>/dev/null)
  else
    STATUS="no manifest yet"
  fi
  echo "[$TS] run_dir=$LATEST pid=${RUNNING:-none} $STATUS" >> "$LOG"
  sleep 300
done
