import sys
import yaml

import marathon_comm
from marathon_app import MarathonApplication

class CassandraApp(MarathonApplication):
    _type = 'cassandra'

    

    def get_info(self):
        
        ens = []
        for task in self.tasks:
            ens.append(task['host'] + ':' + task['portMappings']['9042'])

        return {
            'lbPort': str(self.port_mappings['9042']),
            'endpoints': ','.join(ens),
            'endpointLB': self.lb_host + ':' + str(self.port_mappings['9042'])
        }