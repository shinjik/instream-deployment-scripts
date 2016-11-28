#!/usr/bin/env python3

import sys
import yaml
from utils import *
from ephemeral import CassandraAddMovie
from models import *
from marathon import MarathonClient
from marathon.models import MarathonHealthCheck
import time

args = parse_args()
marathon_client = MarathonClient(get_marathon_url(args))
instances = {}

for instance_id, app in args['launch-instances'].items():
  instance_name = get_conf_prop(app, 'name')
  movie = get_conf_prop(app, 'movie')
  search_since = get_conf_prop(app, 'search-since')
  kafka_broker = get_conf_prop(app, 'kafka-broker')
  cassandra_host = get_conf_prop(app, 'cassandra-host')
  cassandra_port = get_conf_prop(app, 'cassandra-port')
  access_token = get_conf_prop(app, 'twitter-access-token')
  access_token_secret = get_conf_prop(app, 'twitter-access-token-secret')
  consumer_key = get_conf_prop(app, 'twitter-consumer-key')
  consumer_secret = get_conf_prop(app, 'twitter-consumer-secret')

  cmd = 'bash ${{MESOS_SANDBOX}}/twitter-consumer-runner.sh --movie "{}" --search-since "{}"'.format(movie, search_since)
  labels = {
    '_tonomi_application': 'twitter-consumer'
  }
  env = {
    'KAFKA_BROKER_LIST': kafka_broker,
    'TWITTER_ACCESS_TOKEN': access_token,
    'TWITTER_ACCESS_TOKEN_SECRET': access_token_secret,
    'TWITTER_CONSUMER_KEY': consumer_key,
    'TWITTER_CONSUMER_SECRET': consumer_secret
  }
  uris = ['https://s3-us-west-1.amazonaws.com/streaming-artifacts/twitter-consumer.tar.gz']
  name = '{}/{}'.format(instance_name, ''.join([i for i in movie if i.isalpha() or i == ' ']).lower().replace(' ', '-'))

  health_checks = [MarathonHealthCheck(grace_period_seconds=300, interval_seconds=60, max_consecutive_failures=3,
                                       protocol='COMMAND', timeout_seconds=20, ignore_http1xx=False,
                                       command={"value": 'test ! -z \"$(ps ax|egrep \"(twitter-consumer)*.(jar)\"|grep -v grep)\"'})]

  consumer_app = Node(name=name, image='java:8', labels=labels, cmd=cmd, env=env, uris=uris, cpus=0.1, mem=256, disk=0,
                      health_checks=health_checks)

  add_movie = CassandraAddMovie(marathon_client, cassandra_host, cassandra_port, movie)
  add_movie.commit()

  time.sleep(15)

  marathon_client.create_app(name, consumer_app.app)

  instances[instance_name] = {
    'instanceId': instance_id,
    'name': instance_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

return_instances_info(instances)
