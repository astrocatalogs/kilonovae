#! /bin/bash
set -e

PATH=/opt/local/bin:/usr/local/bin:$PATH ; export PATH
LD_LIBRARY_PATH=/usr/local/lib:/opt/local/lib ; export LD_LIBRARY_PATH

cd /var/www/html/kne/astrocats
python -m astrocats.scripts.webcat -c kne &
pids[0]=$!
python -m astrocats.scripts.webcat -c kne -by &
pids[1]=$!
python -m astrocats.kilonovae.scripts.dupecat &
pids[2]=$!
python -m astrocats.kilonovae.scripts.conflictcat &
pids[3]=$!
python -m astrocats.scripts.bibliocat -c kne &
pids[4]=$!
python -m astrocats.kilonovae.scripts.erratacat &
pids[5]=$!
python -m astrocats.scripts.hostcat -c kne &
pids[6]=$!
python -m astrocats.scripts.hammertime -c kne &
pids[7]=$!
python -m astrocats.kilonovae.scripts.histograms &
pids[8]=$!
python -m astrocats.scripts.atelscbetsiaucs -c kne &
pids[9]=$!
#python -m astrocats.kilonovae.scripts.frbcat &
#pids[10]=$!
for pid in ${pids[*]}; do
	wait $pid
done
cd /var/www/html/kne/astrocats/astrocats/kilonovae/output/html
bash thumbs.sh
cd /var/www/html/kne/astrocats
