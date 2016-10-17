import sys
import yaml

import marathon_comm
from marathon_app import MarathonApplication

class KafkaApp(MarathonApplication):
    _type = 'kafka'

    

    def get_info(self):
        
        ens = []
        for task in self.tasks:
            ens.append(task['host'] + ':' + task['portMappings']['9092'])

        return {
            'lbPort': str(self.port_mappings['9092']),
            'endpoints': ','.join(ens),
            'endpointLB': self.lb_host + ':' + str(self.port_mappings['9092'])
        }