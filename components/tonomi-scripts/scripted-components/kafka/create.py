#!/usr/bin/env python3

import sys
import yaml
from lambdas import *
from models import *

args = parse_args()
manager = MarathonManager(get_marathon_url(args))
instances = {}

for instance_id, app in args['launch-instances'].items():
  instance_name = get_name_from_configuration(app)
  zookeeper_host = get_conf_prop(app, 'zookeeper-host')
  zookeeper_port = get_conf_prop(app, 'zookeeper-port')
  port = get_conf_prop(app, 'port')

  kafka = Kafka(name=instance_name, zookeeper_host=zookeeper_host,
                zookeeper_port=zookeeper_port, port=port)
  manager.create(kafka)

  instances[instance_name] = {
    'instanceId': instance_id,
    'name': instance_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

return_instances_info(instances)