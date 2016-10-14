#!/usr/bin/env python3

import sys
import yaml

import marathon_comm



arguments = yaml.safe_load(sys.stdin)
#yaml.safe_dump(arguments, sys.stderr)
marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')
app_ids = list(arguments.get('instances', {}).keys())

instance_results = {}

for app in app_ids:
    #command_id = list(arguments.get('instances', {}).get(app).get('commands').keys())[0]
    marathon_comm.destroy(marathon_url, app)
    instance_results[app] = {}


result = {
    'instances': instance_results
}

yaml.safe_dump(result, sys.stdout)
