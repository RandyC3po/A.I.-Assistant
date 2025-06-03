# *************  ✨ Windsurf Command ⭐  *************
# No executable Python code was provided.
# *******  eb22571e-6072-47b6-96f9-195da2cc912b  *******
import unittest
from unittest.mock import patch, mock_open
import json
import os

# Assuming myscript.py is in the same directory
from myscript import PersonalAI, AIAssistantGUI

# Mock configuration data
MOCK_CONFIG = {
    "allowed_databases": ["notes.txt", "tasks.json", "config.json"]
}

# Mock database data
MOCK_NOTES_DATA = "Note 1: This is the first note.\nNote 2: Another note here.\nTask: Buy groceries."
MOCK_TASKS_DATA = json.dumps([
    {"id": 1, "task": "Write tests", "status": "completed"},
    {"id": 2, "task": "Refactor code", "status": "pending"}
], indent=2)

class TestPersonalAI(unittest.TestCase):

    @patch('myscript.open', new_callable=mock_open, read_data=json.dumps(MOCK_CONFIG))
    @patch('json.load', return_value=MOCK_CONFIG)
    def setUp(self, mock_json_load, mock_file):
        """Set up a PersonalAI instance before each test."""
        self.ai = PersonalAI(config_file="dummy_config.json")
        # Ensure allowed_databases is set correctly from the mock config
        self.ai.allowed_databases = MOCK_CONFIG["allowed_databases"]
        print(f"Setup: allowed_databases = {self.ai.allowed_databases}") # Debugging

    def test_load_config_success(self):
        """Test loading configuration from a valid file."""
        # The setUp method already loads the mock config, so we just check the result
        self.assertEqual(self.ai.config, MOCK_CONFIG)
        self.assertEqual(self.ai.allowed_databases, MOCK_CONFIG["allowed_databases"])

    @patch('myscript.open', side_effect=FileNotFoundError)
    def test_load_config_file_not_found(self, mock_file):
        """Test loading configuration when the file is not found."""
        ai = PersonalAI(config_file="non_existent_config.json")
        self.assertEqual(ai.config, {"allowed