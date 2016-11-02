#!/usr/bin/env python3

from unittest import TestLoader, TextTestRunner, TestSuite
from marathon_test import TestMarathonScripts
from zookeeper_test import TestZookeeperScripts
from redis_test import TestRedisScripts
from cassandra_test import TestCassandraScripts
from kafka_test import TestKafkaScripts
from webui_test import TestWebUIScripts
from spark_test import TestSparkScripts
from environment_test import TestEnvironmentScripts


if __name__ == "__main__":
  loader = TestLoader()
  suite = TestSuite((
    loader.loadTestsFromTestCase(TestMarathonScripts),
    loader.loadTestsFromTestCase(TestZookeeperScripts),
    loader.loadTestsFromTestCase(TestRedisScripts),
    loader.loadTestsFromTestCase(TestCassandraScripts),
    loader.loadTestsFromTestCase(TestKafkaScripts),
    loader.loadTestsFromTestCase(TestWebUIScripts),
    loader.loadTestsFromTestCase(TestSparkScripts),
    loader.loadTestsFromTestCase(TestEnvironmentScripts)
  ))

  runner = TextTestRunner(verbosity = 2)
  runner.run(suite)