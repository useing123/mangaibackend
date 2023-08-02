import os
import openai
import replicate
import time
from ..service import MangaRepository
import replicate
import requests
from dotenv import load_dotenv

import base64
import re

load_dotenv()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
IMGUR_CLIENT_SECRET = os.getenv("IMGUR_CLIENT_SECRET")


#включать выключатель
def fill_manga_info(manga_id: str, manga_genre: str, prompt:str, manga_chapters_cnt: int, repository: MangaRepository) -> None:
    title = generate_title(manga_id, manga_genre, prompt, repository)
    time.sleep(15)
    chapter_title = generate_chapter_title(manga_id, manga_genre, title, manga_chapters_cnt, repository)
    time.sleep(15)
    main_characters = generate_main_characters(manga_id, title, manga_genre, repository)
    time.sleep(15)
    fun_characters = generate_funservice_characters(manga_id, title, manga_genre, repository)
    time.sleep(15)
    detailed_characters = generate_detailed_characters(manga_id, title, main_characters, fun_characters, repository)
    time.sleep(15)
    manga_story = generate_manga_story(manga_id, prompt, manga_genre, title, chapter_title, main_characters, fun_characters, repository)
    time.sleep(15)
    manga_frames_description = agent_create_frames_description(manga_id, title, manga_genre, detailed_characters, manga_story, repository)
    time.sleep(15)
    manga_dialogs = agent_create_dialogs(manga_id, manga_frames_description, detailed_characters, repository)
    time.sleep(15)
    prompt_image_description = agent_create_images_description(manga_id, manga_frames_description, repository)
    # time.sleep(15)
    generate_image(manga_id, prompt_image_description, repository)


def generate_title(manga_id: str, manga_genre: str, prompt:str, repository: MangaRepository) -> str:
    prompt = f"""
    Please generate a title for a manga in the {manga_genre} genre that incorporates the theme of "Keep this {prompt} in mind." The title should be creative, unique, and suitable for a manga in the specified genre. Your response should be a title without quotation marks.
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
    prompt = f"""
    Please analyze the genre {genre} and provide detailed descriptions of the main characters in the manga {manga_title}
    Your descriptions should explore the key features of the genre and highlight the unique traits, personalities, and roles of each character. Please use the following format to introduce each character: "Who is 
    "Character_name": "Description". 
    Make sure to provide specific and engaging details that capture the essence of each character and their significance to the story.
    
    Your response should demonstrate a deep understanding of the genre and the manga's context, and it should showcase your creativity and ability to bring characters to life through vivid descriptions.

    Please note that you should tailor your descriptions to align with the specific genre and manga, ensuring that they accurately represent the style and themes of the story.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=400,
        n=1,
        stop=None,
        temperature=0.7,
    )
    main_characters = response.choices[0].text.strip()
    repository.update_manga(manga_id, {"main_characters": main_characters})
    return main_characters


def generate_funservice_characters(manga_id: str, manga_title: str, genre: str, repository: MangaRepository) -> str:
    prompt = f"""
    Your task is to analyze the manga "{manga_title}" and identify the fanservice characters within the genre of "{genre}". Please provide detailed descriptions of each fanservice character, explaining their unique characteristics and roles within the story.

    In your response, please use the format: "Who is [Character Name]: [Description of the character]". This format will help to clearly identify and present each fanservice character in a structured manner.

    Please note that your descriptions should be detailed and focused on the fanservice elements of the characters, such as their appearance, clothing, mannerisms, and interactions with other characters. Your response should provide an accurate portrayal of the fanservice characters in the manga, while encouraging creativity and unique descriptions.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=400,
        n=1,
        stop=None,
        temperature=0.7,
    )
    funservice_characters = response.choices[0].text.strip()
    repository.update_manga(manga_id, {"funservice_characters": funservice_characters})
    return funservice_characters


def generate_detailed_characters(manga_id: str, manga_title: str, main_characters: str, funservice_characters: str, repository: MangaRepository) -> str:
    prompt = f"""
    Please provide a detailed appearance description for the characters in the manga titled {manga_title}. Your descriptions will be used as a reference for drawing the characters. 

    Include descriptions for the following characters:
    - Main characters: {main_characters}
    - Fun service characters: {funservice_characters}

    For each character, provide a detailed and specific appearance description, including their physical features, clothing, accessories, and any other relevant details. Use clear and concise language to describe each character's appearance in a way that allows for accurate visualization.

    Format each description as follows: 
    Character: "appearance description"

    Please note that your descriptions should be detailed enough to clearly convey the visual aspects of each character, aiding in the accurate depiction and portrayal of the characters in the manga.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    detailed_characters = response.choices[0].text.strip()
    repository.update_manga(manga_id, {"detailed_characters": detailed_characters})
    return detailed_characters


def generate_manga_story(manga_id: str, prompt:str, genre:str, manga_chapters_title: str, manga_title: str, main_characters:str, funservice_characters:str, repository: MangaRepository) -> str:
    prompt = f"""
    You are an experienced manga author with 150 years of experience. Your task is to create a coherent and engaging story for a manga titled "{manga_title}" in the {genre} genre. The story description should be for a chapter titled "{manga_chapters_title}". You are free to explore any ideas and themes for the story, without limitations.

    Your goal is to create a captivating story that is enjoyable and fun to read. The story should have a compelling ending that leaves the reader eager to continue reading. Please ensure that the story description does not contain any explicit or gratuitous fan service, and instead focuses on the development of the characters and their experiences.

    In the story, please incorporate the provided main characters and any additional characters you feel would enhance the plot. Their information is as follows:
    {main_characters}
    {funservice_characters}

    Please provide a clear and concise story description that highlights the key aspects of the chapter, including the setting, conflicts, character development, and any significant events or plot twists. Your description should ignite curiosity and engage the reader's imagination, making them eager to dive into the manga chapter.tory description that highlights the key aspects of the chapter, including the setting, conflicts, character development, and any significant events or plot twists. Your description should ignite curiosity and engage the reader's imagination, making them eager to dive into the manga chapter.
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
def agent_create_frames_description(manga_id: str, manga_title: str, genre: str, detailed_characters: str, manga_chapters_story: str, repository: MangaRepository) -> str:
    prompt = f"""
    Create a manga consisting of 24 frames for the manga titled "{manga_title}" in the {genre} genre. In each frame, avoid including any explicit content or fanservice. Instead, focus on describing the actions of the characters without using their names. You can refer to the provided detailed descriptions of the characters for this purpose. Please ensure that each frame is descriptive and conveys the progression of the story. 

    Use the following format for your response:
    Frame №1: "What happens in frame"
    {manga_chapters_story}
    Avoid using characters names use their appearence from the detailed description: "{detailed_characters}" because painter don't know their names.
    Your goal is to create a coherent and engaging storyline that unfolds over the course of 24 frames. Be creative and utilize the provided character descriptions to develop interesting character interactions and plot developments.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1800,
        n=1,
        stop=None,
        temperature=0.7,
    )
    manga_frames_description = response.choices[0].text.strip()
    repository.update_manga(manga_id, {"manga_frames_description": manga_frames_description})
    return manga_frames_description


#Эта штука извлекает диалоги из фреймов
def agent_create_dialogs(manga_id: str, manga_frames_description: str, detailed_characters: str, repository: MangaRepository) -> str:
    """
    Parameters:
    manga_id (str): The ID of the manga.
    detailed_characters (str): The detailed description of the characters.
    manga_frames_description (str): The frames description of the manga, what happens on the frames.
    repository (MangaRepository): An instance of the MangaRepository class.
    Returns:
    str: Prompts for painting images using Stable Diffusion.
    """
    prompt = f"I need to upgrade the following prompt for generating an image using Stable Diffusion: '{detailed_characters}' '{manga_frames_description}'. Please provide a detailed and specific version of this prompt."
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1600,
        n=1,
        stop=None,
        temperature=0.1,
    )
    manga_story_dialogs = response.choices[0].text.strip()
    repository.update_manga(manga_id, {"manga_story_dialogs": manga_story_dialogs})
    return manga_story_dialogs

#Эта штука извлекает описание сцены из фреймов надо переписать нормальной пока что это затычка нужно будет зайти в https://huggingface.co/datasets/Gustavosta/Stable-Diffusion-Prompts/viewer/Gustavosta--Stable-Diffusion-Prompts/test и взять от туда
def agent_create_images_description(manga_id: str, manga_frames_description: str, repository: MangaRepository) -> str:
    """
    Parameters:
    manga_id (str): The ID of the manga.
    detailed_characters (str): The detailed description of the characters.
    manga_frames_description (str): The frames description of the manga, what happens on the frames.
    repository (MangaRepository): An instance of the MangaRepository class.
    Returns:
    str: Prompts for painting images using Stable Diffusion.
    """
    prompt = f"""
    Upgrade the prompt for generating an image using Stable Diffusion based on the given parameters. The prompt should consist of a detailed and specific description of the characters and the events happening in the manga frames, without including any NSFW (Not Safe for Work) content description.

    Your task is to upgrade the prompt to provide enough information and context for the AI to generate an image using Stable Diffusion. Your description should accurately convey the desired visual elements, actions, emotions, and relationships between the characters. The upgraded prompt should be unique and distinct, encouraging the AI to generate creative and original image outputs based on the given description.

    Please ensure your language is clear and concise, and incorporate the special "{manga_frames_description}" to provide a detailed and specific version of the prompt.

    Note: Make sure to follow ethical guidelines and avoid any inappropriate or offensive content in your description.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=[
            {"role": "system", "content": "You are manga painter with 150 years experience. You need to draw 30 frames for this manga."},
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
        model_version = "cjwbw/anything-v3-better-vae:09a5805203f4c12da649ec1923bb7729517ca25fcac790e640eaa9ed66573b65"
        inputs = {"prompt": frame}

        # We need to set the token environment variable for the replicate.run function
        os.environ['REPLICATE_API_TOKEN'] = replicate_api_token

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