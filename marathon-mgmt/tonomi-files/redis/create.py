#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint
from marathon.models.app import PortDefinition, Residency
from marathon.models.container import *
from redis import *
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)

instances = {}

for instance_id, app in args['launch-instances'].items():
  configuration = app['configuration']
  env_name = configuration.get('configuration.name')
  tonomi_cluster_name = '/{}/redis'.format(env_name)

  redis_cluster = RedisCluster(env_name, marathon_client)
  redis_cluster.create()

  instances[tonomi_cluster_name] = {
    'instanceId': instance_id,
    'name': tonomi_cluster_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

return_instances_info(instances)
