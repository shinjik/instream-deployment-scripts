import sys
import yaml

import marathon_comm
from marathon_app import MarathonApplication

class WebUIApp(MarathonApplication):
    _type = 'web-ui'

    

    def get_info(self):
        
        uis = []
        for task in self.tasks:
            uis.append('http://' + task['host'] + ':' + task['portMappings']['3000'])

        return {
            
            'endpoints': uis,
            'URL': 'http://' + self.lb_host + ':' + str(self.port_mappings['3000'])
        }