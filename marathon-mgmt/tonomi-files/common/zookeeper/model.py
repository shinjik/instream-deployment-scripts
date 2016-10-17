import sys
import yaml

import marathon_comm
from marathon_app import MarathonApplication

class ZookeeperApp(MarathonApplication):
    _type = 'zookeeper'

    

    def get_info(self):
        
        ens = []
        for task in self.tasks:
            ens.append(task['host'] + ':' + task['portMappings']['2181'])

        return {
            'lbPort': str(self.port_mappings['2181']),
            'ensembleUrl': ','.join(ens),
            'ensembleUrlLB': self.lb_host + ':' + str(self.port_mappings['2181'])
        }

    def _get_creation_defaults(self):
        configuration = {}
        configuration['configuration.name'] = self.id
        configuration['configuration.cpu'] = 0.2
        configuration['configuration.ram'] = 256
        configuration['configuration.disk'] = 100
        configuration['configuration.instances'] = 1
        
        configuration['configuration.portMappings'] = [{'2181':'0'}]
        configuration['configuration.imageId'] = 'wurstmeister/zookeeper'
        configuration['configuration.labels'] = {'_tonomi_application': 'zookeeper'}

        return [configuration]
    