from io import StringIO
import sys
import yaml
import json

BASE_DIR = './marathon-mgmt/tonomi-files'
sys.path.append('{}/common'.format(BASE_DIR))

class TestCommon(object):
  def prepare_constants(self, app):
    self.HOST = 'http://localhost'
    self.LAUNCH_SCRIPT = '{}/{}/create.py'.format(BASE_DIR, app)
    self.DISCOVER_SCRIPT = '{}/{}/discover.py'.format(BASE_DIR, app)
    self.HEALTH_CHECK_SCRIPT = '{}/{}/healthCheck.py'.format(BASE_DIR, app)
    self.DESTROY_SCRIPT = '{}/{}/destroy.py'.format(BASE_DIR, app)
    self.SCALE_SCRIPT = '{}/{}/scale.py'.format(BASE_DIR, app)

    self.DISCOVER_INPUT_OBJ = {
      'configuration': {
        'configuration.marathonURL': self.HOST
      }
    }

  def run_script(self, script_path, input_obj):
    old_stdin = sys.stdin
    old_stdout = sys.stdout

    redirected_out = sys.stdout = StringIO()

    sys.stdin = StringIO(yaml.dump(input_obj))
    with open(script_path) as f:
      exec(f.read())
      sys.stdin = old_stdin
      sys.stdout = old_stdout

    return yaml.safe_load(redirected_out.getvalue())

  def check_responses(self, expected_output_obj, result_output_obj):
    expected_out = json.dumps(expected_output_obj)
    result_out = json.dumps(result_output_obj)
    self.assertEqual(expected_out, result_out)