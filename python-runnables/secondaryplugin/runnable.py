# This file is the actual code for the Python runnable secondaryplugin
from dataiku.runnables import Runnable
import os
import yaml
from dku_aws.aws_command import AwsCommand
from dku_utils.cluster import get_cluster_from_dss_cluster, get_cluster_generic_property, set_cluster_generic_property
from dku_utils.access import _has_not_blank_property
from dku_kube.kubectl_command import run_with_timeout, KubeCommandException
from dku_utils.access import _has_not_blank_property, _is_none_or_blank


class MyRunnable(Runnable):
    """The base interface for a Python runnable"""

    def __init__(self, project_key, config, plugin_config):
        """
        :param project_key: the project in which the runnable executes
        :param config: the dict of the configuration of the object
        :param plugin_config: contains the plugin settings
        """
        self.project_key = project_key
        self.config = config
        self.plugin_config = plugin_config

    def get_progress_target(self):
        return None

    def run(self, progress_callback):
        cluster_data, dss_cluster_settings, dss_cluster_config = get_cluster_from_dss_cluster(self.config['clusterId'])

        if cluster_data is None:
            raise Exception("No cluster data (not started?)")
        cluster_def = cluster_data.get("cluster", None)
        if cluster_def is None:
            raise Exception("No cluster definition (starting failed?)")

        cluster_id = cluster_def["Name"]
        kube_config_path = dss_cluster_settings.get_raw()['containerSettings']['executionConfigsGenericOverrides'][
            'kubeConfigPath']
        connection_info = dss_cluster_config.get('config', {}).get('connectionInfo', {})

        # needs to set kubectl context

        # needs to set env variable

        # needs AWS commands to query and get subnets

        # this is creating yaml file for each AZ
        # needs modification so that it can append subnets that are in same AZ
        # create 1 file per AZ
        def create_eniconfig(Eniconfig):

            with open(Eniconfig.name + ".yaml", "w") as f:
                f.write("""apiVersion: crd.k8s.amazonaws.com/v1alpha1
            kind: ENIConfig
            metadata:
              name: """ + Eniconfig.name + """
                spec:
              subnet: """ + Eniconfig.subnetId + """    #add multiple subnets 
              securityGroups:
              - """ + Eniconfig.securityGroupId)
            f.close()

    # ability to run kubectl command
    # kubectl describe nodes | grep 'failure-domain.beta.kubernetes.io/zone'
    # kubectl set env daemonset aws-node -n kube-system ENI_CONFIG_LABEL_DEF=failure-domain.beta.kubernetes.io/zone

    # node restart?

    raise Exception("unimplemented")
