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

  console.log(coef);

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
