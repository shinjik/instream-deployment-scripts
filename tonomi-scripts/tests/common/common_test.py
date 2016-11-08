from io import StringIO
from common.constants import *
import sys
import yaml
import json

sys.path.append(COMMON_PYTHONPATH)


class TestCommon(object):
  def prepare_constants(self, app):
    for script in SCRIPTS:
      setattr(self, script, '{}/{}/{}'.format(BASE_DIR, app, globals()[script]))
    self.application = app

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

  def check_script(self, action):
    input_obj, output_obj = self.get_yaml_obj(action)
    script_result = self.run_script(self.get_script(action), input_obj)
    self.check_responses(output_obj, script_result)

  def get_script(self, action):
    for x in SCRIPTS:
      if action in getattr(self, x):
        return getattr(self, x)
    return None

  def get_obj_from_yaml(self, action, type):
    with open('{}/{}/{}_{}.yml'.format(YAML_TEST_DATA_DIR, self.application, action, type)) as f:
      return yaml.safe_load(f.read())

  def get_input(self, action):
    return self.get_obj_from_yaml(action, INPUT)

  def get_output(self, action):
    return self.get_obj_from_yaml(action, OUTPUT)

  def get_yaml_obj(self, action):
    return self.get_input(action), self.get_output(action)

  def check_responses(self, expected_output_obj, result_output_obj):
    self.assertDictEqual(expected_output_obj, result_output_obj)
