import sys
import yaml

import marathon_comm
from marathon_app import MarathonApplication

class SparkApp(MarathonApplication):
    _type = 'spark'

    

    def get_info(self):
        
        ens = []
        for task in self.tasks:
            ens.append(task['host'] + ':' + task['portMappings']['4040'])

        return {
            
            'sparkManagers': ','.join(ens),
            'sparkManagerLB': self.lb_host + ':' + str(self.port_mappings['4040'])
        }