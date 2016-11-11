FROM qubell/python-scripting:latest

ADD scripted-components/update-scripts.sh /update-scripts.sh
ADD scripted-components/requirements.txt  /requirements.txt
ADD scripted-components/common            /common
ADD scripted-components/marathon          /marathon
ADD scripted-components/zookeeper         /zookeeper
ADD scripted-components/redis             /redis
ADD scripted-components/cassandra         /cassandra
ADD scripted-components/kafka             /kafka
ADD scripted-components/webui             /webui
ADD scripted-components/spark             /spark
ADD scripted-components/isp-environment   /isp-environment
ADD scripted-components/tw-consumer       /tw-consumer

RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt

ENV PYTHONPATH /common
