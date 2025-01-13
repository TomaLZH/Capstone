from openai import OpenAI
import streamlit as st
from pandas import DataFrame
import pandas as pd
from Chat import Chat
import docx
from Initialize import get_resources

bi_encoder, cross_encoder, client, openai_client, assistant = get_resources()


def read_file(file):
    if file.name.endswith('.docx'):
        doc = docx.Document(file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    elif file.name.endswith('.xlsx'):
        df = pd.read_excel(file)
        return df.to_string()
    else:
        return "Unsupported file format"
    
def analyze_file(chat:Chat, file):
    text = read_file(file)
    system_message = """
    You are an assistant that analyzes the content of a file and returns in a structured format, the infrastructure, 
    and the environment of the company mentioned in the file. Analyze the text and provide a summary of the key points.
    Just provide the summary of the key points in the file, no conclusion, explanation or extra information is needed.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": text}]
    )
    Chat.set_infrastructure(chat, response.choices[0].message.content)
    