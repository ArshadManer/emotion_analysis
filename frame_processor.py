# fargate_preprocess.py (Run in Fargate)

import boto3
import redis
import json

# Initialize SQS and Redis clients
sqs_client = boto3.client('sqs')
sqs_url_preprocessing = 'https://sqs.ap-south-1.amazonaws.com/your_account_id/demo_preprocessing_queue.fifo'
redis_client = redis.StrictRedis(host='your_redis_endpoint', port=6379, db=0)

def preprocess_frame(frame_data):
    # Preprocessing logic (e.g., feature extraction)
    return frame_data

def process_sqs_messages():
    while True:
        response = sqs_client.receive_message(
            QueueUrl=sqs_url_preprocessing,
            MaxNumberOfMessages=10,  # Get up to 10 messages at once
            WaitTimeSeconds=20
        )
        messages = response.get('Messages', [])

        for message in messages:
            frame_data = json.loads(message['Body'])
            session_id = frame_data['session_id']

            # Preprocess frame data
            preprocessed_frame = preprocess_frame(frame_data)

            # Push preprocessed frame to Redis
            redis_client.rpush(f'session:{session_id}:frames', json.dumps(preprocessed_frame))

            # Count frames and check if 10 frames are available for the session
            frame_count = redis_client.incr(f'session:{session_id}:frame_count')
            if frame_count == 10:
                # Publish event to Redis Pub/Sub once 10 frames are processed
                redis_client.publish('frames_ready', session_id)

            # Delete the message from the queue once processed
            sqs_client.delete_message(QueueUrl=sqs_url_preprocessing, ReceiptHandle=message['ReceiptHandle'])

if __name__ == "__main__":
    process_sqs_messages()
