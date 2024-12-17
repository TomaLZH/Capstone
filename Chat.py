class Chat:
    def __init__(self, openai_client):
        self.query_counter = 0
        self.chat_history = []
        self.thread_id = openai_client.beta.threads.create()

    def create_thread(self, openai_client):
        # Create a new thread for this chat using the OpenAI client
        thread = openai_client.beta.threads.create()  # Assuming the client is passed correctly
        return thread.id

    def add_message(self, message):
        # Ensure that the message is always added as a dictionary with 'role' and 'content'
        if isinstance(message, dict):
            self.chat_history.append(message)
        else:
            raise ValueError("Message must be a dictionary with 'role' and 'content' keys.")
        self.query_counter += 1

    def get_history(self):
        return self.chat_history

    def get_query_count(self):
        return self.query_counter

    def get_thread_id(self):
        return self.thread_id.id
