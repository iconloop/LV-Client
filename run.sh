if [[ -z $1 ]]; then
  echo "... No clue file supplied: $1"
  echo "... Proceed: VPR -> TOKEN -> READ"
else
  echo "Clue file supplied..."
  echo "... Proceed: VPR -> TOKEN -> STORE -> READ"
fi

# ===========================
lv-tool vpr -e localhost:8487 -o vpr.json
lv-tool vid -e -e localhost:8487 -f vpr.json -o storages.json
lv-tool token -f storages.json -o token_output.json
if [[ -z $1 ]]; then
  lv-tool read -f token_output.json -o restored_clues.txt
else
  lv-tool store "$1" -f token_output.json -o store_output.json
  lv-tool read -f store_output.json -o restored_clues.txt
fi
