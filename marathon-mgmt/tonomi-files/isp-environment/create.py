#!/usr/bin/env python3

import sys
import yaml

import marathon_comm
from model import InstreamEnvironment


arguments = yaml.safe_load(sys.stdin)

marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')

env_ids = list(arguments.get('launch-instances', {}).keys())

instance_results = {}

for env_id in env_ids:
    #command_id = list(arguments.get('instances', {}).get(app).get('commands').keys())[0]
    configuration = arguments.get('launch-instances').get(env_id).get('configuration')
    
    e = InstreamEnvironment(marathon_url)
    e.id = configuration['configuration.name']
    e.create()


    instance_results[configuration['configuration.name']] = {
        'instanceId': env_id,
        '$set': {
            'status.flags.converging': True,
            'status.flags.active': False  
           }
    }


result = {
    'instances': instance_results
}

yaml.safe_dump(result, sys.stdout)
