from dataiku.runnables import Runnable
import os
import yaml
import json
from dku_aws.aws_command import AwsCommand
from dku_utils.cluster import get_cluster_from_dss_cluster, get_cluster_generic_property, set_cluster_generic_property
from dku_utils.access import _has_not_blank_property
from dku_kube.kubectl_command import run_with_timeout, KubeCommandException
from dku_utils.access import _has_not_blank_property, _is_none_or_blank


def make_html(command_outputs):
    divs = []
    for command_output in command_outputs:
        cmd_html = '<div>Run: %s</div>' % json.dumps(command_output[0])
        rv_html = '<div>Returned %s</div>' % command_output[1]
        out_html = '<div class="alert alert-info"><div>Output</div><pre class="debug" style="max-width: 100%%; max-height: 100%%;">%s</pre></div>' % command_output[2]
        err_html = '<div class="alert alert-danger"><div>Error</div><pre class="debug" style="max-width: 100%%; max-height: 100%%;">%s</pre></div>' % command_output[3]
        divs.append(cmd_html)
        divs.append(rv_html)
        divs.append(out_html)
        if command_output[1] != 0 and not _is_none_or_blank(command_output[3]):
            divs.append(err_html)
    return '\n'.join(divs).decode('utf8')

def listToString(s): 
    
    # initialize an empty string
    str1 = " " 
    
    # return string  
    return (str1.join(s))

class MyMacro(Runnable):
    def __init__(self, project_key, config, plugin_config):
        self.project_key = project_key
        self.config = config

      

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
            return make_html(command_outputs)
        print(command_outputs)
        
        #getting the list of subnets and AZs associated with it. Creating a Dict to pass it to ENIConfig template
        subnets = self.config.get('privateSubnets')
        securitygroup = self.config.get('securityGroup')
        
        sublist = []
        subdict = {}
        zonelist = []
        zonedict = {}
        for subnet in subnets:
            t = subdict
            t['enisub'] = subnet
            args = ['ec2', 'describe-subnets']
            args = args + ['--subnet-ids', subnet]
            #args = args + ['| jq ".Subnets[].AvailabilityZone"']
            args = args + ['--query', 'Subnets[0].AvailabilityZone']
            c = AwsCommand(args, connection_info)
            command_outputs.append(c.run())
            t['az'] = command_outputs[1][2].strip().replace('"','')
            print(t['az'])
            sublist.append(t)
            
        #empty list 

        #### empty ENI Config
        d = {'apiVersion':'crd.k8s.amazonaws.com/v1alpha1',
                     'kind':'ENIConfig',
                     'metadata':{'name':''},
                     'spec':{     
                    }
            }
        yamlCfg = ""
        for zone in sublist:
            eniCfg = d
            eniCfg['metadata']['name'] = zone['az']
            eniCfg['spec']['securityGroups'] = []
            eniCfg['spec']['securityGroups'].append(securitygroup)
            eniCfg['spec']['subnet'] = zone['enisub']
            #print(eniCfg)
            yamlCfg += yaml.dump(eniCfg)

        print(yamlCfg)
        
        with open("test.yaml", "w") as f:
            f.write("""apiVersion: crd.k8s.amazonaws.com/v1alpha1
            kind: ENIConfig
            metadata:
              name: """ + "us-east-1a" + """
                spec:
            subnet: """ + str(s[0]) + """    #add multiple subnets 
              securityGroups:
              - """ + securitygroup)
            f.close()
        
        result = "success"
        return result