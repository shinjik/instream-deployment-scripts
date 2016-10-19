#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient

args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL')
marathon_client = MarathonClient(marathon_url)

instance_results = {}

for tonomi_cluster_name in args.get('instances', {}).keys():
    try:
        marathon_client.delete_app(tonomi_cluster_name)
    except:
        pass

    instance_results[tonomi_cluster_name] = {
        '$set': {
            'status.flags.converging': False,
            'status.flags.active': False
        }
    }

yaml.safe_dump({'instances': instance_results}, sys.stdout)
