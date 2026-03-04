document.getElementById("form").addEventListener("submit", async function(e){

e.preventDefault()

const data = {

account: document.getElementById("account").value,

transactions: [

{
amount: parseInt(document.getElementById("amount1").value),
location: document.getElementById("loc1").value
},

{
amount: parseInt(document.getElementById("amount2").value),
location: document.getElementById("loc2").value
},

{
amount: parseInt(document.getElementById("amount3").value),
location: document.getElementById("loc3").value
}

],

time_interval: parseInt(document.getElementById("interval").value)

}

const response = await fetch("http://localhost:8000/analyze",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body: JSON.stringify(data)

})

const result = await response.json()

localStorage.setItem("fraudResult", JSON.stringify(result))

window.location.href = "result.html"

})