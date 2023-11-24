from neo4j import GraphDatabase
import pandas as pd
from tqdm import tqdm
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

# Neo4j connection details
uri = NEO4J_URI  # Update with your Neo4j server URI
username = NEO4J_USER  # Update with your Neo4j username
password = NEO4J_PASSWORD  # Update with your Neo4j password

# Neo4j Cypher queries
create_startup_query = """
MERGE (s:Startup {name: $name})
ON CREATE SET
  s.description = $description,
  s.headquarters = $hq_city,
  s.hq_country = $hq_country,
  s.website = $website,
  s.year_founded = $year_founded,
  s.employees = $employees
"""

create_founder_query = """
MERGE (f:Person {name: $name})
ON CREATE SET
  f.tech_skills = $tech_skills,
  f.founded_before = $founded_before,
  f.managing_experience = $managing_experience,
  f.gender = $gender,
  f.profile_link = $profile_link
"""

create_acceleration_program_query = """
MERGE (p:AccelerationProgram {name: $name, city: $city, country: $country, average_funding: $funding})
"""

create_participation_query = """
MATCH (s:Startup {name: $startup_name}), (p:AccelerationProgram {name: $program_name})
MERGE (s)-[:PARTICIPATED_IN {year: $year}]->(p)
MERGE (p)-[:HAD_PARTICIPANT {year: $year}]->(s)
"""

create_sector_query = """
MERGE (sec:Sector {name: $sector_name})
"""

create_sector_relationship_query = """
MATCH (s:Startup {name: $startup_name}), (sec:Sector {name: $sector_name})
MERGE (s)-[:IN_SECTOR]->(sec)
MERGE (sec)-[:PART_OF_SECTOR]->(s)
"""

create_relationship_query = """
MATCH (s:Startup {name: $startup_name}),
      (f:Person {name: $founder_name})
MERGE (f)-[:FOUNDED]->(s)
MERGE (s)-[:FOUNDED_BY]->(f)
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
            # Process Startup data
            for _, row in tqdm(df_filtered.iterrows(), total=len(df_filtered), desc="Processing Startups"):
                counter += 1

                # Process Industry data (split by commas, lowercase, and create sectors)
                industries = [industry.strip().lower() for industry in row["Industry of Startup"].split(",")]
                for industry in industries:
                    sector_data = {"sector_name": industry}
                    session.execute_write(create_node, create_sector_query, sector_data)
                    relationship_data = {"startup_name": row["Name of Startup"], "sector_name": industry}
                    session.execute_write(create_relationship, create_sector_relationship_query, relationship_data)

                # Process Startup data
                startup_data = {
                    "name": row["Name of Startup"],
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

                # Process Acceleration Program data
                program_data = {
                    "name": row["Accelerator Program"],
                    "city": row["City of Accelerator"],
                    "country": row["Country of Accelerator"],
                    "funding": clean_funding(row["Typical funding by accelerator"]),
                }
                session.execute_write(create_node, create_acceleration_program_query, program_data)

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
