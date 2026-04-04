const home = document.getElementById("home");

home.addEventListener("click", () => {
  window.location.href = "/";
});

const btn = document.getElementById("menuBtn");
const menu = document.getElementById("mobileMenu");

btn.addEventListener("click", () => {
    menu.classList.toggle("hidden");
});


let headlines = [];
const ticker = document.getElementById("updates");

const updateUI = () => {
  ticker.innerHTML = headlines.map(h => 
    `<a href="/news?p=${h.id}" class="mx-4 hover:underline">🔴 ${h.title}</a>`
  ).join(" ");
};

const getHeadlines = () => {
  fetch("http://127.0.0.1:5000/headlines") 
    .then(res => res.json())
    .then(data => {
      headlines = data;
      updateUI(); 
    })
    .catch(err => console.error("Update failed:", err));
};

getHeadlines(); 
setInterval(getHeadlines, 10000);
console.log(headlines)