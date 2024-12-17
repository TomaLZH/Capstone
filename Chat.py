class Chat:
    def __init__(self, openai_client):
        self.query_counter = 0
        self.chat_history = []
        self.thread_id = openai_client.beta.threads.create().id

    def create_thread(self, openai_client):
        # Create a new thread for this chat using the OpenAI client
        thread = openai_client.beta.threads.create()  # Assuming the client is passed correctly
        return thread.id

    def add_message(self, message):
        self.chat_history.append(message)
        self.query_counter += 1

    def get_history(self):
        return self.chat_history

    def get_query_count(self):
        return self.query_counter

    def get_thread_id(self):
        return self.thread_id
