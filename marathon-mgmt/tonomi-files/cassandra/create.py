#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint
from marathon.models.app import PortDefinition, Residency
from marathon.models.container import *
from lambdas import *
from manager import *

args = parse_args()
manager = MarathonManager(get_marathon_url(args))
instances = {}

for instance_id, app in args['launch-instances'].items():
  instance_name = get_name_from_configuration(app)
  ports = get_cassandra_ports(app)

  cassandra = Cassandra(name=instance_name, ports=ports)
  manager.create(cassandra)

  instances[instance_name] = {
    'instanceId': instance_id,
    'name': instance_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

return_instances_info(instances)
