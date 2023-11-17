import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import uuid

# Neo4j connection details
uri = NEO4J_URI  # Update with your Neo4j server URI
username = NEO4J_USER  # Update with your Neo4j username
password = NEO4J_PASSWORD  # Update with your Neo4j password

# Neo4j Cypher
create_program_query = "MERGE (p:AccelerationProgram {name: $name, city: $city, country: $country, average_founding: " \
                       "$funding})"

create_participation_query = """
MATCH (s:Startup {name: $startup_name}), (p:AccelerationProgram {name: $program_name})
MERGE (s)-[:PARTICIPATED_IN {year: $year}]->(p)
"""

create_startup_query = """
MERGE (s:Startup {name: $name})
ON CREATE SET
  s.industry = $industry,
  s.description = $description,
  s.headquarters = $hq_city,
  s.hq_country = $hq_country,
  s.website = $website,
  s.year_founded = $year_founded,
  s.employees = $employees
"""

create_founder_query = """
MERGE (f:Founder {name: $name})
ON CREATE SET
  f.tech_skills = $tech_skills,
  f.founded_before = $founded_before,
  f.managing_experience = $managing_experience,
  f.gender = $gender,
  f.profile_link = $profile_link
"""

create_relationship_query = """
MATCH (s:Startup {name: $startup_name}),
      (f:Founder {name: $founder_name})
MERGE (f)-[:FOUNDED]->(s)
"""


def clean_funding(funding):
    # Clean up funding values: remove non-breaking space and comma, and convert to integer
    res = funding.replace('\xa0', '').replace(',', '')
    if res == "000€":
        return '0'
    return res


def create_node(tx, query, data):
    tx.run(query, **data)


def create_relationship(tx, query, data):
    tx.run(query, **data)


def process_excel_data(file_path):
    # Read Excel file into a pandas DataFrame
    df = pd.read_csv(file_path, sep=';', engine='python')
    df_filtered = df.dropna()

    counter = 0
    # Connect to Neo4j
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            # Process Acceleration Program data
            for _, row in tqdm(df_filtered.iterrows(), total=len(df_filtered), desc="Processing Acceleration Programs"):
                counter += 1
                # Create AccelerationProgram node
                program_data = {
                    "name": row["Accelerator Program"],
                    "city": row["City of Accelerator"],
                    "country": row["Country of Accelerator"],
                    "funding": clean_funding(row["Typical funding by accelerator"]),
                }
                session.execute_write(create_node, create_program_query, program_data)

                # Process Startup data
                startup_data = {
                    "name": row["Name of Startup"],
                    "industry": row["Industry of Startup"],
                    "description": row["Description of Startup"],
                    "hq_city": row["HQ City of Startup"],
                    "hq_country": row["HQ Country of Startup"],
                    "website": row["Website of Startup"],
                    "year_founded": row["Year Founded"],
                    "employees": row["Employees (min)"]
                }
                session.execute_write(create_node, create_startup_query, startup_data)

                # Process Founder data
                founder_data = {
                    "name": row["Name of Founder"],
                    "tech_skills": row["Founder has tech skills"],
                    "founded_before": row["Founder has founded before"],
                    "managing_experience": row["Founder has over 10 years managing experience"],
                    "gender": row["Gender of Founder"],
                    "profile_link": row["Founder profile"]
                }
                session.execute_write(create_node, create_founder_query, founder_data)

                # Create a relationship between Startup and AccelerationProgram
                relationship_data = {
                    "startup_name": row["Name of Startup"],
                    "program_name": row["Accelerator Program"],
                    "year": row["Accelerated in year"]
                }
                session.execute_write(create_relationship, create_participation_query, relationship_data)

                # Create relationships
                relationship_data = {
                    "startup_name": row["Name of Startup"],
                    "founder_name": row["Name of Founder"],
                }
                session.execute_write(create_relationship, create_relationship_query, relationship_data)

            print(f"Processed {counter} rows of data.")


if __name__ == "__main__":
    excel_file_path = r"./resources/cleaned_data.csv"  # Update with the path to your Excel file
    process_excel_data(excel_file_path)
