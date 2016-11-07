#!/usr/bin/env python3

import sys
import yaml
from lambdas import *
from manager import *
import time

args = parse_args()
manager = MarathonManager(get_marathon_url(args))
instances = {}

for env_id, env in args['launch-instances'].items():
  env_name = get_conf_prop(env, 'name')
  short_env_name = env_name.replace('/', '')

  ports_pool = manager.free_ports(11)

  # 1. zookeeper cluster
  zookeeper_ports = ports_pool[0:3]
  zookeeper = Zookeeper(name='{}/zookeeper'.format(env_name), ports=zookeeper_ports, env_name=short_env_name)
  manager.create(zookeeper)

  # 2. redis cluster
  redis_port = ports_pool[3]
  redis = Redis(name='{}/redis'.format(env_name), port=redis_port, env_name=short_env_name)
  manager.create(redis)

  # 3. cassandra cluster
  cassandra_ports = {
    9042: ports_pool[4],
    9160: ports_pool[5],
    7199: ports_pool[6],
    7000: ports_pool[7],
    7001: ports_pool[8]
  }
  cassandra = Cassandra(name='{}/cassandra'.format(env_name), ports=cassandra_ports, env_name=short_env_name)
  manager.create(cassandra)

  # 4. kafka cluster
  zookeeper_host = manager.get_app_host(app_type='zookeeper', env_name=short_env_name)
  zookeeper_port = zookeeper_ports[0]
  kafka_port = ports_pool[9]
  kafka = Kafka(name='{}/kafka'.format(env_name), zookeeper_host=zookeeper_host, zookeeper_port=zookeeper_port,
                port=kafka_port, env_name=short_env_name)
  manager.create(kafka)

  # TODO: populate apps!
  # 5. redis <- dictionaries,
  #    cassandra <- schema + movies list!

  # 6. web ui
  cassandra_host = manager.get_app_host(app_type='cassandra', env_name=short_env_name)
  cassandra_port = cassandra_ports[9042]
  service_port = ports_pool[10]
  webui = UI(name='{}/webui'.format(env_name), cass_host=cassandra_host, cass_port=cassandra_port,
             service_port=service_port, env_name=short_env_name)
  manager.create(webui)

  # 7. spark app
  redis_host = manager.get_app_host(app_type='redis', env_name=short_env_name)
  kafka_host = manager.get_app_host(app_type='kafka', env_name=short_env_name)
  spark = Spark(name='{}/spark'.format(env_name),
                cassandra_host=cassandra_host, cassandra_port=cassandra_port,
                redis_host=redis_host, redis_port=redis_port,
                kafka_host=kafka_host, kafka_port=kafka_port, env_name=short_env_name)
  manager.create(spark)

  instances[env_name] = {
    'instanceId': env_id,
    'name': env_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

return_instances_info(instances)
