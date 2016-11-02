import unittest
from common.marathon_client_fakes import *
from common.common_test import TestCommon
from unittest.mock import patch
from common.constants import *
from mock import MagicMock


class TestRedisScripts(unittest.TestCase, TestCommon):
  def setUp(self):
    self.prepare_constants(REDIS_APP)

  @patch('marathon.MarathonClient.list_apps')
  @patch('marathon.MarathonClient.get_app')
  @patch('requests.Session.request')
  def test_launch(self, request, get_app, list_apps):
    list_apps.return_value = []
    get_app.side_effect = redis_launch_get_app()
    request.return_value = MagicMock(status_code=201)
    self.check_script(CREATE_ACTION)
    self.assertEqual(2, len(request.mock_calls))
    self.assertEqual(1, len(get_app.mock_calls))

  @patch('marathon.MarathonClient.list_apps')
  def test_discover(self, list_apps):
    list_apps.return_value = redis_discover_list_apps()
    self.check_script(DISCOVER_ACTION)
    self.assertEqual(1, len(list_apps.mock_calls))

  @patch('marathon.MarathonClient.list_apps')
  @patch('marathon.MarathonClient.get_app')
  def test_health_check(self, get_app, list_apps):
    list_apps.return_value = redis_health_check_list_apps()
    get_app.side_effect = redis_health_check_get_app()
    self.check_script(HEALTH_CHECK_ACTION)
    self.assertEqual(1, len(list_apps.mock_calls))
    self.assertEqual(2, len(get_app.mock_calls))

  @patch('marathon.MarathonClient.delete_app')
  def test_destroy(self, delete_app):
    self.check_script(DESTROY_ACTION)
    self.assertEqual(2, len(delete_app.mock_calls))

  @unittest.skip('scaling is not implemented yet')
  @patch('marathon.MarathonClient.scale_app')
  def test_scale(self, scale_app):
    pass


if __name__ == '__main__':
  unittest.main()
