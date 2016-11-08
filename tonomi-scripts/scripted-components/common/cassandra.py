from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint, MarathonHealthCheck
from marathon.models.container import *
from marathon.models.app import PortDefinition, Residency
from ephemeral import CassandraCommand
import time


class CassandraNode(object):
  def __init__(self, env_name, marathon_client, ports, seed_hosts=''):
    self.env_name = env_name

    if seed_hosts == '':
      self.app_name = '/{}/{}'.format(self.env_name, 'cassandra-seed')
    else:
      self.app_name = '/{}/{}'.format(self.env_name, 'cassandra-node')

    self.marathon_client = marathon_client
    self.seed_hosts = seed_hosts
    self.ports = ports

  def create(self):

    volume_name = 'vol{}-data'.format(self.app_name.replace('/', '-'))
    volumes = [
      MarathonContainerVolume(container_path=volume_name, host_path=None, mode='RW', persistent={'size': 512}),
      MarathonContainerVolume(container_path='/var/lib/cassandra', host_path=volume_name, mode='RW', persistent=None)
    ]
    docker = MarathonDockerContainer(image='poklet/cassandra', network='HOST', privileged=False)

    labels = {
      '_tonomi_application': 'cassandra',
      '_tonomi_environment': self.env_name,
      '_jmx_port': self.ports['7199'],
      '_internode_communication_port': self.ports['7000'],
      '_tls_internode_communication_port': self.ports['7001'],
      '_thrift_client_port': self.ports['9160'],
      '_cql_native_port': self.ports['9042']
    }

    cmd = None

    if self.seed_hosts == '':
      cmd = "chown -R cassandra /var/lib/cassandra && sed -i 's/{p11}/{p12}/' /etc/cassandra/default.conf/cqlshrc.sample && sed -i 's/{p31}/{p32}/' /etc/cassandra/default.conf/cassandra-env.sh && sed -i 's/{p41}/{p42}/;s/{p51}/{p52}/;s/{p11}/{p12}/;s/{p21}/{p22}/;s/{p31}/{p32}/' /etc/cassandra/default.conf/cassandra.yaml && cd ${{MESOS_SANDBOX}}/cassandra-schema && ./apply_schema.sh & start" \
        .format(p11='9042', p12=self.ports['9042'], p21='9160', p22=self.ports['9160'], p31='7199',
                p32=self.ports['7199'], p41='7000', p42=self.ports['7000'], p51='7001', p52=self.ports['7001'])
    else:
      cmd = "chown -R cassandra /var/lib/cassandra && sed -i 's/{p11}/{p12}/' /etc/cassandra/default.conf/cqlshrc.sample && sed -i 's/{p31}/{p32}/' /etc/cassandra/default.conf/cassandra-env.sh && sed -i 's/{p41}/{p42}/;s/{p51}/{p52}/;s/{p11}/{p12}/;s/{p21}/{p22}/;s/{p31}/{p32}/' /etc/cassandra/default.conf/cassandra.yaml && start" \
        .format(p11='9042', p12=self.ports['9042'], p21='9160', p22=self.ports['9160'], p31='7199',
                p32=self.ports['7199'], p41='7000', p42=self.ports['7000'], p51='7001', p52=self.ports['7001'])

    constraints = [MarathonConstraint(field='hostname', operator='UNIQUE', value=None)]
    container = MarathonContainer(docker=docker, volumes=volumes)
    residency = Residency(task_lost_behavior='WAIT_FOREVER')
    env = {
      'SEEDS': self.seed_hosts,
      'CASSANDRA_PORT': str(self.ports['9042'])
    }

    health_checks = [
      MarathonHealthCheck(grace_period_seconds=300, interval_seconds=20, max_consecutive_failures=3,
                          protocol='TCP', timeout_seconds=20, ignore_http1xx=False, port=int(self.ports['9042']))
    ]

    uris = ['https://s3-us-west-1.amazonaws.com/streaming-artifacts/mk-cassandra-schema.tar.gz']

    new_cassandra_app = MarathonApp(id=self.app_name, cmd=cmd, cpus=0.5, mem=400, instances=1, disk=1024, labels=labels,
                                    container=container, constraints=constraints, residency=residency, env=env,
                                    health_checks=health_checks, uris=uris)
    self.marathon_client.create_app(self.app_name, new_cassandra_app)

class CassandraCluster(object):
  def __init__(self, env_name, marathon_client):
    self.env_name = env_name
    self.marathon_client = marathon_client
    self.seed_nodes = []
    self.regular_nodes = []

  def create(self):
    ports = {
      '9042': '31942',
      '9160': '31916',
      '7199': '31199',
      '7000': '31700',
      '7001': '31701'
    }

    port_inc = 0
    checked_envs = []

    for app in self.marathon_client.list_apps():
      env_name = app.labels.get('_tonomi_environment', '')

      if '/cassandra-seed' in app.id and env_name not in checked_envs:
        port_inc += 2
        checked_envs.append(env_name)

    ports = {k: str(int(v) + port_inc) for k, v in ports.items()}

    seed = CassandraNode(self.env_name, self.marathon_client, ports)
    seed.create()

    seed_host = ''
    while True:
      try:
        seed_host = self.marathon_client.get_app('/{}/cassandra-seed'.format(self.env_name)).tasks[0].host
        break
      except:
        time.sleep(5)

    node = CassandraNode(self.env_name, self.marathon_client, ports, seed_host)
    node.create()

    self.seed_nodes = [seed]
    self.regular_nodes = [node]

  @staticmethod
  def cql_query(cluster_name, marathon_client, query):
    try:
      seed_app = marathon_client.get_app('{}-seed'.format(cluster_name))
      cass_host = seed_app.tasks[0].host
      cass_port = seed_app.labels['_cql_native_port']
      cass_cmd = CassandraCommand(marathon_client, cass_host, cass_port, query)
      cass_cmd.create()
    except:
      pass

  @staticmethod
  def delete_cluster(cluster_name, marathon_client):

    try:
      marathon_client.delete_app('{}-seed'.format(cluster_name), True)
    except:
      pass

    try:
      marathon_client.delete_app('{}-node'.format(cluster_name), True)
    except:
      pass
