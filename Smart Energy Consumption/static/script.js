document.addEventListener("DOMContentLoaded", function(){

let modes = ["daily","weekly","monthly"]
let index = 0

let changeChart, forecastChart, donutChart, deviceChart

const modeLabel = document.getElementById("modeLabel")

// ================= MODE SWITCH =================
function updateMode(){
    modeLabel.innerText =
    modes[index].charAt(0).toUpperCase() + modes[index].slice(1)

    loadCharts()
    loadKPI()
}

window.nextMode = () => { index=(index+1)%3; updateMode() }
window.prevMode = () => { index=(index-1+3)%3; updateMode() }


// ================= TIME SERIES =================
function loadCharts(){

fetch("/daily?mode="+modes[index])
.then(r=>r.json())
.then(d=>{

if(!d.labels.length) return

if(changeChart) changeChart.destroy()
if(forecastChart) forecastChart.destroy()

// BAR CHART
changeChart = new Chart(change,{
type:"bar",
data:{
labels:d.labels.slice(-2),
datasets:[{
data:d.values.slice(-2),
backgroundColor:"#38bdf8"
}]
},
options:{
plugins:{legend:{display:false}},
scales:{
x:{ticks:{color:"#fff"}},
y:{ticks:{color:"#fff"}}
}
}
})

// FORECAST LINE
let pred = d.values.map(v=>v*1.1)

forecastChart = new Chart(forecast,{
type:"line",
data:{
labels:d.labels,
datasets:[
{
label:"Actual",
data:d.values,
tension:.4,
borderColor:"#38bdf8"
},
{
label:"Predicted",
data:pred,
borderDash:[5,5],
tension:.4,
borderColor:"#f87171"
}
]
},
options:{
plugins:{
legend:{
labels:{
color:"#ffffff",
font:{size:13,weight:"600"}
}
}
},
scales:{
x:{ticks:{color:"#fff"}},
y:{ticks:{color:"#fff"}}
}
}
})

})
}


// ================= DEVICES =================
fetch("/devices")
.then(r => r.json())
.then(d => {

if(donutChart) donutChart.destroy()
if(deviceChart) deviceChart.destroy()

let labels = Object.keys(d)

let dataArray = labels.map(label => ({
label: label,
total: d[label].total_kwh,
percentage: d[label].percentage,
std: d[label].std_dev
})).sort((a,b)=>b.percentage-a.percentage)

let sortedLabels = dataArray.map(d=>d.label)
let sortedPercentages = dataArray.map(d=>d.percentage)
let sortedTotals = dataArray.map(d=>d.total)

highestDevice.innerText =
"Highest Usage: "+sortedLabels[0]+" ("+sortedPercentages[0]+"%)"


// ================= POLAR AREA (FIXED LEGEND) =================
donutChart = new Chart(donut,{
type:"polarArea",
data:{
labels:sortedLabels,
datasets:[{
data:sortedPercentages,
backgroundColor:[
"#ef4444","#f97316","#f59e0b","#eab308",
"#84cc16","#22c55e","#14b8a6","#38bdf8",
"#6366f1","#a855f7","#ec4899"
],
borderWidth:1
}]
},
options:{
responsive:true,
maintainAspectRatio:false,

layout:{
padding:10   // reduce extra empty space
},

plugins:{
legend:{
position:"right",   // 🔥 move legend to side
align:"center",
labels:{
color:"#ffffff",
font:{
size:11,        // 🔥 smaller text
weight:"500"
},
boxWidth:12,    // smaller color box
padding:8
}
},
tooltip:{
backgroundColor:"#111827",
titleColor:"#ffffff",
bodyColor:"#ffffff"
},
datalabels:{
color:"#ffffff",
font:{
weight:"bold",
size:10
},
formatter:(value)=> value + "%"
}
},

scales:{
r:{
ticks:{
display:false   // remove outer numbers like 15
},
grid:{
color:"#334155"
}
}
},

elements:{
arc:{
borderWidth:1
}
}
},
plugins:[ChartDataLabels]
})


// ================= DEVICES BAR CHART (ALSO FIXED) =================
deviceChart = new Chart(devices,{
type:"bar",
data:{
labels:sortedLabels,
datasets:[{
label:"Total kWh",
data:sortedTotals,
backgroundColor:"#38bdf8"
}]
},
options:{
indexAxis:"y",
maintainAspectRatio:false,
plugins:{
legend:{
labels:{
color:"#ffffff",
font:{size:13,weight:"600"}
}
}
},
scales:{
x:{ticks:{color:"#ffffff"}},
y:{ticks:{color:"#ffffff"}}
}
}
})

})


// ================= KPI =================
function loadKPI(){
fetch("/kpi?mode="+modes[index])
.then(r=>r.json())
.then(d=>{
intensity.innerText = d.intensity+" kWh"
carbon.innerText = d.carbon+" kg"
cost.innerText = "₹ "+d.cost.toLocaleString()
})
}


// ================= COST BREAKDOWN + SMART SUGGESTIONS =================
fetch("/device-cost")
.then(r=>r.json())
.then(d=>{

const costContainer = document.getElementById("costList")
const suggestionContainer = document.getElementById("suggestions")

costContainer.innerHTML = ""
suggestionContainer.innerHTML = ""

const tips = {

"Lights": [
"Replace bulbs with energy-efficient LEDs, install motion sensors, switch off when not in use, and maximize daylight usage."
],

"Dishwasher": [
"Run only full loads, use eco mode, avoid heat-dry settings, and clean the filter regularly for better efficiency."
],

"Washing Machine": [
"Wash with cold water, run full loads only, select eco mode, and minimize excessive drying cycles."
],

"Air Conditioning": [
"Set the thermostat to 24–26°C, clean filters monthly, use ceiling fans for airflow, and keep doors and windows closed."
],

"Heater": [
"Use a programmable timer, maintain 18–20°C temperature, improve insulation, and turn off when not required."
],

"Fridge": [
"Maintain 3–5°C temperature, avoid frequent door opening, do not overload, and defrost regularly."
],

"TV": [
"Reduce screen brightness, turn off completely instead of standby mode, and enable power-saving features."
],

"Computer": [
"Enable sleep mode, reduce screen brightness, and shut down completely when not in use."
],

"Microwave": [
"Use appropriate power settings, avoid repeated reheating, and keep the interior clean."
],

"Oven": [
"Avoid unnecessary preheating, turn off a few minutes early, and cook multiple items together to save energy."
]

};

let sortedAll = Object.entries(d)
.sort((a,b)=>b[1].units-a[1].units)


// COST BREAKDOWN
sortedAll.forEach(([name,obj])=>{
let div=document.createElement("div")
div.className="cost-item"
div.innerHTML=`<strong>${name}</strong> → ${obj.units} kWh | ₹ ${obj.cost.toLocaleString()}`
costContainer.appendChild(div)
})


// SMART SUGGESTIONS (TOP 5)
let top5 = sortedAll.slice(0,5)

top5.forEach(([name,obj],index)=>{

let tipList = tips[name] || ["Use efficiently"]
let tip = tipList[Math.floor(Math.random()*tipList.length)]

let levelClass=""
let icon=""
let priority=""

if(index===0){
levelClass="critical"
priority="CRITICAL"
icon="🔥"
}
else if(index<=2){
levelClass="high"
priority="HIGH"
icon="⚠"
}
else{
levelClass="moderate"
priority="MODERATE"
icon="ℹ"
}

let div=document.createElement("div")
div.className=`suggestion-item ${levelClass}`
div.innerHTML=`${icon} <strong>${name}</strong> (${priority}) → ${tip}`
suggestionContainer.appendChild(div)

})

})

updateMode()

})