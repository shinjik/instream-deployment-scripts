from io import StringIO
from marathon import MarathonClient
from marathon.models import MarathonApp
import unittest
from unittest.mock import patch
from common_test import *
import requests_mock
import requests
import sys
import yaml
import json
from mock import MagicMock
from marathon_client_fakes import *


class TestMarathonScripts(unittest.TestCase, TestCommon):

  def setUp(self):
    self.prepare_constants(MARATHON_APP)

  @patch('requests.Session.request')
  def test_launch(self, request):
    request.return_value = MagicMock(status_code=201)

    input_obj, output_obj = self.get_yaml_obj(CREATE_ACTION)

    script_result = self.run_script(self.LAUNCH_SCRIPT, input_obj)
    self.check_responses(output_obj, script_result)

    self.assertEqual(1, len(request.mock_calls))

    json_app_configuration = json.loads(tuple(request.mock_calls[0])[2]['data'])
    self.assertDictEqual(json_app_configuration, self.get_expected_app_json(CREATE_ACTION))

  @patch('marathon.MarathonClient.list_apps')
  def test_discover(self, list_apps):

    list_apps.return_value = marathon_discover_list_apps()

    input_obj, output_obj = self.get_yaml_obj(DISCOVER_ACTION)

    script_result = self.run_script(self.DISCOVER_SCRIPT, input_obj)
    self.check_responses(output_obj, script_result)

    self.assertEqual(1, len(list_apps.mock_calls))

  @patch('marathon.MarathonClient.get_app')
  def test_health_check(self, get_app):

    get_app.side_effect = marathon_health_check_get_app()
    input_obj, output_obj = self.get_yaml_obj(HEALTH_CHECK_ACTION)

    script_result = self.run_script(self.HEALTH_CHECK_SCRIPT, input_obj)

    self.assertEqual(2, len(get_app.mock_calls))
    self.check_responses(output_obj, script_result)

  @patch('marathon.MarathonClient.delete_app')
  def test_destroy(self, delete_app):

    input_obj, output_obj = self.get_yaml_obj(DESTROY_ACTION)

    script_result = self.run_script(self.DESTROY_SCRIPT, input_obj)
    self.check_responses(output_obj, script_result)
    self.assertEqual(1, len(delete_app.mock_calls))

  @patch('marathon.MarathonClient.scale_app')
  def test_scale(self, scale_app):

    input_obj, output_obj = self.get_yaml_obj(SCALE_ACTION)

    script_result = self.run_script(self.SCALE_SCRIPT, input_obj)
    self.check_responses(output_obj, script_result)
    self.assertEqual(1, len(scale_app.mock_calls))


if __name__ == '__main__':
  unittest.main()
