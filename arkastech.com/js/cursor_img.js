document.addEventListener("DOMContentLoaded", () => {
  // Crear el elemento de imagen para el cursor
  const cursorImg = document.createElement("img");
  cursorImg.classList.add("cursor-img");
  document.body.appendChild(cursorImg);

  // Seleccionar todas las filas <tr> de la tabla
  const rows = document.querySelectorAll(".solutions-table tr");

  rows.forEach((row) => {
    row.addEventListener("mouseenter", (e) => {
      const imageUrl = row.querySelector("td").getAttribute("data-image");
      if (imageUrl) {
        cursorImg.src = `static/soluciones/${imageUrl}.png`; // Ruta de la imagen
        cursorImg.style.display = "block";
      }
    });

    row.addEventListener("mousemove", (e) => {
      cursorImg.style.left = `${e.pageX}px`;
      cursorImg.style.top = `${e.pageY}px`;
    });

    row.addEventListener("mouseleave", () => {
      cursorImg.style.display = "none";
    });
  });
});
