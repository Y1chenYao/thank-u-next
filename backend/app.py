import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
from fuzzywuzzy import fuzz

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = "MayankRao16Cornell.edu"
MYSQL_PORT = 3306
MYSQL_DATABASE = "project"

mysql_engine = MySQLDatabaseHandler(MYSQL_USER, MYSQL_USER_PASSWORD, MYSQL_PORT, MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

# Sample search, the LIKE operator in this case is hard-coded,
# but if you decide to use SQLAlchemy ORM framework,
# there's a much better and cleaner way to do this


def sql_search(professor):
    professor = professor.lower()
    avg_query = f"""SELECT professor, AVG(overall), AVG(difficulty), AVG(work) FROM reviews WHERE professor = '{professor}'"""
    data = mysql_engine.query_selector(avg_query)
    keys = ["professor", "average_overall",
            "average_difficulty", "average_work"]
    data_list = list(data)
    result_formatted = []
    if data_list[0][0] is None:
        return json.dumps([dict()])
    average_overall = round(data_list[0][1], 2)
    average_difficulty = round(data_list[0][2], 2)
    average_work = round(data_list[0][3], 2)
    print(average_overall)
    # TODO (future): handle the case where overall, difficulty, work might be -1 for missing data
    alike_query = f"""SELECT professor, AVG(overall), AVG(difficulty), AVG(work) \
                    FROM reviews \
                    WHERE professor <> '{professor}' \
                    GROUP BY professor \
                    HAVING ABS(AVG(overall) - {average_overall}) < 0.3 \
                        AND ABS(AVG(difficulty) - {average_difficulty}) < 0.3 \
                        AND ABS(AVG(work) - {average_work}) < 0.3 \
                    ORDER BY ABS(AVG(overall) - {average_overall}) ASC;
                    """
    alike_data = list(mysql_engine.query_selector(alike_query))
    for result in alike_data:
        if result[0] is None:
            break
        result_formatted.append((result[0], str(round(result[1], 2)), str(
            round(result[2], 2)), str(round(result[3], 2))))
    return json.dumps([dict(zip(keys, i)) for i in result_formatted])

def search_by_course(course):
    '''
    return json of professor names similar to professor that teach the same course
    '''
    # course = course_name.lower()
    avg_query = f"""SELECT professor, AVG(overall), AVG(difficulty), AVG(work) FROM reviews WHERE course = '{course}'"""
    data = mysql_engine.query_selector(avg_query)
    keys = ["professor", "average_overall",
            "average_difficulty", "average_work"]
    data_list = list(set(data))
    result_formatted = []
    if data_list[0][0] is None:
        return json.dumps([dict()])
    average_overall = round(data_list[0][1], 2)
    average_difficulty = round(data_list[0][2], 2)
    average_work = round(data_list[0][3], 2)
    print(average_overall)
    alike_query = f"""SELECT professor, AVG(overall), AVG(difficulty), AVG(work) \
                    FROM reviews \
                    GROUP BY professor \
                    HAVING ABS(AVG(overall) - {average_overall}) < 0.3 \
                        AND ABS(AVG(difficulty) - {average_difficulty}) < 0.3 \
                        AND ABS(AVG(work) - {average_work}) < 0.3 \
                    ORDER BY ABS(AVG(overall) - {average_overall}) ASC;
                    """
    alike_data = list(mysql_engine.query_selector(alike_query))
    for result in alike_data:
        if result[0] is None:
            break
        result_formatted.append((result[0], str(round(result[1], 2)), str(
            round(result[2], 2)), str(round(result[3], 2))))
    return json.dumps([dict(zip(keys, i)) for i in result_formatted])

def prof_name_suggest(input_prof):
    data_path = "./static/json"
    file_path = "prof_dedup.json"
    with open(os.path.join(data_path, file_path), "r") as f:
        data=json.load(f)
    prof_scores = {}
    for prof in data["prof_name_list"]:
        score = fuzz.token_sort_ratio(input_prof.lower(), prof.lower())
        prof_scores[prof] = score
    sorted_profs = sorted(prof_scores.items(), key=lambda x:x[1], reverse=True)[:5]
    return json.dumps([prof[0] for prof in sorted_profs])

@app.route("/")
def home():
    return render_template('base.html', title="sample html")


@app.route("/reviews")
def reviews_search():
    text = request.args.get("title")
    return sql_search(text)

@app.route("/courses")
def courses_search():
    text = request.args.get("title")
    return search_by_course(text)

@app.route("/suggestion")
def suggest_prof():
    text = request.args.get("title")
    return prof_name_suggest(text)

# app.run(debug=True)
