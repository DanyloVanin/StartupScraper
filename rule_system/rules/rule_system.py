from neo4j import GraphDatabase
import config

from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


def check_tech_skills(startup_name):
    # Query to check if tech_skills is not null for the given startup
    query = f"""
    MATCH (s:Startup {{name: $startup_name}})
    OPTIONAL MATCH (f:Person)-[:FOUNDED]->(s)
    RETURN f.tech_skills IS NOT NULL AS tech_skills
    """

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            result = session.run(query, startup_name=startup_name).single()

    return result["tech_skills"]


def check_founded_before(startup_name):
    # Query to check if founded_before is not null for the given startup
    query = f"""
    MATCH (s:Startup {{name: $startup_name}})
    OPTIONAL MATCH (f:Person)-[:FOUNDED]->(s)
    RETURN f.founded_before IS NOT NULL AS founded_before
    """

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            result = session.run(query, startup_name=startup_name).single()

    return result["founded_before"]


def check_managing_experience(startup_name):
    # Query to check if managing_experience is not null for the given startup
    query = f"""
    MATCH (s:Startup {{name: $startup_name}})
    OPTIONAL MATCH (f:Person)-[:FOUNDED]->(s)
    RETURN f.managing_experience IS NOT NULL AS managing_experience
    """

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            result = session.run(query, startup_name=startup_name).single()

    return result["managing_experience"]


def check_acceleration_participation(startup_name):
    # Query to check if the startup has participated in an acceleration program
    query = f"""
    MATCH (s:Startup {{name: $startup_name}})
    OPTIONAL MATCH (s)-[:PARTICIPATED_IN]->(p:AccelerationProgram)
    RETURN p.name IS NOT NULL AS acceleration_participation
    """

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            result = session.run(query, startup_name=startup_name).single()

    return result["acceleration_participation"]


def check_average_sector_reputation(startup_name, reputation_threshold=4.0):
    # Query to check if average_sector_reputation is higher than the threshold for the given startup
    query = f"""
    MATCH (s:Startup {{name: $startup_name}})
    OPTIONAL MATCH (s)-[:IN_SECTOR]->(sec:Sector)
    WITH s, AVG(sec.reputation) AS average_sector_reputation
    RETURN average_sector_reputation > $reputation_threshold AS average_reputation
    """

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            result = session.run(query, startup_name=startup_name, reputation_threshold=reputation_threshold).single()

    return result["average_reputation"]


def get_all_startups():
    query = """
    MATCH (s:Startup)
    RETURN DISTINCT s.name AS startup_name
    """

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            result = session.run(query).value()

    return result


def evaluate_startup(startup_name, threshold=3, reputation_threshold=4.0):
    true_count = 0

    # Call each rule check function and count True responses
    if check_tech_skills(startup_name):
        true_count += 1

    if check_founded_before(startup_name):
        true_count += 1

    if check_managing_experience(startup_name):
        true_count += 1

    if check_acceleration_participation(startup_name):
        true_count += 1

    if check_average_sector_reputation(startup_name, reputation_threshold):
        true_count += 1

    # Return True if the count is less than the threshold
    return true_count < threshold

