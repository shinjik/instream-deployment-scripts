from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint, MarathonHealthCheck
from marathon.models.container import *
from marathon.models.app import PortDefinition, Residency
from urllib.parse import urlparse
import socket
import time


class RedisNode(object):
  def __init__(self, env_name, marathon_client, port, is_slave=False):

    self.marathon_client = marathon_client
    self.is_slave = is_slave
    self.env_name = env_name
    self.port = port

    if self.is_slave:
      self.app_name = '/{}/redis-slave'.format(self.env_name)
    else:
      self.app_name = '/{}/redis-master'.format(self.env_name)

  def create(self):
    volume_name = 'vol{}-data'.format(self.app_name.replace('/', '-'))
    volumes = [
      MarathonContainerVolume(container_path=volume_name, host_path=None, mode='RW', persistent={'size': 512}),
      MarathonContainerVolume(container_path='/var/lib/redis', host_path=volume_name, mode='RW', persistent=None)
    ]

    service_port = 0 if self.is_slave else self.port

    port_mappings = [
      MarathonContainerPortMapping(name=None, container_port=int(self.port), host_port=int(self.port),
                                   service_port=service_port, protocol='tcp', labels={})
    ]

    docker = MarathonDockerContainer(image='redis', network='BRIDGE', privileged=False, port_mappings=port_mappings)

    labels = {
      '_tonomi_application': 'redis',
      '_tonomi_environment': self.env_name,
      '_cluster_port': str(self.port)
    }

    cmd = 'docker-entrypoint.sh redis-server --port $REDIS_PORT '

    if self.is_slave:
      parsed_uri = urlparse(self.marathon_client.servers[0])
      master_host = socket.gethostbyname('{uri.netloc}'.format(uri=parsed_uri).split(':')[0])

      cmd += '--slaveof {} $REDIS_PORT'.format(master_host)

    constraints = [MarathonConstraint(field='hostname', operator='UNIQUE', value=None)]
    container = MarathonContainer(docker=docker, volumes=volumes)
    residency = Residency(task_lost_behavior='WAIT_FOREVER')

    env = {
      'REDIS_PORT': str(self.port)
    }

    health_checks = [
      MarathonHealthCheck(grace_period_seconds=300, interval_seconds=20, max_consecutive_failures=3,
                          protocol='TCP', timeout_seconds=20, ignore_http1xx=False, port=int(self.port))
    ]

    new_redis_app = MarathonApp(id=self.app_name, cmd=cmd, cpus=0.5, mem=300, instances=1, disk=512, labels=labels,
                                    container=container, constraints=constraints, residency=residency, env=env,
                                    health_checks=health_checks)

    self.marathon_client.create_app(self.app_name, new_redis_app)


class RedisCluster(object):
  def __init__(self, env_name, marathon_client):
    self.env_name = env_name
    self.marathon_client = marathon_client

  def create(self):
    port = 31379
    port_inc = 0

    checked_envs = []

    for app in self.marathon_client.list_apps():
      env_name = app.labels.get('_tonomi_environment', '')

      if '/redis-master' in app.id and env_name not in checked_envs:
        port_inc += 1
        checked_envs.append(env_name)

    port += port_inc

    master = RedisNode(self.env_name, self.marathon_client, port)
    master.create()

    self.wait_for_slave()

    slave = RedisNode(self.env_name, self.marathon_client, port, is_slave=True)
    slave.create()

  def wait_for_slave(self):
    while True:
      try:
        self.marathon_client.get_app('/{}/redis-master'.format(self.env_name)).tasks[0].host
        break
      except:
        time.sleep(5)
    return


  @staticmethod
  def delete_cluster(cluster_name, marathon_client):
    try:
      marathon_client.delete_app('{}-master'.format(cluster_name), True)
    except:
      pass
    try:
      marathon_client.delete_app('{}-slave'.format(cluster_name), True)
    except:
      pass