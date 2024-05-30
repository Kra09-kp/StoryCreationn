# importing all the necessary libraries
import numpy as np
import openai
from openai import OpenAI
import requests
import io
from PIL import Image
import cv2
from moviepy.editor import *
import subprocess
import shutil

# Function to read the api keys
def read_api_key(file_path):
    with open(file_path, 'r') as file:
        api_key = file.readline()
    return api_key

huggingface_api_key = read_api_key("hugging_face_api_key.txt")
openai.api_key = read_api_key("openai_api_key.txt")

client = OpenAI(api_key = openai.api_key)

system = """ You will have provided some topic or interest on which you need to create a story. 
            Remember, Stories are for describing the culture of the company. It is used to train the new employees and to make them understand the company's culture.
            Write a story that also explains what it is and the definition of the topic.
            The story also gives the image prompt for each frame to generate the image.
            Remember if there is any character or person in the frame please provide if there is a male or female.
            Your responses must be in this format:
            Prompt : (write image-prompt for frame here) \n\n
            Dialogue : (write narrator's dialogue for frame here)\n\n.
            Prompt : (write image-prompt for another frame here) \n\n
            Dialogue : (write narrator's dialogue for another frame here)\n\n.
            means prompt should be followed by dialogue."""

assistant = """ Write a fictional story on a provided topic as a narrator.
            A story should be engaging so that everyone can listen to it without getting bored."""
# Function to generate the story and prompt
def create_story(prompt,system=system,assistant=assistant):
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        temperature = 0.5,
        messages = [
            {
                "role":'system',
                 "content": system
            },
            {
                "role":'assistant',
                'content': assistant
            },
            {
                'role':'user',
                'content':f"write a story on {prompt}."
            }
        ]
    )
    return response.choices[0].message.content


# Function to extract prompt and dialogue from the generated response
def extract_prompt_and_dialogue(story):
    l = story.split('\n\n')
    prompt = []
    dialogue = []
    n = len(l)
    for i in range(n):
        s = l[i].index(":")
        if i%2==0:
            prompt.append(l[i][s+1:])
        else:
            dialogue.append(l[i][s+1:])
    
    return prompt,dialogue

# Function to generate image from the prompt
def generate_image(payload,api_key):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content


# Function to save the images
def save_images(prompt, output_folder):
    custom_instruction = ''' Image should be realistic and clear. Image should not be unappropriate. '''
    image_path = []
    t = len(prompt)
    for i,p in enumerate(prompt):
        image_bytes = generate_image({"inputs":p+custom_instruction,},huggingface_api_key)
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        image_path.append(output_folder+f"image{i}.jpg")
        # Save the image to a file
        cv2.imwrite(output_folder+f"image{i}.jpg", cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
        print(f"Image generated {i+1} out of {t} and saved at {output_folder}image{i}.jpg .")
    return image_path
    
# function to create the audio file
def create_audio(story,file_path):
    response = client.audio.speech.create(
          model="tts-1",
          voice="echo",
          input=story
    )

    response.stream_to_file(file_path)
    print(f"Audio file is created at {file_path}")
    return file_path

# Function to create video from images
def create_video_from_images(images, audio_file, output_file):
     # Load the image
    image = cv2.imread(images[0])
    height, width, _ = image.shape

    # Get the duration of the audio file
    audio_duration = AudioFileClip(audio_file).duration

    # Set up video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 24
    video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # Iterate over each image file
    for image_file in images:
        image = cv2.imread(image_file)
        # Write each frame with the loaded image
        for _ in range(int(audio_duration * fps)//7):
            video_writer.write(image)

    # Release resources
    video_writer.release()

    print(f"Video file is created at {output_file}")
    return output_file


# Function to process files using ffmpeg
def process_files(video_file, audio_file,folder_path):
    output_file = f"{folder_path}/output_final.mp4"
    final_file = f"{folder_path}/output_compressed.mp4"
    
    
    try:
        # First command to combine video and audio
        command1 = [
            "ffmpeg", "-i", video_file, "-i", audio_file,
            "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", output_file
        ]
        proc1 = subprocess.Popen(command1)
        proc1.communicate()  # Wait for process to finish
        
        # Second command to compress the output file
        command2 = [
            "ffmpeg", "-i", output_file, 
            "-c:v", "libx264", "-crf", "23", "-preset", "medium",
            "-c:a", "aac", "-b:a", "128k", final_file
        ]
        proc2 = subprocess.Popen(command2)
        proc2.communicate()  # Wait for process to finish
        
    except subprocess.CalledProcessError as e:
        print("Error:", e)
    
    finally:
        # Kill all subprocesses to ensure they are terminated
        if proc1.poll() is None:
            proc1.kill()
        if proc2.poll() is None:
            proc2.kill()

    return final_file
