import sys
import yaml

import marathon_comm
from marathon_app import MarathonApplication

class WebUIApp(MarathonApplication):
    _type = 'web-ui'

    _dependencies = {
        'cassandraEndpoint': None,
        'applicationUrl': 'https://s3-us-west-1.amazonaws.com/streaming-artifacts/ui.tar.gz'
    }

    def get_info(self):
        
        uis = []
        for task in self.tasks:
            uis.append('http://' + task['host'] + ':' + task['portMappings']['3000'])

        return {
            
            'endpoints': uis,
            'URL': 'http://' + self.lb_host + ':' + str(self.port_mappings['3000'])
        }

    def _get_creation_defaults(self):
        configuration = {}
        configuration['configuration.name'] = self.id
        configuration['configuration.cpu'] = 0.2
        configuration['configuration.ram'] = 768
        configuration['configuration.disk'] = 1024
        configuration['configuration.instances'] = 1
        configuration['configuration.portMappings'] = [{'3000':'0'}]

    
        cassandra = self.get_dependency('cassandraEndpoint').split(':')

    
        configuration['configuration.env'] = {
            "CASSANDRA_HOST": cassandra[0],
            "CASSANDRA_PORT": cassandra[1] 
        }  
        # configuration['configuration.applicationUrl']
        
        configuration['configuration.cmd'] = "cd ${MESOS_SANDBOX}/webclient && npm install && npm start"
        configuration['fetch'] = [{ "uri": self.get_dependency('applicationUrl'), "executable": False, "cache": False}]


        configuration['configuration.imageId'] = 'node'
        configuration['configuration.labels'] = {'_tonomi_application': 'web-ui'}

        return [configuration]