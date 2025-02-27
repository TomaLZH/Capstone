from databasefunctions import add_evaluation, add_gpt_answer
from query import handle_query
from Chat import Chat
from Initialize import get_resources

clauses = [
    "B.22.2",
    "B.22.3",
    "B.22.4",
    "B.22.5",
    "B.22.6",
    "B.22.7",
    "B.22.8",
    "B.22.9",
    "B.22.10"
]

clause_questions = [
    "Identifying assets requiring high availability: Has the organisation identified the critical assets in the organisation that require high availability and performed measures to ensure that there are redundancies for them?",
    "Business impact analysis: Has the organisation defined and applied the process of business impact analysis to identify the critical processes and expected RTO and RPO for business resumption?",
    "Redundancy process: Has the organisation defined and applied the process to perform redundancy on systems to ensure the cyber resilience of its systems?",
    "Business continuity/disaster recovery policy: Has the organisation established and implemented the business continuity/disaster recovery policies with the requirements, roles and responsibilities and guidelines including the RTO and RPO to ensure that business resumption can be carried out in accordance with the system's criticality?",
    "Business continuity/disaster recovery plan: Has the organisation established and implemented a business continuity/disaster recovery plan to respond and recover against the common business disruption scenarios including those caused by cybersecurity incidents to ensure cyber resiliency.",
    "Business continuity/disaster recovery plan review: Does the organisation perform regular reviews at least on an annual basis on the business continuity/disaster recovery plan to ensure that it is kept up to date?",
    "Business continuity/disaster recovery plan test: Has the organisation established and implemented the policy process to test on its business continuity/disaster recovery plan regularly at least on an annual basis to ensure the effectiveness of the plan in achieving its objectives?",
    "Monitoring against RTO/RPO: Does the organisation perform monitoring on the RTO and RPO during business continuity/disaster recovery to ensure that it falls within the targets and report the findings to the Board and/or senior management?",
    "Business continuity/disaster recovery exercise: Does the organisation perform coordinated business continuity/disaster recovery exercise with its third parties for an extended period of time to evaluate the effectiveness of the processes and procedures?"

]

conn, bi_encoder, cross_encoder, collection, openai_client, assistant = get_resources()

for i in range(len(clauses)):
    print("Running for clause " + clauses[i])
    current_clause_number = "How do i implement clause " + clauses[i] + "?"
    current_clause = "How do i implement clause " + clause_questions[i] + "?"

    #Call open ai completion to get the response
    response = openai_client.chat.completions.create(
        model = "gpt-4o-mini",
        messages=[{"role":"user", "content":current_clause}],
    )
    #Get the response from the assistant
    response = response.choices[0].message.content
    print(response)
    add_gpt_answer(current_clause_number, response)