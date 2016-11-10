#!/usr/bin/env python3

import json
import unittest
from common.constants import *
from common.common_test import *
from common.marathon_fake_methods import *
from mock import MagicMock
from unittest.mock import patch


class TestSparkScripts(unittest.TestCase, TestCommon):
  def setUp(self):
    self.prepare_constants(SPARK_APP)

  @patch('requests.Session.request')
  def test_launch(self, request):
    request.return_value = MagicMock(status_code=201)
    self.check_script(CREATE_ACTION)
    self.assertEqual(1, len(request.mock_calls))

  @patch('marathon.MarathonClient.list_apps')
  def test_discover(self, list_apps):
    list_apps.return_value = spark_discover_list_apps()
    self.check_script(DISCOVER_ACTION)
    self.assertEqual(1, len(list_apps.mock_calls))

  @patch('marathon.MarathonClient.get_app')
  def test_health_check(self, get_app):
    get_app.side_effect = spark_health_check_get_app()
    self.check_script(HEALTH_CHECK_ACTION)
    self.assertEqual(1, len(get_app.mock_calls))

  @patch('marathon.MarathonClient.delete_group')
  def test_destroy(self, delete_group):
    self.check_script(DESTROY_ACTION)
    self.assertEqual(1, len(delete_group.mock_calls))

  @unittest.skip('not implemented yet')
  def test_scale(self):
    pass


if __name__ == '__main__':
  unittest.main()
