#!/usr/bin/env python3

import sys
import yaml

import marathon_comm
from model import InstreamEnvironment


arguments = yaml.safe_load(sys.stdin)
#yaml.safe_dump(arguments, sys.stderr)
marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')
env_ids = list(arguments.get('instances', {}).keys())

instance_results = {}

for envid in env_ids:
    env = InstreamEnvironment(marathon_url)
    env.load(envid)
    env.destroy()

    instance_results[app] = {}


result = {
    'instances': instance_results
}

yaml.safe_dump(result, sys.stdout)
