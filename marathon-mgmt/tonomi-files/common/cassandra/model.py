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

    def _get_creation_defaults(self):
        configuration = {}
  
        volume_size = 2048
        
        volume_name = 'vol' + self.id.replace('/', '-') + '-data'
        
        if volume_size > 0:
            configuration['volumes'] =  [
              {
                "containerPath": volume_name,
                "mode": "RW",
                "persistent": {
                  "type": "root",
                  "size": volume_size
                }
              },
              {
                "containerPath": "/var/lib/cassandra",
                "hostPath": volume_name,
                "mode": "RW"
              }
            ]

            configuration['residency'] = {
                "taskLostBehavior": "WAIT_FOREVER"
            }


        configuration['configuration.cmd'] = "chown -R cassandra /var/lib/cassandra && start"

        configuration['configuration.name'] = self.id
        configuration['configuration.cpu'] = 0.5
        configuration['configuration.ram'] = 1024
        configuration['configuration.disk'] = 1024
        configuration['configuration.instances'] = 1
        
        configuration['configuration.constraints'] = [["hostname", "UNIQUE"]]
        configuration['configuration.portMappings'] = [{'9042':'0'}, {'9160':'0'}]
        configuration['configuration.imageId'] = 'poklet/cassandra'
        configuration['configuration.labels'] = {'_tonomi_application': 'cassandra'}

        return [configuration]