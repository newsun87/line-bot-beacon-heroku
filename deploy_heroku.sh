git config --global user.email 'newsun87@mail.sju.edu.tw'
git config --global user.name 'newsun87'
git init
heroku git:remote -a line-beacon-bot #設定你要上傳的app
heroku config:add TZ="Asia/Taipei"
#上傳
git add .
git commit -m "init."
git push heroku master #將主幹(master)進度部屬至Heroku
