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
with open(os.path.join(path,"prof_index_to_name.json"), "r") as f2:
    prof_index_to_name=json.load(f2)
with open(os.path.join(path,"prof_name_to_index.json"), "r") as f3:
    prof_name_to_index=json.load(f3)
with open(os.path.join(path,"tf_idf.json"), "r") as f4:
    tfidf=np.array(json.load(f4))
with open(os.path.join(path,"prof_dedup.json"), "r") as f5:
    prof_list=json.load(f5) 
with open(os.path.join(path,"course_dedup.json"), "r") as f6:
    course_list=json.load(f6) 
with open(os.path.join(path,"course_to_prof.json"), "r") as f7:
    course_to_prof=json.load(f7) 
with open(os.path.join(path,"prof_to_course.json"), "r") as f8:
    prof_to_course=json.load(f8)
with open(os.path.join(path,"course_tfidf.json"), "r") as f9:
    course_tfidf=json.load(f9)
prof_num, term_num = tfidf.shape


# def sql_search(professor):
#     professor = professor.lower()
#     avg_query = f"""SELECT professor, \
#         SUM(CASE WHEN overall = -1 THEN 0 ELSE overall END) / SUM(CASE WHEN overall = -1 THEN 0 ELSE 1 END) as avg_overall, \
#         SUM(CASE WHEN difficulty = -1 THEN 0 ELSE difficulty END) / SUM(CASE WHEN difficulty = -1 THEN 0 ELSE 1 END) as avg_difficulty, \
#         SUM(CASE WHEN work = -1 THEN 0 ELSE work END) / SUM(CASE WHEN work = -1 THEN 0 ELSE 1 END) as avg_work \
#         FROM reviews WHERE professor = '{professor}'"""
#     data = mysql_engine.query_selector(avg_query)
#     keys = ["professor", "average_overall",
#             "average_difficulty", "average_work"]
#     data_list = list(data)
#     result_formatted = []
#     if data_list[0][0] is None:
#         return json.dumps([dict()])
#     average_overall = round(data_list[0][1], 2)
#     average_difficulty = round(data_list[0][2], 2)
#     average_work = round(data_list[0][3], 2)
#     print(average_overall)
#     # TODO (future): handle the case where overall, difficulty, work might be -1 for missing data

#     alike_query = f"""
#     SELECT professor, \
#         SUM(CASE WHEN overall = -1 THEN 0 ELSE overall END) / SUM(CASE WHEN overall = -1 THEN 0 ELSE 1 END) as avg_overall, \
#         SUM(CASE WHEN difficulty = -1 THEN 0 ELSE difficulty END) / SUM(CASE WHEN difficulty = -1 THEN 0 ELSE 1 END) as avg_difficulty, \
#         SUM(CASE WHEN work = -1 THEN 0 ELSE work END) / SUM(CASE WHEN work = -1 THEN 0 ELSE 1 END) as avg_work \
#     FROM reviews \
#     WHERE professor IN (SELECT prof2 FROM cossim WHERE prof1 = '{professor}') \
#     GROUP BY professor \
#     ORDER BY ABS(avg_overall - {average_overall}) ASC \
#     LIMIT 10; """    
#     # WHERE professor <> '{professor}' \
#     alike_data = list(mysql_engine.query_selector(alike_query))
#     for result in alike_data:
#         if result[0] is None:
#             break
#         result_formatted.append((result[0], str(round(result[1], 2)), str(
#             round(result[2], 2)), str(round(result[3], 2))))
#     return json.dumps([dict(zip(keys, i)) for i in result_formatted])

def prof_name_suggest(input_prof):
    prof_scores = {}
    for prof in prof_list:
        score = fuzz.partial_ratio(input_prof.lower(), prof.lower())
        prof_scores[prof] = score
    sorted_profs = sorted(prof_scores.items(), key=lambda x:x[1], reverse=True)[:5]
    return json.dumps([prof[0] for prof in sorted_profs])

def course_name_suggest(input_course):
    course_scores = {}
    for course in course_list:
        score = fuzz.partial_ratio(input_course.lower(), course.lower())
        course_scores[course] = score
    sorted_courses = sorted(course_scores.items(), key=lambda x:x[1], reverse=True)[:5]
    return json.dumps([course[0] for course in sorted_courses])

def get_prof_keywords(any_prof,exclude_prof):
    prof_id=prof_name_to_index[any_prof]
    term_scores=np.array(tfidf[prof_id])
    term_ids = term_scores.argsort()[::-1][:8]
    prof_kw=[]
    for idx in term_ids:
        prof_kw.append(index_to_vocab[str(idx)])
    kw_tier = get_correlation_by_keyword(term_ids,any_prof,exclude_prof)
    return prof_kw, kw_tier

def get_correlation_by_keyword(term_ids,any_prof,exclude_prof):
    prof1_doc = tfidf[prof_name_to_index[any_prof]]
    prof2_doc = tfidf[prof_name_to_index[exclude_prof]]
    correlation = np.multiply(prof1_doc,prof2_doc)
    kw_score=[]
    for idx in term_ids:
        kw_score.append(correlation[idx])
    kw_rank=np.array(kw_score).argsort()[::-1] #ranking of keyword ids by correlation
    first_third = len(kw_rank)//3 #0,1,2
    second_third = len(kw_rank)-len(kw_rank)//3 #5,6,7
    first_third_threshold = kw_score[first_third]
    second_third_threshold = kw_score[second_third]
    kw_tier=[]
    for score in kw_score:
        if score>=first_third_threshold:
            kw_tier.append(0)
        elif score>=second_third_threshold:
            kw_tier.append(2)
        else:
            kw_tier.append(1)
    # print(kw_tier)
    return kw_tier

def get_sim(vector, prof2, input_doc_mat, prof_name_to_index):
    prof2_doc = input_doc_mat[prof_name_to_index[prof2]]
    dot_product = np.dot(vector, prof2_doc)
    vector_norm = LA.norm(vector)
    prof2_norm = LA.norm(prof2_doc)
    cossim=0
    if vector_norm!=0 and prof2_norm!=0:
        cossim = dot_product / (vector_norm * prof2_norm)
    return cossim

def get_similar_profs(vector,exclude_prof):
    score_arr=[]
    for i in range(prof_num):
        temp=get_sim(vector, prof_index_to_name[str(i)],tfidf, prof_name_to_index)
        score_arr.append(temp)
    prof_ids = np.array(score_arr).argsort()[::-1][:20]
    prof_arr=[]
    prof_score=[]
    for idx in prof_ids:
        cur_prof = prof_index_to_name[str(idx)]
        if exclude_prof!="" and cur_prof!=exclude_prof: #not sending the prof searched
            prof_arr.append(cur_prof)
            prof_score.append(score_arr[idx])
    return prof_arr,prof_score

def get_professor_data(vector,exclude_prof):
    data =[]
    prof_arr,prof_score = get_similar_profs(vector,exclude_prof)
    for i,prof in enumerate(prof_arr):
        prof_kw, kw_tier=get_prof_keywords(prof,exclude_prof)
        courses = prof_to_course[prof][:4]
        temp = {
            "professor": prof,
            "keyword":prof_kw,
            "tier":kw_tier,
            "similarity":round(prof_score[i], 3),
            "course":courses,
        }
        data.append(temp)
    return json.dumps(data)

def get_prof_vec(input_prof):
    prof1_doc = tfidf[prof_name_to_index[input_prof]]
    return prof1_doc
    
def get_course_vec(input_course):
    course_doc = np.array(course_tfidf[input_course])
    return course_doc

@app.route("/")
def home():
    return render_template('base.html', title="sample html")

@app.route("/reviews")
def reviews_search():
    prof = request.args.get("prof")
    course = request.args.get("course")
    
    fine_tune_coeff = 2
    prof_weight = int(request.args.get("prof_weight"))
    course_weight = int(request.args.get("course_weight"))*fine_tune_coeff
    
    total_weight = 0
    total_vector = np.zeros(932)
    if prof!="":
        total_weight+=prof_weight
        total_vector+=get_prof_vec(prof)*prof_weight
    if course!="":
        total_weight+=course_weight
        total_vector+=get_course_vec(course)*course_weight
    if total_weight == 0:
        return None
    total_vector/=total_weight
    return get_professor_data(total_vector,prof)

@app.route("/suggestion/prof")
def suggest_prof():
    text = request.args.get("title")
    return prof_name_suggest(text)

@app.route("/suggestion/course")
def suggest_course():
    text = request.args.get("title")
    return course_name_suggest(text)

# app.run(debug=True)
