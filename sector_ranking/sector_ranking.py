from neo4j import GraphDatabase

import config


# Neo4j database connection details
uri = config.NEO4J_URI
username = config.NEO4J_USER
password = config.NEO4J_PASSWORD

# Function to update sectors in the Neo4j database
def update_sectors(tx, sector_name, reputation):
    query = (
        "MERGE (sec:Sector {name: $sector_name}) "
        "SET sec.reputation = $reputation"
    )
    tx.run(query, sector_name=sector_name, reputation=reputation)

# Read the file and update Neo4j database
file_path = "sectors.txt"  # Replace with the actual path to your file

with open(file_path, 'r') as file:
    lines = file.readlines()

update_counter = 0

# Connect to Neo4j and update sectors
with GraphDatabase.driver(uri, auth=(username, password)) as driver:
    with driver.session() as session:
        for line in lines:
            sector_name, reputation = map(str.strip, line.split(','))
            reputation = int(reputation)
            print(f"Updating {sector_name} with reputation {reputation}...")
            update_counter += 1
            session.write_transaction(update_sectors, sector_name, reputation)

print("Sectors updated successfully.")
print(f"Total sectors updated: {update_counter}")
