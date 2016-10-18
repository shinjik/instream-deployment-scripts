from urllib.parse import urlsplit
import marathon_comm

class MarathonApplication(object):
    _model = {}
    _type = 'generic'
    _dependencies = {}

    def __init__(self, marathon_url, model={}):
        self.marathon_url = marathon_url
        self._model = model

    @property
    def id(self):
        return self._model.get('id')

    @id.setter
    def id(self, value):
        self._model['id'] = value

    @property
    def environment_name(self):
        return self._environment_name
    @environment_name.setter
    def environment_name(self, value):
        self._environment_name = value
    
    def list_dependencies(self):
        return self._dependencies.keys()

    def set_dependency(self, name, value):
        self._dependencies[name] = value

    def get_dependency(self, name):
        return self._dependencies.get(name, None)

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

    def create(self, configurations = None):
        if not configurations:
            configurations = self._get_creation_defaults()
        for conf in configurations:
            if self._environment_name:
                conf['configuration.labels'].update({'_tonomi_environment': self._environment_name})
            marathon_comm.create(self.marathon_url, conf)

        self.load(self.id)

    def update(self):
        if not self._model:
            raise RuntimeError
        self._model.pop('uris', None)
        self._model.pop('tasks', None)
        self._model.pop('version', None)
        marathon_comm.update(self.marathon_url, self.id, self._model)
        self.load(self.id)

    # Naive destroy, won't work with multi-container deployments
    def destroy(self):
        marathon_comm.destroy(self.marathon_url, self.id)

    # app-related logic goes here

    def get_info(self):
        return {}

    def __str__(self):
        return "MarathonApp({})".format(self.id)

    def __repr__(self):
        return str(self)
