BASE_DIR = './tonomi-scripts/scripted-components'
COMMON_PYTHONPATH = '{}/{}'.format(BASE_DIR, 'common')
YAML_TEST_DATA_DIR = './tonomi-scripts/tests/yaml_test_data'
INPUT = 'input'
OUTPUT = 'output'
HOST = 'http://localhost'

SCRIPTS = ['{}_SCRIPT'.format(x) for x in ['CREATE', 'DISCOVER', 'HEALTH_CHECK', 'DESTROY', 'SCALE', 'RESTART']]

MARATHON_APP = 'marathon'
ZOOKEEPER_APP = 'zookeeper'
REDIS_APP = 'redis'
CASSANDRA_APP = 'cassandra'
KAFKA_APP = 'kafka'
WEBUI_APP = 'webui'
SPARK_APP = 'spark'
ENVIRONMENT_APP = 'isp-environment'
TW_CONSUMER_APP = 'tw-consumer'

CREATE_SCRIPT = 'create.py'
DISCOVER_SCRIPT = 'discover.py'
HEALTH_CHECK_SCRIPT = 'healthCheck.py'
DESTROY_SCRIPT = 'destroy.py'
SCALE_SCRIPT = 'scale.py'
RESTART_SCRIPT = 'restart.py'

CREATE_ACTION = 'create'
DISCOVER_ACTION = 'discover'
HEALTH_CHECK_ACTION = 'healthCheck'
DESTROY_ACTION = 'destroy'
SCALE_ACTION = 'scale'
RESTART_ACTION = 'restart'
