class Chat:
    def __init__(self, openai_client, skill_level="Beginner"):
        self.query_counter = 0
        self.chat_history = []
        thread = openai_client.beta.threads.create()
        self.thread_id = thread.id
        self.skill_level = skill_level
        self.infrastructure = None
        self.checklist = None
        self.username = None

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

    def get_infrastructure(self):
        """Return the checklist of the user."""
        return self.infrastructure

    def set_infrastructure(self, infrastructure):
        """Set the checklist of the user."""
        self.infrastructure = infrastructure

    def get_checklist(self):
        """Return the checklist of the user."""
        return self.checklist

    def set_checklist(self, checklist):
        """Set the checklist of the user."""
        self.checklist = checklist

    def get_username(self):
        """Return the username of the user."""
        return self.username

    def set_username(self, username):
        """Set the username of the user."""
        self.username = username
