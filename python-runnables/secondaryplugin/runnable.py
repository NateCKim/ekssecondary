from dataiku.runnables import Runnable
import os
import yaml
from dku_aws.aws_command import AwsCommand
from dku_utils.cluster import get_cluster_from_dss_cluster, get_cluster_generic_property, set_cluster_generic_property
from dku_utils.access import _has_not_blank_property
from dku_kube.kubectl_command import run_with_timeout, KubeCommandException
from dku_utils.access import _has_not_blank_property, _is_none_or_blank

class MyMacro(Runnable):
    def __init__(self, project_key, config, plugin_config):
        self.project_key = project_key
        self.config = config

    def get_progress_target(self):
        return None

    def run(self, progress_callback):
        cluster_data, dss_cluster_settings, dss_cluster_config = get_cluster_from_dss_cluster(self.config['clusterId'])

        node_group_id = self.config.get('privateSubnets')
        print(node_group_id)


        result = node_group_id
        return result