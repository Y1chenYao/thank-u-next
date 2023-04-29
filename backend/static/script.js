//init
function init() {
  console.log(document.readyState);
}
window.onload = init();
console.log("Window onload is", window.onload);

//template
function answerBoxTemplate(name,
  department,
  overall,
  difficulty,
  workload,
  keyword,
  tier,
  similarity,
  course,
  review) {
  // console.log(tier)
  return `<div class="flex-box">
      <div class="vote-button-group">
        <button type="submit" onclick="updateRelevance()" id="upvote">
          +
        </button>
        <div id="vote-count">0</div>
        <button type="submit" onclick="updateRelevance()" id="downvote">
          -
        </button>
      </div>
      <div class="flex-box result">
        <div class="left">
          <h3 class="professor-name">${name}</h3>
          <p class="info"><b>Department: </b><br>${department}</p>
          <p class="info"><b>Overall: </b>${overall}</p>
          <p class="info"><b>Difficulty: </b>${difficulty}</p>
          <p class="info"><b>Workload: </b>${workload}</p>
        </div>
        <div class="right">
          <p class="info"><b>Past Courses: </b>${course}</p>
          <p class="info"><b>Keywords: </b>${keyword}</p>
          <p class="info"><b>Similarity Score: </b>${similarity}</p>
          <p class="info"><b>Reviews: </b></p>
          <div class="review">${review}</div>
        </div>
      </div>
    </div>`;
}
function noResultTemplate() {
  return `<div class=''>
          <h3 class='professor-name'>No result found.</h3>
      </div>`;
}

//consts
const answerBox = document.getElementById("answer-box")
const profInputBox = document.querySelector("#search-professor")
const profSearchBox = document.querySelector("#prof-search-box")
const profAutoBox = document.querySelector("#prof-auto-box")
const courseInputBox = document.querySelector("#search-course")
const courseSearchBox = document.querySelector("#course-search-box")
const courseAutoBox = document.querySelector("#course-auto-box")

const profWeight = document.querySelector("#prof-weight")
const courseWeight = document.querySelector("#course-weight")

//query
function sendQuery() {
  answerBox.innerHTML = "";
  if (profInputBox.value != "" || courseInputBox.value != "") {
    fetch(
      "/reviews?" +
      new URLSearchParams({
        prof: profInputBox.value,
        course: courseInputBox.value,
        prof_weight: profWeight.value,
        course_weight: courseWeight.value
      }).toString()
    ).then((response) => response.json())
    .then((data) =>
      data.filter(v=>checkDepartment(v)).forEach((row) => {
        let tempDiv = document.createElement("div");
        tempDiv.innerHTML = row.professor
          ? answerBoxTemplate(
            row.professor,
            row.department,
            scoreToLevel(row.overall),
            scoreToLevel(row.difficulty),
            scoreToLevel(row.workload),
            row.keyword,
            row.tier,
            row.similarity,
            row.course,
            row.review
          )
          : noResultTemplate();
        answerBox.appendChild(tempDiv);
      })
    );
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

function updateRelevance() {
  return None;
}

//prof suggestion
function loadProfSuggestion(){
  profInputBox.onkeyup = (e)=>{
    let userData = e.target.value
    let emptyArray = []
    let allList = []
    if(userData!=""){
      fetch(
          "/suggestion/prof?" +
          new URLSearchParams({
            title: userData,
          }).toString()
        ).then((response) => response.json())
        .then((data) =>
          emptyArray = data,
        ).then(()=>{
          emptyArray = emptyArray.map((i)=>{
          return i = "<li>"+i+"</li>"
          }),
          (
            profSearchBox.classList.add("active"),
            profAutoBox.innerHTML = emptyArray.join(''),
            allList = profAutoBox.querySelectorAll("li"),
            setProfClickable(allList)
          )
        }
      );
    }else{
      profSearchBox.classList.remove("active")
    }
  }
  }

function setProfClickable(list){
  for(let i=0;i<list.length;i++){
    list[i].setAttribute("onclick","selectProf(this)")
  }
}

function selectProf(element){
  let selectUserData = element.textContent;
  profInputBox.value=selectUserData;
  profSearchBox.classList.remove("active")
}

//course suggestion
function loadCourseSuggestion(){
  courseInputBox.onkeyup = (e)=>{
    let userData = e.target.value
    let emptyArray = []
    let allList = []
    if(userData!=""){
      fetch(
          "/suggestion/course?" +
          new URLSearchParams({
            title: userData,
          }).toString()
        ).then((response) => response.json())
        .then((data) =>
          emptyArray = data,
        ).then(()=>{
          emptyArray = emptyArray.map((i)=>{
          return i = "<li>"+i+"</li>"
          }),
          (
            courseSearchBox.classList.add("active"),
            courseAutoBox.innerHTML = emptyArray.join(''),
            allList = courseAutoBox.querySelectorAll("li"),
            setCourseClickable(allList)
          )
        }
      );
    }else{
      courseSearchBox.classList.remove("active")
    }
  }
  }

function setCourseClickable(list){
  for(let i=0;i<list.length;i++){
    list[i].setAttribute("onclick","selectCourse(this)")
  }
}

function selectCourse(element){
  let selectUserData = element.textContent;
  courseInputBox.value=selectUserData;
  courseSearchBox.classList.remove("active")
}

//accordion
const acc = document.getElementsByClassName("accordion");
for (var i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
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
const departmentBox = document.querySelector("#department")
function checkDepartment(prof){
  if(range.includes(departmentBox.value)){
    const cat=approx[departmentBox.value]
    return prof.department.includes(cat)
  }else{
    return true
  }
}