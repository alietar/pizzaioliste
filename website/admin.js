tableHeaders = document.querySelector('thead tr');
tableBody = document.querySelector('tbody');


async function gatherSOS() {
  const response = await fetch("/api/admin", {
    method: "GET",
    headers: {
      "Credential": "pwd"
    },
  });
  
  if (!response.ok) {
    alert('Erreur')
    return
  }

  const SOS = await response.json();
      
  displayTable(SOS);
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
