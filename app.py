import streamlit as st
import CreateStory as cs
st.title("Story creation using AI")

import os

def behind_the_scenes():
    st.subheader("Behind the scenes")
    st.write("The story creation process involves the following steps:")
    st.write("1. create_story(user_input): This function generates a story based on the user input using openai's GPT-3 model.")
    st.write("2. extract_prompt_and_dialogue(story): This function extracts the prompt and dialogue from the generated response.")
    st.write("3. save_images(prompt,folder_path): This function generates images based on the prompt.\
        It uses Huggingface's Stable Diffusion model to generate the images by using inference API.")
    st.write("4. create_audio(story,file_path): This function generates audio based on the dialogue.\
        It uses Openai's TTS model to generate the audio by using the speech API.")
    st.write("5. create_video_from_images(image_path,audio_file,output_file): This function creates a video from the images and audio.\
        It uses OpenCV and moviepy to create the video by combining the images and audio.")
    st.write("6. process_files(video_file,audio_file,folder_path): This function processes the video and audio files to create the final video file.\
        It uses moviepy to process the files and create the final video file.\
        The audio file is combined with the video file to create the final video file using ffmpeg command.\
        Then, the final video was compressed using ffmpeg command to reduce the file size.")
    st.write("The final video file is then displayed to the user.\
        The user can download the video file by clicking on the download button.\
        The user can also generate a new story by entering a new title and clicking on the generate button.\
        The user can also view the behind the scenes of the story creation process by clicking on the behind the scenes button.")



def main(user_input,folder_path):
    with st.spinner("Generating story..."):
        story = cs.create_story(user_input)
        prompt,dialogue = cs.extract_prompt_and_dialogue(story)
        print(prompt)
        print("*"*50)
        print(dialogue)
    with st.spinner("Generating images..."):
        image_path = cs.save_images(prompt,f"{folder_path}/images/")
    with st.spinner("Generating audio..."):
        audio_file = cs.create_audio(' '.join(dialogue),f"{folder_path}/audio.mp3")
    with st.spinner("Creating video..."):
        video_file = cs.create_video_from_images(image_path,audio_file,f"{folder_path}/video.mp4")
    with st.spinner("Processing files..."):
        final_file = cs.process_files(video_file,audio_file,f"{folder_path}")
    print(f"Final video file is created at {final_file}")
    return final_file

final_file=''
with st.sidebar:
    st.header("Give your story a title")
    story = st.text_input("Title")
    if st.button("Generate"):
        st.caption("Note: It may take some time to generate the story. Please be patient.")
        try:
            if not os.path.exists("Story"):
                os.makedirs("Story")
                os.makedirs(f"Story/images")
            final_file = main(story, "Story")
        except Exception as e:
            if e=="Substring not found":
                final_file = main(story, "Story")
            else:
                st.error("An error occured. Please try again.")
                print(e)


        
if final_file == '':
    st.caption("Please enter the title and click on 'Generate' button to create the story.")
else:
    st.caption(f"Here is the story for {story}")
    video_file = open(final_file, 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes, start_time=0)

st.sidebar.caption("Want to know how this works?")
if st.sidebar.button("Behind the scenes"):
    behind_the_scenes()
# prompt = "A story on the topic of 'The Magic of Friendship'"