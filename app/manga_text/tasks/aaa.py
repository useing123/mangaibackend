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


#включать выключатель
def fill_manga_info(manga_id: str, manga_genre: str, prompt:str, manga_chapters_cnt: int, repository: MangaRepository) -> None:
    title = generate_title(manga_id, manga_genre, prompt, repository)
    time.sleep(25)
    chapter_title = generate_chapter_title(manga_id, manga_genre, title, manga_chapters_cnt, repository)
    time.sleep(25)
    main_characters = generate_main_characters(manga_id, title, manga_genre, repository)
    time.sleep(25)
    fun_characters = generate_funservice_characters(manga_id, title, manga_genre, repository)
    time.sleep(25)
    detailed_characters = generate_detailed_characters(manga_id, title, main_characters, fun_characters, repository)
    time.sleep(25)
    manga_story = generate_manga_story(manga_id, prompt, manga_genre, title, chapter_title, main_characters, fun_characters, detailed_characters, repository)
    time.sleep(25)
    manga_frames_description = agent_create_frames_description(manga_id, manga_story, repository)
    time.sleep(25)
    manga_dialogs = agent_create_dialogs(manga_id, manga_frames_description, repository)
    time.sleep(25)
    manga_images_description = agent_create_images_description(manga_id, manga_frames_description, detailed_characters, repository)
    time.sleep(25)
    images=generate_image(manga_id, manga_images_description, repository)


def generate_title(manga_id: str, manga_genre: str, prompt:str, repository: MangaRepository) -> str:
    prompt = f"""
    Generate 1 title for a manga in the {manga_genre} genre, give output without quotation marks:
    Keep this {prompt} in mind 
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=1,
    )
    manga_title = response.choices[0].text.strip()
    repository.update_manga(manga_id, {"title": manga_title})
    return manga_title


def generate_chapter_title(manga_id: str, manga_genre: str, manga_title: str, manga_chapters_cnt: int, repository: MangaRepository) -> None:
    chapters = []
    for index in range(manga_chapters_cnt):
        prompt = f"Generate a title for a chapter #{index + 1}/{manga_chapters_cnt} in manga called '{manga_title}' in {manga_genre} genre:"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7,
        )
        chapters.append(response.choices[0].text.strip())
    repository.update_manga(manga_id, {"chapters_title": chapters})


def generate_main_characters(manga_id: str, manga_title: str, genre: str, repository: MangaRepository) -> str:
    """
    Parameters:
    manga_id (str): The ID of the manga.
    manga_title (str): The title of the manga.
    genre (str): The genre of the manga.
    repository (MangaRepository): An instance of the MangaRepository class.
    Returns:
    str: Character descriptions tailored to the genre
    """
    prompt = f"""
    Don't write title, genre, etc. Just write a description of the characters.
    Provide a detailed description for the main characters in the manga {manga_title}:
    Study the features of this genre: {genre} and write detailed main character descriptions    
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are manga writer with 150 years experience."},
            {"role": "user", "content": prompt}
        ]
    )
    
    main_characters = response['choices'][0]['message']['content'].strip()
    repository.update_manga(manga_id, {"main_characters": main_characters})
    return main_characters


def generate_funservice_characters(manga_id: str, manga_title: str, genre: str, repository: MangaRepository) -> str:
    """
    Parameters:
    manga_id (str): The ID of the manga.
    manga_title (str): The title of the manga.
    genre (str): The genre of the manga.
    repository (MangaRepository): An instance of the MangaRepository class.
    Returns:
    str: Character descriptions tailored to the genre
    """
    prompt = f"""
    Don't write title, genre, etc. Just write a description of the characters.
    Provide a detailed description for the funservice characters in the manga {manga_title}:
    Study the features of this genre: {genre} and write detailed main character descriptions  
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are manga writer with 150 years experience."},
            {"role": "user", "content": prompt}
        ]
    )
    
    funservice_characters = response['choices'][0]['message']['content'].strip()
    repository.update_manga(manga_id, {"funservice_characters": funservice_characters})
    return funservice_characters


def generate_detailed_characters(manga_id: str, manga_title: str, main_characters: str, funservice_characters: str, repository: MangaRepository) -> str:
    """
    Parameters:
    manga_id (str): The ID of the manga.
    manga_title (str): The title of the manga.
    main_characters (str): The main characters of the manga.
    funservice_characters (str): The funservice characters of the manga.
    repository (MangaRepository): An instance of the MangaRepository class.
    Returns:
    str: Description of the characters' appearances so that you can draw them
    """
    prompt = f"""
    Don't write title, genre, etc. Just write a description of the characters.
    Provide a detailed description for the characters in the manga {manga_title} Description of the characters' appearance in order to draw them:
    {main_characters} {funservice_characters}    
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are manga write with 150 years experience."},
            {"role": "user", "content": prompt}
        ]
    )
    
    detailed_characters = response['choices'][0]['message']['content'].strip()
    repository.update_manga(manga_id, {"detailed_characters": detailed_characters})
    return detailed_characters




def generate_manga_story(manga_id: str, prompt:str, genre:str, manga_chapters_title: str, manga_title: str, main_characters:str, funservice_characters:str, detailed_characters: str, repository: MangaRepository) -> str:
    prompt = f"""
    You are a manga author with 150 years of experience.Create a coherent story that's fun to read, don't limit yourself in anything. Make an interesting ending that makes you want to keep reading. Write an interesting story description for the manga {manga_title} in {genre}, for a chapter called {manga_chapters_title}.
    Avoid meaning "funservice" in the story just write names of the characters
    Write a story that honours that wish.
    {prompt}
    Character Info:
    {main_characters}
    {funservice_characters}
    Appearance description:
    {detailed_characters}
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    manga_chapters_story = response.choices[0].text.strip()
    repository.update_manga(manga_id, {"manga_chapters_story": manga_chapters_story})
    return manga_chapters_story


#Описываем 15 кадров манги
def agent_create_frames_description(manga_id: str, manga_chapters_story: str, repository: MangaRepository) -> str:
    prompt = f"""
    Make it 20 frames for this manga what happens in 20 frames
    give output like this:
    avoid meaning "funservice" in the frames just write names of the characters
    Design text like this:
    Frame №1: "What happens in this frame"
    {manga_chapters_story}
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    manga_frames_description = response.choices[0].text.strip()
    repository.update_manga(manga_id, {"manga_frames_description": manga_frames_description})
    return manga_frames_description


#Эта штука извлекает диалоги из фреймов
def agent_create_dialogs(manga_id: str, manga_frames_description: str, repository: MangaRepository) -> str:
    prompt = f"""
    Write what happens(dialogs, sound effects, etc.) for this manga frames:
    give output like this:
    Frame №1: "What happens in this frame"
    {manga_frames_description}
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=900,
        n=1,
        stop=None,
        temperature=0.1,
    )
    manga_story_dialogs = response.choices[0].text.strip()
    repository.update_manga(manga_id, {"manga_story_dialogs": manga_story_dialogs})
    return manga_story_dialogs

#Эта штука извлекает описание сцены из фреймов надо переписать нормальной пока что это затычка нужно будет зайти в https://huggingface.co/datasets/Gustavosta/Stable-Diffusion-Prompts/viewer/Gustavosta--Stable-Diffusion-Prompts/test и взять от туда
def agent_create_images_description(manga_id: str, manga_frames_description: str, detailed_characters: str, repository: MangaRepository) -> str:
    prompt = f"""
    Upgrade prompt for generating an image using Stable Diffusion:

    Given the provided manga ID and the detailed description of the characters and frames, your task is to upgrade the prompt for generating an image using Stable Diffusion. The upgraded prompt should focus on the specific details and requirements for generating an accurate and realistic image based on the given manga.

    Please provide a detailed and specific version of the prompt that includes the necessary information and instructions for generating the image. The upgraded prompt should clearly specify the desired output format, such as "{detailed_characters} {manga_frames_description}", and should exclude any unnecessary details or instructions unrelated to generating the image.

    Please note that you should leverage the capabilities of Stable Diffusion to generate high-quality and visually appealing images based on the provided manga ID, the detailed description of the characters, and the frames.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are manga painter with 150 years experience. You need to draw 20 frames for this manga."},
            {"role": "user", "content": prompt}
        ]
    )
    
    manga_images_description = response['choices'][0]['message']['content'].strip()
    repository.update_manga(manga_id, {"manga_images_description": manga_images_description})
    return manga_images_description


def generate_image(manga_id: str, manga_images_description: str, repository: MangaRepository): 
    replicate_api_token = REPLICATE_API_TOKEN
    imgur_client_id_value = IMGUR_CLIENT_ID

    frames = re.split(r'Frame №\d+: ', manga_images_description)[1:]

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

    # Return the Imgur links
    return {"imgur_links": imgur_links}