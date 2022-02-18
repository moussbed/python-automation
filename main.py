import boto3 as boto
from util import get_vpcs, create_vpc_and_subnets, get_instance_state, get_status_check, schedule_tasks, add_tags_to_instances

# Ohio Region
ohio_session = boto.Session(profile_name='admin', region_name='us-east-2')
ohio_ec2_client = ohio_session.client('ec2')  # client to describe
ohio_ec2_resource = boto.resource('ec2')  # resource to create

# Virginia Region
virginia_session = boto.Session(profile_name='admin', region_name='us-east-1')
virginia_ec2_client = virginia_session.client('ec2')  # client to describe
virginia_ec2_resource = boto.resource('ec2')  # resource to create

# create_vpc_and_subnets(ec2_resource)
# get_vpcs(ec2_client)
# get_instance_state(ec2_client)
# get_status_check(ec2_client)

add_tags_to_instances(ohio_ec2_resource, ohio_ec2_client, "prod")
add_tags_to_instances(virginia_ec2_resource, virginia_ec2_resource, "staging")

schedule_tasks(ohio_ec2_client)
