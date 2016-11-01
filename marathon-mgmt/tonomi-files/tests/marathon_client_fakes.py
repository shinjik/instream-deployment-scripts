from marathon.models import MarathonApp
from marathon.models.container import *


def marathon_discover_list_apps():
  return [
    MarathonApp(id='/test/sample', labels={'_tonomi_environment': 'test', '_tonomi_application': 'sample'}),
    MarathonApp(id='/sandbox/sample', labels={'_tonomi_environment': 'sandbox', '_tonomi_application': 'sample'}),
    MarathonApp(id='/sandbox/sample2', labels={'_tonomi_application': 'sample'})
  ]

def marathon_health_check_get_app():

  marathon_apps = []

  docker = MarathonDockerContainer(image='image')

  container = MarathonContainer(docker=docker)

  labels = {'_tonomi_environment': 'sandbox', '_tonomi_application': 'sample'}
  marathon_app1 = MarathonApp(id='/sandbox/sample', labels=labels, cpus=0.5, mem=256, disk=256, instances=1, container=container)
  marathon_app1.tasks_unhealthy = 0

  marathon_app2 = MarathonApp(id='/test/sample', labels={})

  marathon_apps.append(marathon_app1)
  marathon_apps.append(marathon_app2)

  return marathon_apps