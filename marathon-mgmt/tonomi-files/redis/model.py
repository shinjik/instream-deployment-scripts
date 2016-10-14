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