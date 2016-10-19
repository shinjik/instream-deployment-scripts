from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint, MarathonHealthCheck
from marathon.models.container import *
from marathon.models.app import PortDefinition, Residency
import time
import requests
import json


class ZookeeperNode(object):
    def __init__(self, env_name, node_index, marathon_client, ports, hostnames):
        self.env_name = env_name
        self.marathon_client = marathon_client
        self.node_index = node_index
        self.app_name = '/{}/{}-{}'.format(self.env_name, 'zookeeper', self.node_index)
        self.application = None
        self.ports = ports
        self.hostnames = hostnames

    def create(self):
        volume_name = 'vol{}-data'.format(self.app_name.replace('/', '-'))
        volumes = [
            MarathonContainerVolume(container_path=volume_name, host_path=None, mode='RW', persistent={'size': 512}),
            MarathonContainerVolume(container_path='/var/lib/zookeeper', host_path=volume_name, mode='RW',
                                    persistent=None)
        ]

        docker = MarathonDockerContainer(image='zookeeper', network='HOST', privileged=False)

        labels = {
            '_tonomi_application': 'zookeeper',
            '_tonomi_environment': self.env_name,
            '_client_conn_port': str(self.ports[0]),
            '_follower_conn_port': str(self.ports[1]),
            '_server_conn_port': str(self.ports[2])
        }

        zoo_servers = ''
        for i in range(1, 4):
            zoo_servers += 'server.{}={}:{}:{} '.format(i, self.hostnames[i-1],
                                                        self.ports[1], self.ports[2])

        cmd = 'export ZOO_SERVERS="{}" && /docker-entrypoint.sh zkServer.sh start-foreground' \
            .format(zoo_servers)

        constraints = [MarathonConstraint(field='hostname', operator='LIKE', value=self.hostnames[self.node_index-1])]
        container = MarathonContainer(docker=docker, volumes=volumes)
        residency = Residency(task_lost_behavior='WAIT_FOREVER')
        env = {
            'ZOO_MY_ID': str(self.node_index),
            'ZOO_PORT': str(self.ports[0])
        }

        health_checks = [
            MarathonHealthCheck(grace_period_seconds=300, interval_seconds=20, max_consecutive_failures=3,
                                protocol='TCP', timeout_seconds=20, ignore_http1xx=False, port=self.ports[0])
        ]

        new_zookeeper_app = MarathonApp(id=self.app_name, cmd=cmd, cpus=0.5, mem=300, instances=1, disk=512,
                                        labels=labels,
                                        container=container, constraints=constraints, residency=residency, env=env,
                                        health_checks=health_checks)
        self.marathon_client.create_app(self.app_name, new_zookeeper_app)
        self.application = self.marathon_client.get_app(self.app_name)
        return self.application


class ZookeeperCluster(object):
    def __init__(self, env_name, marathon_client):
        self.env_name = env_name
        self.marathon_client = marathon_client
        self.nodes = []

    def create(self):
        # prepare list of hostanames for constraints
        hostnames = []
        slaves = json.loads(requests.get('http://{}:5050/slaves'.format(self.marathon_client.servers[0].split(':')[1][2:])).text)['slaves']
        for slave in slaves:
            if slave['active']:
                hostnames.append(slave['hostname'])


        ports = [12181, 12888, 13888]
        port_inc = 0

        checked_envs = []

        for app in self.marathon_client.list_apps():
            env_name = app.labels.get('_tonomi_environment', '')
            app_type = app.labels.get('_tonomi_application', '')

            if app_type == 'zookeeper' and env_name not in checked_envs:
                port_inc += 1
                checked_envs.append(env_name)

        ports = [p + port_inc for p in ports]

        for i in range(1, 4):
            node = ZookeeperNode(self.env_name, i, self.marathon_client, ports, hostnames)
            node.create()
            self.nodes.append(node)

    @staticmethod
    def delete_cluster(cluster_name, marathon_client):
        for app in marathon_client.list_apps():
            try:
                env_name = app.labels['_tonomi_environment']
                app_type = app.labels['_tonomi_application']
                if app_type == 'zookeeper' and cluster_name in app.id:
                    marathon_client.delete_app(app.id, True)
            except:
                pass
