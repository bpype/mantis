#!/bin/bash

# # delete stale grandalf
# rm -rf ./grandalf
# # oddly, github can convert to svn and then I can checkout the folder as an svn repo...?
# # get it
# svn checkout https://github.com/bdcht/grandalf/trunk/grandalf/
# # delete the .svn stuff and the __pycache__ if they exist
# rm -rf ./grandalf/.svn
# github no longer supports this, darn
#
# https://www.educative.io/answers/how-to-download-a-single-folder-or-directory-from-a-github-repo
#
# i have already set it up for sparse checkout but it doesn't do exactly what I want so I have top fudge it
# pass
if [[ -d "./grandalf/__pycache__" ]]
then
    rm -r ./grandalf/__pycache__
fi
if [[ -d "./grandalf/utils/__pycache__" ]]
then
    rm -r ./grandalf/utils/__pycache__
fi

mkdir grandalf 2>/dev/null # we don't need the error message
cd grandalf

if [[ -d "./.git" ]]
then
    echo 'skipping initialize grandalf because it already exists'
    rm -rf utils
    rm -rf *.py # danger here
else
    git init
    git remote add origin https://github.com/bdcht/grandalf.git
    echo 'grandalf' > .git/info/sparse-checkout
    git config core.sparseCheckout true
fi

git restore *
git pull origin master
mv ./grandalf/* .
rmdir grandalf
rm ./utils/__init__.py
rm __init__.py
# there is probably a right way to do this but the extensions thing makes it really irritating
# annoying

# fix the imports, they need to be made relative to Mantis.
sed -i 's/grandalf\.utils/.utils/g' ./*.py # annoyingly, it isn't consistent in the repo
# sed -i 's/\.utils/.grandalf.utils/g' ./*.py

# no idea why anything this stupid and bad and dumb is necessary
sed -i 's/from \.utils import Poset/from \.utils.poset import Poset/g' ./*.py
# this works
cd ..
