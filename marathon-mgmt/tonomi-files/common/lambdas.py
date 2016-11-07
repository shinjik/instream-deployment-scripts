from marathon import MarathonClient
from functools import reduce
import yaml
import json
import requests
import sys

parse_args = lambda: yaml.safe_load(sys.stdin)
return_instances_info = lambda instances: yaml.safe_dump({'instances': instances}, sys.stdout)
get_marathon_url = lambda args: args['configuration']['configuration.marathonURL']
get_marathon_client = lambda args: MarathonClient(get_marathon_url(args))
get_name_from_configuration = lambda app: app['configuration']['configuration.name']
get_conf_prop = lambda app, prop: app['configuration']['configuration.{}'.format(prop)]
get_cassandra_ports = lambda app: {
  9042: get_conf_prop(app, 'cql-native-port'),
  9160: get_conf_prop(app, 'jmx-port'),
  7199: get_conf_prop(app, 'thrift-client-port'),
  7000: get_conf_prop(app, 'internode-communication-port'),
  7001: get_conf_prop(app, 'tls-internode-communication-port')
}
get_redis_port = lambda app: get_conf_prop(app, 'port')
get_cassandra_conf = lambda app: (get_conf_prop(app, 'cassandra-host'), get_conf_prop(app, 'cassandra-port'))
get_volume_name = lambda name: 'vol{}-data'.format(name.replace('/', '-'))
reduce_app_name = lambda x: reduce(lambda a, kv: a.replace(kv, ''), ['/cassandra-seed', '/cassandra-node',
                                                                     '/redis-master', '/redis-slave',
                                                                     '/webui-app', '/kafka-broker',
                                                                     '/zookeeper-1', '/zookeeper-2', '/zookeeper-3',
                                                                     '/spark-app'], x)
def get_mesos_hostnames(client):
  hostnames = []
  slaves = json.loads(requests.get('http://{}:5050/slaves'.format(client.servers[0].split(':')[1][2:])).text)['slaves']
  for slave in slaves:
    if slave['active']:
      hostnames.append(slave['hostname'])
  return hostnames