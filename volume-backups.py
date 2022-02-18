import boto3 as boto
import schedule
from operator import itemgetter

ohio_session = boto.Session(profile_name='admin', region_name='us-east-2')
ohio_ec2_client = ohio_session.client('ec2')  # client to describe
ohio_ec2_resource = boto.resource('ec2')  # resource to create

filters = [{'Name': 'tag:Name', 'Values': ['prod', 'dev']}]


def get_volumes(filters):
    response = ohio_ec2_client.describe_volumes(
        Filters=filters
    )
    volumes = response['Volumes']
    return volumes


def create_volume_snapshots(filters):
    volumes = get_volumes(filters)
    for volume in volumes:
        volume_id = volume['VolumeId']
        snapshot_created = ohio_ec2_client.create_snapshot(VolumeId=volume_id)
        print(snapshot_created)


def get_snapshots(volume):
    response = ohio_ec2_client.describe_snapshots(
        OwnerIds=['self'],
        Filters=[
            {
                'Name': 'volume-id',
                'Values': [
                    volume['VolumeId']
                ]
            }
        ]
    )
    snapshots = response['Snapshots']
    return snapshots


def cleans_up_snapshots(filters):
    volumes = get_volumes(filters)
    for volume in volumes:
        snapshots = get_snapshots(volume)
        snapshots_sorted_by_start_time = sorted(snapshots, key=itemgetter("StartTime"), reverse=True)
        for snapshot in snapshots_sorted_by_start_time[2:]:
            snapshot_id = snapshot['SnapshotId']
            response = ohio_ec2_client.delete_snapshot(
                SnapshotId=snapshot_id
            )
            print(response)


def restore_ec2():
    instance_id = "i-02111398c62e02b15"
    filters = [
        {'Name': 'attachment.instance-id', 'Values': [instance_id]}
    ]
    volumes = get_volumes(filters)
    instance_volume = volumes[0]
    snapshots = get_snapshots(instance_volume)
    snapshots_sorted_by_start_time = sorted(snapshots, key=itemgetter("StartTime"), reverse=True)
    latest_snapshot = snapshots_sorted_by_start_time[0]
    print(latest_snapshot)
    volume_created = ohio_ec2_client.create_volume(
        AvailabilityZone='us-east-2b',
        SnapshotId=latest_snapshot['SnapshotId'],
        TagSpecifications=[
            {
                'ResourceType': 'volume',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'dev'
                    },
                ]
            },
        ],
    )

    instance = ohio_ec2_resource.Instance(instance_id)
    while True:
        volume_retrieved = ohio_ec2_resource.Volume(volume_created['VolumeId'])
        if volume_retrieved.state == 'available':
            instance.attach_volume(
                Device='/dev/xvdb',
                VolumeId=volume_created['VolumeId']
            )
            break


restore_ec2()
schedule.every().day.do(create_volume_snapshots, filters)
schedule.every().week.do(cleans_up_snapshots, filters)

while True:
    schedule.run_pending()
