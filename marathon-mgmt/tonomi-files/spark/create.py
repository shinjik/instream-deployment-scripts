#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint
from marathon.models.container import *
from marathon.models.app import PortDefinition, Residency
from spark import *
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for instance_id, app in args['launch-instances'].items():
  configuration = app['configuration']
  env_name = configuration.get('configuration.name')
  instance_name = '/{}/spark'.format(env_name)

  spark_app = SparkCluster(env_name, marathon_client)
  spark_app.create()

  instances[instance_name] = {
    'instanceId': instance_id,
    'name': instance_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

return_instances_info(instances)
