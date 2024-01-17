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



document.getElementById("submit").addEventListener("click", function(event){
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
  var json = JSON.stringify(object);


  const xhr = new XMLHttpRequest();

  xhr.open("POST", "http://127.0.0.1:8200/");
  xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");

  xhr.onload = () => {
    console.log(xhr.status);

    if (xhr.status == 200) {
      console.log(JSON.parse(xhr.responseText));
    } else {
      alert('Erreur : ' + JSON.parse(xhr.responseText)['error'])
    }
  };

  console.log(json);
  xhr.send(json);
});
