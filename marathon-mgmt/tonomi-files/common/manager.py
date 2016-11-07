from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint, MarathonHealthCheck
from marathon.models.container import *
from marathon.models.app import PortDefinition, Residency
from lambdas import *
import time


class MarathonManager(object):
  def __init__(self, server):
    self._client = MarathonClient(server)

  def __repr__(self):
    return self.server

  def create(self, app):
    app._create(self._client)

  def discover(self, app_filter):
    apps = set()
    for app in self._client.list_apps():
      if ('_tonomi_application', app_filter) in app.labels.items():
        apps.add(reduce_app_name(app.id))

    return list(apps)

  def health_check(self):
    pass

  def destroy(self, name):
    try:
      self._client.delete_group(name, force=True)
    except:
      pass

  def update(self):
    pass

  def restart(self):
    pass

  def scale(self):
    pass


class Node(object):
  def __init__(self, name, image, volumes=[], network='BRIDGE', privileged=False, labels={}, cmd=None, constraints=[],
               residency=None, env={}, health_checks=[], uris=[], cpus=0.5, mem=256, instances=1, disk=512,
               port_mappings=[]):
    self.name = name
    docker = MarathonDockerContainer(image=image, network=network, privileged=privileged,
                                     port_mappings=port_mappings)
    container = MarathonContainer(docker=docker, volumes=volumes)
    self.app = MarathonApp(id=name, cmd=cmd, cpus=cpus, mem=mem, instances=instances,
                           disk=disk, labels=labels, container=container, constraints=constraints,
                           residency=residency, env=env, health_checks=health_checks, uris=uris)

  def _get_entity(self):
    return self.app


class Application(object):

  def __init__(self, name):
    self.INSTANCE_TYPES = []
    self.APPLICATION = None
    self.name = name


class ZookeeperNode(Node):
  def __init__(self, name, ports):
    self.name = name
    self.ports = ports

    volume_name = 'vol{}-data'.format(name.replace('/', '-'))
    volumes = [
      MarathonContainerVolume(container_path=volume_name, host_path=None, mode='RW', persistent={'size': 512}),
      MarathonContainerVolume(container_path='/var/lib/zookeeper', host_path=volume_name, mode='RW',
                              persistent=None)
    ]

    constraints = [MarathonConstraint(field='hostname', operator='LIKE', value='')]
    residency = Residency(task_lost_behavior='WAIT_FOREVER')
    health_checks = [
      # MarathonHealthCheck(grace_period_seconds=300, interval_seconds=20, max_consecutive_failures=3,
      #                     protocol='TCP', timeout_seconds=20, ignore_http1xx=False, port=ports[9042])
    ]

    cmd = 'export ZOO_SERVERS="{}" && /docker-entrypoint.sh zkServer.sh start-foreground'

    labels = {
      '_tonomi_application': 'zookeeper',
      '_client_conn_port': str(ports[0]),
      '_follower_conn_port': str(ports[1]),
      '_server_conn_port': str(ports[2])
    }

    env = {
      'ZOO_MY_ID': '',
      'ZOO_PORT': str(ports[0])
    }

    super().__init__(name, image='zookeeper', volumes=volumes, network='HOST', labels=labels,
                     cmd=cmd, constraints=constraints, residency=residency, env=env,
                     health_checks=health_checks, cpus=0.5, mem=400, instances=1, disk=400)

  def set_cluster(self, index, hostnames):
    self.app.constraints[0].value = hostnames[index-1]

    self.app.env['ZOO_MY_ID'] = str(index)

    zoo_servers = ''
    for i in range(1, 4):
      zoo_servers += 'server.{}={}:{}:{} '.format(i, hostnames[i-1],
                                                  self.ports[1], self.ports[2])

    self.app.cmd = self.app.cmd.format(zoo_servers)

  def _get_entity(self):
    return self.app


class Zookeeper(Application):

  def __init__(self, name, env=None, slaves=None, ports=None):
    self.INSTANCE_TYPES = ['zookeeper-1', 'zookeeper-2', 'zookeeper-3']
    self.APPLICATION = 'zookeeper'

    self.name = name
    self.env = env
    self.slaves = slaves
    self.ports = ports

    self.zoo_1 = ZookeeperNode(name='{}/{}'.format(self.name, 'zookeeper-1'), ports=self.ports)
    self.zoo_2 = ZookeeperNode(name='{}/{}'.format(self.name, 'zookeeper-2'), ports=self.ports)
    self.zoo_3 = ZookeeperNode(name='{}/{}'.format(self.name, 'zookeeper-3'), ports=self.ports)

  def _create(self, client):
    hostnames = get_mesos_hostnames(client)
    self.zoo_1.set_cluster(1, hostnames)
    client.create_app(self.zoo_1.name, self.zoo_1._get_entity())
    self.zoo_2.set_cluster(2, hostnames)
    client.create_app(self.zoo_2.name, self.zoo_2._get_entity())
    self.zoo_3.set_cluster(3, hostnames)
    client.create_app(self.zoo_3.name, self.zoo_3._get_entity())


class RedisNode(Node):
  def __init__(self, name, port, is_master=True):

    volume_name = get_volume_name(name)
    volumes = [
      MarathonContainerVolume(container_path=volume_name, host_path=None, mode='RW', persistent={'size': 512}),
      MarathonContainerVolume(container_path='/var/lib/redis', host_path=volume_name, mode='RW', persistent=None)
    ]

    constraints = [MarathonConstraint(field='hostname', operator='UNIQUE')]
    residency = Residency(task_lost_behavior='WAIT_FOREVER')
    health_checks = [
      # MarathonHealthCheck(grace_period_seconds=300, interval_seconds=20, max_consecutive_failures=3,
      #                     protocol='TCP', timeout_seconds=20, ignore_http1xx=False, port=port)
    ]

    service_port = 0 if not is_master else port
    port_mappings = [
      MarathonContainerPortMapping(container_port=port, host_port=port,
                                   service_port=service_port, protocol='tcp')
    ]

    cmd = 'docker-entrypoint.sh redis-server --port $REDIS_PORT '
    if not is_master:
      cmd += '--slaveof {} $REDIS_PORT'

    labels = {
      '_tonomi_application': 'redis',
      '_cluster_port': str(port)
    }

    env = {
      'REDIS_PORT': str(port)
    }

    super().__init__(name, image='redis', volumes=volumes, network='BRIDGE', labels=labels, cmd=cmd,
                     constraints=constraints, residency=residency, env=env, health_checks=health_checks,
                     cpus=0.5, mem=300, instances=1, disk=512, port_mappings=port_mappings)

  def _get_entity(self):
    return self.app


class Redis(Application):

  def __init__(self, name, env=None, port=None):
    self.INSTANCE_TYPES = ['redis-master', 'redis-slave']
    self.APPLICATION = 'redis'
    self.name = name
    self.env = env
    self.port = port

    self.master_app = RedisNode(name='{}/{}'.format(self.name, 'redis-master'),
                                port=self.port)
    self.slave_app = RedisNode(name='{}/{}'.format(self.name, 'redis-slave'),
                               port=self.port, is_master=False)

  def _create(self, client):
    client.create_app(self.master_app.name, self.master_app._get_entity())

    client.create_app(self.slave_app.name, self.slave_app._get_entity())


class CassandraNode(Node):
  def __init__(self, name, ports, is_seed=True):

    volume_name = 'vol{}-data'.format(name.replace('/', '-'))
    volumes = [
      MarathonContainerVolume(container_path=volume_name, host_path=None, mode='RW', persistent={'size': 512}),
      MarathonContainerVolume(container_path='/var/lib/cassandra', host_path=volume_name, mode='RW', persistent=None)
    ]

    constraints = [MarathonConstraint(field='hostname', operator='UNIQUE')]
    residency = Residency(task_lost_behavior='WAIT_FOREVER')
    health_checks = [
      # MarathonHealthCheck(grace_period_seconds=300, interval_seconds=20, max_consecutive_failures=3,
      #                     protocol='TCP', timeout_seconds=20, ignore_http1xx=False, port=ports[9042])
    ]

    ports_map = {
      'p11': 9042,
      'p12': ports[9042],
      'p21': 9160,
      'p22': ports[9160],
      'p31': 7199,
      'p32': ports[7199],
      'p41': 7000,
      'p42': ports[7000],
      'p51': 7001,
      'p52': ports[7001]
    }

    cmd = "chown -R cassandra /var/lib/cassandra && sed -i 's/{p11}/{p12}/' /etc/cassandra/default.conf/cqlshrc.sample && sed -i 's/{p31}/{p32}/' /etc/cassandra/default.conf/cassandra-env.sh && sed -i 's/{p41}/{p42}/;s/{p51}/{p52}/;s/{p11}/{p12}/;s/{p21}/{p22}/;s/{p31}/{p32}/' /etc/cassandra/default.conf/cassandra.yaml".format(**ports_map)
    if is_seed:
      cmd += ' && cd ${MESOS_SANDBOX}/cassandra-schema && ./apply_schema.sh & start'
    else:
      cmd += ' && start'

    labels = {
      '_tonomi_application': 'cassandra',
      '_jmx_port': str(ports[7199]),
      '_internode_communication_port': str(ports[7000]),
      '_tls_internode_communication_port': str(ports[7001]),
      '_thrift_client_port': str(ports[9160]),
      '_cql_native_port': str(ports[9042])
    }

    env = {
      'SEEDS': '',
      'CASSANDRA_PORT': str(ports[9042])
    }

    uris = ['https://s3-us-west-1.amazonaws.com/streaming-artifacts/mk-cassandra-schema.tar.gz']

    super().__init__(name, image='poklet/cassandra', volumes=volumes, network='HOST', labels=labels, cmd=cmd,
                     constraints=constraints, residency=residency, env=env, health_checks=health_checks,
                     uris=uris, cpus=0.5, mem=400, instances=1, disk=512)

  def set_seeds(self, seeds=''):
    self.app.env['SEEDS'] = seeds

  def _get_entity(self):
    return self.app


class Cassandra(Application):

  def __init__(self, name, env=None, ports=None, seed_app=None, node_app=None):
    self.INSTANCE_TYPES = ['cassandra-seed', 'cassandra-node']
    self.APPLICATION = 'cassandra'
    self.seeds = []
    self.nodes = []

    self.name = name
    self.env = env
    self.ports = ports
    self.seed_app = CassandraNode(name='{}/{}'.format(self.name, 'cassandra-seed'),
                                  ports=self.ports) if not seed_app else seed_app

    self.node_app = CassandraNode(name='{}/{}'.format(self.name, 'cassandra-node', is_seed=False),
                                  ports=self.ports) if not node_app else node_app

  def _create(self, client):
    client.create_app(self.seed_app.name, self.seed_app._get_entity())

    seed_host = ''
    while True:
      try:
        seed_host = client.get_app(self.seed_app.name).tasks[0].host
        break
      except:
        time.sleep(5)

    self.node_app.set_seeds(seed_host)
    client.create_app(self.node_app.name, self.node_app._get_entity())


class KafkaBroker(Node):
  def __init__(self, name, port, zoo_host, zoo_port):
    self.name = name
    self.port = port
    self.zoo_host = zoo_host
    self.zoo_port = zoo_port

    volume_name = get_volume_name(name)
    volumes = [
      MarathonContainerVolume(container_path=volume_name, host_path=None, mode='RW', persistent={'size': 512}),
      MarathonContainerVolume(container_path='/var/lib/kafka', host_path=volume_name, mode='RW', persistent=None)
    ]

    port_mappings = [
      MarathonContainerPortMapping(container_port=port, host_port=port,
                                   service_port=port, protocol='tcp')
    ]

    constraints = [MarathonConstraint(field='hostname', operator='UNIQUE')]
    residency = Residency(task_lost_behavior='WAIT_FOREVER')

    labels = {
      '_tonomi_application': 'kafka',
      '_cluster_port': str(port)
    }

    cmd = 'export KAFKA_ADVERTISED_HOST_NAME=$HOST && start-kafka.sh'

    env = {
      'KAFKA_ADVERTISED_PORT': str(port),
      'KAFKA_ZOOKEEPER_CONNECT': '{}:{}'.format(self.zoo_host, self.zoo_port),
      'KAFKA_PORT': str(port)
    }

    health_checks = [
      # MarathonHealthCheck(path='/', protocol='HTTP', port_index=0, grace_period_seconds=300, interval_seconds=60,
      #                     timeout_seconds=30, max_consecutive_failures=3, ignore_http1xx=True)
    ]

    super().__init__(name, image='wurstmeister/kafka', network='BRIDGE', labels=labels, cmd=cmd,
                     env=env, health_checks=health_checks, cpus=0.4, mem=300, instances=3,
                     disk=256, volumes=volumes, port_mappings=port_mappings, residency=residency,
                     constraints=constraints)


class Kafka(Application):
  def __init__(self, name, port=None, zookeeper_host=None, zookeeper_port=None):
    self.INSTANCE_TYPES = ['kafka-broker']
    self.APPLICATION = 'kafka'

    self.name = name
    self.port = port
    self.zoo_host = zookeeper_host
    self.zoo_port = zookeeper_port

    self.kafka = KafkaBroker(name='{}/{}'.format(self.name, 'kafka-broker'),
                             zoo_host=self.zoo_host, zoo_port=self.zoo_port,
                             port=self.port)

  def _create(self, client):
    client.create_app(self.kafka.name, self.kafka._get_entity())


class UINode(Node):
  def __init__(self, name, service_port=0, cassandra_host=None, cassandra_port=None):
    port_mappings = [
      MarathonContainerPortMapping(container_port=3005, host_port=0,
                                   service_port=service_port, protocol='tcp')
    ]

    labels = {
      '_tonomi_application': 'webui'
    }

    cmd = 'cd ${MESOS_SANDBOX}/webclient && npm install && NODE_ENV=production WEB_CLIENT_PORT=3005 npm start'

    env = {
      'CASSANDRA_HOST': cassandra_host,
      'CASSANDRA_PORT': str(cassandra_port)
    }

    uris = ['https://s3-us-west-1.amazonaws.com/streaming-artifacts/ui.tar.gz']

    health_checks = [
      MarathonHealthCheck(path='/', protocol='HTTP', port_index=0, grace_period_seconds=300, interval_seconds=60,
                          timeout_seconds=30, max_consecutive_failures=3, ignore_http1xx=True)
    ]

    super().__init__(name, image='node', network='BRIDGE', labels=labels, cmd=cmd, env=env,
                     health_checks=health_checks, uris=uris, cpus=0.5, mem=300, instances=2,
                     disk=256, port_mappings=port_mappings)

  def _get_entity(self):
    return self.app


class UI(Application):
  def __init__(self, name, service_port=None, cass_host=None, cass_port=None):
    self.INSTANCE_TYPES = ['webui']
    self.APPLICATION = 'webui'

    self.name = name
    self.service_port = service_port
    self.cass_host = cass_host
    self.cass_port = cass_port

    self.webui = UINode(name='{}/{}'.format(self.name, 'webui-app'),
                        cassandra_host=self.cass_host, cassandra_port=self.cass_port,
                        service_port=self.service_port)

  def _create(self, client):
    client.create_app(self.webui.name, self.webui._get_entity())


class SparkNode(Node):
  def __init__(self, name, cassandra_host, cassandra_port,
               kafka_host, kafka_port, redis_host, redis_port):
    self.name = name
    self.cassandra_host = cassandra_host
    self.cassandra_port = cassandra_port
    self.redis_host = redis_host
    self.redis_port = redis_port
    self.kafka_host = kafka_host
    self.kafka_port = kafka_port

    port_mappings = [
      MarathonContainerPortMapping(container_port=8088, host_port=0, service_port=0, protocol='tcp'),
      MarathonContainerPortMapping(container_port=8042, host_port=0, service_port=0, protocol='tcp'),
      MarathonContainerPortMapping(container_port=4040, host_port=0, service_port=0, protocol='tcp'),
      MarathonContainerPortMapping(container_port=2122, host_port=0, service_port=0, protocol='tcp')
    ]

    labels = {
      '_tonomi_application': 'spark'
    }

    env = {
      'CASSANDRA_HOST': self.cassandra_host,
      'CASSANDRA_PORT': str(self.cassandra_port),
      'KAFKA_BROKER_LIST': '{}:{}'.format(self.kafka_host, self.kafka_port),
      'REDIS_HOST': self.redis_host,
      'REDIS_PORT': str(self.redis_port)
    }

    cmd = 'cd ${MESOS_SANDBOX} && bash ./streaming-runner.sh'

    uris = [
      'https://s3-us-west-1.amazonaws.com/streaming-artifacts/in-stream-tweets-analyzer.tar.gz',
      'https://s3-us-west-1.amazonaws.com/streaming-artifacts/dictionary-populator.tar.gz'
    ]

    health_checks = [
      MarathonHealthCheck(grace_period_seconds=300, interval_seconds=20, max_consecutive_failures=3,
                          protocol='HTTP', timeout_seconds=20, ignore_http1xx=True, port_index=2)
    ]

    super().__init__(name, image='sequenceiq/spark:1.6.0', network='BRIDGE', labels=labels, cmd=cmd,
                     env=env, health_checks=health_checks, cpus=0.5, mem=500, instances=1,
                     disk=512, port_mappings=port_mappings, uris=uris)


class Spark(Application):
  def __init__(self, name, redis_host=None, redis_port=None,
               cassandra_host=None, cassandra_port=None,
               kafka_host=None, kafka_port=None):
    self.INSTANCE_TYPES = ['spark']
    self.APPLICATION = 'spark'

    self.name = name
    self.redis_host = redis_host
    self.redis_port = redis_port
    self.cassandra_host = cassandra_host
    self.cassandra_port = cassandra_port
    self.kafka_host = kafka_host
    self.kafka_port = kafka_port

    self.spark_app = SparkNode(name='{}/{}'.format(self.name, 'spark-app'),
                               cassandra_host=cassandra_host, cassandra_port=cassandra_port,
                               redis_host=redis_host, redis_port=redis_port,
                               kafka_host=kafka_host, kafka_port=kafka_port)

  def _create(self, client):
    client.create_app(self.spark_app.name, self.spark_app._get_entity())