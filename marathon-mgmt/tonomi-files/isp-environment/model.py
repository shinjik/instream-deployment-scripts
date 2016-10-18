import sys
import yaml

import marathon_comm
from helpers import marathon_helpers


from redis.model import RedisApp
from zookeeper.model import ZookeeperApp
from kafka.model import KafkaApp
from cassandra.model import CassandraApp
from webui.model import WebUIApp
from spark.model import SparkApp

class InstreamEnvironment:
    def __init__(self, marathon_url):
        self.marathon_url = marathon_url
    
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value
    

    @property
    def applications(self):
        return self._applications
    


    def load(self, id):
        self.id = id
        apps = marathon_comm.list_apps(self.marathon_url, {'_tonomi_environment': id})
        self._applications = []
        for app in apps:
            self._applications.append(marathon_helpers.get_app_by_type(app.marathon_model['labels']['_tonomi_application'])(self.marathon_url, marathon_comm.get_app_info(self.marathon_url, app.id)))


    def get_apps_by_type(self, apptype):
        a = filter(lambda x: x.labels.get('_tonomi_application') == apptype, self.applications)
        return list(a)

    def create(self):
        # for now let's create only default configs, sizing for components will be added when they will support it

        z = ZookeeperApp(self.marathon_url)
        z.id = '/' + self.id + '/zookeeper'
        z.environment_name = self.id
        z.create()

        r = RedisApp(self.marathon_url)
        r.id = '/' + self.id + '/redis'
        r.environment_name = self.id
        r.create()

        c = CassandraApp(self.marathon_url)
        c.id = '/' + self.id + '/cassandra'
        c.environment_name = self.id
        c.create()

        k = KafkaApp(self.marathon_url)
        k.id = '/' + self.id + '/kafka'
        k.environment_name = self.id
        k.set_dependency('zookeeperEndpoint', z.get_info()['ensembleUrlLB'])
        k.set_dependency('topics', 'events_topic:1:1')

        k.create()


        # TODO: populate apps!
        # redis <- dictionaries, cassandra <- schema + movies list!

        ui = WebUIApp(self.marathon_url)
        ui.id = '/' + self.id + '/ui'
        ui.environment_name = self.id
        ui.set_dependency('cassandraEndpoint', c.get_info()['endpointLB'])

        ui.create()

        s = SparkApp(self.marathon_url)
        s.id = '/' + self.id + '/spark'
        s.environment_name = self.id
        s.set_dependency('cassandraEndpoint', c.get_info()['endpointLB'])
        s.set_dependency('redisEndpoint', r.get_info()['instanceEndpointLB'])
        s.set_dependency('kafkaBrokers', k.get_info()['endpointLB'])
        s.create()

    def destroy(self):
        for app in self.applications:
            app.destroy()
