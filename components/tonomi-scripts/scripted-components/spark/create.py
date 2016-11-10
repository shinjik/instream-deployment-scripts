#!/usr/bin/env python3

import sys
import yaml
from utils import *
from models import *

args = parse_args()
manager = MarathonManager(get_marathon_url(args))
instances = {}

for instance_id, app in args['launch-instances'].items():
  instance_name = get_name_from_conf(app)
  cassandra_host = get_conf_prop(app, 'cassandra-host')
  cassandra_port = get_conf_prop(app, 'cassandra-port')
  redis_host = get_conf_prop(app, 'redis-host')
  redis_port = get_conf_prop(app, 'redis-port')
  kafka_host = get_conf_prop(app, 'kafka-host')
  kafka_port = get_conf_prop(app, 'kafka-port')

  spark = Spark(name=instance_name,
                cassandra_host=cassandra_host, cassandra_port=cassandra_port,
                redis_host=redis_host, redis_port=redis_port,
                kafka_host=kafka_host, kafka_port=kafka_port)
  manager.create(spark)

  instances[instance_name] = {
    'instanceId': instance_id,
    'name': instance_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

return_instances_info(instances)