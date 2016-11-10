from marathon import MarathonClient
from functools import reduce
import yaml
import json
import requests
import sys


def parse_args():
  return yaml.safe_load(sys.stdin)


def return_instances_info(instances):
  return yaml.safe_dump({'instances': instances}, sys.stdout)


def get_marathon_url(args):
  return args['configuration']['configuration.marathonURL']


def get_marathon_client(args):
  return MarathonClient(get_marathon_url(args))


def get_name_from_conf(app):
  return app['configuration']['configuration.name']


def get_conf_prop(app, prop):
  return app['configuration']['configuration.{}'.format(prop)]


def get_cassandra_ports(app):
  return {
    9042: get_conf_prop(app, 'cql-native-port'),
    9160: get_conf_prop(app, 'jmx-port'),
    7199: get_conf_prop(app, 'thrift-client-port'),
    7000: get_conf_prop(app, 'internode-communication-port'),
    7001: get_conf_prop(app, 'tls-internode-communication-port')
  }


def get_redis_port(app):
  return get_conf_prop(app, 'port')


def get_cassandra_conf(app):
  return get_conf_prop(app, 'cassandra-host'), get_conf_prop(app, 'cassandra-port')


def get_volume_name(name):
  return 'vol{}-data'.format(name.replace('/', '-'))


def reduce_app_name(x):
  return reduce(lambda a, kv: a.replace(kv, ''), ['/zookeeper-1', '/zookeeper-2', '/zookeeper-3',
                                                  '/redis-master', '/redis-slave',
                                                  '/cassandra-seed', '/cassandra-node',
                                                  '/kafka-broker', '/webui-app', 'spark-app'], x)


def get_hostname_from_client(client):
  return client.servers[0].split(':')[1][2:]


def get_mesos_slaves_json(client):
  return json.loads(requests.get('http://{}:5050/slaves'.format(get_hostname_from_client(client))).text)['slaves']


def get_mesos_hostnames(client):
  hostnames = []
  for slave in get_mesos_slaves_json(client):
    if slave['active']:
      hostnames.append(slave['hostname'])
  return hostnames


def get_used_ports(client):
  used_ports = []
  for slave in get_mesos_slaves_json(client):
    try:
      str_ports_ranges = slave['used_resources']['ports'].replace('[', '').replace(']', '').split(', ')
      for x in str_ports_ranges:
        used_ports.extend([x for x in range(int(x.split('-')[0]), int(x.split('-')[1]) + 1)])
    except:
      continue
  return set(used_ports)


def get_free_ports(client, num=1):
  start_port = 31100
  end_port = 31900
  ports = []
  used_ports = get_used_ports(client)
  for x in range(start_port, end_port):
    if num == 0:
      break
    if x not in used_ports:
      ports.append(x)
      num -= 1
  return ports
