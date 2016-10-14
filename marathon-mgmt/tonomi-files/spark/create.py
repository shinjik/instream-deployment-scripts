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
    configuration['configuration.portMappings'] = [{'8088':'0'},{'8042':'0'},{'4040':'0'},{'2122':'0'}]
    configuration['configuration.imageId'] = 'sequenceiq/spark:1.6.0'
    configuration['configuration.labels'] = {'_tonomi_application': 'spark'}
    cassandra = configuration['configuration.cassandraEndpoint'].split(':')
    redis = configuration['configuration.redisEndpoint'].split(':')
    configuration['configuration.env'] = {
        "CASSANDRA_HOST": cassandra[0],
        "CASSANDRA_PORT": cassandra[1],
        "KAFKA_BROKER_LIST": configuration['configuration.kafkaBrokers'],
        "REDIS_HOST": redis[0],
        "REDIS_PORT": redis[1]  
    }  
    configuration['configuration.cmd'] = "bash ${MESOS_SANDBOX}/streaming-runner.sh"
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
