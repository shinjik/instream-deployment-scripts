import sys
import yaml

import marathon_comm
from marathon_app import MarathonApplication

class SparkApp(MarathonApplication):
    _type = 'spark'

    _dependencies = {
        'cassandraEndpoint': None,
        'redisEndpoint': None,
        'kafkaBrokers': None,
        'applicationUrl': 'https://s3-us-west-1.amazonaws.com/streaming-artifacts/in-stream-tweets-analyzer.tar.gz'
    }

    def get_info(self):
        
        ens = []
        for task in self.tasks:
            ens.append(task['host'] + ':' + task['portMappings']['4040'])

        return {
            
            'sparkManagers': ','.join(ens),
            'sparkManagerLB': self.lb_host + ':' + str(self.port_mappings['4040'])
        }

    def _get_creation_defaults(self):
        configuration = {}
    
        configuration['configuration.cmd'] = "bash ${MESOS_SANDBOX}/streaming-runner.sh"
        configuration['fetch'] = [{ "uri": self.get_dependency('applicationUrl'), "executable": False, "cache": False}]

        cassandra = self.get_dependency('cassandraEndpoint').split(':')
        redis = self.get_dependency('redisEndpoint').split(':')
        kafka = self.get_dependency('kafkaBrokers')

        configuration['configuration.env'] = {
            "CASSANDRA_HOST": cassandra[0],
            "CASSANDRA_PORT": cassandra[1],
            "KAFKA_BROKER_LIST": kafka,
            "REDIS_HOST": redis[0],
            "REDIS_PORT": redis[1]  
        }  

        configuration['configuration.name'] = self.id
        configuration['configuration.cpu'] = 1
        configuration['configuration.ram'] = 1024
        configuration['configuration.disk'] = 1024
        configuration['configuration.instances'] = 1
        
        configuration['configuration.portMappings'] = [{'8088':'0'},{'8042':'0'},{'4040':'0'},{'2122':'0'}]
        configuration['configuration.imageId'] = 'sequenceiq/spark:1.6.0'
        configuration['configuration.labels'] = {'_tonomi_application': 'spark'}

        return [configuration]