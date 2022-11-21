#!/bin/bash

function cleanGitLog () {
   echo '=========清除git日志========='

   git pull
   git checkout -b shaun
   git checkout main
   logHashCode=$(git log --pretty=format:"%ad=%H=%s" | grep -v 'CST' | head -n 1 | awk -F "=" '{print $2}')
   logInfo=$(git log --pretty=format:"%ad=%H=%s" | grep -v 'CST' | head -n 1 | awk -F "=" '{print $1, $3}')

   echo '查看git提交日志'
   # git log -n 5
   git log --pretty=format:"%ad %H %s" | xargs -I {} echo {};

   # echo "git回退日志信息: ${logInfo}"
   git reset --hard "$logHashCode"
   git merge --squash shaun
}

function updateRepository () {
    echo '=========更新代码仓库========='

   #  python -m pip install --upgrade pip
   #  pip install -r requirements.txt
    python3 update.py
    if [[ -z $(git diff) ]]; then exit 0; fi
    wget -O ./images/weather.png  wttr.in/Shenzhen_0pqm_lang=en.png
}

function commitRepository () {
   echo '=========提交代码仓库========='
   
   git add .
   git config --global user.email "dukenan006@163.com"
   git config --global user.name "shaun"
   git commit -m "update README,  $(date "+%a %b %d %H:%M %Z")" || echo "No changes to commit"
   git checkout -D shaun
   git push -f
}

cleanGitLog
updateRepository
commitRepository