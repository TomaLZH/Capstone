import openai
import pandas as pd
from Initialize import get_resources

# Load the Excel file
file_path = "evaluation.xlsx"  # Update with your file path
df = pd.read_excel(file_path, sheet_name="Sheet1")  # Adjust sheet name if needed

conn, bi_encoder, cross_encoder, collection, openai_client, assistant = get_resources()

# Function to evaluate answers
def grade_answers(question, my_answer, gpt_answer):

    # beginner prompt = f"""
    # You are an expert evaluator grading two answers to the same question. Assess each answer based on the following four criteria:

    # 1. **Practicality and Actionability** (25 points) - How useful and actionable is the answer for fulfilling the clause?  
    # 2. **Conciseness** (25 points) - Does the answer provide the necessary detail for the clause without unnecessary information? Lower score if it includes unnecessary information for the clause.  
    # 3. **Ease of Understanding** (25 points) - Can a beginner easily understand the response? Prioritize clarity and simplicity, making sure the answer is easy for someone new to the topic.  
    # 4. **Specificity** (25 points) - Is the answer too vague or generic, or is it specific and well-tailored to the clause? Higher scores mean more specificity.  

    # Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible.
 
    # ---
    # **Question:** {question}

    # **Answer 1:** {my_answer}

    # **Answer 2:** {gpt_answer}

    # ---
    # Output Format (Only output the scores in the following format and nothing else):

    # Answer 1 Score: [score]/100  
    # Answer 2 Score: [score]/100  
    # Higher Scoring Answer: [Answer 1/Answer 2]
    # """




    prompt = f"""
    You are an expert evaluator grading two answers to the same question. Assess each answer based on the following four criteria:
    
    1) Practicality and Actionability (25 points) - How useful and actionable is the answer for fulfilling the clause?
    2) Depth and Technical Accuracy (25 points) - Does the answer provide a comprehensive, in-depth, and technically accurate explanation suitable for advanced users? Answers should cover complexities, nuances, and potential edge cases.
    3) Clarity for Experts (25 points) - Is the explanation clear and well-structured for someone already experienced in the field? The answer should avoid unnecessary simplifications while maintaining logical flow.
    4) Relevance and Focus (25 points) - Does the answer provide the right level of detail without unnecessary or excessive information? Responses should be thorough but stay directly relevant to the clause, avoiding off-topic or overly verbose explanations.

    Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible.
 
    ---
    **Question:** {question}

    **Answer 1:** {my_answer}

    **Answer 2:** {gpt_answer}

    ---
    Output Format (Only output the scores in the following format and nothing else):

    Answer 1 Score: [score]/100  
    Answer 2 Score: [score]/100  
    Higher Scoring Answer: [Answer 1/Answer 2]
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert evaluator."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# Loop through only the first 3 rows
for index, row in df.iterrows():
    evaluation = grade_answers(row["question"], row["advanced_answer"], row["gpt_answer"])
    lines = evaluation.split("\n")
    print(evaluation)
    df.at[index, "advanced_grade"] = lines[0].split(":")[1].strip().split("/")[0].replace("**", "")
    df.at[index, "advanced_gpt_grade"] = lines[1].split(":")[1].strip().split("/")[0].replace("**", "")
    df.at[index, "advanced_better_answer"] = lines[2].split(":")[1].strip().replace("**", "")

# Save the updated file
df.to_excel("advanced_graded_output.xlsx", index=False)
