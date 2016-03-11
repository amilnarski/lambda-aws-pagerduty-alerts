# lambda-aws-pagerduty-alerts

This python lambda function makes your alerting to PagerDuty a bit smarter for your Route53 and Autoscaling (upscaling) alerts.

### Route53

By default, when you chain an alert from Route53, to CloudWatch, to PagerDuty, it does not show the actual name of the healthcheck. The reason for this, is that this data (the name) is simply not available in the AWS API.
But we do want to show some useful data, so we get the FQDN of the endpoint domain, and shove the rest of the data we grab from that Healthcheck into the "Detailed" view on Pagerduty.

### AWS Upscaling

You can set your alerts, for when an ASG has to upscale according to your rules, to always alert you. The filter on this function actually only alerts you when the upscaling rules have hit a wall:
The ASG can't upscale any further, but still has high load, this means you need eyes immediately. When the ASG can still upscale, there are no eyes needed as this is actually kind behaviour.

## Develop how-to

- Install https://github.com/fugue/emulambda
- Test with `emulambda main.handler test/event-$EVENT.json`
- Zip the contents of `lambda-alerting`, and upload to s3 bucket (TODO: pick s3 bucket)

## How to virtualenv

- Project root: `virtualenv env`
- Project root: `source venv/bin/activate`
- Do your pip installs in the project dir `pip install boto3` / `pip install -r requirements.txt`
- Freeze them `pip freeze > requirements.txt`
- Step out of the virtualenv `deactivate`

## How to deploy

- Set your ENV vars in a deploy.env file (you'll have to create this file)
- Zip the contents (!!) of this directory (not the directory itself!) by following the docs here http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html
- Place on s3 or upload directly when creating your lambda function
- It shouldn't need more than 128MB or 5s to execute
- Connect to your alarms
- ???
- Profit!

## Gotcha

- Route53 healthchecks live in US-EAST-1, **always**! This means that the lambda function will have to be deployed to multiple regions when you're not using US-EAST-1 as your default region.
- Make sure the name of your upscale alarm contains "alarmscaleup" (can be Alarm-Scale-Up)

## Todo

- Tests!