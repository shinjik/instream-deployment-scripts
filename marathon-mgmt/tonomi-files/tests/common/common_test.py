from io import StringIO
from common.constants import *
import sys
import yaml
import json

sys.path.append('{}/common'.format(BASE_DIR))


class TestCommon(object):
  def prepare_constants(self, app):
    self.LAUNCH_SCRIPT = '{}/{}/{}'.format(BASE_DIR, app, CREATE_SCRIPT)
    self.DISCOVER_SCRIPT = '{}/{}/{}'.format(BASE_DIR, app, DISCOVER_SCRIPT)
    self.HEALTH_CHECK_SCRIPT = '{}/{}/{}'.format(BASE_DIR, app, HEALTH_CHECK_SCRIPT)
    self.DESTROY_SCRIPT = '{}/{}/{}'.format(BASE_DIR, app, DESTROY_SCRIPT)
    self.SCALE_SCRIPT = '{}/{}/{}'.format(BASE_DIR, app, SCALE_SCRIPT)
    self.RESTART_SCRIPT = '{}/{}/{}'.format(BASE_DIR, app, RESTART_SCRIPT)
    self.application = app

  def run_script(self, script_path, input_obj):
    old_stdin = sys.stdin
    old_stdout = sys.stdout

    redirected_out = sys.stdout = StringIO()

    sys.stdin = StringIO(yaml.dump(input_obj))
    with open(script_path) as f:
      exec (f.read())
      sys.stdin = old_stdin
      sys.stdout = old_stdout

    return yaml.safe_load(redirected_out.getvalue())

  def check_script(self, action):
    input_obj, output_obj = self.get_yaml_obj(action)
    script_result = self.run_script(self.get_script(action), input_obj)
    self.check_responses(output_obj, script_result)

  def get_script(self, action):
    if action in self.LAUNCH_SCRIPT:
      return self.LAUNCH_SCRIPT
    elif action in self.DISCOVER_SCRIPT:
      return self.DISCOVER_SCRIPT
    elif action in self.HEALTH_CHECK_SCRIPT:
      return self.HEALTH_CHECK_SCRIPT
    elif action in self.DESTROY_SCRIPT:
      return self.DESTROY_SCRIPT
    elif action in self.SCALE_SCRIPT:
      return self.SCALE_SCRIPT
    elif action in self.RESTART_SCRIPT:
      return self.RESTART_SCRIPT
    return None

  def get_obj_from_yaml(self, action, type):
    with open('{}/{}/{}_{}.yml'.format(YAML_MESSAGES_DIR, self.application, action, type)) as f:
      return yaml.safe_load(f.read())

  def get_input(self, action):
    return self.get_obj_from_yaml(action, INPUT)

  def get_output(self, action):
    return self.get_obj_from_yaml(action, OUTPUT)

  def get_yaml_obj(self, action):
    return self.get_input(action), self.get_output(action)

  def get_expected_app_json(self, action):
    with open('{}/tests/requests/{}_{}_request.json'.format(BASE_DIR, self.application, action)) as f:
      return json.loads(f.read())

  def get_mocked_app_json(self, action):
    with open('{}/tests/requests/{}_{}_response.json'.format(BASE_DIR, self.application, action)) as f:
      return json.loads(f.read())

  def check_responses(self, expected_output_obj, result_output_obj):
    self.assertDictEqual(expected_output_obj, result_output_obj)
