import google.generativeai as genai
import os
import time
import argparse

def main():
    # Configure API key
    genai.configure(api_key=os.environ["API_KEY"])

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Ask questions about videos using Gemini 2.5 Pro")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("question", help="Question to ask about the video")

    args = parser.parse_args()

    video_file_name = args.video_path
    question = args.question

    print(f"Uploading file...")
    video_file = genai.upload_file(path=video_file_name)
    print(f"Completed upload: {video_file.uri}")

    while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)

    model = genai.GenerativeModel(model_name="gemini-2.5-pro")

    print(f"Generating response...")
    response = model.generate_content([video_file, question],
                                      request_options={"timeout": 600})

    print(f"Response: {response.text}")

if __name__ == "__main__":
    main()