#!/usr/bin/env bash
# Push a python snippet into the live `mats` ipython kernel via atomic bracketed paste.
#   src/push.sh path/to/snippet.py          # paste a file
#   echo "print(6*7)" | src/push.sh         # paste from stdin
# nnsight 0.7 needs `with lm.trace()` blocks as real cell input, so this beats %run.
set -euo pipefail
SESS="${MATS_TMUX:-mats}"
tmpf="$(mktemp)"
if [ "${1:-}" = "" ] || [ "${1:-}" = "-" ]; then cat > "$tmpf"; else cat "$1" > "$tmpf"; fi
printf '\n' >> "$tmpf"                       # ensure trailing newline executes the cell
tmux send-keys -t "$SESS" C-u                # clear any stale input buffer
tmux load-buffer -b mats_push "$tmpf"
tmux paste-buffer -t "$SESS" -b mats_push -d -p
sleep 0.3
tmux send-keys -t "$SESS" Enter              # submit (bracketed paste needs a final Enter)
tmux send-keys -t "$SESS" Enter              # close any open def/block
rm -f "$tmpf"
