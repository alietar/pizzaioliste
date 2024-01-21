main = document.querySelector('main');

function lerp(x, y, a) {
  return x * (1 - a) + y * a;
}


let div = document.querySelector('header');
let img = div.querySelector('img');
let h1 = div.querySelector('h1');

let width = window.innerWidth;
let height = window.innerHeight;

window.addEventListener('resize', scrollFunction, true);
window.addEventListener('scroll', scrollFunction, true);
window.addEventListener('load', scrollFunction, true);

function scrollFunction() {
  let coef = window.scrollY / window.innerHeight;

  if (coef > 0.8 && coef < 2) {
    div.classList.add('_scrolled1')
    div.classList.remove('_scrolled2')
  } else if (coef > 2) {
    div.classList.remove('_scrolled1')
    div.classList.add('_scrolled2')
  } else if (coef <= 0.8) {
    div.classList.remove('_scrolled1')
    div.classList.remove('_scrolled2')
  }
} 



async function displaySOS() {
  const response = await fetch("/api/student", {
    method: "GET"
  });

  const availableSOS = await response.json();
    
  console.log("Success:", availableSOS);
      
  if (!response.ok) {
    alert('Erreur')
  } else {
    console.log(availableSOS)

    sosSelect = document.getElementById('sos');

    for (const [idx, name] of Object.entries(availableSOS)) {
      sosSelect.innerHTML += '<option value="' + idx.toString() + '">' + name + '</option>';
    }
  }
}

displaySOS()



document.getElementById("submit").addEventListener("click", async function(event){
  event.preventDefault()

  let formData = new FormData(document.querySelector('form'));

  for (const [key, value] of formData) {
    console.log(`${key}: ${value}\n`);
  }


  var object = {};
  formData.forEach((value, key) => {
      // Reflect.has in favor of: object.hasOwnProperty(key)
      if(!Reflect.has(object, key)){
          object[key] = value;
          return;
      }
      if(!Array.isArray(object[key])){
          object[key] = [object[key]];    
      }
      object[key].push(value);
  });


  const response = await fetch("/api/student", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(object),
  });

  const result = await response.json();
  
  console.log("Success:", result);
    
  if (!response.ok) {
    alert('Erreur')
  }
});
