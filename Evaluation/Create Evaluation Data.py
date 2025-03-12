from databasefunctions import add_evaluation, add_gpt_answer
from query import handle_query
from Chat import Chat
from Initialize import get_resources

clauses = [
    "B.22.9",
    "B.22.10"
]

clause_questions = [
    "Monitoring against RTO/RPO: Does the organisation perform monitoring on the RTO and RPO during business continuity/disaster recovery to ensure that it falls within the targets and report the findings to the Board and/or senior management?",
    "Business continuity/disaster recovery exercise: Does the organisation perform coordinated business continuity/disaster recovery exercise with its third parties for an extended period of time to evaluate the effectiveness of the processes and procedures?"
]


conn, bi_encoder, cross_encoder, collection, openai_client, assistant = get_resources()

for i in range(len(clauses)):
    print("Running for clause " + clauses[i])
    current_clause_number = "How do I implement clause " + clauses[i] + "?"
    current_clause = "How do i implement clause " + clause_questions[i] + "?"

    # Call open ai completion to get the response
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": current_clause}],
    )
    # Get the response from the assistant
    response = response.choices[0].message.content
    print(current_clause_number)
    add_gpt_answer(current_clause_number, response)
