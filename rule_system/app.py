from flask import Flask, render_template, request
from rules.rule_system import check_acceleration_participation, check_average_sector_reputation, \
    check_founded_before, check_managing_experience, check_tech_skills, get_all_startups

app = Flask(__name__)

def evaluate_startup(startup_name):
    rules = {
        'Acceleration Participation': check_acceleration_participation(startup_name),
        'Founded Before': check_founded_before(startup_name),
        'Managing Experience': check_managing_experience(startup_name),
        'Tech Skills': check_tech_skills(startup_name),
        'Average Sector Reputation': check_average_sector_reputation(startup_name)
    }

    total_followed = sum(rules.values())
    should_invest = total_followed > 2

    return rules, total_followed, should_invest

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/all_startups')
def all_startups_route():
    all_startups_list = get_all_startups()

    if all_startups_list is not None:
        all_startups_count = len(all_startups_list)
    else:
        all_startups_count = 0

    return render_template('all_startups.html', all_startups=all_startups_list, all_startups_count=all_startups_count)


@app.route('/evaluate_startup', methods=['POST'])
def evaluate_startup_route():
    if request.method == 'POST':
        startup_name = request.form['startup_name']
        rules_evaluation, total_followed, should_invest = evaluate_startup(startup_name)
        return render_template('result.html', startup_name=startup_name, rules_evaluation=rules_evaluation,
                               total_followed=total_followed, should_invest=should_invest)

if __name__ == '__main__':
    app.run(debug=True)
