tableHeaders = document.querySelector('thead tr');
tableBody = document.querySelector('tbody');


function gatherSOS() {
  const xhr = new XMLHttpRequest();
  xhr.open("GET", "http://127.0.0.1:8100/");
  xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
  xhr.setRequestHeader("Credential", "pwd");

  xhr.onload = () => {
    console.log(xhr.status);
    if (xhr.status == 200) {
      json = JSON.parse(xhr.responseText);

      console.log(json);

      displayTable(json);
    } else {
      alert('Erreur : ' + JSON.parse(xhr.responseText)['error'])
    }
  };

  xhr.send();
}


function displayTable(content) {
  format = content['format']
  sos = content['sos']

  format.forEach((title) => {
    columnHeader = document.createElement("th");
    columnHeader.innerHTML = title;
    tableHeaders.appendChild(columnHeader);
  });
  
  sos.forEach((row) => {
    rowElement = document.createElement('tr');

    row.forEach((text) => {
      cell = document.createElement("td");
      cell.innerHTML = text;
      rowElement.appendChild(cell);
    });

    tableBody.appendChild(rowElement);
  });
}


gatherSOS();
