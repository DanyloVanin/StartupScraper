# app.py

from flask import Flask, render_template, request
from neo4j_logic.production_model import get_matching_startups_with_scores, does_startup_match_rules

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_matching_startups')
def get_matching_startups_route():
    reputation_threshold = float(request.args.get('reputation_threshold', 4.0))
    matching_startups = get_matching_startups_with_scores(reputation_threshold)

    if matching_startups is not None:
        matching_startups_count = len(matching_startups)
    else:
        matching_startups_count = 0

    return render_template('index.html', startups=matching_startups, startups_count=matching_startups_count,
                           threshold=reputation_threshold)

@app.route('/does_startup_match_rules')
def does_startup_match_rules_route():
    startup_name = request.args.get('startup_name')
    reputation_threshold = float(request.args.get('reputation_threshold', 4.0))

    # Define selected rules based on your criteria
    selected_rules = [
        'tech_skills',
        'founded_before',
        'managing_experience',
        'acceleration_participation',
        'average_sector_reputation',
    ]

    matches_rules = does_startup_match_rules(startup_name, reputation_threshold, selected_rules)

    # Check if matches_rules is not None
    if matches_rules is not None:
        return render_template('index.html', startup_name=startup_name, matches_rules=matches_rules,
                               threshold=reputation_threshold)
    else:
        # Handle the case where matches_rules is None (e.g., startup not found)
        return render_template('index.html', startup_name=startup_name, matches_rules=False,
                               threshold=reputation_threshold)

if __name__ == '__main__':
    app.run(debug=True)
