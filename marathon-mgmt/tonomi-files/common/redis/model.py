import sys
import yaml

import marathon_comm
from marathon_app import MarathonApplication

class RedisApp(MarathonApplication):
    _type = 'redis'

    def get_info(self):

        instances = []
        for task in self.tasks:
            instances.append(task['host'] + ':' + task['portMappings']['6379'])

        return {
            'lbPort': str(self.port_mappings['6379']),
            'instanceEndpoints': ','.join(instances),
            'instanceEndpointLB': self.lb_host + ':' + str(self.port_mappings['6379'])
        }

    def _get_creation_defaults(self):
        configuration = {}
        configuration['configuration.name'] = self.id
        configuration['configuration.cpu'] = 0.2
        configuration['configuration.ram'] = 256
        configuration['configuration.disk'] = 100
        configuration['configuration.instances'] = 1
        
        configuration['configuration.portMappings'] = [{'6379':'0'}]
        configuration['configuration.imageId'] = 'redis'
        configuration['configuration.labels'] = {'_tonomi_application': 'redis'}

        return [configuration]