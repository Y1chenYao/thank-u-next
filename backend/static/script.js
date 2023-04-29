//init
function init() {
  console.log(document.readyState);
}
window.onload = init();
console.log("Window onload is", window.onload);

//template
function answerBoxTemplate(name, keyword, tier, similarity, course) {
  console.log(tier)
  return `<div class="flex-box result">
      <div class="left">
        <h3 class="professor-name">${name}</h3>
        <p class="info"><b>Department: </b></p>
        <p class="info"><b>Difficulty: </b></p>
        <p class="info"><b>Workload: </b></p>
      </div>
      <div class="right">
        <p class="info"><b>Past Courses: </b>${course}</p>
        <p class="info"><b>Keywords: </b>${keyword}</p>
        <p class="info"><b>Similarity Score: </b>${similarity}</p>
        <p class="info"><b>Reviews: </b></p>
        <div class="review"></div>
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
      data.forEach((row) => {
        let tempDiv = document.createElement("div");
        tempDiv.innerHTML = row.professor
          ? answerBoxTemplate(
            row.professor,
            // scoreToLevel(row.average_overall),
            // scoreToLevel(row.average_difficulty),
            // scoreToLevel(row.average_workload),
            row.keyword,
            row.tier,
            row.similarity,
            row.course
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
