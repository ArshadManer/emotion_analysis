import boto3
import base64
import dlib
import cv2
import os
import json
import numpy as np
from PIL import Image
from io import BytesIO

# AWS clients
sqs = boto3.client('sqs', region_name='ap-south-1')
s3 = boto3.client('s3', region_name='ap-south-1')

# Configuration
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/821670482746/ImageFrameQueue.fifo'
BUCKET_NAME = 'arsh-demo'
S3_FOLDER = 'processed-frames/'  # Folder to store processed frames in S3

def process_image(frame_data_base64):
    """
    Decodes the base64 image, processes it using dlib to detect faces,
    and returns the list of bounding boxes of detected faces.
    """
    # Decode the base64 frame data to binary
    img_data = base64.b64decode(frame_data_base64)
    
    # Convert binary to an image
    img = Image.open(BytesIO(img_data))
    img_array = np.array(img)

    # Convert to grayscale for dlib processing
    gray_img = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # Use dlib's HOG-based face detector
    detector = dlib.get_frontal_face_detector()
    faces = detector(gray_img, 1)

    # List to hold the bounding boxes of detected faces
    face_bounding_boxes = []
    for i, rect in enumerate(faces):
        # Each face will be represented by a dict with the coordinates
        face_bounding_boxes.append({
            "top": rect.top(),
            "bottom": rect.bottom(),
            "left": rect.left(),
            "right": rect.right()
        })

    return face_bounding_boxes

def store_data_in_s3(data, file_name):
    """
    Stores the processed frame data in JSON format in the specified S3 bucket.
    """
    json_data = json.dumps(data)

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f"{S3_FOLDER}{file_name}",
        Body=json_data,
        ContentType='application/json'
    )
    print(f"Data {file_name} stored in S3 bucket {BUCKET_NAME}")

def delete_message_from_sqs(receipt_handle):
    """
    Deletes the processed message from the SQS queue.
    """
    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt_handle
    )
    print("Message deleted from SQS")

def process_sqs_messages():
    """
    Poll the SQS FIFO queue, process each message, and delete it after processing.
    """
    while True:
        # Receive messages from the SQS queue
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,  # Process one message at a time
            WaitTimeSeconds=10,     # Long polling
            MessageAttributeNames=['All'],
            AttributeNames=['All']
        )

        messages = response.get('Messages', [])
        if not messages:
            print("No messages in the queue.")
            continue

        for message in messages:
            # Parse the message content
            body = message['Body']
            receipt_handle = message['ReceiptHandle']
            msg_attributes = message.get('MessageAttributes', {})
            
            session_id = msg_attributes.get('session_id', {}).get('StringValue', 'unknown')
            user_id = msg_attributes.get('user_id', {}).get('StringValue', 'unknown')
            frame_num = msg_attributes.get('frame_num', {}).get('StringValue', '0')
            frame_data = msg_attributes.get('frame_data', {}).get('StringValue', '')

            print(f"Processing frame {frame_num} for session {session_id}, user {user_id}")

            if not frame_data:
                print(f"No frame data found for message {frame_num}")
                delete_message_from_sqs(receipt_handle)
                continue

            # Process the image
            try:
                face_bounding_boxes = process_image(frame_data)

                # Prepare the data to store in JSON format
                json_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "frame_num": frame_num,
                    "detected_faces": face_bounding_boxes
                }

                # Store the processed data in S3 as a JSON file
                file_name = f"{session_id}_{user_id}_frame_{frame_num}.json"
                store_data_in_s3(json_data, file_name)

                # Delete the message from SQS
                delete_message_from_sqs(receipt_handle)

            except Exception as e:
                print(f"Error processing message: {e}")

if __name__ == "__main__":
    process_sqs_messages()
