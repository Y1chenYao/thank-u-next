//init
function init() {
  console.log(document.readyState);
}
window.onload = init();
console.log("Window onload is", window.onload);

// upvotes and downvotes
let votes = new Map();

//template
function answerBoxTemplate(
  name,
  department,
  overall,
  difficulty,
  workload,
  keyword,
  tier,
  similarity,
  course,
  review,
  sentiment
) {
  like_disabled = "";
  dislike_disabled = "";
  up_button = "up.png";
  down_button = "down.png";
  if (votes.has(name)) {
    if (votes.get(name) === 1) {
      like_disabled = "disabled: disabled";
      up_button = "up_clicked.png";
    } else if (votes.get(name) === -1) {
      dislike_disabled = "disabled: disabled";
      down_button = "down_clicked.png";
    }
  }
  return `<div class="flex-box">
      <div class="flex-box result">
        <div class="vote-button-group">
          <button class="vote_button" type="submit" ${like_disabled} onclick="updateRelevance(\'${name}\', 1)" id="like-button-${name}">
            <img src="/static/images/${up_button}" id="thumb-up-${name}" alt="Thumb Up"/>
          </button>
          <button class="vote_button" type="submit" ${dislike_disabled} onclick="updateRelevance(\'${name}\', -1)" id="dislike-button-${name}">
            <img src="/static/images/${down_button}" id="thumb-down-${name}" alt="Thumb Down"/>
          </button>
        </div>
        <div class="left">
          <h3 class="professor-name">${name}</h3>
          <b>Department: </b><br>
          <div class="keyword-box"> ${update_department_list(department)}</div>
          <div class="keyword-box rating-box"><b>Overall: </b><div class="keyword ${overall}">${overall}</div></div>
          <div class="keyword-box rating-box"><b>Difficulty: </b><div class="keyword ${difficulty}">${difficulty}</div></div>
          <div class="keyword-box rating-box"><b>Workload: </b><div class="keyword ${workload}">${workload}</div></div>
          <div class="info"><b>Similarity Score: </b>${similarity}</div>
        </div>
        <div class="right"><b>Past Courses: </b>
          <div class="keyword-box">
            ${update_course_list(course)}
          </div>
          <p class="info"><b>Keywords: </b></p>
          <div class="keyword-box">
            <div class="keyword ${tier[0]}">${keyword[0]}</div>
            <div class="keyword ${tier[1]}">${keyword[1]}</div>
            <div class="keyword ${tier[2]}">${keyword[2]}</div>
            <div class="keyword ${tier[3]}">${keyword[3]}</div>
            <div class="keyword ${tier[4]}">${keyword[4]}</div>
            <div class="keyword ${tier[5]}">${keyword[5]}</div>
            <div class="keyword ${tier[6]}">${keyword[6]}</div>
            <div class="keyword ${tier[7]}">${keyword[7]}</div>
          </div>
          <p class="info"><b>Review, but from an anonymous student 👀</b></p>
          <div class="review">${review}</div>
          <b>Students' sentiment toward this professor's course: </b><br>
          <div class="keyword-box">
            <div class="keyword course-box">${emojize[sentiment[0]]}</div>
            <div class="keyword course-box">${emojize[sentiment[1]]}</div>
            <div class="keyword course-box">${emojize[sentiment[2]]}</div>
          </div>
        </div>
      </div>
    </div>`;
}
function noResultTemplate() {
  answerBox.innerHTML =  `<div>
          <h3>Uh oh, 404 not found</h3>
          <p>No result found under the department filter in the top 30 most similar profs</p>
      </div>`;
}

//consts
const answerBox = document.getElementById("answer-box");
const profInputBox = document.querySelector("#search-professor");
const profSearchBox = document.querySelector("#prof-search-box");
const profAutoBox = document.querySelector("#prof-auto-box");
const courseInputBox = document.querySelector("#search-course");
const courseSearchBox = document.querySelector("#course-search-box");
const courseAutoBox = document.querySelector("#course-auto-box");
const freeInputBox = document.querySelector("#search-free");
const profWeight = document.querySelector("#prof-weight");
const courseWeight = document.querySelector("#course-weight");
const freeWeight = document.querySelector("#free-weight");

//query
function sendQuery() {
  answerBox.innerHTML = "";
  if (
    profInputBox.value != "" ||
    courseInputBox.value != "" ||
    freeInputBox.value != ""
  ) {
    fetch(
      "/reviews?" +
        new URLSearchParams({
          prof: profInputBox.value,
          course: courseInputBox.value,
          free: freeInputBox.value,
          prof_weight: profWeight.value,
          course_weight: courseWeight.value,
          free_weight: freeWeight.value,
          votes: get_vote_param_string(votes),
        }).toString()
    )
      .then((response) => response.json())
      .then((data) =>
        data.filter((v) => checkDepartment(v)))
      .then((data)=> data.length===0 ? noResultTemplate():(
        console.log("debugging"),
        data.forEach((row) => {
          let tempDiv = document.createElement("div");
          tempDiv.innerHTML = answerBoxTemplate(
                row.professor,
                row.department,
                scoreToLevel(row.overall),
                scoreToLevel(row.difficulty),
                scoreToLevel(row.workload),
                row.keyword,
                row.tier,
                row.similarity,
                row.course,
                row.review,
                row.sentiment
              )
          answerBox.appendChild(tempDiv);
        })
      ))
    ;
  }
}

function scoreToLevel(score) {
  if (score < 3) {
    return "Low";
  } else if (score >= 4) {
    return "High";
  } else {
    return "Medium";
  }
}

function get_vote_param_string() {
  s = "";
  for (let [key, value] of votes) {
    if (value != 0) {
      s += "," + key + ":" + value;
    }
  }
  return s.substring(1);
}

function update_like_dislike_list() {
  like_list_string = "";
  dislike_list_string = "";
  for (let [prof, vote] of votes) {
    if (vote === 1) {
      like_list_string += `<div class="keyword course-box"> ${prof} </div>`
    } else if (vote === -1) {
      dislike_list_string += `<div class="keyword course-box"> ${prof} </div>`;
    }
  }
  document.getElementById("like-list").innerHTML = like_list_string;
  document.getElementById("dislike-list").innerHTML = dislike_list_string;
}

function update_department_list(departments){
  html = ""
  for(let c of departments){
    html+=`<div class="keyword course-box"> ${c} </div>`
  }
  return html
}

function update_course_list(courses){
  html = ""
  for(let c of courses){
    html+=`<div class="keyword course-box"> ${c} </div>`
  }
  return html
}

function updateRelevance(name, update) {
  votes.set(name, update);
  if (update === 1) {
    document.getElementById("like-button-" + name).disabled = true;
    document.getElementById("dislike-button-" + name).disabled = false;
    document.getElementById("thumb-up-" + name).src =
      "/static/images/up_clicked.png";
    document.getElementById("thumb-down-" + name).src =
      "/static/images/down.png";
    // document.getElementById("dislike-button-" + name).img = (
    //   <img src="/static/images/up_clicked.png" alt="Thumb Up" />
    // );
  } else if (update === -1) {
    document.getElementById("dislike-button-" + name).disabled = true;
    document.getElementById("like-button-" + name).disabled = false;
    document.getElementById("thumb-up-" + name).src = "/static/images/up.png";
    document.getElementById("thumb-down-" + name).src =
      "/static/images/down_clicked.png";
  }
  update_like_dislike_list();
}

//prof suggestion
function loadProfSuggestion() {
  profInputBox.onkeyup = (e) => {
    let userData = e.target.value;
    let emptyArray = [];
    let allList = [];
    if (userData != "") {
      fetch(
        "/suggestion/prof?" +
          new URLSearchParams({
            title: userData,
          }).toString()
      )
        .then((response) => response.json())
        .then((data) => (emptyArray = data))
        .then(() => {
          (emptyArray = emptyArray.map((i) => {
            return (i = "<li>" + i + "</li>");
          })),
            (profSearchBox.classList.add("active"),
            (profAutoBox.innerHTML = emptyArray.join("")),
            (allList = profAutoBox.querySelectorAll("li")),
            setProfClickable(allList));
        });
    } else {
      profSearchBox.classList.remove("active");
    }
  };
}

function setProfClickable(list) {
  for (let i = 0; i < list.length; i++) {
    list[i].setAttribute("onclick", "selectProf(this)");
  }
}

function selectProf(element) {
  let selectUserData = element.textContent;
  profInputBox.value = selectUserData;
  profSearchBox.classList.remove("active");
}

//course suggestion
function loadCourseSuggestion() {
  courseInputBox.onkeyup = (e) => {
    let userData = e.target.value;
    let emptyArray = [];
    let allList = [];
    if (userData != "") {
      fetch(
        "/suggestion/course?" +
          new URLSearchParams({
            title: userData,
          }).toString()
      )
        .then((response) => response.json())
        .then((data) => (emptyArray = data))
        .then(() => {
          (emptyArray = emptyArray.map((i) => {
            return (i = "<li>" + i + "</li>");
          })),
            (courseSearchBox.classList.add("active"),
            (courseAutoBox.innerHTML = emptyArray.join("")),
            (allList = courseAutoBox.querySelectorAll("li")),
            setCourseClickable(allList));
        });
    } else {
      courseSearchBox.classList.remove("active");
    }
  };
}

function setCourseClickable(list) {
  for (let i = 0; i < list.length; i++) {
    list[i].setAttribute("onclick", "selectCourse(this)");
  }
}

function selectCourse(element) {
  let selectUserData = element.textContent;
  courseInputBox.value = selectUserData;
  courseSearchBox.classList.remove("active");
}

//accordion
const acc = document.getElementsByClassName("accordion");
for (var i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function () {
    this.classList.toggle("active");
    var panel = this.nextElementSibling;
    if (panel.style.display === "block") {
      panel.style.display = "none";
    } else {
      panel.style.display = "block";
    }
  });
}

//department select
//range and approx imported from department.js
const departmentBox = document.querySelector("#department");
function checkDepartment(prof) {
  if (range.includes(departmentBox.value)) {
    const cat = approx[departmentBox.value];
    return prof.department.includes(cat);
  } else {
    return true;
  }
}
