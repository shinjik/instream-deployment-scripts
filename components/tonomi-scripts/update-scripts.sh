#!/bin/sh

read input
url=`echo "$input" | sed -n "s|{url: [\'\"]\(.*\)[\'\"]}|\1|p"`
rm -rf repo.zip
wget -q -O repo.zip "$url" || apk add --update openssl && wget -q -O repo.zip "$url"
folder=`echo "$url" | cut -d/ -f 5`
branch=`echo "$url" | sed -n 's/\(.*\)archive\/\(.*\).zip/\2/p'`
rm -rf ${folder}-${branch}
unzip repo.zip > /dev/null
find ${folder}-${branch}/components/tonomi-scripts/scripted-components -name "*.py" -type f -exec chmod +x {} \;
rm -rf /common /marathon /zookeeper /redis /cassandra /kafka /webui /spark /isp-environment /tw-consumer
mv ${folder}-${branch}/components/tonomi-scripts/scripted-components/* /
rm -rf ${folder}-${branch}
echo "{result: \"$url\"}"
exit 0
