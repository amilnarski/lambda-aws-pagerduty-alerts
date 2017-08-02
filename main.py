#!/usr/bin/env python
"""Entry point."""

import logging
import json
import boto3
import string
import random

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

    # Attempt to JSON decode the message for more info
    try:
        alarm = json.loads(sns['Message'])
        # Generate a key for this alarm
        key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    except:
        raise Exception('Could not read JSON! %s', sns['Message'])

    pagerduty.send(subject, key, alarm)
    logger.info('Finished, sent out type "%s" alarm!', subject)
