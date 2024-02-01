document.getElementById('menu-btn').addEventListener("click", async function(event) {
  document.querySelector('header').classList.add('_extended');
});


document.querySelectorAll('header div a').forEach((button) => {
  button.addEventListener("click", async function(event) {
    document.querySelector('header').classList.remove('_extended');
  });
});



function showAlert(title, description) {
  element = `<div id="error-container"><h2>${title}</h2><p>${description}</p><button>OK</button></div>`;

  document.body.insertAdjacentHTML('beforeend', element);

  main = document.querySelector('main')
  main.classList.add('_blurred');

  document.querySelector('#error-container button').addEventListener("click", () => {
    main.classList.remove('_blurred');
    document.querySelector('#error-container').remove();
  });
}


async function displaySOS() {
  const response = await fetch("/api/student", {
    method: "GET"
  });

  const responseContent = await response.json();
      
  if (!response.ok) {
    showAlert('Erreur', responseContent.error);
  } else {
    sosSelect = document.getElementById('sos');
    sosList = document.querySelector('ul');

    for (const [idx, _sos] of Object.entries(responseContent)) {
      sosSelect.innerHTML += '<option value="' + idx.toString() + '">' + _sos['name'] + '</option>';
      sosList.innerHTML += '<li><b>' + _sos['name'] + '</b> : ' + _sos['description'] +'</li>';
    }
  }
}

displaySOS()



document.querySelector('form').addEventListener('submit', async function(event){
  event.preventDefault()

  form = document.querySelector('form')

  isValid = form.checkValidity();
  form.reportValidity();

  if (!isValid) return;

  let formData = new FormData(form);

  var object = {};
  formData.forEach((value, key) => {
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

  const responseContent = await response.json();

  if (!response.ok) {
    showAlert('Erreur', responseContent.error);
  } else {
    showAlert('🤌', 'SOS commandé !');

    document.getElementById('confirmation').checked = false;

    //form.reset();
  }
});
