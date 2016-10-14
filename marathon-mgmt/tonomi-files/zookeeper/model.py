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