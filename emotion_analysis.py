# fargate_emotion_analysis.py (Run in Fargate)

import boto3
import json
import random

s3_client = boto3.client('s3')
bucket_name = 'arsh-demo'

def perform_emotion_analysis(frames):
    emotions = ['happy', 'sad', 'neutral', 'angry']
    return [random.choice(emotions) for _ in frames]

def process_aggregated_data(aggregated_data):
    session_id = aggregated_data['session_id']
    frames = aggregated_data['frames']

    # Perform emotion analysis
    emotions = perform_emotion_analysis(frames)

    # Store result in S3
    result = {
        'session_id': session_id,
        'frames': frames,
        'emotions': emotions
    }
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f'emotion_analysis/{session_id}.json',
        Body=json.dumps(result)
    )

if __name__ == "__main__":
    # Assuming command-line input or environment variable containing the JSON data
    import sys
    aggregated_data = json.loads(sys.argv[1])
    process_aggregated_data(aggregated_data)
