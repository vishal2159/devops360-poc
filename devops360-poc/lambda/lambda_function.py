import json

import time

import boto3

 

dynamodb = boto3.resource('dynamodb')

sns = boto3.client('sns')

 

# names - change if you want

LOCK_TABLE = 'DevOps360_Locks'

SNS_ARN = ''  # set to your topic ARN after deploy

 

 

def resp(code, body):

    return { 'statusCode': code, 'body': json.dumps(body), 'headers': { 'Content-Type': 'application/json' } }

 

 

def lambda_handler(event, context):

    path = event.get('rawPath') if 'rawPath' in event else event.get('path','')

    method = event.get('requestContext',{}).get('http',{}).get('method') if 'requestContext' in event else event.get('httpMethod','')

 

    table = dynamodb.Table(LOCK_TABLE)

 

    # POST /env-lock

    if path.endswith('/env-lock') and method == 'POST':

        body = json.loads(event.get('body') or '{}')

        user = body.get('user','unknown')

        item = { 'env': 'staging', 'locked_by': user, 'ts': int(time.time()) }

        table.put_item(Item=item)

        if SNS_ARN:

            sns.publish(TopicArn=SNS_ARN, Message=f"🔒 {user} locked staging", Subject='DevOps360 Lock')

        return resp(200, {'locked': True, 'by': user})

 

    # DELETE /env-lock

    if path.endswith('/env-lock') and method == 'DELETE':

        table.delete_item(Key={'env':'staging'})

        if SNS_ARN:

            sns.publish(TopicArn=SNS_ARN, Message=f"🔓 staging unlocked", Subject='DevOps360 Lock')

        return resp(200, {'locked': False})

 

    # GET /env-lock-check

    if path.endswith('/env-lock-check') and (method == 'GET' or method == ''):

        r = table.get_item(Key={'env':'staging'})

        if 'Item' in r:

            return resp(200, {'locked': True, 'by': r['Item']['locked_by']})

        else:

            return resp(200, {'locked': False})

 

    # POST /analyze-log  (Auto-heal simulator)

    if path.endswith('/analyze-log') and method == 'POST':

        body = json.loads(event.get('body') or '{}')

        log = body.get('log','')

        action = 'none'

        message = 'No pattern matched.'

        if 'OutOfMemoryError' in log or 'heap out of memory' in log:

            action = 'reboot'

            message = 'Detected OOM - recommend reboot EC2.'

        elif 'ENOSPC' in log or 'no space left' in log:

            action = 'cleanup'

            message = 'Detected disk full - recommend cleanup via SSM.'

        # publish to SNS

        if SNS_ARN:

            sns.publish(TopicArn=SNS_ARN, Message=message, Subject='DevOps360 AutoHeal')

        return resp(200, {'action': action, 'message': message})

 

    return resp(400, {'error': 'unknown path'})

