#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from utils import *
from models import MarathonManager

args = parse_args()
marathon_client = get_marathon_client(args)
manager = MarathonManager(get_marathon_url(args))
marathon_node_hostname = marathon_client.servers[0].split(':')[1][2:]
instances = {}

for env_app in args['instances'].keys():
  env = marathon_client.get_group(env_app)
  env_name = env.id.replace('/', '')

  status = {
    'flags': {
      'active': True,
      'converging': False,
      'failed': False
    }
  }

  interfaces = {}
  components = {}

  # zookeeper
  zookeeper_apps = manager.get_apps('zookeeper', env_name)
  zookeeper_hosts = []
  zookeeper_port = 0

  if len(zookeeper_apps) > 0:
    zookeeper_port = zookeeper_apps[0].labels['_client_conn_port']
    for app in zookeeper_apps:
      zookeeper_hosts += [task.host for task in app.tasks]

  interfaces['zookeeper'] = {
    'signals': {
      'zookeeper-hosts': zookeeper_hosts,
      'zookeeper-port': zookeeper_port
    }
  }

  # redis
  redis_masters = []
  redis_slaves = []
  redis_port = 0

  redis_master_apps = manager.get_apps('redis', env_name, 'redis-master')
  redis_slave_apps = manager.get_apps('redis', env_name, 'redis-slave')

  if len(redis_master_apps) > 0:
    redis_port = redis_master_apps[0].labels['_cluster_port']
    for app in redis_master_apps:
      redis_masters += [task.host for task in app.tasks]

  if len(redis_slave_apps) > 0:
    for app in redis_slave_apps:
      redis_slaves += [task.host for task in app.tasks]

  interfaces['redis'] = {
    'signals': {
      'master-hosts': redis_masters,
      'slave-hosts': redis_slaves,
      'port': redis_port
    }
  }

  # cassandra
  cassandra_seed_hosts = []
  cassandra_node_hosts = []
  cql_native_port = 0

  cassandra_seed_apps = manager.get_apps('cassandra', env_name, 'cassandra-seed')
  cassandra_node_apps = manager.get_apps('cassandra', env_name, 'cassandra-node')

  if len(cassandra_seed_apps) > 0:
    cql_native_port = cassandra_seed_apps[0].labels['_cql_native_port']
    for app in cassandra_seed_apps:
      cassandra_seed_hosts += [task.host for task in app.tasks]

  if len(cassandra_node_apps) > 0:
    for app in cassandra_node_apps:
      cassandra_node_hosts += [task.host for task in app.tasks]

  interfaces['cassandra'] = {
    'signals': {
      'seed-hosts': cassandra_seed_hosts,
      'node-hosts': cassandra_node_hosts,
      'cql-native-port': cql_native_port
    }
  }

  # kafka
  kafka_apps = manager.get_apps('kafka', env_name)
  kafka_hosts = []
  kafka_port = 0

  if len(kafka_apps) > 0:
    kafka_port = kafka_apps[0].labels['_cluster_port']
    for app in kafka_apps:
      kafka_hosts += [task.host for task in app.tasks]

  interfaces['kafka'] = {
    'signals': {
      'kafka-hosts': kafka_hosts,
      'kafka-port': kafka_port
    }
  }

  # webui
  link = ''
  webui_hosts = []

  webui_apps = manager.get_apps('webui', env_name)
  if len(webui_apps) > 0:
    service_port = webui_apps[0].container.docker.port_mappings[0].service_port
    link = 'http://{}:{}'.format(marathon_client.servers[0].split(':')[1][2:], service_port)
    for app in webui_apps:
      webui_hosts += [task.host for task in app.tasks]

  interfaces['webui'] = {
    'signals': {
      'link': link,
      'hosts': webui_hosts
    }
  }

  # spark
  spark_hosts = []
  spark_link = ''

  spark_apps = manager.get_apps('spark', env_name)
  if len(spark_apps) > 0:
    service_port = spark_apps[0].container.docker.port_mappings[2].service_port
    spark_link = 'http://{}:{}'.format(marathon_client.servers[0].split(':')[1][2:], service_port)
    for app in spark_apps:
      spark_hosts += [task.host for task in app.tasks]

  interfaces['spark'] = {
    'signals': {
      'hosts': spark_hosts,
      'web-interface': spark_link
    }
  }

  # endpoint
  interfaces['application-entrypoint'] = {
    'signals': {
      'URL': link
    }
  }

  for app_name in ['zookeeper', 'redis', 'cassandra', 'kafka', 'webui', 'spark']:
    components[app_name] = {
      'reference': {
        'mapping': '{}.{}-by-id'.format(app_name, app_name),
        'key': '/{}/{}'.format(env_name, app_name)
      }
    }

  instances[env_app] = {
    'instanceId': env_app,
    'name': env_app,
    'status': status,
    'interfaces': interfaces,
    'components': components,
  }

return_instances_info(instances)
