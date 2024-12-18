class Chat:
    def __init__(self, openai_client, skill_level= "Beginner"):
        self.query_counter = 0
        self.chat_history = [{"role": "assistant", "content": "Welcome! I'm here to assist you in understanding and meeting the requirements of Singapore's Cyber Trust Mark. Whether you have questions about compliance, cybersecurity best practices, or specific guidelines, I'll provide clear and focused guidance to help your SME achieve certification. How can I assist you today?"}]
        thread = openai_client.beta.threads.create()
        self.thread_id = thread.id
        self.skill_level = skill_level

    def add_message(self, message):
        """Add a message to the chat history and increment the query counter."""
        self.chat_history.append(message)
        self.query_counter += 1

    def get_history(self):
        """Return the chat history in a consistent format."""
        return self.chat_history

    def get_query_count(self):
        """Return the count of queries in the chat."""
        return self.query_counter

    def get_thread_id(self):
        """Return the thread ID."""
        return self.thread_id

    def get_skill_level(self):
        """Return the skill level of the user."""
        return self.skill_level
    
    def set_skill_level(self, skill_level):
        """Set the skill level of the user."""
        self.skill_level = skill_level