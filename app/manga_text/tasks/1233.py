import os
import openai
import replicate
import time
from ..service import MangaRepository
import requests
import base64
import re

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
IMGUR_CLIENT_SECRET = os.getenv("IMGUR_CLIENT_SECRET")

def fill_manga_info(manga_id: str, manga_genre: str, prompt:str, manga_chapters_cnt: int, repository: MangaRepository) -> None:
    # Generate title
    title_prompt = f"""
    Generate 1 title for a manga in the {manga_genre} genre, give output without quotation marks:
    Keep this {prompt} in mind 
    """
    title_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a manga writer with 150 years experience."},
            {"role": "user", "content": title_prompt}
        ]
    )
    manga_title = title_response['choices'][0]['message']['content'].strip()
    repository.update_manga(manga_id, {"title": manga_title})
    time.sleep(25)

    # Generate chapter titles
    chapters = []
    for index in range(manga_chapters_cnt):
        chapter_prompt = f"Generate a title for a chapter #{index + 1}/{manga_chapters_cnt} in manga called '{manga_title}' in {manga_genre} genre:"
        chapter_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a manga writer with 150 years experience."},
                {"role": "user", "content": chapter_prompt}
            ]
        )
        chapters.append(chapter_response['choices'][0]['message']['content'].strip())
    repository.update_manga(manga_id, {"chapters_title": chapters})
    time.sleep(25)

    # Generate main characters
    main_characters_prompt = f"""
    Don't write title, genre, etc. Just write a description of the characters.
    Provide a detailed description for the main characters in the manga {manga_title}:
    Study the features of this genre: {manga_genre} and write detailed main character descriptions    
    """
    main_characters_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are manga writer with 150 years experience."},
            {"role": "user", "content": main_characters_prompt}
        ]
    )
    main_characters = main_characters_response['choices'][0]['message']['content'].strip()
    repository.update_manga(manga_id, {"main_characters": main_characters})
    time.sleep(25)

    # Generate funservice characters
    funservice_characters_prompt = f"""
    Don't write title, genre, etc. Just write a description of the characters.
    Provide a detailed description for the funservice characters in the manga {manga_title}:
    Study the features of this genre: {manga_genre} and write detailed main character descriptions  
    """
    funservice_characters_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are manga writer with 150 years experience."},
            {"role": "user", "content": funservice_characters_prompt}
        ]
    )
    funservice_characters = funservice_characters_response['choices'][0]['message']['content'].strip()
    repository.update_manga(manga_id, {"funservice_characters": funservice_characters})
    time.sleep(25)

    # Generate detailed characters
    detailed_characters_prompt = f"""
    Don't write title, genre, etc. Just write a description of the characters.
    Provide a detailed description for the characters in the manga {manga_title} Description of the characters' appearance in order to draw them:
    {main_characters} {funservice_characters}    
    """
    detailed_characters_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are manga write with 150 years experience."},
            {"role": "user", "content": detailed_characters_prompt}
        ]
    )
    detailed_characters = detailed_characters_response['choices'][0]['message']['content'].strip()
    repository.update_manga(manga_id, {"detailed_characters": detailed_characters})
    time.sleep(25)

    # Generate manga story
    manga_story_prompt = f"""
    You are a manga author with 150 years of experience.Create a coherent story that's fun to read, don't limit yourself in anything. Make an interesting ending that makes you want to keep reading. Write an interesting story description for the manga {manga_title} in {manga_genre}, for a chapter called {chapters[0]}.
    Avoid meaning "funservice" in the story just write names of the characters
    Write a story that honours that wish.
    {prompt}
    Character Info:
    {main_characters}
    {funservice_characters}
    Appearance description:
    {detailed_characters}
    """
    manga_story_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a manga author with 150 years experience."},
            {"role": "user", "content": manga_story_prompt}
        ]
    )
    manga_story = manga_story_response['choices'][0]['message']['content'].strip()
    repository.update_manga(manga_id, {"manga_story": manga_story})
    time.sleep(25)

    # Generate frames description
    frames_description_prompt = f"""
    Make it 20 frames for this manga what happens in 20 frames
    give output like this:
    avoid meaning "funservice" in the frames just write names of the characters
    Design text like this:
    Frame №1: "What happens in this frame"
    {manga_story}
    """
    frames_description_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a manga author with 150 years experience."},
            {"role": "user", "content": frames_description_prompt}
        ]
    )
    frames_description = frames_description_response['choices'][0]['message']['content'].strip()
    repository.update_manga(manga_id, {"frames_description": frames_description})
    time.sleep(25)

    # Generate dialogs
    dialogs_prompt = f"""
    Write what happens(dialogs, sound effects, etc.) for this manga frames:
    give output like this:
    Frame №1: "What happens in this frame"
    {frames_description}
    """
    dialogs_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a manga author with 150 years experience."},
            {"role": "user", "content": dialogs_prompt}
        ]
    )
    dialogs = dialogs_response['choices']['message']['content'].strip()
    repository.update_manga(manga_id, {"dialogs": dialogs})
    time.sleep(25)

    # Generate images description
    images_description_prompt = f"""
    Upgrade prompt for generating an image using Stable Diffusion:

    Given the provided manga ID and the detailed description of the characters and frames, your task is to upgrade the prompt for generating an image using Stable Diffusion. The upgraded prompt should focus on the specific details and requirements for generating an accurate and realistic image based on the given manga.

    Please provide a detailed and specific version of the prompt that includes the necessary information and instructions for generating the image. The upgraded prompt should clearly specify the desired output format, such as "{detailed_characters} {frames_description}", and should exclude any unnecessary details or instructions unrelated to generating the image.

    Please note that you should leverage the capabilities of Stable Diffusion to generate high-quality and visually appealing images based on the provided manga ID, the detailed description of the characters, and the frames.
    """
    images_description_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are manga painter with 150 years experience. You need to draw 20 frames for this manga."},
            {"role": "user", "content": images_description_prompt}
        ]
    )
    images_description = images_description_response['choices'][0]['message']['content'].strip()
    repository.update_manga(manga_id, {"images_description": images_description})
    time.sleep(25)

    # Generate images
    replicate_api_token = REPLICATE_API_TOKEN
    imgur_client_id_value = IMGUR_CLIENT_ID
    frames = re.split(r'Frame №\d+: ', images_description)[1:]
    imgur_links = []
    for frame in frames:
        # Call the Replicate API to generate an image
        model_version = "cjwbw/anything-v4.0:42a996d39a96aedc57b2e0aa8105dea39c9c89d9d266caf6bb4327a1c191b061"
        inputs = {"prompt": frame}
        # We need to set the token environment variable for the replicate.run function
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
        outputs = replicate.run(model_version, input=inputs)
        # The outputs contains a list of URLs, we'll just use the first one
        image_url = outputs[0]
        # Download the image
        image_response = requests.get(image_url)
        # Convert the image to base64
        image_base64 = base64.b64encode(image_response.content).decode()
        # Call the Imgur API to upload the image
        headers = {
            "Authorization": f"Client-ID {imgur_client_id_value}"
        }
        data = {
            "image": image_base64,
            "type": "base64"
        }
        response = requests.post("https://api.imgur.com/3/image", headers=headers, data=data)
        # Add the Imgur link to the list
        imgur_links.append(response.json()["data"]["link"])
    # Update manga information with the Imgur links in the repository
    repository.update_manga(manga_id, {"imgur_links": imgur_links})
    return {"imgur_links": imgur_links}

