import sys
import yaml

import marathon_comm
from helpers import marathon_helpers

class InstreamEnvironment:
    def __init__(self, marathon_url):
        self.marathon_url = marathon_url
    
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value
    

    @property
    def applications(self):
        return self._applications
    


    def load(self, id):
        self.id = id
        apps = marathon_comm.list_apps(self.marathon_url, {'_tonomi_environment': id})
        self._applications = []
        for app in apps:
            self._applications.append(marathon_helpers.get_app_by_type(app.marathon_model['labels']['_tonomi_application'])(self.marathon_url, marathon_comm.get_app_info(self.marathon_url, app.id)))


    def get_apps_by_type(self, apptype):
        a = filter(lambda x: x.labels.get('_tonomi_application') == apptype, self.applications)
        return list(a)

