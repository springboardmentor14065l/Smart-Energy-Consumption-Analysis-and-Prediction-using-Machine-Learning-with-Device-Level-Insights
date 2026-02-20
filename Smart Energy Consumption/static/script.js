document.addEventListener("DOMContentLoaded", function(){

let modes=["daily","weekly","monthly"]
let index=0

let changeChart,forecastChart,donutChart,deviceChart


function updateMode(){
modeLabel.innerText=modes[index].charAt(0).toUpperCase()+modes[index].slice(1)
loadCharts()
loadKPI()
}

window.nextMode=()=>{index=(index+1)%3;updateMode()}
window.prevMode=()=>{index=(index-1+3)%3;updateMode()}


// charts
function loadCharts(){

fetch("/daily?mode="+modes[index])
.then(r=>r.json())
.then(d=>{

if(!d.labels.length) return

if(changeChart) changeChart.destroy()
if(forecastChart) forecastChart.destroy()

changeChart=new Chart(change,{
type:"bar",
data:{labels:d.labels.slice(-2),datasets:[{data:d.values.slice(-2)}]}
})

let pred=d.values.map(v=>v*1.1)

forecastChart=new Chart(forecast,{
type:"line",
data:{labels:d.labels,
datasets:[{data:d.values,tension:.4},{data:pred,borderDash:[5,5],tension:.4}]}
})
})
}


// devices
fetch("/devices")
.then(r => r.json())
.then(d => {

let labels = Object.keys(d)
let values = Object.values(d)

highestDevice.innerText = "Highest Usage: " + 
labels[values.indexOf(Math.max(...values))]

/* ===== DONUT CHART ===== */
donutChart = new Chart(donut, {
    type: "doughnut",
    data: {
        labels: labels,
        datasets: [{
            data: values,
            backgroundColor: [
                "#38bdf8",  // blue
                "#f87171",  // red
                "#fbbf24",  // yellow
                "#34d399",  // green
                "#a78bfa",  // purple
                "#fb923c",  // orange
                "#60a5fa",  // light blue
                "#f472b6",  // pink
                "#22c55e",  // emerald
                "#c084fc"   // violet
            ],
            borderWidth: 2,
            borderColor: "#1f2a3a"
        }]
    },
    options: {
        plugins: {
            legend: {
                position: "top",
                labels: {
                    color: "#e2e8f0",   // 🔥 Appliance name color (clear & sharp)
                    font: {
                        size: 13,
                        weight: "600"
                    },
                    padding: 15
                }
            }
        }
    }
})

/* ===== BAR CHART ===== */
deviceChart = new Chart(devices, {
    type: "bar",
    data: {
        labels: labels,
        datasets: [{
            data: values,
            backgroundColor: "#38bdf8",
            barThickness: 16,          // thinner bars
            categoryPercentage: 0.7,   // spacing control
            barPercentage: 0.8
        }]
    },
    options: {
        indexAxis: "y",
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
                ticks: { color: "#e2e8f0" },
                grid: { color: "#2c3e50" }
            },
            y: {
                ticks: { 
                    color: "#e2e8f0",
                    font: { size: 12 }   // smaller device labels
                },
                grid: { display: false }
            }
        }
    }
})

})


// KPI
function loadKPI(){
fetch("/kpi?mode="+modes[index])
.then(r=>r.json())
.then(d=>{
intensity.innerText=d.intensity+" kWh"
carbon.innerText=d.carbon+" kg"
cost.innerText="₹ "+d.cost.toLocaleString()
})
}


// cost + smart suggestions
fetch("/device-cost")
.then(r=>r.json())
.then(d=>{

costList.innerHTML=""
suggestions.innerHTML=""

const tips={
"Air Conditioning":["Use only when temperature is high","Keep doors closed while AC is running","Set temperature to 24°C"],
"Heater":["Turn off after room warms","Use timer instead of continuous"],
"Lights":["Switch off when leaving room","Use daylight"],
"Fridge":["Avoid frequent opening","Don't store hot food"],
"Washing Machine":["Run only full load","Use eco mode"],
"TV":["Turn off instead of standby","Reduce brightness"],
"Computer":["Enable power saver","Shutdown when idle"]
}

let sorted=Object.entries(d).sort((a,b)=>b[1].units-a[1].units)

sorted.forEach(([name,obj],index)=>{

let li=document.createElement("li")
li.innerText=`${name} → ${obj.units} kWh | ₹ ${obj.cost}`
costList.appendChild(li)

let tipList=tips[name]||["Use efficiently"]
let tip=tipList[Math.floor(Math.random()*tipList.length)]

let msg=""

if(index===0)
msg=`${name}: Highest consumer ⚡ — ${tip}`
else if(index<sorted.length*0.3)
msg=`${name}: High usage — ${tip}`
else if(index<sorted.length*0.7)
msg=`${name}: Normal usage — ${tip}`
else
msg=`${name}: Efficient ✔ — ${tip}`

let s=document.createElement("li")
s.innerText=msg
suggestions.appendChild(s)

})

})

updateMode()

})
