#!/bin/bash
user="";
if [ -n "$1" ]; then
    user="$1"@
fi
ssh "$user"tools-dev.wmflabs.org <<'ENDSSH'
become visualcategories
cd bestImage

echo "Pulling changes from Git..."
git pull
git log @{1}.. --oneline --reverse -C --no-merges

echo "Updating dependencies..."
./bin/build.sh

echo "Deploy done."
echo "Please update the Server Admin Log via IRC:"
echo "https://webchat.freenode.net/?channels=#wikimedia-labs"

webservice restart
ENDSSH
