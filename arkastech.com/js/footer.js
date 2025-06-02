document.addEventListener("DOMContentLoaded", () => {
  const footer = document.getElementById("footer-container");
  if (footer) {
    footer.classList.add("visible");
  }
});

document.addEventListener("scroll", () => {
  const footer = document.getElementById("footer-container");
  const scrollPosition = window.scrollY + window.innerHeight;
  const documentHeight = document.documentElement.scrollHeight;

  // Si el usuario está cerca del final de la página, muestra el footer
  if (scrollPosition >= documentHeight - 400) {
    footer.classList.add("visible");
  } else {
    footer.classList.remove("visible");
  }
});
