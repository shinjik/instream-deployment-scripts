from io import StringIO
from marathon import MarathonClient
import unittest
import common_test
import requests_mock
import requests
import sys
import yaml
import json


class TestMarathonScripts(unittest.TestCase, common_test.TestCommon):
  def setUp(self):
    self.prepare_constants('marathon')

  @requests_mock.mock()
  def test_launch(self, mock):
    mock.post('{}/v2/apps'.format(self.HOST), text='{"apps": []}')

    input_obj = {
      'configuration': {
        'configuration.marathonURL': self.HOST
      },
      'launch-instances': {
        'sandbox': {
          'configuration': {
            'configuration.name': '/sandbox/sample',
            'configuration.portMappings': [],
            'configuration.cmd': 'python -m SimpleHTTPServer',
            'configuration.cpu': '0.5',
            'configuration.ram': '256',
            'configuration.disk': '256',
            'configuration.instances': '1',
            'configuration.imageId': 'python'
          }
        }
      }
    }

    output_obj = {
      'instances': {
        '/sandbox/sample': {
          'instanceId': 'sandbox',
          '$set': {
            'status.flags.active': False,
            'status.flags.converging': True,
          }
        }
      }
    }

    script_result = self.run_script(self.LAUNCH_SCRIPT, input_obj)
    self.check_responses(output_obj, script_result)

  @requests_mock.mock()
  def test_discover(self, mock):
    mock.get('{}/v2/apps'.format(self.HOST), text='{"apps": []}')

    input_obj = self.DISCOVER_INPUT_OBJ

    output_obj = {
      'instances': {}
    }

    script_result = self.run_script(self.DISCOVER_SCRIPT, input_obj)
    self.check_responses(output_obj, script_result)

  @requests_mock.mock()
  def test_health_check(self, mock):
    pass

  @requests_mock.mock()
  def test_destroy(self, mock):
    mock.delete('{}/v2/apps//sample?force=False'.format(self.HOST), text='{"apps": []}')

    input_obj = {
      'configuration': {
        'configuration.marathonURL': self.HOST
      },
      'instances': {
        '/sample': {
        }
      }
    }

    output_obj = {
      'instances': {
        '/sample': {
          '$set': {
            'status.flags.converging': False,
            'status.flags.active': False,
            'status.flags.failed': False
          }
        }
      }
    }

    script_result = self.run_script(self.DESTROY_SCRIPT, input_obj)
    self.check_responses(output_obj, script_result)

  @requests_mock.mock()
  def test_scale(self, mock):
    pass


if __name__ == '__main__':
  unittest.main()
