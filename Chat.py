class Chat:
    def __init__(self, openai_client):
        self.query_counter = 0
        self.chat_history = [{"role": "assistant", "content": "Welcome! I'm here to assist you in understanding and meeting the requirements of Singapore's Cyber Trust Mark. Whether you have questions about compliance, cybersecurity best practices, or specific guidelines, I'll provide clear and focused guidance to help your SME achieve certification. How can I assist you today?"}]
        thread = openai_client.beta.threads.create()
        self.thread_id = thread.id

    def add_message(self, message):
        """Add a message to the chat history and increment the query counter."""
        if isinstance(message, str):  # If the message is just a string, convert it to a dictionary
            self.chat_history.append(message)
        else:
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
