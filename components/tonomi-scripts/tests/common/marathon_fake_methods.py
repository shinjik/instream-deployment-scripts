from marathon.models import MarathonApp, MarathonTask
from marathon.models.container import *
from collections import namedtuple


def marathon_discover_list_apps():
  return [
    MarathonApp(id='/sandbox/cassandra/cassandra-seed', labels={'_tonomi_environment': 'test',
                                                                '_tonomi_application': 'cassandra'}),
    MarathonApp(id='/sample2/cassandra-seed', labels={'_tonomi_application': 'cassandra'}),
    MarathonApp(id='/sample3', labels={})
  ]

def webui_launch_get_app():
  app1 = MarathonApp(id='/sandbox/cassandra-seed', tasks=[MarathonTask(host='127.0.0.1')],
                     labels={'_cql_native_port': '31942'})
  return [app1]

def cassandra_launch_get_app():
  app1 = MarathonApp(id='/new-cassandra', tasks=[MarathonTask(host='127.0.0.1')])
  return [app1]

def redis_launch_get_app():
  app1 = MarathonApp(id='/sandbox/redis-master', tasks=[MarathonTask(host='127.0.0.0')])
  return [app1]

def cassandra_health_check_list_apps():
  app1 = MarathonApp(id='/sandbox/cassandra')
  app2 = MarathonApp(id='/new-cassandra')
  app3 = MarathonApp(id='/test/cassandra')
  return [app1, app2, app3]

def redis_health_check_list_apps():
  app1 = MarathonApp(id='/sandbox/redis')
  app2 = MarathonApp(id='/test/redis')
  app3 = MarathonApp(id='/new-redis')
  return [app1, app2, app3]

def cassandra_health_check_get_app():
  labels = {
    '_jmx_port': '123',
    '_internode_communication_port': '123',
    '_tls_internode_communication_port': '123',
    '_thrift_client_port': '123',
    '_cql_native_port': '123'
  }
  app1 = MarathonApp(id='/sandbox/cassandra-seed', labels=labels,
                     tasks_unhealthy=0, tasks_running=1, mem=256, cpus=0.5, disk=256)
  app2 = MarathonApp(id='/test/non-env-cassandra', labels=labels,
                     tasks_unhealthy=0, tasks_running=1, mem=256, cpus=0.5, disk=256)
  return [app1, app2]

def environment_health_check_get_app():
  zoo1 = MarathonApp(id='/sandbox/zookeeper/zookeeper-1', env={'ZOO_PORT': '10001'})
  zoo2 = MarathonApp(id='/sandbox/zookeeper/zookeeper-2', env={'ZOO_PORT': '10001'})
  zoo3 = MarathonApp(id='/sandbox/zookeeper/zookeeper-3', env={'ZOO_PORT': '10001'})
  redis1 = MarathonApp(id='/sandbox/redis/redis-master', env={'REDIS_PORT': '20001'})
  redis2 = MarathonApp(id='/sandbox/redis/redis-slave', env={'REDIS_PORT': '20001'})
  cass_labels = {
    '_jmx_port': '30001',
    '_internode_communication_port': '30002',
    '_tls_internode_communication_port': '30003',
    '_thrift_client_port': '30004',
    '_cql_native_port': '30005'
  }
  cass1 = MarathonApp(id='/sandbox/cassandra/cassandra-seed', labels=cass_labels)
  cass2 = MarathonApp(id='/sandbox/cassandra/cassandra-node', labels=cass_labels)
  kafka1 = MarathonApp(id='/sandbox/kafka/kafka-broker', env={'KAFKA_PORT': '60001'})

  port_mappings = [MarathonContainerPortMapping(service_port=90001)]
  docker = MarathonDockerContainer(image='node', port_mappings=port_mappings)
  container = MarathonContainer(docker=docker)
  webui1 = MarathonApp(id='/sandbox/webui/webui-app', container=container)

  port_mappings = [MarathonContainerPortMapping(service_port=i) for i in [80000, 80002, 80001]]
  docker = MarathonDockerContainer(image='spark', port_mappings=port_mappings)
  container = MarathonContainer(docker=docker)
  spark1 = MarathonApp(id='/sandbox/spark/spark-app', container=container)
  return [zoo1, zoo2, zoo3, redis1, redis2, cass1, cass2, kafka1, webui1, spark1]

def environment_health_check_get_group():
  zoo1 = MarathonApp(id='/sandbox/zookeeper/zookeeper-1',
                     labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'zookeeper'})
  zoo2 = MarathonApp(id='/sandbox/zookeeper/zookeeper-2',
                     labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'zookeeper'})
  zoo3 = MarathonApp(id='/sandbox/zookeeper/zookeeper-3',
                     labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'zookeeper'})
  redis1 = MarathonApp(id='/sandbox/redis/redis-master',
                       labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'redis'})
  redis2 = MarathonApp(id='/sandbox/redis/redis-slave',
                       labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'redis'})
  cass1 = MarathonApp(id='/sandbox/cassandra/cassandra-seed',
                      labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'cassandra'})
  cass2 = MarathonApp(id='/sandbox/cassandra/cassandra-node',
                      labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'cassandra'})
  kafka1 = MarathonApp(id='/sandbox/kafka/kafka-broker',
                       labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'kafka'})
  webui1 = MarathonApp(id='/sandbox/webui/webui-app',
                       labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'webui'})
  spark1 = MarathonApp(id='/sandbox/spark/spark-app',
                       labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'spark'})

  apps = [zoo1, zoo2, zoo3, redis1, redis2, cass1, cass2, kafka1, webui1, spark1]
  return namedtuple('Struct', 'id apps')(id='/sandbox', apps=apps)

def kafka_health_check_get_app():
  env = {
    'KAFKA_PORT': '31001'
  }
  app1 = MarathonApp(id='/new-kafka/kafka-broker', env=env,
                     tasks_unhealthy=0, tasks_running=1, mem=256, cpus=0.5, disk=256)
  app2 = MarathonApp(id='/sandbox/kafka/kafka-broker', env=env,
                     tasks_unhealthy=0, tasks_running=1, mem=256, cpus=0.5, disk=256)
  return [app1, app2]

def zookeeper_health_check_list_apps():
  labels = {
    '_client_conn_port': 31001,
    '_follower_conn_port': 31002,
    '_server_conn_port': 31003
  }

  app1 = MarathonApp(id='/new-zookeeper/zookeeper-1', labels=labels, tasks=[MarathonTask(host='127.0.0.1')],
                     tasks_unhealthy=0, tasks_running=1, mem=256, cpus=0.5, disk=256)
  app2 = MarathonApp(id='/new-zookeeper/zookeeper-2', labels=labels, tasks=[MarathonTask(host='127.0.0.2')],
                     tasks_unhealthy=0, tasks_running=1, mem=256, cpus=0.5, disk=256)
  app3 = MarathonApp(id='/new-zookeeper/zookeeper-3', labels=labels, tasks=[MarathonTask(host='127.0.0.3')],
                     tasks_unhealthy=0, tasks_running=1, mem=256, cpus=0.5, disk=256)
  return [[app1, app2, app3]]

def zookeeper_health_check_get_app():
  labels = {
    '_client_conn_port': 31001,
    '_follower_conn_port': 31002,
    '_server_conn_port': 31003
  }

  app1 = MarathonApp(id='/new-zookeeper/zookeeper-1', labels=labels, tasks=[MarathonTask(host='127.0.0.1')],
                     tasks_unhealthy=0, tasks_running=1, mem=256, cpus=0.5, disk=256)
  app2 = MarathonApp(id='/new-zookeeper/zookeeper-2', labels=labels, tasks=[MarathonTask(host='127.0.0.2')],
                     tasks_unhealthy=0, tasks_running=1, mem=256, cpus=0.5, disk=256)
  app3 = MarathonApp(id='/new-zookeeper/zookeeper-3', labels=labels, tasks=[MarathonTask(host='127.0.0.3')],
                     tasks_unhealthy=0, tasks_running=1, mem=256, cpus=0.5, disk=256)
  return [app1, app2, app3]

def redis_health_check_get_app():
  app1 = MarathonApp(id='/sandbox/redis-master', tasks=[MarathonTask(host='127.0.0.1')],
                     tasks_unhealthy=0, tasks_running=1, mem=256, cpus=0.5, disk=256)

  app2 = MarathonApp(id='/sandbox/redis-slave', tasks=[MarathonTask(host='127.0.0.1')],
                     cmd='docker-entrypoint.sh redis-server --port $REDIS_PORT --slaveof 127.0.0.1 $REDIS_PORT',
                     tasks_running=1, mem=256, cpus=0.5, disk=256)
  return [app1, app2]

def cassandra_discover_list_apps():
  return [
    MarathonApp(id='/new-cassandra', labels={'_tonomi_application': 'cassandra'}),
    MarathonApp(id='/sandbox/cassandra', labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'cassandra'})
  ]

def environment_launch_free_ports():
  return [10000+i for i in range(1, 12)]

def environment_discover_list_apps():
  return [
    MarathonApp(id='/new-cassandra/cassandra-seed', labels={'_tonomi_application': 'cassandra'}),
    MarathonApp(id='/test/redis/redis-master', labels={'_tonomi_environment': 'test', '_tonomi_application': 'redis'}),
    MarathonApp(id='/sandbox/spark/spark-app', labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'spark'})
  ]

def zookeeper_discover_list_apps():
  return [
    MarathonApp(id='/new-zookeeper', labels={'_tonomi_application': 'zookeeper'}),
    MarathonApp(id='/sandbox/zookeeper', labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'zookeeper'})
  ]

def kafka_discover_list_apps():
  return [
    MarathonApp(id='/sandbox/kafka', labels={'_tonomi_environment': 'sandbox',
                                             '_tonomi_application': 'kafka'}),
    MarathonApp(id='/new-kafka', labels={'_tonomi_application': 'kafka'})
  ]

def redis_discover_list_apps():
  return [
    MarathonApp(id='/sandbox/redis', labels={'_tonomi_environment': 'sandbox',
                                             '_tonomi_application': 'redis'}),
    MarathonApp(id='/new-redis', labels={'_tonomi_application': 'redis'})
  ]

def webui_discover_list_apps():
  return [
    MarathonApp(id='/sandbox/webui', labels={'_tonomi_environment': 'sandbox',
                                             '_tonomi_application': 'webui'}),
    MarathonApp(id='/new-webui', labels={'_tonomi_application': 'webui'})
  ]

def spark_discover_list_apps():
  return [
    MarathonApp(id='/sandbox/spark', labels={'_tonomi_environment': 'sandbox',
                                             '_tonomi_application': 'spark'}),
    MarathonApp(id='/new-spark', labels={'_tonomi_application': 'spark'})
  ]

def webui_health_check_get_app():
  port_mappings = [MarathonContainerPortMapping(service_port=1000)]
  docker = MarathonDockerContainer(image='node', port_mappings=port_mappings)
  container = MarathonContainer(docker=docker)
  labels = {'_tonomi_environment': 'sandbox', '_tonomi_application': 'webui'}
  app1 = MarathonApp(id='/sandbox/webui/webui-app', labels=labels, cpus=0.5, mem=256, disk=256, instances=1, container=container)
  app1.tasks_unhealthy = 0
  app1.tasks_running = 1
  return [app1]

def spark_health_check_get_app():
  port_mappings = [MarathonContainerPortMapping(service_port=10001),
                   MarathonContainerPortMapping(service_port=10002),
                   MarathonContainerPortMapping(service_port=10003),
                   MarathonContainerPortMapping(service_port=10004)]
  docker = MarathonDockerContainer(image='node', port_mappings=port_mappings)
  container = MarathonContainer(docker=docker)
  labels = {'_tonomi_environment': 'sandbox', '_tonomi_application': 'spark'}
  app1 = MarathonApp(id='/sandbox/spark/spark-app', labels=labels, cpus=0.5, mem=256, disk=256,
                     instances=1, container=container, tasks=[MarathonTask(host='127.0.0.1')])
  app1.tasks_unhealthy = 0
  app1.tasks_running = 1
  return [app1]

def marathon_health_check_get_app():
  docker = MarathonDockerContainer(image='image')
  container = MarathonContainer(docker=docker)
  app1 = MarathonApp(id='/sample', labels={}, cpus=0.5, mem=256, disk=256, instances=1, container=container)
  app1.tasks_unhealthy = 0
  return [app1]
