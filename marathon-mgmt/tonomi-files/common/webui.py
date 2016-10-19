from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint, MarathonHealthCheck
from marathon.models.container import *
from marathon.models.app import PortDefinition, Residency
import time


class WebUINodes(object):
  def __init__(self, env_name, marathon_client):
    self.env_name = env_name
    self.app_name = '/{}/webui'.format(self.env_name)
    self.marathon_client = marathon_client

  def create(self):
    cassandra_seed = None
    while True:
      try:
        cassandra_seed = self.marathon_client.get_app('/{}/cassandra-seed'.format(self.env_name))
        cassandra_seed.tasks[0].host
        break
      except:
        time.sleep(5)

    port_mappings = [
      MarathonContainerPortMapping(name=None, container_port=3005, host_port=0,
                                   service_port=0, protocol='tcp', labels={})
    ]

    docker = MarathonDockerContainer(image='node', network='BRIDGE', privileged=False, port_mappings=port_mappings)

    labels = {
      '_tonomi_application': 'webui',
      '_tonomi_environment': self.env_name
    }

    cmd = 'cd ${MESOS_SANDBOX}/webclient && npm install && NODE_ENV=production WEB_CLIENT_PORT=3005 npm start'

    constraints = []

    container = MarathonContainer(docker=docker)

    env = {
      'CASSANDRA_HOST': cassandra_seed.tasks[0].host,
      'CASSANDRA_PORT': cassandra_seed.labels['_cql_native_port']
    }

    fetch = [{"uri": 'https://s3-us-west-1.amazonaws.com/streaming-artifacts/ui.tar.gz', "executable": False, "cache": False}]

    health_checks = [
      MarathonHealthCheck(path='/', protocol='HTTP', port_index=0, grace_period_seconds=300, interval_seconds=60,
                          timeout_seconds=30, max_consecutive_failures=3, ignore_http1xx=True)
    ]

    webui_app = MarathonApp(id=self.app_name, cmd=cmd, cpus=0.5, mem=300, instances=2, disk=512, labels=labels,
                            container=container, constraints=constraints, env=env, fetch=fetch,
                            health_checks=health_checks)

    self.marathon_client.create_app(self.app_name, webui_app)

    return self.marathon_client.get_app(self.app_name)