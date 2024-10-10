import json
import uuid
import random
import time
import threading
import asyncio
import websockets

# WebSocket API Gateway endpoint
WS_ENDPOINT = "wss://6o8ge9m8be.execute-api.ap-south-1.amazonaws.com/production/"  # Update with your WebSocket API endpoint

# Function to send a frame for a specific user via WebSocket
async def send_frames_for_user(user_id):
    session_id = str(uuid.uuid4())  # Unique session ID for each user
    
    async with websockets.connect(WS_ENDPOINT) as websocket:
        for frame_num in range(1, 901):  # Each user has 900 frames
            frame_data = f'random_frame_data_{random.randint(1, 1000)}'
            payload = {
                "action": "sendFrames",  # WebSocket route action
                "session_id": session_id,
                "user_id": user_id,
                "frame_num": frame_num,
                "frame_data": frame_data
            }

            # Send the payload via WebSocket
            await websocket.send(json.dumps(payload))
            print(f"Sent frame {frame_num} for user {user_id}")

            # You can add a small delay between frames to simulate real-time
            await asyncio.sleep(0.05)

# Function to simulate sending frames for multiple users
def start_test_for_multiple_users(num_users=2):
    # To handle the event loop in each thread for async WebSocket calls
    def run_async_task(user_id):
        asyncio.run(send_frames_for_user(user_id))

    threads = []

    # Start sending frames for each user in a separate thread
    for user_id in range(1, num_users + 1):
        t = threading.Thread(target=run_async_task, args=(user_id,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

if __name__ == "__main__":
    start_test_for_multiple_users(2)


# import asyncio
# import websockets
# import json
# import uuid

# # WebSocket endpoint from API Gateway
# WS_ENDPOINT = "wss://qy13jsst66.execute-api.ap-south-1.amazonaws.com/production/"

# async def send_frame(user_id, frame_data):
#     session_id = str(uuid.uuid4())  # Generate unique session ID for each user
#     frame_payload = {
#         "action": "sendMessage",  # Action linked to the WebSocket route
#         "sessionId": session_id,
#         "frameData": frame_data
#     }

#     async with websockets.connect(WS_ENDPOINT) as websocket:
#         await websocket.send(json.dumps(frame_payload))
#         print(f"Sent frame for session {session_id}")

# # Create a list of 900 frames per user
# def generate_frame_data():
#     return [{"frame": i} for i in range(900)]  # Example frame data

# async def main():
#     users = 10  # Number of users
#     tasks = []
#     for user in range(users):
#         frame_data = generate_frame_data()
#         tasks.append(send_frame(user, frame_data))
    
#     await asyncio.gather(*tasks)

# # Run the async event loop
# if __name__ == "__main__":
#     asyncio.run(main())
