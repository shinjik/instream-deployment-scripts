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

  @unittest.skip('not implemented yet')
  def test_scale(self):
    pass


if __name__ == '__main__':
  unittest.main()
