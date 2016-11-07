#!/usr/bin/env python3

import sys
import yaml
from lambdas import *
from manager import *

args = parse_args()
manager = MarathonManager(get_marathon_url(args))
instances = {}

for instance_id, app in args['launch-instances'].items():
  instance_name = get_name_from_configuration(app)
  ports = get_conf_prop(app, 'ports')

  zookeeper = Zookeeper(name=instance_name, ports=ports)
  manager.create(zookeeper)

  instances[instance_name] = {
    'instanceId': instance_id,
    'name': instance_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

return_instances_info(instances)
