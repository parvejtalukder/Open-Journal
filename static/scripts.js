const home = document.getElementById("home");

home.addEventListener("click", () => {
  window.location.href = "/";
});

const btn = document.getElementById("menuBtn");
const menu = document.getElementById("mobileMenu");

btn.addEventListener("click", () => {
    menu.classList.toggle("hidden");
});

const notice = document.getElementById("flash-message");
const dashba = document.getElementById("notice_dash");
if (notice) {
    notice.classList.remove("hidden");
    setTimeout(() => {
        notice.classList.add("opacity-0", "transition", "duration-1000");
        setTimeout(() => {
            notice.classList.add("hidden");
            notice.classList.remove("opacity-0", "transition", "duration-1000");
        }, 1000); 
    }, 3000);
}

if (dashba) {
  dashba.classList.remove("hidden");
  setTimeout(() => {
    notice.classList.add("opacity-0", "transition", "duration-1000");
    setTimeout(() => {
      notice.classList.add("hidden");
      notice.classList.remove("opacity-0", "transition", "duration-1000");
    }, 1000)
  }, 3000)
}

let headlines = [];
const ticker = document.getElementById("updates");

const updateUI = () => {
  ticker.innerHTML = headlines.map(h => 
    `<a href="/news?p=${h.id}" class="mx-4 hover:underline">🔴 ${h.title}</a>`
  ).join(" ");
};

const getHeadlines = () => {
  fetch("http://localhost:5000/headlines") 
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