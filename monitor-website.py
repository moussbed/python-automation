import requests
import smtplib
import os
import logging
import paramiko
import boto3 as boto
import time
import schedule

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORDS = os.environ.get("EMAIL_PASSWORDS")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")
KEY_FILE_NAME = os.environ.get("KEY_FILE_NAME")
SERVER_HOST = os.environ.get("SERVER_HOST")
USER_NAME = os.environ.get("USER_NAME")
INSTANCE_ID = 'i-0e0a4dad3d5fd7000'
ohio_session = boto.Session(profile_name='admin', region_name='us-east-2')
ohio_ec2_client = ohio_session.client('ec2')


def send_email(msg):
    print("Sending an email ... ")
    # Send email to me
    # https://myaccount.google.com/lesssecureapps (Disable MFA )
    # https://myaccount.google.com/u/1/apppasswords (temporary passwords)
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        # This custom password is generated here (https://myaccount.google.com/u/1/apppasswords)
        # This process is useful because we don't have to give our password to a third-party application
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORDS)
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_RECEIVER, msg)


def restart_app():
    print("Restarting the application ... ")
    # Restart application
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=USER_NAME, key_filename=KEY_FILE_NAME)
    # Retrieve container id
    command = "docker ps -a --filter \"name=nginx\" | awk -F \" \" '{print $1}' | sort -r | head -1"
    stdin, stdout, stderr = ssh.exec_command(command)
    container_id = stdout.readline()
    # Start container
    command = f"docker start {container_id}"
    ssh.exec_command(command)
    ssh.close()


def rebooting_server_and_start_app():
    # Restart EC2 Server
    print("Rebooting the server ...")
    ohio_ec2_client.reboot_instances(
        InstanceIds=[
            INSTANCE_ID
        ],
    )
    while True:
        instance_state = ohio_ec2_client.describe_instances(
            InstanceIds=[
                INSTANCE_ID
            ]
        )['Reservations'][0]['Instances'][0]['State']['Name']
        print(instance_state)
        if instance_state == 'running':
            time.sleep(10)
            restart_app()
            break


def monitor_application():
    try:
        response = requests.get("http://ec2-18-191-227-200.us-east-2.compute.amazonaws.com:8080")
        status_code = response.status_code
        if status_code == 200:
            print("Application is running successfully!")
        else:
            print("Application down!")
            msg = f"Subject: SITE DOWN\nApplication returned {status_code}."
            send_email(msg)
            restart_app()

    except Exception as ex:
        msg = "Subject: SITE DOWN\nApplication not accessible at all."
        send_email(msg)
        logging.error(f"Connection error happened {ex}")
        rebooting_server_and_start_app()


schedule.every(5).seconds.do(monitor_application)

while True:
    schedule.run_pending()
