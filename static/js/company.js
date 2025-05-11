document.querySelectorAll(".tabs button").forEach((button, index) => {
  button.addEventListener("click", () => {
    const sections = document.querySelectorAll(".section");
    if (sections[index]) {
      sections[index].scrollIntoView({ behavior: "smooth" });
    }
  });
});
