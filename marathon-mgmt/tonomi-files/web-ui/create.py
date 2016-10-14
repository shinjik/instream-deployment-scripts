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
    configuration['configuration.portMappings'] = [{'3000':'0'}]
    configuration['configuration.imageId'] = 'node'
    configuration['configuration.labels'] = {'_tonomi_application': 'web-ui'}
    cassandra = configuration['configuration.cassandraEndpoint'].split(':')
    
    configuration['configuration.env'] = {
        "CASSANDRA_HOST": cassandra[0],
        "CASSANDRA_PORT": cassandra[1] 
    }  
    configuration['configuration.cmd'] = "cd ${MESOS_SANDBOX}/cinema-chart && npm install && npm start"
    configuration['fetch'] = [{ "uri": configuration['configuration.applicationUrl'], "executable": False, "cache": False}]

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
