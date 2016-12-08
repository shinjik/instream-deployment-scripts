#!/bin/sh

read input
url=`echo "$input" | sed -n "s|{url: [\'\"]\(.*\)[\'\"]}|\1|p"` &&
rm -f repo.zip repo.tar.gz &&

case "$url" in
	*github\.com*\.zip)
		wget -q -O repo.zip "$url" || apk add --update openssl && wget -q -O repo.zip "$url" &&
		folder=`echo "$url" | cut -d/ -f 5` &&
		branch=`echo "$url" | sed -n 's/\(.*\)archive\/\(.*\).zip/\2/p'` &&

		if [[ ! -z "$branch" && ! -z "$folder" ]]; then
			# usage of such links is deprecated
			rm -rf ${folder}-${branch} &&
			unzip repo.zip > /dev/null &&
			find ${folder}-${branch}/components/tonomi-scripts/scripted-components -name "*.py" -type f -exec chmod +x {} \; &&
			rm -rf /common /marathon /zookeeper /redis /cassandra /kafka /webui /spark /isp-environment /tw-consumer &&
			mv ${folder}-${branch}/components/tonomi-scripts/scripted-components/* / &&
			rm -rf ${folder}-${branch}
		else
			rm -rf manifests tonomi-scripts &&
			unzip repo.zip > /dev/null &&
			find tonomi-scripts/scripted-components -name "*.py" -type f -exec chmod +x {} \; &&
			rm -rf /common /marathon /zookeeper /redis /cassandra /kafka /webui /spark /isp-environment /tw-consumer &&
			mv tonomi-scripts/scripted-components/* /
		fi
		;;

	*\.tar\.gz*)
		wget -q -O repo.tar.gz "$url" || apk add --update openssl && wget -q -O repo.tar.gz "$url" &&
		rm -rf manifest tonomi-scripts &&
		tar -zxf repo.tar.gz &&
		find tonomi-scripts/scripted-components -name "*.py" -type f -exec chmod +x {} \; &&
		rm -rf /common /marathon /zookeeper /redis /cassandra /kafka /webui /spark /isp-environment /tw-consumer &&
		mv tonomi-scripts/scripted-components/* /
		;;

	*)
	  echo "unknown url"
	  exit 1
	  ;;
esac &&

echo "{result: \"$url\"}"
exit 0
