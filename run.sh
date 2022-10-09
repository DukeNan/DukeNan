#!/bin/bash

function cleanGitLog () {
   echo '=========清除git日志========='
   
    logHashCode=$(git log --pretty=format:"%ad=%H=%s" | grep -v 'CST' | head -n 1 | awk -F "=" '{print $2}')
    git pull
    git reset "$logHashCode"
    git checkout .
}

function updateRepository () {
    echo '=========更新代码仓库========='

    python -m pip install --upgrade pip
    pip install -r requirements.txt
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
   git push -f
}

cleanGitLog
updateRepository
commitRepository