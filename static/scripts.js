const home = document.getElementById("home");

home.addEventListener("click", () => {
  window.location.href = "/";
})

const btn = document.getElementById("menuBtn");
const menu = document.getElementById("mobileMenu");

btn.addEventListener("click", () => {
    menu.classList.toggle("hidden");
});

const headlines = [
  "Breaking: New policy announced today",
  "Sports: Team wins championship",
  "Tech: New AI model released",
  "World: Major global event happening",
  "Breaking: New policy announced today",
  "Sports: Team wins championship",
  "Tech: New AI model released",
  "World: Major global event happening",
];

const ticker = document.getElementById("updates");
ticker.innerHTML = headlines.map(h => `    🔴 ${h}    `).join(" ");

