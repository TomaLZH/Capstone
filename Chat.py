class Chat:
    def __init__(self, openai_client):
        self.query_counter = 0
        self.chat_history = []
        # Create the thread directly in the __init__ method
        thread = openai_client.beta.threads.create()
        self.thread_id = thread.id  # Store only the thread ID

    def add_message(self, message):
        """Add a message to the chat history and increment the query counter."""
        self.chat_history.append(message)
        self.query_counter += 1

    def get_history(self):
        """Return the chat history."""
        return self.chat_history

    def get_query_count(self):
        """Return the count of queries in the chat."""
        return self.query_counter

    def get_thread_id(self):
        """Return the thread ID."""
        return self.thread_id
