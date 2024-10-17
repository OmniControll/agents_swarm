from swarm import Swarm, Agent
from random import random
import sqlite3


# gotta start the swarm
client = Swarm()

#swarm function includes args: 
# 1. number of agents
# 2. number of iterations
# 3. number of dimensions
# 4. number of objectives
# 5. number of constraints
# 6. number of variables
# 7. number of objectives
# 8. number of constraints

# create sqlite database
def init_database():
    conn = sqlite3.connect('swarm.db')
    cursor = conn.cursor()
    # create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_value TEXT
        )
    ''')
    conn.commit()
    conn
init_database()

#store the data in sqlite base
def store_in_database(context_variables, new_data):
    # Connect to the SQLite database
    conn = sqlite3.connect('swarm_database.db')
    cursor = conn.cursor()
    
    # Insert data into the table
    for value in new_data:
        cursor.execute('INSERT INTO data_table (data_value) VALUES (?)', (str(value),))
    
    conn.commit()
    conn.close()
    print(f"Storing {new_data} in database")
    
    return agent_2  # Handoff to Agent 2

# create agents

def store_in_database(context_variables, new_data):
    global database
    print(f"Storing {new_data} in database")
    database.append(new_data)
    return agent_2 # handoff to 


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


# Define Agents
agent_1 = Agent(
    name='Agent_1',
    instructions='You are an expert database manager. You are given a database and a set of instructions. You need to store the data in the correct table or create it if it does not exist.',
    functions=[store_in_database]
)

agent_2 = Agent(
    name='Agent_2',
    instructions='You are an expert data processor. You are given a database and a set of instructions. You need to process the data in the database to remove duplicates.',
    functions=[remove_duplicates]
)

# Run the Swarm interaction
response = client.run(
    agent=agent_1,  # Start with Agent 1
    messages=[{"role": "user", "content": "Here is some data: [1, 2, 2, 3, 4]"}],
    context_variables={"new_data": [1, 2, 2, 3, 4]}  # Pass the data
)

# Output the final response
print(response.messages[-1]["content"])