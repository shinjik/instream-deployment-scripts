#!/usr/bin/env python3

import sys
import yaml

import marathon_comm


arguments = yaml.safe_load(sys.stdin)

marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')

app_ids = list(arguments.get('launch-instances', {}).keys())

instance_results = {}

for app in app_ids:
    #command_id = list(arguments.get('instances', {}).get(app).get('commands').keys())[0]
    configuration = arguments.get('launch-instances').get(app).get('configuration')
    configuration['configuration.instances'] = 1
    #configuration['configuration.disk'] = 0
    configuration['configuration.portMappings'] = [{'9042':'0'}, {'9160':'0'}]
    configuration['configuration.imageId'] = 'poklet/cassandra'
    configuration['configuration.labels'] = {'_tonomi_application': 'cassandra'}
    configuration['configuration.constraints'] = [["hostname", "UNIQUE"]]
    configuration['configuration.cmd'] = "chown -R cassandra /var/lib/cassandra && start"
    volume_size = 2048
    if configuration.get('configuration.volumeSize', None):
        volume_size = configuration['configuration.volumeSize'] 
    volume_name = 'vol' + configuration['configuration.name'].replace('/', '-') + '-data'
    if volume_size > 0:
        configuration['volumes'] =  [
          {
            "containerPath": volume_name,
            "mode": "RW",
            "persistent": {
              "type": "root",
              "size": volume_size
            }
          },
          {
            "containerPath": "/var/lib/cassandra",
            "hostPath": volume_name,
            "mode": "RW"
          }
        ]

        configuration['residency'] = {
            "taskLostBehavior": "WAIT_FOREVER"
        }

    marathon_comm.create(marathon_url, configuration)

    instance_results[configuration['configuration.name']] = {
        'instanceId': app,
        '$set': {
            'status.flags.converging': True,
            'status.flags.active': False  
           }
    }


result = {
    'instances': instance_results
}

yaml.safe_dump(result, sys.stdout)
