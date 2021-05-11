git add .
git config --global user.email "dukenan@163.com"
git config --global user.name "shaun"
git commit -m "update README,  $(date "+%a %b %d %H:%M %Z")" || echo "No changes to commit"
git push