#!/bin/sh

cd LivEx/
npm i
npm run langium:generate
npm run build
node out/app.js &
node_pid=$!
cd ../
docker compose up -d --build
echo "liverec  |  * Running on http://127.0.0.1:5000"
echo "liverec  |  * Running on http://172.19.0.2:5000"
echo "Press q to stop the app"
while read -n1 char
do
    if [ $char == "q" ]; then
        break
    fi
done
kill $node_pid
docker kill liverec