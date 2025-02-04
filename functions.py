from openai import OpenAI
import streamlit as st
from pandas import DataFrame
import pandas as pd
from Chat import Chat
import docx
from Initialize import get_resources

conn, cur, bi_encoder, cross_encoder, client, openai_client, assistant = get_resources()


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


def analyze_file(chat: Chat, file):
    text = read_file(file)
    system_message = """
        You are a cybersecurity compliance assistant that extracts critical information needed for security certifications (e.g., ISO 27001, SOC 2, PCI DSS). 
        Analyze the text and strictly include only details relevant to:
        
        - Technology stack: Software, cloud providers (AWS/Azure/GCP), and security tools
        - Workforce details: Number of employees/contractors and their locations
        - Infrastructure: Data centers, physical offices, and network architecture
        - Data management: Sensitive data types and storage locations
        - Compliance status: Existing security frameworks or certifications
        - Access controls: Authentication methods and privilege management
        - Third-party integrations: Vendors/partners with system access
        - Security measures: Encryption standards, network segmentation, audit processes
        - Physical security: Facility controls and surveillance systems
        - Incident response: Breach history and recovery procedures
        
        Return a structured summary with only factual, explicit information found in the text. 
        Exclude projections, marketing claims, and unrelated operational details.
        """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": text}]
    )
    Chat.set_infrastructure(chat, response.choices[0].message.content)
