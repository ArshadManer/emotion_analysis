import asyncio
import websockets
import json
import uuid
import datetime

async def send_frames():
    session_id = str(uuid.uuid4())
    websocket_url = "wss://6o8ge9m8be.execute-api.ap-south-1.amazonaws.com/production/"  # WebSocket URL from API Gateway

    async with websockets.connect(websocket_url) as websocket:
        for frame_num in range(900):
            # Prepare JSON data with session ID and frame data
            frame_data = f"Frame data {frame_num + 1}"
            message = {
                "frame_data": frame_data,
                "session_id": session_id
            }
            
            await websocket.send(json.dumps(message))
            print(f"Sent frame {frame_num + 1} for session {session_id}")
        
        print("All frames sent.")

# Run the function
asyncio.get_event_loop().run_until_complete(send_frames())
