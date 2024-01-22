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
    
    row.forEach((text, i) => {
      cell = document.createElement("td");
      
      if (i === 1) {
        date = new Date(text);

        day = date.getDate();
        month = date.getMonth() + 1;
        hour = date.getHours();
        minute = date.getMinutes();

        cell.innerHTML = day + '/' + month + ' ' + hour + 'h' + minute;
      } else if (i === 7) {
        date = new Date(text);

        day = date.getDay();
        dayName = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"][day];
        hour = date.getHours();
        minute = date.getMinutes();

        cell.innerHTML = dayName + ' ' + hour + 'h' + minute;

      } else {
        cell.innerHTML = text;
      }

      rowElement.appendChild(cell);
    });

    tableBody.appendChild(rowElement);
  });
}


gatherSOS();
