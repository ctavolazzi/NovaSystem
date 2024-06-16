#/bin/sh

PB_URL=${PB_URL:-https://${HTTP_HOSTNAME}}
TOKEN=${TOKEN:-"please-provide-a-token"}

first=1
last=100
i=$first

while [ $i -le $last ]
do
  data="{\"title\": \"post ${i}\",  \"body\": \"body for post ${i}\"}"
  curl "${PB_URL}/api/collections/posts/records" \
    -H 'Content-Type: application/json' \
    -H "Authorization: $TOKEN" \
    --data "$data"
  i=$(($i+1))
done