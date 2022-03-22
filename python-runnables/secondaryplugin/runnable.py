from dataiku.runnables import Runnable

class MyMacro(Runnable):
    def __init__(self, project_key, config, plugin_config):
        self.project_key = project_key
        self.config = config

    def get_progress_target(self):
        return None

    def run(self, progress_callback):
        # Do some things. You can use the dataiku package here

        result = "It worked"
        return result