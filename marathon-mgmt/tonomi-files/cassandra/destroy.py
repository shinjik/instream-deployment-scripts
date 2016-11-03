#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from cassandra import *
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)

instances = {}

for instance_name in args['instances'].keys():
  CassandraCluster.delete_cluster(instance_name, marathon_client)

  instances[instance_name] = {
    '$set': {
      'status.flags.converging': False,
      'status.flags.active': False,
      'status.flags.failed': False
    }
  }

return_instances_info(instances)
