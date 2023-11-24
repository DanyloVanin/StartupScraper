from neo4j import GraphDatabase

import config

uri = config.NEO4J_URI
username = config.NEO4J_USER
password = config.NEO4J_PASSWORD


def execute_query(query, **params):
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            result = session.run(query, **params)
            records = list(result)
            return records



def get_all_startups_and_sectors():
    query = "MATCH (s:Startup)-[:IN_SECTOR]->(sec:Sector) RETURN s.name AS startup, COLLECT(sec.name) AS sectors"
    records = execute_query(query)

    print("Get all startups and their sectors")
    for record in records:
        print(f"{record['startup']} - Sectors: {', '.join(record['sectors'])}")



def find_persons_at_startup(startup_name):
    query = "MATCH (p:Person)-[:WORKS_AT]->(s:Startup {name: $startup_name}) RETURN p.name AS person, p.position AS position"
    result = execute_query(query, startup_name=startup_name)
    print(f"Find persons who work at {startup_name}")
    for record in result:
        print(f"{record['person']} - Position: {record['position']}")


def find_startups_in_sector(sector_name):
    query = "MATCH (s:Startup)-[:IN_SECTOR]->(sec:Sector {name: $sector_name}) RETURN s.name AS startup"
    result = execute_query(query, sector_name=sector_name)
    print(f"Find startups in the {sector_name} sector")
    for record in result:
        print(record['startup'])


def get_total_startups():
    query = "MATCH (s:Startup) RETURN COUNT(s) AS total_startups"
    records = execute_query(query)

    # Check if there are records
    if records:
        print("Get the total number of startups")
        print(f"Total Startups: {records[0]['total_startups']}")
    else:
        print("No startups found.")



def get_most_common_sector():
    query = "MATCH (s:Startup)-[:IN_SECTOR]->(sec:Sector) RETURN sec.name AS sector, COUNT(s) AS startup_count ORDER BY startup_count DESC LIMIT 1"
    records = execute_query(query)

    # Check if there are records
    if records:
        print("Get the most common sector")
        record = records[0]
        print(f"Most Common Sector: {record['sector']} (Number of Startups: {record['startup_count']})")
    else:
        print("No sectors found.")



def get_total_persons():
    query = "MATCH (p:Person) RETURN COUNT(p) AS total_persons"
    records = execute_query(query)

    # Check if there are records
    if records:
        print("Get the number of persons in the database")
        print(f"Total Persons: {records[0]['total_persons']}")
    else:
        print("No persons found.")



def get_startups_founded_last_five_years():
    query = "MATCH (s:Startup) WHERE s.year_founded >= date().year - 5 RETURN s.name AS startup, s.year_founded AS year_founded"
    result = execute_query(query)
    print("Get startups founded in the last five years")
    for record in result:
        print(f"{record['startup']} - Year Founded: {record['year_founded']}")


def get_founders_and_startups():
    query = "MATCH (p:Person)-[:FOUNDED]->(s:Startup) RETURN p.name AS person, s.name AS startup"
    result = execute_query(query)
    print("Get persons who are founders and their startups")
    for record in result:
        print(f"{record['person']} - Founder of: {record['startup']}")


if __name__ == "__main__":
    get_all_startups_and_sectors()
    print("\n" + "=" * 50 + "\n")
    find_persons_at_startup("Zimmerman Metals")  # Replace with the desired startup name
    print("\n" + "=" * 50 + "\n")
    find_startups_in_sector("machinery")  # Replace with the desired sector name
    print("\n" + "=" * 50 + "\n")
    get_total_startups()
    print("\n" + "=" * 50 + "\n")
    get_most_common_sector()
    print("\n" + "=" * 50 + "\n")
    get_total_persons()
    print("\n" + "=" * 50 + "\n")
    get_startups_founded_last_five_years()
    print("\n" + "=" * 50 + "\n")
    get_founders_and_startups()
