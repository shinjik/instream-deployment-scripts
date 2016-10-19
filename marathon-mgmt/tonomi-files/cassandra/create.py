#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint
from marathon.models.container import *
from marathon.models.app import PortDefinition, Residency
from cassandra import *


args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL')
marathon_client = MarathonClient(marathon_url)

instance_results = {}

for tonomi_cluster_id, app in args.get('launch-instances', {}).items():
  configuration = app.get('configuration')
  env_name = configuration.get('configuration.name')
  tonomi_cluster_name = '/{}/cassandra'.format(env_name)

  cassandra_cluster = CassandraCluster(env_name, marathon_client)
  cassandra_cluster.create()

  instance_results[tonomi_cluster_name] = {
    'instanceId': tonomi_cluster_id,
    'name': tonomi_cluster_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

yaml.safe_dump({ 'instances': instance_results }, sys.stdout)
