from marathon import MarathonClient
import yaml
import sys

parse_args = lambda: yaml.safe_load(sys.stdin)
return_instances_info = lambda instances: yaml.safe_dump({'instances': instances}, sys.stdout)
get_marathon_url = lambda args: args['configuration']['configuration.marathonURL']
get_marathon_client = lambda args: MarathonClient(get_marathon_url(args))

