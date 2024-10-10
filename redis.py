# lambda_json_aggregator.py (AWS Lambda - Aggregates Preprocessed Frames)

import boto3
import redis
import json

redis_client = redis.StrictRedis(host='your_redis_endpoint', port=6379, db=0)

def lambda_handler(event, context):
    session_id = event['session_id']

    # Retrieve preprocessed frames from Redis
    frames = [json.loads(f) for f in redis_client.lrange(f'session:{session_id}:frames', 0, -1)]

    # Aggregate preprocessed frames into a JSON file
    aggregated_data = {
        'session_id': session_id,
        'frames': frames
    }

    # Trigger Fargate emotion analysis by passing the JSON file
    fargate_client = boto3.client('ecs')
    fargate_client.run_task(
        cluster='your_fargate_cluster',
        taskDefinition='your_fargate_emotion_analysis_task',
        launchType='FARGATE',
        overrides={
            'containerOverrides': [{
                'name': 'emotion_analysis_container',
                'command': [json.dumps(aggregated_data)]
            }]
        },
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': ['your_subnet'],
                'assignPublicIp': 'ENABLED'
            }
        }
    )

    # Cleanup Redis data after aggregation
    redis_client.delete(f'session:{session_id}:frame_count')
    redis_client.delete(f'session:{session_id}:frames')

    return {
        'statusCode': 200,
        'body': json.dumps('JSON aggregation complete and emotion analysis triggered')
    }
