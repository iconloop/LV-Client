if [[ -z $1 ]]; then
  echo "... No clue file supplied: $1"
  echo "... Proceed: VPR -> TOKEN -> READ"
else
  echo "Clue file supplied..."
  echo "... Proceed: VPR -> TOKEN -> STORE -> READ"
fi

# ===========================
echo "--Run Local Test--"
echo "GET VPR from LV-Manager"
lv-tool vpr -e localhost:8487 -o vpr.json
cat vpr.json
echo "GET Storages from LV-Manager"
lv-tool vid -e localhost:8487 -f vpr.json -o storages.json
cat storages.json
echo ""
echo "GET Tokens from LV-Storages"
lv-tool token -f storages.json -o token_output.json
cat tokens.json

if [[ -z $1 ]]; then
  echo ""
  echo "READ clues from LV-Storages"
  lv-tool read -f token_output.json -o restored_clues.txt
else
  echo ""
  echo "STORE clues to LV-Storages"
  lv-tool store "$1" -f token_output.json -o store_output.json
  cat store_output.json
  echo ""
  echo "READ clues from LV-Storages"
  lv-tool read -f store_output.json -o restored_clues.txt

  #cat restored_clues.txt
  cmp --silent $1 restored_clues.txt && echo 'Restore success.' || echo 'Fail: Clues Are Different!'
fi
