import os
import json
from neo4j import GraphDatabase
from tqdm import tqdm

import config

uri = config.NEO4J_URI
username = config.NEO4J_USER
password = config.NEO4J_PASSWORD


def create_startup(tx, data):
    tx.run(
        """
        MERGE (s:Startup {name: $name})
        SET
          s.description = $description,
          s.headquarters = $hq,
          s.website = $website,
          s.year_founded = $year_founded,
          s.employees = $employees
        """,
        name=data["Company Name"],
        description=data["Overview"],
        hq=data["HQ"],
        website=data["Website"],
        year_founded=data["FoundationYear"],
        employees=data["Employees"]
    )


def create_person(tx, person):
    tx.run(
        """
        MERGE (p:Person {name: $name})
        SET
          p.position = $position,
          p.linkedin = $linkedin
        """,
        name=person["Name"],
        position=person["Position"],
        linkedin=person["LinkedIn"]
    )


def create_relationship(tx, data):
    for person in data["KeyPeople"]:
        tx.run(
            """
            MATCH (s:Startup {name: $startup_name}), (p:Person {name: $person_name})
            MERGE (p)-[:WORKS_AT]->(s)
            MERGE (s)-[:HAS_WORKER]->(p)
            """,
            startup_name=data["Company Name"],
            person_name=person["Name"]
        )


def create_sector(tx, sector_name):
    tx.run(
        """
        MERGE (s:Sector {name: $name})
        """,
        name=sector_name.lower()
    )


def create_sector_relationship(tx, data):
    for sector in data["Sectors"]:
        tx.run(
            """
            MATCH (s:Startup {name: $startup_name}), (sec:Sector {name: $sector_name})
            MERGE (s)-[:IN_SECTOR]->(sec)
            MERGE (sec)-[:PART_OF_SECTOR]->(s)
            """,
            startup_name=data["Company Name"],
            sector_name=sector.lower()
        )


def save_to_neo4j(json_path):
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            for filename in tqdm(os.listdir(json_path), desc="Processing Files", unit="file"):
                if filename.endswith(".json"):
                    file_path = os.path.join(json_path, filename)
                    with open(file_path, 'r') as json_file:
                        input_data = json.load(json_file)
                        for person in input_data["KeyPeople"]:
                            session.execute_write(create_person, person)
                        session.execute_write(create_startup, input_data)
                        session.execute_write(create_relationship, input_data)
                        for sector in input_data["Sectors"]:
                            session.execute_write(create_sector, sector)
                            session.execute_write(create_sector_relationship, input_data)


if __name__ == "__main__":
    # Replace this with the directory containing your JSON files
    json_directory = "./company_data_with_names"

    save_to_neo4j(json_directory)
