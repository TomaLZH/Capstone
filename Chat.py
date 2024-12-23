class Chat:
    def __init__(self, openai_client, skill_level= "Beginner", environment = "None Selected"):
        self.query_counter = 0
        self.chat_history = [] 
        thread = openai_client.beta.threads.create()
        self.thread_id = thread.id
        self.skill_level = skill_level
        self.environment = environment
        self.checklist = {}

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
        
    def get_environment(self):
        """Return the environment of the user."""
        return self.environment

    def set_environment(self, environment):
        """Set the environment of the user."""
        self.environment = environment
        
    def get_checklist(self):
        """Return the checklist of the user."""
        return self.checklist
    
    def set_checklist(self, checklist):
        """Set the checklist of the user."""
        self.checklist = checklist