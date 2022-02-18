import boto3 as boto
import schedule

ohio_eks_client = boto.client('eks')

clusters_names = ohio_eks_client.list_clusters()['clusters']


def getClustersInfo():
    for cluster_name in clusters_names:
        response = ohio_eks_client.describe_cluster(name=cluster_name)
        cluster = response['cluster']
        cluster_status = cluster['status']
        cluster_endpoint = cluster['endpoint']
        cluster_version = cluster['version']
        print(f"Cluster {cluster_name} is {cluster_status}")
        print(f"Cluster endpoint : {cluster_endpoint}")
        print(f"Cluster version : {cluster_version}")


def getNodegroupsInfo():
    for cluster_name in clusters_names:
        response = ohio_eks_client.list_nodegroups(
            clusterName=cluster_name
        )
        nodegroups_names = response['nodegroups']
        if nodegroups_names:
            for nodegroup_name in nodegroups_names:
                response = ohio_eks_client.describe_nodegroup(
                    clusterName=cluster_name,
                    nodegroupName=nodegroup_name
                )
                nodegroup = response['nodegroup']
                nodegroup_status = nodegroup['status']
                nodegroup_capacity_type = nodegroup['capacityType']
                nodegroup_scaling_config = nodegroup['scalingConfig']
                print(f"Nodegroup {nodegroup_name} is {nodegroup_status}")
                print(f"Nodegroup capacity type {nodegroup_capacity_type}")
                print(f"Nodegroup scaling configuration :\n \t"
                      f" min size ({nodegroup_scaling_config['minSize']}) max size ({nodegroup_scaling_config['maxSize']}) "
                      f"desired size ({nodegroup_scaling_config['desiredSize']})")
                nodegroup_instance_types = nodegroup['instanceTypes']
                for nodegroup_instance_type in nodegroup_instance_types:
                    print(f"Instance type  {nodegroup_instance_type}")
                    
            print("###################################################\n")


schedule.every(5).seconds.do(getClustersInfo)
schedule.every(5).seconds.do(getNodegroupsInfo)

while True:
    schedule.run_pending()
