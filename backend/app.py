import json
import os
import numpy as np
from numpy import linalg as LA
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
from fuzzywuzzy import fuzz
from random import sample
import spacy
from spacy.tokenizer import Tokenizer

os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

#deprecate db
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = ""
MYSQL_PORT = 3306
MYSQL_DATABASE = "project"
mysql_engine = MySQLDatabaseHandler(MYSQL_USER, MYSQL_USER_PASSWORD, MYSQL_PORT, MYSQL_DATABASE)
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

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
with open(os.path.join(path,"prof_to_department.json"), "r") as f9:
    prof_to_department=json.load(f9)
with open(os.path.join(path,"prof_scores.json"), "r") as f10:
    prof_scores=json.load(f10)
with open(os.path.join(path,"prof_to_review.json"), "r") as f11:
    prof_to_review=json.load(f11)
with open(os.path.join(path,"course_tfidf.json"), "r") as f12:
    course_tfidf=json.load(f12)
with open(os.path.join(path,"prof_to_sentiment.json"), "r") as f13:
    prof_to_sentiment=json.load(f13)
prof_num, term_num = tfidf.shape

#preparing model and tokens
try:
    spacy.cli.download("en_core_web_md")
    nlp = spacy.load('en_core_web_md')
    token_raw=""
    for k,v in index_to_vocab.items():
        token_raw+=v
        token_raw+=" "
    token_raw=token_raw[:-1]
    tokenizer = Tokenizer(nlp.vocab)
    tokens = tokenizer(token_raw)
except:
    print("failed to load nlp model")

"""
note: functions for edit distance in dropdowns
"""
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

"""
input: any_prof (string of prof), vector (any weight vector with length 932)
output: keyword list with tiers 0 (most relevant),1,2 (least relevant)
"""
def get_prof_keywords(any_prof,vector):
    prof_id=prof_name_to_index[any_prof]
    term_scores=np.array(tfidf[prof_id])
    all_ids = term_scores.argsort()[::-1][:30]
    all_terms = ' '.join([index_to_vocab[str(idx)] for idx in all_ids])
    prof_kw = []
    term_ids = []
    for idx, token in zip(all_ids, nlp(all_terms)):
        if len(prof_kw) < 10:
            if token.pos_ == 'ADJ' or token.pos_ == 'VERB':
                prof_kw.append(index_to_vocab[str(idx)])
                term_ids.append(idx)
        else: break
    
    kw_tier = get_correlation_by_keyword(term_ids,any_prof,vector)
    return prof_kw, kw_tier

#helper function for get_prof_keywords
def get_correlation_by_keyword(term_ids,any_prof,vector):
    prof1_doc = tfidf[prof_name_to_index[any_prof]]
    correlation = np.multiply(prof1_doc,vector)
    kw_score=[]
    for idx in term_ids:
        kw_score.append(correlation[idx])
    kw_rank=np.array(kw_score).argsort()[::-1] #ranking of keyword ids by correlation
    first_third = len(kw_rank)//3
    second_third = len(kw_rank)-len(kw_rank)//3
    first_third_threshold = kw_score[kw_rank[first_third]]
    second_third_threshold = kw_score[kw_rank[second_third]]
    kw_tier=[]
    for score in kw_score:
        if score==0:
            kw_tier.append("low")
        if score<=second_third_threshold:
            kw_tier.append("low")
        elif score<=first_third_threshold:
            kw_tier.append("med")
        else:
            kw_tier.append("high")
    return kw_tier

"""
note: helper function for get_professor_data
input: vector (any weight vector with length 932), exclude_prof (prof in the search bar)
output: prof_arr (array of relevant profs), prof_score (array of similarity scores)
"""
def get_similar_profs(vector,exclude_prof):
    score_arr=[]
    for i in range(prof_num):
        temp=get_sim(vector, prof_index_to_name[str(i)],tfidf, prof_name_to_index)
        score_arr.append(temp)
    prof_ids = np.array(score_arr).argsort()[::-1][:30]
    prof_arr=[]
    prof_score=[]
    for idx in prof_ids:
        cur_prof = prof_index_to_name[str(idx)]
        if cur_prof==exclude_prof: #not sending the prof searched
            continue
        prof_arr.append(cur_prof)
        prof_score.append(score_arr[idx])
    return prof_arr,prof_score
#helper function for get_similar_profs
def get_sim(vector, prof2, input_doc_mat, prof_name_to_index):
    prof2_doc = input_doc_mat[prof_name_to_index[prof2]]
    dot_product = np.dot(vector, prof2_doc)
    vector_norm = LA.norm(vector)
    prof2_norm = LA.norm(prof2_doc)
    cossim=0
    if vector_norm!=0 and prof2_norm!=0:
        cossim = dot_product / (vector_norm * prof2_norm)
    return cossim

"""
input: vector (any weight vector with length 932), exclude_prof (prof in the search bar)
output: json for html
"""
def get_professor_data(vector,exclude_prof):
    data =[]
    prof_arr,prof_score = get_similar_profs(vector,exclude_prof)
    for i,prof in enumerate(prof_arr):
        prof_kw, kw_tier=get_prof_keywords(prof,vector)
        courses = prof_to_course[prof][:4]
        department = prof_to_department[prof]
        temp = {
            "professor": prof,
            "overall": prof_scores[prof][0],
            "difficulty": prof_scores[prof][1],
            "workload": prof_scores[prof][2],
            "department": department,
            "keyword":prof_kw,
            "tier":kw_tier,
            "similarity":round(prof_score[i], 3),
            "course":courses,
            "review": sample(prof_to_review[prof], 1),
            "sentiment":prof_to_sentiment[prof]
        }
        data.append(temp)
    return json.dumps(data)

def get_prof_vec(input_prof):
    prof1_doc = tfidf[prof_name_to_index[input_prof]]
    return prof1_doc

def get_course_vec(input_course):
    course_doc = np.array(course_tfidf[input_course])
    return course_doc

def get_free_search_kw_and_vec(input_keyword):
    scores=[]
    similar_word=nlp(input_keyword)
    for token in tokens:
        scores.append(similar_word.similarity(token))
    indices=np.argsort(scores)[::-1][:30]
    kw_list = []
    vector = np.zeros(932)
    for i in indices:
        kw_list.append(index_to_vocab[str(i)])
        vector[i]=1
    return kw_list, vector

def parse_vote_string(s) -> dict:
    entries = s.split(',')
    vote_dict = dict()
    if entries[0]: # nonempty vote param
        for entry in entries:
            name, vote = entry.split(':')
            vote_dict[name] = vote
    return vote_dict

def clip_np_vector(vector):
    return np.where(vector<0, 0, vector)
    
@app.route("/")
def home():
    return render_template('base.html', title="sample html")

@app.route("/reviews")
def reviews_search():
    prof = request.args.get("prof")
    course = request.args.get("course")
    free = request.args.get("free")

    vote_string = request.args.get("votes")
    vote_dict = parse_vote_string(vote_string)
    likes_update_weight = np.zeros(932)
    dislikes_update_weight = np.zeros(932)
    likes, dislikes = 0, 0
    for p, update in vote_dict.items(): # update is either 1 or -1
        if update == 1:
            likes_update_weight += get_prof_vec(p)
            likes += 1
        else:
            dislikes_update_weight += get_prof_vec(p)
            dislikes += 1
    
    fine_tune_coeff_course = 1.5
    fint_tune_coeff_free = 3
    prof_weight = int(request.args.get("prof_weight"))
    course_weight = int(request.args.get("course_weight"))*fine_tune_coeff_course
    free_weight = int(request.args.get("free_weight"))*fint_tune_coeff_free
    
    total_weight = 0
    total_vector = np.zeros(932)
    if prof!="":
        total_weight+=prof_weight
        total_vector+=get_prof_vec(prof)*prof_weight
    if course!="":
        total_weight+=course_weight
        total_vector+=get_course_vec(course)*course_weight
    if free!="":
        total_weight+=free_weight
        free_kw_list, free_vector = get_free_search_kw_and_vec(free)
        total_vector+=free_vector
    if total_weight == 0:
        return None
    total_vector/=total_weight


    # Rocchio: adjust relevant / irrevelant professor weights
    # _a, _b, _c = 0.55, 0.55, 0.1
    _a, _b, _c = 0.5, 0.2, 0.2

    total_vector = _a * total_vector
    
    #modified rocchio by yichen
    ori_vector = total_vector.copy()
    if likes > 0:
        rel_vector = likes_update_weight / likes
        total_vector += _b * clip_np_vector(rel_vector-ori_vector)
    if dislikes > 0:
        irrel_vector = dislikes_update_weight / dislikes
        total_vector -= _c * clip_np_vector(irrel_vector-ori_vector)
    total_vector = clip_np_vector(total_vector)
    
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
