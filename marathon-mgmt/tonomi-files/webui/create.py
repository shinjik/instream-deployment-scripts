#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from webui import *
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for instance_id, app in args['launch-instances'].items():
  configuration = app.get('configuration')
  env_name = configuration.get('configuration.name')
  tonomi_cluster_name = '/{}/webui'.format(env_name)

  webui_app = WebUINodes(env_name, marathon_client)
  webui_app.create()

  instances[tonomi_cluster_name] = {
    'instanceId': instance_id,
    'name': tonomi_cluster_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

return_instances_info(instances)
