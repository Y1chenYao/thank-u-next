# Thank-u-next: Cornell Professor Recommender

## Contents

- [Summary](#summary)
- [Demo](#demo)
- [Running Locally](#running-locally)


## Summary
Find your next Cornell professor based on real-world student reviews :star_struck:

You can search by the following metrics :monocle_face:
- Professor that you like
- Course that you like
- Keyword (free search, anything!)
- Filter by department/subject

You will retrieve a list of similar professors recommended to you with :partying_face:
- Professor department
- Professor featuring courses
- Professor overall/difficulty/workload rating
- Cosine similarity score (based on the input)
- Professor keywords extracted from student reviews
- Professor sentiment analysis
- A random sample review from an anonymous student :eyes:

## Demo
Update: Our project is now in [cs4300 hall of fame](https://4300-hall-of-fame.infosci.cornell.edu/)! 

Visit the website [here](http://4300showcase.infosci.cornell.edu:4503/)

<img width="1155" alt="image" src="https://github.com/Y1chenYao/thank-u-next/assets/68068854/30108562-90c7-4e55-a442-451e96d1ea94">


## Running locally

### Step 1: Set up a virtual environment
Create a virtual environment in Python. 
### Step 2: Install dependencies
You need to install dependencies by running `python -m pip install -r requirements.txt` in the backend folder.
### Step 3: Running the app
Uncomment the last line in app.py and run `python app.py` and comment the mysql code.



