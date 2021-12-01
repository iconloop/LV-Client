if [[ -z $1 ]]; then
  echo "... No clue file supplied: $1"
  echo "... Proceed: VPR -> TOKEN -> READ"
else
  echo "Clue file supplied..."
  echo "... Proceed: VPR -> TOKEN -> STORE -> READ"
fi

# ===========================
echo ""
echo "GET VPR from LV-Manager"
lv-tool vpr -e lv-manager.iconscare.com -o vpr.json
cat vpr.json
echo "GET Storages from LV-Manager"
lv-tool vid -e lv-manager.iconscare.com -f vpr.json -o storages.json
cat storages.json
echo ""
echo "GET Tokens from LV-Storages"
lv-tool token -f storages.json -o tokens.json
cat tokens.json

if [[ -z $1 ]]; then
  echo ""
  echo "READ clues from LV-Storages"
  lv-tool read -f tokens.json -o restored_clues.txt
else
  echo ""
  echo "STORE clues to LV-Storages"
  lv-tool store "$1" -f tokens.json -o store_output.json
  cat store_output.json
  echo ""
  echo "READ clues from LV-Storages"
  lv-tool read -f store_output.json -o restored_clues.txt
fi
cat restored_clues.txt

