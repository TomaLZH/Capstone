class Chat:
    def __init__(self):
        self.query_counter = 0
        self.chat_history = []

    def add_message(self, message):
        self.chat_history.append(message)
        self.query_counter += 1

    def get_history(self):
        return self.chat_history

    def get_query_count(self):
        return self.query_counter