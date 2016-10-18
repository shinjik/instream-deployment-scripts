import sys
import yaml

import marathon_comm
from marathon_app import MarathonApplication

class KafkaApp(MarathonApplication):
    _type = 'kafka'

    _dependencies = {
        'zookeeperEndpoint': None,
        'topics': None,
        'advertisedHost': None,
        'advertisedPort': None
    }

    def get_info(self):
        
        ens = []
        for task in self.tasks:
            ens.append(task['host'] + ':' + task['portMappings']['9092'])

        return {
            'lbPort': str(self.port_mappings['9092']),
            'endpoints': ','.join(ens),
            'endpointLB': self.lb_host + ':' + str(self.port_mappings['9092'])
        }

    def create(self, configurations = None):
        # we need to re-start app after initial launch because we need to catch real external port. 
        # alternatively it has to be set explicitly
        # TODO: support this
        super(KafkaApp, self).create(configurations)
        self._model['env']['KAFKA_ADVERTISED_PORT'] = str(self.port_mappings['9092'])
        self.update()


    def _get_creation_defaults(self):
        configuration = {}

        if not self.get_dependency('advertisedHost'):
            self.set_dependency('advertisedHost', self.lb_host)
        if not self.get_dependency('advertisedPort'):
            self.set_dependency('advertisedPort', '1000')

        configuration['configuration.env'] = {
            "KAFKA_ZOOKEEPER_CONNECT": self.get_dependency('zookeeperEndpoint'),
            "KAFKA_CREATE_TOPICS": self.get_dependency('topics'),
            "KAFKA_ADVERTISED_HOST_NAME": self.get_dependency('advertisedHost'),
            "KAFKA_ADVERTISED_PORT": self.get_dependency('advertisedPort'),
            "KAFKA_HEAP_OPTS": "-Xmx512m -Xms512m"
        }  

        configuration['configuration.name'] = self.id
        configuration['configuration.cpu'] = 0.5
        configuration['configuration.ram'] = 1024
        configuration['configuration.disk'] = 1024
        configuration['configuration.instances'] = 1
        
        configuration['configuration.portMappings'] = [{'9092':'0'}]
        configuration['configuration.imageId'] = 'wurstmeister/kafka'
        configuration['configuration.labels'] = {'_tonomi_application': 'kafka'}

        return [configuration]