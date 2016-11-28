from marathon.models import MarathonApp
from marathon.models.container import *
import uuid


class EphemeralApplication(object):
  def __init__(self):
    self.cpus = 0.3
    self.mem = 256
    self.app_name = '/ephemeral-{}'.format(uuid.uuid4())

  def commit(self):
    docker = MarathonDockerContainer(image=self.image, network='BRIDGE')
    container = MarathonContainer(docker=docker)
    self.cmd = '{} && wget --method=DELETE {}/v2/apps/{}'.format(self.cmd, self.marathon_client.servers[0], self.app_name)
    app = MarathonApp(id=self.app_name, cmd=self.cmd, cpus=self.cpus, mem=self.mem, instances=1, container=container)
    self.marathon_client.create_app(self.app_name, app)


class CassandraCommand(EphemeralApplication):
  def __init__(self, marathon_client, cass_host, cass_port, content=''):
    super().__init__()
    self.marathon_client = marathon_client
    self.image = 'mesosphere/cqlsh:2.2.5'
    self.cmd = 'echo "{}" > input.cql && cqlsh -f input.cql {} {}'.format(content, cass_host, cass_port)


class CassandraAddMovie(CassandraCommand):
  def __init__(self, marathon_client, cass_host, cass_port, movie, release='2016-01-01', rating='5.0'):
    super().__init__(marathon_client, cass_host, cass_port,
                     "insert into twitter_sentiment.movies (title, release, rating) values ('{}', '{}', {});".format(movie, release, rating))
