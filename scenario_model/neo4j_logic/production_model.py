from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def get_matching_startups_with_scores(reputation_threshold=4.0):
    # Constructing the query to find startups that match the rules
    query = f"""
    MATCH (s:Startup)
    OPTIONAL MATCH (f:Person)-[:FOUNDED]->(s)
    OPTIONAL MATCH (s)-[:IN_SECTOR]->(sec:Sector)
    OPTIONAL MATCH (s)-[:PARTICIPATED_IN]->(p:AccelerationProgram)
    WITH s,
         f,
         sec,
         AVG(sec.reputation) AS average_sector_reputation,
         COLLECT(DISTINCT p.name) AS accelerator_names
    WITH s,
         f,
         sec,
         average_sector_reputation,
         accelerator_names,
         CASE WHEN f.managing_experience IS NOT NULL THEN 1 ELSE 0 END AS managing_experience_score,
         CASE WHEN f.tech_skills IS NOT NULL THEN 1 ELSE 0 END AS tech_skills_score,
         CASE WHEN accelerator_names IS NOT NULL THEN 1 ELSE 0 END AS accelerator_names_score,
         CASE WHEN f.founded_before IS NOT NULL THEN 1 ELSE 0 END AS founded_before_score
    WHERE
        (f.managing_experience IS NOT NULL OR f.tech_skills IS NOT NULL OR accelerator_names IS NOT NULL OR f.founded_before IS NOT NULL) AND
        average_sector_reputation > {reputation_threshold}
    RETURN DISTINCT s.name AS startup_name,
           managing_experience_score + tech_skills_score + accelerator_names_score + founded_before_score AS score
    """

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            result = session.run(query).data()

    return result

# prediction_model.py

def does_startup_match_rules(startup_name, reputation_threshold=4.0, selected_rules=None):
    # Constructing the query to check if a given startup matches the rules
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            query = construct_match_rules_query(startup_name, reputation_threshold, selected_rules)
            result = session.run(query, startup_name=startup_name, reputation_threshold=reputation_threshold).single()

    if result is None:
        return None
    return result["matches_rules"]


def construct_match_rules_query(startup_name, reputation_threshold, selected_rules):
    # Build the query dynamically based on selected rules
    with_clauses = []
    where_clauses = []

    if 'tech_skills' in selected_rules:
        with_clauses.append("f.tech_skills AS tech_skills")

    if 'founded_before' in selected_rules:
        with_clauses.append("f.founded_before AS founded_before")

    if 'managing_experience' in selected_rules:
        with_clauses.append("CASE WHEN f.managing_experience IS NOT NULL THEN f.managing_experience ELSE NULL END AS managing_experience")

    if 'acceleration_participation' in selected_rules:
        with_clauses.append("CASE WHEN p.name IS NOT NULL THEN p.name ELSE NULL END AS accelerator_name")

    if 'average_sector_reputation' in selected_rules:
        with_clauses.append("AVG(sec.reputation) AS average_sector_reputation")

    # Add more clauses for other rules as needed

    # Construct the WITH clause dynamically
    with_clause = ', '.join(with_clauses)

    # Construct the WHERE clause dynamically
    if 'managing_experience' in selected_rules:
        where_clauses.append("(managing_experience IS NOT NULL OR managing_experience IS NULL)")
    else:
        where_clauses.append("managing_experience IS NULL")

    if 'acceleration_participation' in selected_rules:
        where_clauses.append("(accelerator_name IS NOT NULL OR accelerator_name IS NULL)")
    else:
        where_clauses.append("accelerator_name IS NULL")

    if 'average_sector_reputation' in selected_rules:
        where_clauses.append("(average_sector_reputation > $reputation_threshold OR average_sector_reputation IS NULL)")
    else:
        where_clauses.append("average_sector_reputation IS NULL")

    # Add more clauses for other rules as needed

    # Construct the final query
    query = f"""
    MATCH (s:Startup {{name: $startup_name}})
    OPTIONAL MATCH (f:Person)-[:FOUNDED]->(s)
    OPTIONAL MATCH (s)-[:IN_SECTOR]->(sec:Sector)
    OPTIONAL MATCH (s)-[:PARTICIPATED_IN]->(p:AccelerationProgram)
    WITH s, {with_clause}
    WHERE {' AND '.join(where_clauses)}
    AND (average_sector_reputation > $reputation_threshold OR average_sector_reputation IS NULL)
    RETURN
        s.name AS startup_name,
        average_sector_reputation > $reputation_threshold AS matches_rules
    """

    return query


