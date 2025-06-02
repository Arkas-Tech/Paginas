document
.getElementById("scrollToTop")
.addEventListener("click", function () {
  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
});

document.addEventListener("DOMContentLoaded", function () {
    const button = document.querySelector("button");
    const f12 = document.querySelector(".f12");
  
    button.addEventListener("click", function () {
      if (f12.classList.contains("hidden")) {
        f12.classList.remove("hidden");
        f12.style.animation = "slideIn 0.6s ease-out forwards";
      } else {
        f12.style.animation = "slideOut 0.6s ease-out forwards";
        setTimeout(() => {
          f12.classList.add("hidden");
        }, 600);
      }
    });
  });