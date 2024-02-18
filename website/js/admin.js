tableHeaders = document.querySelector('thead tr');
tableBody = document.querySelector('tbody');

let SOS = {}

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

  SOS = await response.json();
      
  displayTable(SOS, ["0", "0", "0", "0"]);
}


function displayTable(content, filter) {
  format = content['format']
  sos = content['sos']

  tableHeaders.innerHTML = "";
  tableBody.innerHTML = "";

  format.forEach((title) => {
    columnHeader = document.createElement("th");
    columnHeader.innerHTML = title;
    tableHeaders.appendChild(columnHeader);
  });
    
  filterButton = document.createElement("th");
  filterButton.innerHTML = `<a id="filter-btn"><span class="material-symbols-outlined">filter_alt</span></a>`;
  tableHeaders.appendChild(filterButton);

  document.getElementById('filter-btn').addEventListener('click', function() {
    document.getElementById('filter-container').classList.toggle('_hidden');
  });
  
  sos.forEach((row) => {
    // day
    if (filter[0] !== "0") {
      if (row[7].charAt(0) !== filter[0]) {
        return
      }
    }
    
    // timeslot
    if (filter[1] !== "0") {
      if (row[7].charAt(2) !== filter[1]) {
        return
      }
    }
    
    // bat
    if (filter[2] !== "0") {
      if (row[8] !== filter[2]) {
        return
      }
    }
    
    // floor
    if (filter[3] !== "0") {
      if (row[9].toString().charAt(0) !== filter[3]) {
        return
      }
    }

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
        day = parseInt(text.charAt(0)) - 1;
        hour = parseInt(text.charAt(2)) - 1;

        dayName = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"][day];
        hourName = ["7h-8h", "12h-14h", "18h-21h"][hour];
        
        cell.innerHTML = dayName + ' ' + hourName;
      } else {
        cell.innerHTML = text;
      }

      rowElement.appendChild(cell);
    });
      
    rowElement.appendChild(document.createElement("td"));

    tableBody.appendChild(rowElement);
  });
}


gatherSOS();


document.querySelector('form').addEventListener('submit', async function(event){
  event.preventDefault()

  form = document.querySelector('form')
  let formData = new FormData(form);
  
  displayTable(SOS, [formData.get('day'), formData.get('hour'), formData.get('bat'), formData.get('floor')]);

  document.querySelector('form').classList.add('_hidden');
});
