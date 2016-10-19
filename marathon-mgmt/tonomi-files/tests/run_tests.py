from unittest import TestLoader, TextTestRunner, TestSuite
from cassandra_test import TestCassandraScripts
from marathon_test import TestMarathonScripts


if __name__ == "__main__":
  loader = TestLoader()
  suite = TestSuite((
    loader.loadTestsFromTestCase(TestCassandraScripts),
    loader.loadTestsFromTestCase(TestMarathonScripts)
  ))

  runner = TextTestRunner(verbosity = 2)
  runner.run(suite)