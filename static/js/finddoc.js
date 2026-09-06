(function () {
  const searchInput = document.getElementById("searchInput");
  const chips = document.querySelectorAll(".chip");
  const cards = document.querySelectorAll(".doctor-card");
  const resultsCount = document.getElementById("resultsCount");
  const noResults = document.getElementById("noResults");

  let activeFilter = "all";

  function applyFilters() {
    const query = searchInput.value.trim().toLowerCase();
    let visibleCount = 0;

    cards.forEach((card) => {
      const name = card.getAttribute("data-name").toLowerCase();
      const specialty = card.getAttribute("data-specialty").toLowerCase();

      const matchesFilter =
        activeFilter === "all" ||
        card.getAttribute("data-specialty") === activeFilter;
      const matchesQuery =
        !query || name.includes(query) || specialty.includes(query);

      const visible = matchesFilter && matchesQuery;
      card.classList.toggle("hidden", !visible);
      if (visible) visibleCount++;
    });

    resultsCount.textContent = `${visibleCount} doctor${visibleCount === 1 ? "" : "s"} available`;
    noResults.classList.toggle("show", visibleCount === 0);
  }

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      activeFilter = chip.getAttribute("data-filter");
      applyFilters();
    });
  });

  searchInput.addEventListener("input", applyFilters);

  applyFilters();
})();
