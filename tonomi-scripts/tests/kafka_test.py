import json
import unittest
from common.constants import *
from common.common_test import *
from common.marathon_client_fakes import *
from mock import MagicMock
from unittest.mock import patch


class TestKafkaScripts(unittest.TestCase, TestCommon):
  def setUp(self):
    self.prepare_constants(KAFKA_APP)

  @unittest.skip('not implemented yet')
  def test_launch(self):
    pass

  @patch('marathon.MarathonClient.list_apps')
  def test_discover(self, list_apps):
    list_apps.return_value = kafka_discover_list_apps()
    self.check_script(DISCOVER_ACTION)
    self.assertEqual(1, len(list_apps.mock_calls))

  @unittest.skip('not implemented yet')
  def test_health_check(self):
    pass

  @patch('marathon.MarathonClient.delete_app')
  def test_destroy(self, delete_app):
    self.check_script(DESTROY_ACTION)
    self.assertEqual(1, len(delete_app.mock_calls))

  @patch('marathon.MarathonClient.scale_app')
  def test_scale(self, scale_app):
    self.check_script(SCALE_ACTION)
    self.assertEqual(1, len(scale_app.mock_calls))


if __name__ == '__main__':
  unittest.main()
