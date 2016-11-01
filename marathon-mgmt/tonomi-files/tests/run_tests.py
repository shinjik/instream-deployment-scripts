from unittest import TestLoader, TextTestRunner, TestSuite
from marathon_test import TestMarathonScripts


if __name__ == "__main__":
  loader = TestLoader()
  suite = TestSuite((
    loader.loadTestsFromTestCase(TestMarathonScripts)
  ))

  runner = TextTestRunner(verbosity = 2)
  runner.run(suite)