#! /bin/bash
set -e

PATH=/root/miniconda3/bin:/opt/local/bin:/usr/local/bin:$PATH ; export PATH
LD_LIBRARY_PATH=/usr/local/lib:/opt/local/lib ; export LD_LIBRARY_PATH

cd /var/www/html/kne/astrocats
python -m astrocats kilonovae git-pull
python -m astrocats kilonovae import
SNEUPDATE=$?
echo $SNEUPDATE
if [[ $SNEUPDATE == 0 ]]; then
	astrocats/kilonovae/scripts/generate-web.sh
	python -m astrocats kilonovae git-pull
	python -m astrocats kilonovae git-push
	#stamp=$(date +"%Y-%m-%d %k:%M")
	#./commit-and-push-repos.sh "Auto update: $stamp"
fi
