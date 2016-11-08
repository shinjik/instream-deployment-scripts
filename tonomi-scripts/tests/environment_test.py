import json
import unittest
from common.constants import *
from common.common_test import *
from common.marathon_client_fakes import *
from mock import MagicMock
from unittest.mock import patch


class TestEnvironmentScripts(unittest.TestCase, TestCommon):
  def setUp(self):
    self.prepare_constants(ENVIRONMENT_APP)

  @unittest.skip('not implemented yet')
  def test_launch(self):
    pass

  @unittest.skip('not implemented yet')
  def test_discover(self):
    pass

  @unittest.skip('not implemented yet')
  def test_health_check(self):
    pass

  @unittest.skip('not implemented yet')
  def test_destroy(self):
    pass


if __name__ == '__main__':
  unittest.main()
