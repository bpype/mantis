#!/bin/bash

# delete stale grandalf
rm -rf ./grandalf
# oddly, github can convert to svn and then I can checkout the folder as an svn repo...?
# get it
svn checkout https://github.com/bdcht/grandalf/trunk/grandalf/
# delete the .svn stuff and the __pycache__ if they exist
rm -rf ./grandalf/.svn
if [[ -d "./grandalf/__pycache__" ]]
then
    rm -r ./grandalf/__pycache__
fi
if [[ -d "./grandalf/utils/__pycache__" ]]
then
    rm -r ./grandalf/utils/__pycache__
fi
# fix the imports, they need to be made relative to Mantis.
sed -i 's/grandalf\.utils/.utils/g' ./grandalf/*.py # annoyingly, it isn't consistent in the repo
sed -i 's/\.utils/mantis.grandalf.utils/g' ./grandalf/*.py
# this works
