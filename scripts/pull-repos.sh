#!/bin/bash

git pull
repos=($(awk -F= '{print $1}' ../input/rep-folders.txt))
repos+=('../input/kne-internal')
repos+=('../input/kne-external')
repos+=('../input/kne-external-radio')
repos+=('../input/kne-external-xray')
repos+=('../input/kne-external-spectra')
repos+=('../input/kne-external-WISEREP')
echo ${repos[*]}
cd ../output
for repo in ${repos[@]}; do
	cd ${repo}
	pwd
	git pull
	cd ..
done
