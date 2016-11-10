#!/usr/bin/env python3

import json
import unittest
from common.constants import *
from common.common_test import *
from common.marathon_fake_methods import *
from mock import MagicMock
from unittest.mock import patch
from collections import namedtuple


class TestZookeeperScripts(unittest.TestCase, TestCommon):
  def setUp(self):
    self.prepare_constants(ZOOKEEPER_APP)

  @patch('requests.get')
  @patch('requests.Session.request')
  def test_launch(self, request, get):
    mesos_response_json = {'slaves': [{'active': True, 'hostname': '127.0.0.{}'.format(i)} for i in range(1, 4)]}
    get.return_value = namedtuple('Struct', 'text')(text=json.dumps(mesos_response_json))
    request.return_value = MagicMock(status_code=201)
    self.check_script(CREATE_ACTION)
    self.assertEqual(1, len(get.mock_calls))
    self.assertEqual(3, len(request.mock_calls))

  @patch('marathon.MarathonClient.list_apps')
  def test_discover(self, list_apps):
    list_apps.return_value = zookeeper_discover_list_apps()
    self.check_script(DISCOVER_ACTION)
    self.assertEqual(1, len(list_apps.mock_calls))

  @patch('marathon.MarathonClient.list_apps')
  @patch('marathon.MarathonClient.get_app')
  def test_health_check(self, get_app, list_apps):
    get_app.side_effect = zookeeper_health_check_get_app()
    list_apps.side_effect = zookeeper_health_check_list_apps()
    self.check_script(HEALTH_CHECK_ACTION)
    self.assertEqual(1, len(list_apps.mock_calls))
    self.assertEqual(3, len(get_app.mock_calls))

  @patch('marathon.MarathonClient.delete_group')
  def test_destroy(self, delete_group):
    self.check_script(DESTROY_ACTION)
    self.assertEqual(1, len(delete_group.mock_calls))

  @unittest.skip('not implemented yet')
  def test_scale(self):
    pass


if __name__ == '__main__':
  unittest.main()
