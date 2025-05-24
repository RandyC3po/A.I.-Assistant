import json
import nltk
import tkinter as tk
from tkinter import scrolledtext

# Assuming response_generator.py and data_access.py are in the same directory
from response_generator import generate_response
from data_access import query_database as da_query_database # Renamed to avoid conflict


class PersonalAI:
    

    def load_config(self, config_file):
    """
    Loads the configuration from a JSON file.

    Args:
        config_file (str): The path to the configuration file.

    Returns:
        dict: The configuration data loaded from the file. If the file is not found, 
        returns a default configuration with an empty list of allowed databases.

    Raises:
        json.JSONDecodeError: If there is an error decoding the JSON.
    """

        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"allowed_databases": []}
        # Add other error handling like json.JSONDecodeError if needed

    def process_command(self, command):
        
        def _read_json_database(database_name):  # Renamed to be more specific
           
            try:
                with open(database_name, 'r') as f:
                    data = json.load(f)
                return json.dumps(data, indent=2)
            except FileNotFoundError as e:
                print(f"Error: Database file '{database_name}' not found. {e}")
                return None
            except json.JSONDecodeError as e:
                print(f"Error: Failed to decode JSON from '{database_name}'. {e}")
                return None
            except Exception as e:
                print(f"Unexpected error reading database '{database_name}': {type(e).__name__} - {e}")
                return None

        intent = self.recognize_intent(command)        
        if intent:
            if intent["action"] == "find":
                data = self.access_data(intent)
                response = generate_response(intent, data)
                return response
            elif intent["action"] == "read":
                data = _read_json_database(intent["database"])  # Use the specific JSON reader
                response = generate_response(intent, data)
                return response
            elif intent["action"] == "define_word":
                definition_data = self.get_word_definition(intent["word"])
                response = generate_response(intent, definition_data)
                return response
        else:            
            return generate_response(None, None)

    def recognize_intent(self, command):
        command = command.lower()
        words = []
        tagged_words = []

        try:
            words = nltk.word_tokenize(command)
            tagged_words = nltk.pos_tag(words)
        except Exception as e:
            print(f"Error during tokenization or tagging: {e}")
            return None

        # Intent: Find
        if "find" in words and "in" in words:
            try:
                find_index = words.index("find")
                in_index = words.index("in", find_index + 1) # Search for "in" after "find"

                query_parts = words[find_index + 1 : in_index]
                query = " ".join(query_parts).strip()  # Convert list to string and remove leading/trailing spaces

                database_parts = words[in_index + 1 :]
                database_name = " ".join(database_parts).strip()  # Convert list to string and remove leading/trailing spaces

                print(f"Debug: 'find' intent - query: '{query}', database: '{database_name}'")

                # Check if the extracted database_name is in allowed_databases (case-insensitive)
                if database_name and any(db.lower() == database_name.lower() for db in self.allowed_databases):
                    # Find the exact casing from allowed_databases to use
                    actual_db_name = next(db for db in self.allowed_databases if db.lower() == database_name.lower())
                    return {"action": "find", "query": query, "database": actual_db_name}
                else:
                    print(f"Debug: 'find' intent - database '{database_name}' not in allowed_databases: {self.allowed_databases}")

            except ValueError: # If "find" or "in" is not found in the expected order
                pass

        # Intent: Read
        elif "read" in words and "from" in words:
            try:
                read_index = words.index("read")
                from_index = words.index("from")
                if from_index > read_index: # Ensure "from" comes after "read"
                    database_parts = words[from_index + 1:]
                    database_name = " ".join(database_parts).strip()  # Convert list to string and remove leading/trailing spaces

                    print(f"Debug: 'read' intent - database: '{database_name}'")


                    if database_name and any(db.lower() == database_name.lower() for db in self.allowed_databases):
                        actual_db_name = next(db for db in self.allowed_databases if db.lower() == database_name.lower())
                        return {"action": "read", "database": actual_db_name}
                    else:
                        print(f"Debug: 'read' intent - database '{database_name}' not in allowed_databases: {self.allowed_databases}")
            except ValueError: # If "read" or "from" is not found
                pass

        # Intent: Define Word
        elif words and words[0] == "define" and len(words) > 1:
            # The term to define is everything after "define"
            term_to_define = " ".join(words[1:]).strip()
            print(f"Debug: 'define' intent - word: '{term_to_define}'")
            return {"action": "define_word", "word": term_to_define}

        return None

    def access_data(self, intent):
        if isinstance(intent, dict) and intent.get("action") == "find":
            database_name = intent.get("database")
            query = intent.get("query")
            print(f"Debug: access_data - database: '{database_name}', query: '{query}'")
            # The check for database_name in allowed_databases is now done in recognize_intent
            if database_name and query is not None:
                return self.query_database(database_name, query)
        return None

    def query_database(self, database_filename, query):
        # This method now calls the imported function from data_access.py
        # It assumes database_filename is the full name (e.g., "notes.txt")
        print(f"Debug: query_database - filename: '{database_filename}', query: '{query}'")
        return da_query_database(database_filename, query)

    def get_word_definition(self, word):
        # Placeholder: Implement actual word definition logic here
        # e.g., using an API like WordNet through NLTK, or another dictionary API
        print(f"Placeholder: Would define '{word}' here.")
        return f"Definition for '{word}': (Not implemented yet)"

class AIAssistantGUI:
    """
    A graphical user interface (GUI) for a personal AI assistant application.
    Attributes:
        master (tk.Tk): The root window of the Tkinter application.
        ai_assistant (PersonalAI): An instance of the PersonalAI class to handle AI-related functionality.
        command_label (tk.Label): A label widget prompting the user to enter a command.
        command_entry (tk.Entry): An entry widget for the user to input commands.
        response_label (tk.Label): A label widget indicating the response section.
        response_text (tk.scrolledtext.ScrolledText): A text widget to display the AI assistant's responses.
        exit_button (tk.Button): A button widget to exit the application.
    Methods:
        __init__(master):
            Initializes the GUI components and sets up the layout.
        process_input():
            Processes the user's input command and displays the AI assistant's response.
        exit_program():
            Exits the application when the exit button is clicked.
    """
    def __init__(self, master):
        self.master = master
        master.title("Personal AI Assistant")

        config = self.load_config("config.json")
        self.allowed_databases = config.get("allowed_databases", [])

        self.ai_assistant = PersonalAI() # Create an instance of the AI

        self.command_label = tk.Label(master, text="Enter command:")
        self.command_label.pack()

        self.command_entry = tk.Entry(master, width=50)
        self.command_entry.pack()
        self.command_entry.bind("<Return>", self.process_input)

        self.response_label = tk.Label(master, text="Response:")
        self.response_label.pack()

        self.response_text = scrolledtext.ScrolledText(master, width=60, height=10, state=tk.DISABLED)
        self.response_text.pack()

        self.exit_button = tk.Button(master, text="Exit", command=self.exit_program)
        self.exit_button.pack()

        self.ai_assistant.allowed_databases = self.allowed_databases

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"allowed_databases": []}
    def process_input(self, event=None):
        user_command = self.command_entry.get()
        print(f"User Command: {user_command}")  # Debugging
        self.command_entry.delete(0, tk.END)
        if user_command.strip():
            response = self.ai_assistant.process_command(user_command)
            print(f"Response: {response}")  # Debugging
        else:
            response = "Please enter a command."
            print("No command entered.")  # Debugging
        self.display_response(response)

    def display_response(self, response):
        self.response_text.config(state=tk.NORMAL)
        self.response_text.insert(tk.END, response + "\n")
        self.response_text.config(state=tk.DISABLED)
        self.response_text.see(tk.END) # Scroll to the end

    def exit_program(self):
        self.master.destroy()

def main():
    root = tk.Tk()
    gui = AIAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()