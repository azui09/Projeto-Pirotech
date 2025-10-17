document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const sidebarToggler = document.getElementById("sidebar-toggle");
  const sidebarTogglerIcon = document.getElementById("sidebar-toggle-icon");
  const sidebarTitle = document.getElementById("sidebar-title");
  const sidebarTexts = document.querySelectorAll("#sidebar-text");
  if (sidebarToggler) {
    sidebarToggler.addEventListener("click", () => {
      sidebar.classList.toggle("w-64");
      sidebar.classList.toggle("w-20");
      sidebarTitle.classList.toggle("hidden");
      sidebarTogglerIcon.classList.toggle("rotate-180");

      sidebarTexts.forEach((text) => {
        text.classList.toggle("hidden");
      });
    });
  }
});
