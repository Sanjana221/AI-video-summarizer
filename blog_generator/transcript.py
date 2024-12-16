from dotenv import load_dotenv 

load_dotenv()
import os
import google.generativeai as genai
from pytube import extract , YouTube
from youtube_transcript_api import YouTubeTranscriptApi

import markdown

import google.generativeai as genai

from IPython.display import display,HTML
from IPython.display import Markdown

def to_html(text):
  #text = text.replace(" * ", '<li>')
  html = markdown.markdown(text)
  html = html.replace(' * ','<br>')
  return html

#getting title
def extract_title(youtube_video_url):
    yt = YouTube(youtube_video_url)
    title = yt.title
    return title

#getting transcript
def extract_transcript_details(youtube_video_url):
    try:
        id= extract.video_id(youtube_video_url)

        transcript_text=YouTubeTranscriptApi.get_transcript(id)

    except Exception as e:
        transcript_list = YouTubeTranscriptApi.list_transcripts(id)

        for transcript in transcript_list:
            transcript_text = transcript.translate('en').fetch()

    transcript = ""
    for i in transcript_text:
        transcript += " " + i["text"]

    return transcript 
    
genai.configure(api_key = os.getenv("Google_API_KEY "))

#getting the summary
def generate_gemini_content(transcript_text):
    prompt =  """You are Youtube Video summarizer.You will take the trascript text and summarize the entire video 
    and provide the important summary in points within 400 words Please provide the summary of the text given here."""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text
    #return to_html(response.text)

