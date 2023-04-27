import json
import os
import numpy as np
from numpy import linalg as LA
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

#data loaded
path= "./static/json"
with open(os.path.join(path, "index_to_vocab.json"), "r") as f1:
    index_to_vocab=json.load(f1)
    print("stage 1")
with open(os.path.join(path,"prof_index_to_name.json"), "r") as f2:
    prof_index_to_name=json.load(f2)
    print("stage 2")
with open(os.path.join(path,"prof_name_to_index.json"), "r") as f3:
    prof_name_to_index=json.load(f3)
    print("stage 3")
with open(os.path.join(path,"tf-idf.json"), "r") as f4:
    tfidf=np.array(json.load(f4))
    print("stage 4")
prof_num, term_num = tfidf.shape

# SELECT professor, \
#     SUM(CASE WHEN overall = -1 THEN 0 ELSE overall END) / SUM(CASE WHEN overall = -1 THEN 0 ELSE 1 END) as avg_overall, \
#     SUM(CASE WHEN difficulty = -1 THEN 0 ELSE difficulty END) / SUM(CASE WHEN difficulty = -1 THEN 0 ELSE 1 END) as avg_difficulty, \
#     SUM(CASE WHEN work = -1 THEN 0 ELSE work END) / SUM(CASE WHEN work = -1 THEN 0 ELSE 1 END) as avg_work \
# FROM reviews \
# WHERE professor IN ( \
#     SELECT prof2 \
#     FROM cossim \
#     WHERE prof1 = '{professor}' \
#     ORDER BY cosine_similarity DESC \
#     LIMIT 5; ) \
# GROUP BY professor \
# ORDER BY ABS(avg_overall - {average_overall}) ASC;


def sql_search(professor):
    professor = professor.lower()
    avg_query = f"""SELECT professor, \
        SUM(CASE WHEN overall = -1 THEN 0 ELSE overall END) / SUM(CASE WHEN overall = -1 THEN 0 ELSE 1 END) as avg_overall, \
        SUM(CASE WHEN difficulty = -1 THEN 0 ELSE difficulty END) / SUM(CASE WHEN difficulty = -1 THEN 0 ELSE 1 END) as avg_difficulty, \
        SUM(CASE WHEN work = -1 THEN 0 ELSE work END) / SUM(CASE WHEN work = -1 THEN 0 ELSE 1 END) as avg_work \
        FROM reviews WHERE professor = '{professor}'"""
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

    alike_query = f"""
    SELECT professor, \
        SUM(CASE WHEN overall = -1 THEN 0 ELSE overall END) / SUM(CASE WHEN overall = -1 THEN 0 ELSE 1 END) as avg_overall, \
        SUM(CASE WHEN difficulty = -1 THEN 0 ELSE difficulty END) / SUM(CASE WHEN difficulty = -1 THEN 0 ELSE 1 END) as avg_difficulty, \
        SUM(CASE WHEN work = -1 THEN 0 ELSE work END) / SUM(CASE WHEN work = -1 THEN 0 ELSE 1 END) as avg_work \
    FROM reviews \
    WHERE professor IN (SELECT prof2 FROM cossim WHERE prof1 = '{professor}') \
    GROUP BY professor \
    ORDER BY ABS(avg_overall - {average_overall}) ASC \
    LIMIT 10; """    
    # WHERE professor <> '{professor}' \
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
        score = fuzz.partial_ratio(input_prof.lower(), prof.lower())
        prof_scores[prof] = score
    sorted_profs = sorted(prof_scores.items(), key=lambda x:x[1], reverse=True)[:5]
    return json.dumps([prof[0] for prof in sorted_profs])

def get_prof_keywords(input_prof):
    prof_id=prof_name_to_index[input_prof]
    term_scores=np.array(tfidf[prof_id])
    term_ids = term_scores.argsort()[::-1][:8]
    prof_vector=[]
    for idx in term_ids:
        prof_vector.append(index_to_vocab[str(idx)])
    return prof_vector

def get_sim(prof1, prof2, input_doc_mat, prof_name_to_index):
    prof1_doc = input_doc_mat[prof_name_to_index[prof1]]
    prof2_doc = input_doc_mat[prof_name_to_index[prof2]]
    dot_product = np.dot(prof1_doc, prof2_doc)
    prof1_norm = LA.norm(prof1_doc)
    prof2_norm = LA.norm(prof2_doc)
    cossim=0
    if prof1_norm!=0 and prof2_norm!=0:
        cossim = dot_product / (prof1_norm * prof2_norm)
    return cossim

def get_similar_profs(input_prof):
    score_arr=[]
    for i in range(prof_num):
        temp=get_sim(input_prof, prof_index_to_name[str(i)],tfidf, prof_name_to_index)
        score_arr.append(temp)
    prof_ids = np.array(score_arr).argsort()[::-1][1:21]
    prof_arr=[]
    prof_score=[]
    for idx in prof_ids:
        prof_arr.append(prof_index_to_name[str(idx)])
        prof_score.append(score_arr[idx])
    print(prof_score)
    return prof_arr,prof_score

def get_professor_data(input_prof):
    data =[]
    prof_arr,prof_score = get_similar_profs(input_prof)
    for i,prof in enumerate(prof_arr):
        prof_kw=get_prof_keywords(prof)
        temp = {
            "professor": prof,
            "keyword":prof_kw,
            "similarity":round(prof_score[i], 3)
        }
        data.append(temp)
    return json.dumps(data)

@app.route("/")
def home():
    return render_template('base.html', title="sample html")

@app.route("/reviews")
def reviews_search():
    text = request.args.get("title")
    # return sql_search(text)
    return get_professor_data(text)

@app.route("/courses")
def courses_search():
    text = request.args.get("title")
    return search_by_course(text)

@app.route("/suggestion")
def suggest_prof():
    text = request.args.get("title")
    return prof_name_suggest(text)

@app.route("/keyword")
def suggest_keyword():
    text = request.args.get("title")
    return get_similar_profs(text)

# app.run(debug=True)
