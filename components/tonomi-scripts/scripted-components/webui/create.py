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
  cassandra_host, cassandra_port = get_cassandra_conf(app)
  service_port = get_conf_prop(app, 'service-port')

  webui = UI(name=instance_name, cass_host=cassandra_host,
             cass_port=cassandra_port, service_port=service_port)
  manager.create(webui)

  instances[instance_name] = {
    'instanceId': instance_id,
    'name': instance_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

return_instances_info(instances)
