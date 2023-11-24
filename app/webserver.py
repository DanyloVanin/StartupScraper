from flask import Flask, render_template, request

from neo4j import GraphDatabase
import config

app = Flask(__name__)

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
    return execute_query(query)


def find_persons_at_startup(startup_name):
    query = "MATCH (p:Person)-[:WORKS_AT]->(s:Startup {name: $startup_name}) RETURN p.name AS person, p.position AS position"
    return execute_query(query, startup_name=startup_name)


def find_startups_in_sector(sector_name):
    query = "MATCH (s:Startup)-[:IN_SECTOR]->(sec:Sector {name: $sector_name}) RETURN s.name AS startup"
    return execute_query(query, sector_name=sector_name)


def get_total_startups():
    query = "MATCH (s:Startup) RETURN COUNT(s) AS total_startups"
    records = execute_query(query)

    if records:
        return f"Total Startups: {records[0]['total_startups']}"
    else:
        return "No startups found."


def get_most_common_sector():
    query = "MATCH (s:Startup)-[:IN_SECTOR]->(sec:Sector) RETURN sec.name AS sector, COUNT(s) AS startup_count ORDER BY startup_count DESC LIMIT 1"
    records = execute_query(query)

    if records:
        record = records[0]
        return f"Most Common Sector: {record['sector']} (Number of Startups: {record['startup_count']})"
    else:
        return "No sectors found."


def get_total_persons():
    query = "MATCH (p:Person) RETURN COUNT(p) AS total_persons"
    records = execute_query(query)

    if records:
        return f"Total Persons: {records[0]['total_persons']}"
    else:
        return "No persons found."


def get_startups_founded_last_five_years():
    query = "MATCH (s:Startup) WHERE s.year_founded >= date().year - 5 RETURN s.name AS startup, s.year_founded AS year_founded"
    return execute_query(query)


def get_founders_and_startups():
    query = "MATCH (p:Person)-[:FOUNDED]->(s:Startup) RETURN p.name AS person, s.name AS startup"
    return execute_query(query)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def run_query():
    query_type = request.form.get('query_type')
    user_query = request.form.get('user_query')

    if query_type == 'custom':
        result = execute_query(user_query)
    elif query_type == 'all_startups_and_sectors':
        result = get_all_startups_and_sectors()
    elif query_type == 'persons_at_startup':
        startup_name = request.form.get('startup_name')
        result = find_persons_at_startup(startup_name)
    elif query_type == 'startups_in_sector':
        sector_name = request.form.get('sector_name')
        result = find_startups_in_sector(sector_name)
    elif query_type == 'total_startups':
        result = get_total_startups()
    elif query_type == 'most_common_sector':
        result = get_most_common_sector()
    elif query_type == 'total_persons':
        result = get_total_persons()
    elif query_type == 'startups_last_five_years':
        result = get_startups_founded_last_five_years()
    elif query_type == 'founders_and_startups':
        result = get_founders_and_startups()
    else:
        result = "Invalid query type"

    return render_template('result.html', query=user_query, result=result, query_type=query_type)


if __name__ == '__main__':
    app.run(debug=True)
