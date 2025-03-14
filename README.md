## Project Title: Chatbot to Assist SMEs in Achieving Singapore's CSA Cyber Trust Mark

### Overview
This capstone project focuses on developing a chatbot that supports Small and Medium Enterprises (SMEs) in attaining the Cyber Trust Mark certification issued by the Cyber Security Agency (CSA) of Singapore. The chatbot provides interactive guidance to help SMEs understand and meet the certification requirements, thereby enhancing their cybersecurity posture and credibility.

### Problem Statement
SMEs often face challenges in:
- Lacking in-house IT experts who can interpret and implement cybersecurity measures.
- Limited budgets that make it difficult to hire external consultants or invest in comprehensive solutions.
- Struggling to understand the complex and technical guidelines of the CSA Cyber Trust Mark certification.

This project addresses these gaps by leveraging a chatbot to provide real-time, tailored guidance and resources to SMEs throughout their certification journey.

### Objectives
1. **Simplify the Cyber Trust Mark Requirements**: Break down the certification criteria into easily digestible components via chatbot interactions.
2. **Provide Real-Time Guidance**: Offer instant responses to SMEs’ questions about cybersecurity requirements.
3. **Deliver Step-by-Step Support**: Provide actionable recommendations and best practices for achieving compliance.
4. **Raise Awareness**: Educate SMEs about the importance of robust cybersecurity practices through interactive conversations.

### Features
1. **Interactive Cyber Trust Mark Checklist**: Accessible through chatbot queries for step-by-step progress.
2. **Customizable Experience**: Able to get tailored responses based on user's environment type and IT skill level.
3. **Resource Recommendations**: Centralized access to templates, guides, and policy documents.

### Technology Stack
- **Frontend**: Streamlit for user interface and deployment.
- **Backend**: Python for chatbot logic and integrations.
- **Database**: Milvus for storing of embeddings, Google Cloud Platform PostgreSQL main database
- **Models Used**: GPT4o-mini, all-mpnet-base-v2 (bi-encoder), ms-marco-MiniLM-L-6-v2 (re-ranking)

### Target Audience
- SMEs in Singapore aiming to enhance their cybersecurity posture.
- Cybersecurity consultants working with SMEs.
- Business owners and managers responsible for IT and security compliance.

### Key Benefits
- **Streamlined Certification Process**: Simplifies the steps required to attain the Cyber Trust Mark via interactive chatbot guidance.
- **Cost-Effective Solution**: Reduces the need for extensive external consultation.
- **Improved Security Posture**: Helps SMEs establish a strong foundation in cybersecurity.
- **Enhanced Trustworthiness**: Strengthens the enterprise’s reputation in the market.

### Usage
The chatbot is hosted online for easy access. Users can simply visit the provided link to start interacting with the chatbot:

[Access the Chatbot Here]()

### Results
I have used a method called [LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) to use gpt4o-mini to grade my answers as compared to gpt4o-mini answers. These are the results

![Beginner Evaluation Result](https://raw.githubusercontent.com/TomaLZH/Capstone/main/beginner_evaluation_result.png)
![Advanced Evaluation Result](https://raw.githubusercontent.com/TomaLZH/Capstone/main/advanced_evaluation_result.png)

### Future Enhancements
- **Fine Tuning of Model**: Fine Tune model for better performance.
- **More Datasets**: With more datasets to retrieve from Retrieval Augmented Generation (RAG), accuracy will be better.

### Acknowledgments
- **CSA Singapore**: For providing guidelines and resources on the Cyber Trust Mark.
- **Mentors and Advisors**: For their invaluable guidance and feedback.
- **Open-Source Libraries and Tools**: For enabling the development of this project.

