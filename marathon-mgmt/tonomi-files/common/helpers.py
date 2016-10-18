from marathon_app import MarathonApplication
from redis.model import RedisApp
from zookeeper.model import ZookeeperApp
from kafka.model import KafkaApp
from cassandra.model import CassandraApp
from webui.model import WebUIApp
from spark.model import SparkApp

app_classes = {
    'zookeeper': ZookeeperApp,
    'redis': RedisApp,
    'kafka': KafkaApp,
    'cassandra': CassandraApp,
    'spark': SparkApp,
    'web-ui': WebUIApp,
    'generic': MarathonApplication
}

class marathon_helpers:
    def get_app_by_type(type):
        if type in app_classes.keys():
            return app_classes[type]
        else:
            return app_classes['generic']
            #raise RuntimeError, "Application of given type is not registered"