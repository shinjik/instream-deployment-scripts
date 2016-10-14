from urllib.parse import urlsplit
import marathon_comm

class MarathonApplication:
    _model = {}
    _type = 'generic'

    def __init__(self, marathon_url):
        self.marathon_url = marathon_url

    def __init__(self, marathon_url, model):
        self.marathon_url = marathon_url
        self._model = model

    @property
    def id(self):
        return self._model.get('id')

    @id.setter
    def id(self, value):
        self._model['id'] = value

    @property
    def type(self):
        return self._type

    @property
    def port_mappings(self):
        return {str(p['containerPort']): str(p['servicePort']) for p in self._model['container']['docker']['portMappings']}
  
    @property
    def labels(self):
        return self._model.get('labels', {})

    @property
    def tasks(self):
        tasks = []
        for task in self._model['tasks']:
            
            t = {
                    'taskId': task['id'],
                    'host': task['host'],
                    'state': task['state'],
                    'portMappings': { str(p): str(task['ports'][i]) for i,p in enumerate(self.port_mappings.keys())}
                }
            
            tasks.append(t)
        return tasks

    @property
    def lb_host(self):
        url = urlsplit(self.marathon_url)
        return url.netloc.split(':')[0]  

    def load(self, app_id):
        self._model = marathon_comm.get_app_info(self.marathon_url, app_id)


    # app-related logic goes here

    def get_info(self):
        return {}

    def __str__(self):
        return "MarathonApp({})".format(self.id)

    def __repr__(self):
        return str(self)
