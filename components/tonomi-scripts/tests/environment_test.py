#!/usr/bin/env python3

import json
import unittest
from common.constants import *
from common.common_test import *
from common.marathon_fake_methods import *
from mock import MagicMock
from unittest.mock import patch
from mock import mock


class TestEnvironmentScripts(unittest.TestCase, TestCommon):
  def setUp(self):
    self.prepare_constants(ENVIRONMENT_APP)

  @patch('models.MarathonManager.get_app_host')
  @patch('models.MarathonManager.free_ports')
  @patch('models.MarathonManager.create')
  def test_launch(self, create, free_ports, get_app_host):
    get_app_host.side_effect = ['127.0.0.1', '127.0.0.2', '127.0.0.3', '127.0.0.4']
    free_ports.return_value = [10000+i for i in range(1, 12)]
    create.return_value = True
    self.check_script(CREATE_ACTION)
    self.assertEqual(6, len(create.mock_calls))
    self.assertEqual(4, len(get_app_host.mock_calls))
    self.assertEqual(1, len(free_ports.mock_calls))

  @patch('marathon.MarathonClient.list_apps')
  def test_discover(self, list_apps):
    list_apps.return_value = environment_discover_list_apps()
    self.check_script(DISCOVER_ACTION)
    self.assertEqual(1, len(list_apps.mock_calls))

  @patch('marathon.MarathonClient.get_group')
  @patch('marathon.MarathonClient.get_app')
  def test_health_check(self, get_app, get_group):
    get_group.return_value = environment_health_check_get_group()
    get_app.side_effect = environment_health_check_get_app()
    self.check_script(HEALTH_CHECK_ACTION)
    self.assertEqual(1, len(get_group.mock_calls))
    self.assertEqual(10, len(get_app.mock_calls))

  @patch('marathon.MarathonClient.delete_group')
  def test_destroy(self, delete_group):
    self.check_script(DESTROY_ACTION)
    self.assertEqual(1, len(delete_group.mock_calls))


if __name__ == '__main__':
  unittest.main()
