import sqlite3
import subprocess
import json
import requests
import time

# Create SQLite database and table if they don't exist
def initialize_database():
    # Connect to SQLite database (creates the database file if it doesn't exist)
    conn = sqlite3.connect('swarm_database.db')
    cursor = conn.cursor()
    # Create table if it doesn't already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_value TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the SQLite database
initialize_database()

# Define a base class for an Agent
class Agent:
    def __init__(self, name, instructions, function):
        self.name = name
        self.instructions = instructions
        self.function = function

    def run(self, context_variables):
        # Before executing the function, query Ollama to get context-aware instructions
        prompt = f"{self.instructions} Current context: {context_variables}"
        context_from_llm = query_local_llm(prompt)
        print(f"Agent {self.name} received additional context: {context_from_llm}")
        # Update the context variables with the response from the LLM
        context_variables['llm_context'] = context_from_llm
        return self.function(context_variables)

# Store data in SQLite database
def store_in_database(context_variables):
    # Connect to the SQLite database
    new_data = context_variables["new_data"]
    conn = sqlite3.connect('swarm_database.db')
    cursor = conn.cursor()
    
    # Insert data into the table
    for value in new_data:
        cursor.execute('INSERT INTO data_table (data_value) VALUES (?)', (str(value),))
    
    conn.commit()
    conn.close()
    print(f"Storing {new_data} in database")
    
    # Proceed to Agent 2 (removing duplicates)
    return agent_2.run(context_variables)

# Remove duplicates from SQLite database
def remove_duplicates(context_variables):
    # Connect to the SQLite database
    conn = sqlite3.connect('swarm_database.db')
    cursor = conn.cursor()

    # Fetch all rows from the database and select distinct values to remove duplicates
    cursor.execute('SELECT DISTINCT data_value FROM data_table')
    unique_data = cursor.fetchall()

    # Clear the existing table
    cursor.execute('DELETE FROM data_table')

    # Insert only the unique rows back into the table
    for value in unique_data:
        cursor.execute('INSERT INTO data_table (data_value) VALUES (?)', (value[0],))
    
    conn.commit()
    conn.close()
    
    print(f"Database after removing duplicates: {unique_data}")
    return "Duplicates removed, data processed."

# Use Ollama to interact with a local LLM
def query_local_llm(prompt):
    # Check if the Ollama server is running before attempting to start it
    try:
        response = requests.get('http://localhost:11434')
        if response.status_code == 200:
            print("Ollama server is already running.")
    except requests.ConnectionError:
        # Start Ollama server if it's not already running
        subprocess.Popen(['ollama', 'serve'])
        time.sleep(5)  # Wait for the server to start
    
    # Query the LLM using Ollama's REST API
    try:
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "llama3.2",
            "prompt": prompt
        })
        response_data = response.text  # Changed from .json() to .text to avoid JSON decoding issues
        
        # Extract complete response from multi-line JSON data
        response_lines = response_data.splitlines()
        complete_response = ""
        for line in response_lines:
            try:
                line_json = json.loads(line)
                complete_response += line_json.get('response', '')
            except json.JSONDecodeError:
                continue
        
        return complete_response if complete_response else f"Error: Invalid response from LLM - {response_data}"
    except requests.RequestException as e:
        return f"Error: Request failed - {str(e)}"

# Define custom Agents
agent_1 = Agent(
    name='Agent_1',
    instructions='You are an expert database manager. You are given a database and a set of instructions. You need to store the data in the correct table or create it if it does not exist.',
    function=store_in_database
)

agent_2 = Agent(
    name='Agent_2',
    instructions='You are an expert data processor. You are given a database and a set of instructions. You need to process the data in the database to remove duplicates.',
    function=remove_duplicates
)

# Run the agent interaction manually
context_variables = {"new_data": [1, 2, 2, 3, 4]}
response = agent_1.run(context_variables)

# Output the final response from the agents
print(response)

# Example usage of the local LLM via Ollama
prompt = "Summarize the current state of the database."
llm_response = query_local_llm(prompt)
print(llm_response)
