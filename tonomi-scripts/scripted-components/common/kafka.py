from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint, MarathonHealthCheck
from marathon.models.container import *
from marathon.models.app import PortDefinition, Residency


class KafkaCluster(object):
  def __init__(self, env_name, zoo_host, zoo_port, marathon_client):
    self.env_name = env_name
    self.app_name = '/{}/kafka'.format(self.env_name)
    self.zoo_host = zoo_host
    self.zoo_port = zoo_port
    self.marathon_client = marathon_client

    self.kafka_port = 31992

    checked_envs = []
    for app in self.marathon_client.list_apps():
      env_name = app.labels.get('_tonomi_environment', '')
      app_type = app.labels.get('_tonomi_application', '')
      if app_type == 'kafka' and env_name not in checked_envs:
        self.kafka_port += 1
        checked_envs.append(env_name)

  def create(self):
    volume_name = 'vol{}-data'.format(self.app_name.replace('/', '-'))
    volumes = [
      MarathonContainerVolume(container_path=volume_name, host_path=None, mode='RW', persistent={'size': 512}),
      MarathonContainerVolume(container_path='/var/lib/kafka', host_path=volume_name, mode='RW', persistent=None)
    ]

    port_mappings = [
      MarathonContainerPortMapping(name=None, container_port=int(self.kafka_port), host_port=int(self.kafka_port),
                                   service_port=int(self.kafka_port), protocol='tcp', labels={})
    ]

    docker = MarathonDockerContainer(image='wurstmeister/kafka', network='BRIDGE', privileged=False,
                                     port_mappings=port_mappings)

    labels = {
      '_tonomi_application': 'kafka',
      '_tonomi_environment': self.env_name,
      '_cluster_port': str(self.kafka_port)
    }

    cmd = 'export KAFKA_ADVERTISED_HOST_NAME=$HOST && start-kafka.sh'

    constraints = [MarathonConstraint(field='hostname', operator='UNIQUE', value=None)]

    container = MarathonContainer(docker=docker, volumes=volumes)
    residency = Residency(task_lost_behavior='WAIT_FOREVER')
    env = {
      'KAFKA_ADVERTISED_PORT': str(self.kafka_port),
      'KAFKA_ZOOKEEPER_CONNECT': '{}:{}'.format(self.zoo_host, self.zoo_port),
      'KAFKA_PORT': str(self.kafka_port)
    }

    health_checks = [
      MarathonHealthCheck(grace_period_seconds=300, interval_seconds=20, max_consecutive_failures=3,
                          protocol='TCP', timeout_seconds=20, ignore_http1xx=False, port=int(self.kafka_port))
    ]

    kafka_app = MarathonApp(id=self.app_name, cmd=cmd, cpus=0.5, mem=300, instances=2, disk=512, labels=labels,
                            container=container, constraints=constraints, residency=residency, env=env,
                            health_checks=health_checks)
    self.marathon_client.create_app(self.app_name, kafka_app)
    self.application = self.marathon_client.get_app(self.app_name)
    return self.application