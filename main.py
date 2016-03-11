#!/usr/bin/env python
"""Entry point."""

import logging
import json
import boto3

from lib.pagerduty import PagerDuty
from lib.config import Config

logging.basicConfig()
logger = logging.getLogger('alerter')


# pylint: disable=C0103
def handler(event, context):
    """Handle incoming SNS events for R53 and ASG Upscaling alarms."""
    logger.setLevel(logging.DEBUG)

    config = Config()
    config.load()

    pagerduty = PagerDuty()

    # Test if we got a message
    try:
        message = event['Records'][0]
    except:
        raise Exception('No records found in SNS message!')

    # Test if the message came from SNS
    if message['EventSource'] != 'aws:sns':
        raise Exception('SNS is not the source of this message!')

    # Determine if Sns is filled and get the subject
    sns = message['Sns']
    try:
        subject = sns['Subject']
    except:
        raise Exception('No subject in SNS message!')

    # Determine what we're handling here
    type = ''
    if subject.lower().find('alarmscaleup') > -1:
        type = 'scaling'
    if subject.lower().find('awsroute53') > -1:
        type = 'r53'

    if type == '':
        raise Exception('Type of alarm cannot be handled! (not scaling/r53)')

    # Attempt to JSON decode the message for more info
    try:
        alarm = json.loads(sns['Message'])
        # Fetch a unique key for this alarm, based off of the actual subject
        key = alarm['Trigger']['Dimensions'][0]['value']
    except:
        raise Exception('Could not read JSON! %s', sns['Message'])

    details = {}
    if type == 'scaling':
        # Check if the ASG can still upscale
        asg = boto3.client('autoscaling')
        response = asg.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
                key
            ]
        )

        try:
            group = response['AutoScalingGroups'][0]
            desired_size = int(group['DesiredCapacity'])
            max_size = int(group['MaxSize'])
        except:
            raise Exception('Could probably not find ASG "%s"!', key)

        if desired_size < max_size:
            raise Exception('ASG can still grow, no need to alert!')

        details = group
        subject = 'ASG: Upscaling "%s" failed, already at MAX_INSTANCES!' % key
    if type == 'r53':
        # Get the actual route53 endpoint
        r53 = boto3.client('route53')
        response = r53.get_health_check(
            HealthCheckId=key
        )
        try:
            check = response['HealthCheck']
            domain = check['HealthCheckConfig']['FullyQualifiedDomainName']
        except:
            raise Exception('Could probably not find that healthcheck "%s"!',
                            key)

        details = check
        subject = 'Route53: Endpoint "%s" is down!' % domain

    if alarm['NewStateValue'] == 'OK':
        pagerduty.resolve(key)

    if alarm['NewStateValue'] == 'ALARM':
        pagerduty.send(subject, key, details)

    logger.info('Finished, sent out type "%s" alarm!', type)
