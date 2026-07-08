import cv2
import ollama
import time
import os

MODEL = "qwen3.5:4b"
CAMERA_INDEX = 0
IMAGE_FILE = "camera_frame.jpg"

client = ollama.Client(host="http://127.0.0.1:11434")

def capture_image():
    cam = cv2.VideoCapture(CAMERA_INDEX)
    if not cam.isOpened():
        print("ERROR: Camera not found")
        return None
    time.sleep(1)
    ret, frame = cam.read()
    cam.release()
    if not ret:
        print("ERROR: Failed to capture image")
        return None
    cv2.imwrite(IMAGE_FILE, frame)
    return IMAGE_FILE

def ask_qwen_about_image(image_path, question):
    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": question,
                "images": [image_path]
            }
        ],
        think=False
    )

    return response.message.content

def main():
    print("Capturing image...")
    image_path = capture_image()
    if image_path is None:
        return
    print("Image saved:", image_path)
    question = "Describe what you see in this image. Please elaborate"
    print("Sending image to Qwen3.5...")
    answer = ask_qwen_about_image(image_path, question)
    print()
    print("Qwen says:")
    print(answer)

if __name__ == "__main__":
    main()