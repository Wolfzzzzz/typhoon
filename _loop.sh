#!/bin/zsh
export HTTP_PROXY=http://127.0.0.1:60059
export HTTPS_PROXY=http://127.0.0.1:60059
export NO_PROXY=localhost,127.0.0.1,*.local
cd /Users/zzn/WorkBuddy/Claw/typhoon_realtime/site
echo "$(date) loop start" >> _cron.log
while true; do
  /Users/zzn/.workbuddy/binaries/python/versions/3.13.12/bin/python3 build_data.py >> _cron.log 2>&1
  /Users/zzn/.workbuddy/binaries/python/versions/3.13.12/bin/python3 _api_push.py >> _cron.log 2>&1
  echo "$(date) cycle done" >> _cron.log
  sleep 600
done
