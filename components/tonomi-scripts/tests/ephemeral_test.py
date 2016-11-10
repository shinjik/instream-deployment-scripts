#!/usr/bin/env python3

from marathon import MarathonClient
from unittest.mock import patch
import unittest
import sys

sys.path.append('tonomi-scripts/scripted-components/common')
from ephemeral import CassandraCommand

class TestEphemeralApplications(unittest.TestCase):
  def setUp(self):
    self.marathon_url = 'http://localhost'

  @patch('marathon.MarathonClient.create_app')
  def test_cassandra_command(self, create_app):
    marathon_client = MarathonClient(self.marathon_url)

    cass_cql = 'insert into movies (movie, release, rating) values (\'my movie\', \'2016-01-01\', 5.5);'
    cass_host = '127.0.0.2'
    cass_port = '9042'

    cass_app = CassandraCommand(marathon_client, cass_host, cass_port, cass_cql)
    cass_app.create()
    self.assertEqual(1, len(create_app.mock_calls))

    app_id = tuple(create_app.mock_calls)[0][1][0]
    gen_cmd = tuple(create_app.mock_calls)[0][1][1].cmd

    cmd = 'echo "{}" > input.cql && cqlsh -f input.cql {} {} && curl -X DELETE {}/v2/apps/{}'\
      .format(cass_cql, cass_host, cass_port, self.marathon_url, app_id)

    self.assertEqual(cmd, gen_cmd)


if __name__ == '__main__':
  unittest.main()
