import schedule


def get_vpcs(ec2_client):
    vpcs = ec2_client.describe_vpcs().get('Vpcs')
    for vpc in vpcs:
        print(f"Vpc ID : {vpc.get('VpcId')}")
        for cidr in vpc.get('CidrBlockAssociationSet'):
            print(f"CIDR : {cidr.get('CidrBlock')} \n")


def create_vpc_and_subnets(ec2_resource):
    created_vpc = ec2_resource.create_vpc(
        CidrBlock='10.0.0.0/16'
    )
    created_vpc.create_subnet(
        CidrBlock='10.0.1.0/24'
    )
    created_vpc.create_subnet(
        CidrBlock='10.0.2.0/24'
    )
    created_vpc.create_tags(
        Tags=[
            {
                'Key': 'Name',
                'Value': 'my-vpc'
            },
        ]
    )


def get_instance_state(ec2_client):
    reservations = ec2_client.describe_instances()
    for reservation in reservations.get('Reservations'):
        for instance in reservation.get('Instances'):
            print(f"Instance {instance['InstanceId']} is {instance['State']['Name']}")


def get_instance_ids(ec2_client):
    reservations = ec2_client.describe_instances()
    instance_ids = []
    for reservation in reservations.get('Reservations'):
        for instance in reservation.get('Instances'):
            instance_ids.append(instance.get('InstanceId'))
    return instance_ids


def add_tags_to_instances(ec2_resource, ec2_client, environment):
    instances_ids = get_instance_ids(ec2_client)
    ec2_resource.create_tags(
        Resources=instances_ids,
        Tags=[
            {
                'Key': 'environment',
                'Value': environment
            },
        ]
    )


# Status check (Check if instance is fully initialised)
def get_status_check(ec2_client):
    statuses = ec2_client.describe_instance_status(
        IncludeAllInstances=True
    )

    for status in statuses['InstanceStatuses']:
        ins_status = status['InstanceStatus']['Status']
        sys_status = status['SystemStatus']['Status']
        print(f"Instance {status['InstanceId']} status is {ins_status} and system status is {sys_status}")


def schedule_tasks(ec2_client):
    schedule.every().day.at("00:00").do(get_vpcs, ec2_client)
    schedule.every(5).seconds.do(get_instance_state, ec2_client)
    schedule.every(5).seconds.do(get_status_check, ec2_client)

    while True:
        schedule.run_pending()
