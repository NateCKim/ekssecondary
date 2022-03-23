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

        
    def listToString(c): 
    
        # initialize an empty string
        str1 = " " 
    
        # return string  
        return (str1.join(c))

    def get_progress_target(self):
        return None

    def run(self, progress_callback):
        cluster_data, dss_cluster_settings, dss_cluster_config = get_cluster_from_dss_cluster(self.config['clusterId'])

        command_outputs = []
            
        if cluster_data is None:
            raise Exception("No cluster data (not started?)")
        cluster_def = cluster_data.get("cluster", None)
        if cluster_def is None:
            raise Exception("No cluster definition (starting failed?)")        
        
        cluster_id = cluster_def["Name"]
        kube_config_path = dss_cluster_settings.get_raw()['containerSettings']['executionConfigsGenericOverrides'][
            'kubeConfigPath']
        connection_info = dss_cluster_config.get('config', {}).get('connectionInfo', {})
        

        args = ['eks', 'update-kubeconfig']
        args = args + ['--name', str(self.config['clusterId'])]

        if _has_not_blank_property(connection_info, 'region'):
            args = args + ['--region', connection_info['region']]
        elif 'AWS_DEFAULT_REGION' is os.environ:
            args = args + ['--region', os.environ['AWS_DEFAULT_REGION']]

        c = AwsCommand(args, connection_info)
        command_outputs.append(c.run())
        if command_outputs[-1][1] != 0:
            return command_outputs

        
       # subnets = self.config.get('privateSubnets')
       # securitygroup = self.config.get('securityGroup')
        #getting AZ of the private subnet
        #CLI command to get a list of AZ based on subnetID (need JQ or Sed like command to filter it)

        
  #      with open("test.yaml", "w") as f:
 #           f.write("""apiVersion: crd.k8s.amazonaws.com/v1alpha1
 #           kind: ENIConfig
  #          metadata:
   #           name: """ + subnets + """
    #            spec:
     #         subnet: """ + Eniconfig.subnetId + """    #add multiple subnets 
      #        securityGroups:
       #       - """ + Eniconfig.securityGroupId)
        #    f.close()
        
        #result = subnets
        #return result