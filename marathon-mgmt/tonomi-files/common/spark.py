from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint, MarathonHealthCheck
from marathon.models.container import *
from marathon.models.app import PortDefinition, Residency
import time


class SparkCluster(object):
  def __init__(self, env_name, marathon_client):
    self.env_name = env_name
    self.app_name = '/{}/spark'.format(self.env_name)
    self.marathon_client = marathon_client

  def create(self):
    port_mappings = [
      MarathonContainerPortMapping(name=None, container_port=8088, host_port=0, service_port=0, protocol='tcp', labels={}),
      MarathonContainerPortMapping(name=None, container_port=8042, host_port=0, service_port=0, protocol='tcp', labels={}),
      MarathonContainerPortMapping(name=None, container_port=4040, host_port=0, service_port=0, protocol='tcp', labels={}),
      MarathonContainerPortMapping(name=None, container_port=2122, host_port=0, service_port=0, protocol='tcp', labels={})
    ]

    docker = MarathonDockerContainer(image='sequenceiq/spark:1.6.0', network='BRIDGE', privileged=False,
                                     port_mappings=port_mappings)

    labels = {
      '_tonomi_application': 'spark',
      '_tonomi_environment': self.env_name
    }

    cmd = 'cd ${MESOS_SANDBOX} && bash ./streaming-runner.sh'

    constraints = []

    container = MarathonContainer(docker=docker)

    redis_host = ''
    redis_port = ''
    cassandra_host = ''
    cassandra_port = ''
    kafka_broker_list = ''

    while True:
      try:
        redis_host = self.marathon_client.get_app('/{}/redis-master'.format(self.env_name)).tasks[0].host
        redis_port = self.marathon_client.get_app('/{}/redis-master'.format(self.env_name)).labels['_cluster_port']
        cassandra_host = self.marathon_client.get_app('/{}/cassandra-seed'.format(self.env_name)).tasks[0].host
        cassandra_port = self.marathon_client.get_app('/{}/cassandra-seed'.format(self.env_name)).labels['_cql_native_port']
        kafka_broker_list = '{}:{}'.format(self.marathon_client.get_app('/{}/kafka'.format(self.env_name)).tasks[0].host,
                                           self.marathon_client.get_app('/{}/kafka'.format(self.env_name)).labels['_cluster_port'])
        break
      except:
        time.sleep(3)

    env = {
      'CASSANDRA_HOST': cassandra_host,
      'CASSANDRA_PORT': cassandra_port,
      'KAFKA_BROKER_LIST': kafka_broker_list,
      'REDIS_HOST': redis_host,
      'REDIS_PORT': redis_port
    }

    fetch = [
      {
        'uri': 'https://s3-us-west-1.amazonaws.com/streaming-artifacts/in-stream-tweets-analyzer.tar.gz',
        'executable': False,
        'cache': False
      },
      {
        'uri': 'https://s3-us-west-1.amazonaws.com/streaming-artifacts/dictionary-populator.tar.gz',
        'executable': False,
        'cache': False
      }
    ]

    spark_app = MarathonApp(id=self.app_name, cmd=cmd, cpus=1, mem=500, instances=1, disk=512, labels=labels,
                            container=container, constraints=constraints, env=env, fetch=fetch)
    self.marathon_client.create_app(self.app_name, spark_app)