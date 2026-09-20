document.addEventListener("DOMContentLoaded", function () {
  wireSidebarToggle();

  toggleEmptyStates();

  wireSearch();

  wireConfirmations();

  wireProfileButtons();
});

/* ==============================
   SIDEBAR TOGGLE
   ============================== */

function wireSidebarToggle() {
  const toggle = document.getElementById("menuToggle");

  const sidebar = document.getElementById("sidebar");

  if (toggle && sidebar) {
    toggle.addEventListener("click", function () {
      sidebar.classList.toggle("open");
    });
  }
}

/* ==============================
   EMPTY STATES
   ============================== */

function toggleEmptyStates() {
  const pendingRows = document.querySelectorAll("#pendingTableBody tr");

  const pendingEmpty = document.getElementById("noPending");

  const pendingTable = document.getElementById("pendingTable");

  if (pendingEmpty && pendingTable) {
    const hasPending = pendingRows.length > 0;

    pendingEmpty.style.display = hasPending ? "none" : "block";

    pendingTable.style.display = hasPending ? "table" : "none";
  }

  /* Notification dot */

  const dot = document.getElementById("notifDot");

  if (dot) {
    dot.style.display = pendingRows.length > 0 ? "block" : "none";
  }

  /* Certified doctors */

  const noCertifiedEl = document.getElementById("noCertified");

  if (noCertifiedEl) {
    const table = noCertifiedEl.previousElementSibling;

    if (table && table.tagName === "TABLE") {
      const rows = table.querySelectorAll("tbody tr");

      const hasRows = rows.length > 0;

      noCertifiedEl.style.display = hasRows ? "none" : "block";

      table.style.display = hasRows ? "table" : "none";
    }
  }

  /* Rejected doctors */

  const noRejectedEl = document.getElementById("noRejected");

  if (noRejectedEl) {
    const table = noRejectedEl.previousElementSibling;

    if (table && table.tagName === "TABLE") {
      const rows = table.querySelectorAll("tbody tr");

      const hasRows = rows.length > 0;

      noRejectedEl.style.display = hasRows ? "none" : "block";

      table.style.display = hasRows ? "table" : "none";
    }
  }
}

/* ==============================
   SEARCH
   ============================== */

function wireSearch() {
  const input = document.getElementById("doctorSearch");

  if (!input) {
    return;
  }

  input.addEventListener("input", function () {
    const term = input.value.trim().toLowerCase();

    document.querySelectorAll(".admin-table tbody tr").forEach(function (row) {
      const text = row.textContent.toLowerCase();

      if (text.includes(term)) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  });
}

/* ==============================
   CERTIFY / REJECT CONFIRMATION
   ============================== */

function wireConfirmations() {
  /* Certify */

  document.querySelectorAll(".certify-btn").forEach(function (btn) {
    btn.addEventListener("click", function (event) {
      const confirmed = confirm(
        "Certify this doctor? They will become visible to patients.",
      );

      if (!confirmed) {
        event.preventDefault();
      }
    });
  });

  /* Reject */

  document.querySelectorAll(".reject-btn").forEach(function (btn) {
    btn.addEventListener("click", function (event) {
      const confirmed = confirm("Reject this doctor's registration?");

      if (!confirmed) {
        event.preventDefault();
      }
    });
  });
}

/* ==============================
   DOCTOR PROFILE MODAL
   ============================== */

function wireProfileButtons() {
  const modal = document.getElementById("profileModal");

  const closeButton = document.getElementById("profileModalClose");

  /* Check whether modal exists */

  if (!modal) {
    console.log("Profile modal not found.");

    return;
  }

  /* Find all View Profile buttons */

  const buttons = document.querySelectorAll(".view-doc-btn");

  console.log("Profile buttons found:", buttons.length);

  /* Add click event */

  buttons.forEach(function (button) {
    button.addEventListener("click", function (event) {
      event.preventDefault();

      /* Doctor information */

      const name = button.dataset.name || "Not available";

      const specialization = button.dataset.specialization || "Not available";

      const email = button.dataset.email || "Not available";

      const phone = button.dataset.phone || "Not available";

      const status = button.dataset.status || "Not available";

      const nmc = button.dataset.nmc || "Not available";

      const experience = button.dataset.experience || "0";

      const qualification = button.dataset.qualification || "Not available";

      const location = button.dataset.location || "Not available";

      const about = button.dataset.about || "No information provided.";

      const fee = button.dataset.fee || "0";

      const image = button.dataset.image;

      /* Put information into modal */

      document.getElementById("profileName").textContent = "Dr. " + name;

      document.getElementById("profileSpecialization").textContent =
        specialization;

      document.getElementById("profileStatus").textContent = status;

      document.getElementById("profileNmc").textContent = nmc;

      document.getElementById("profileExperience").textContent =
        experience + " years";

      document.getElementById("profileQualification").textContent =
        qualification;

      document.getElementById("profileEmail").textContent = email;

      document.getElementById("profilePhone").textContent = phone;

      document.getElementById("profileLocation").textContent = location;

      document.getElementById("profileFee").textContent = "Rs. " + fee;

      document.getElementById("profileAbout").textContent = about;

      /* Doctor image */

      const profileImage = document.getElementById("profileImage");

      if (image && image.trim() !== "") {
        profileImage.src = image;
      } else {
        profileImage.src = "/static/img/doctor.jpeg";
      }

      /* Show modal */

      modal.classList.add("show");

      console.log("Profile modal opened for:", name);
    });
  });

  /* ==============================
       CLOSE BUTTON
       ============================== */

  if (closeButton) {
    closeButton.addEventListener("click", function () {
      modal.classList.remove("show");
    });
  }

  /* ==============================
       CLICK OUTSIDE MODAL
       ============================== */

  modal.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.classList.remove("show");
    }
  });

  /* ==============================
       ESCAPE KEY
       ============================== */

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      modal.classList.remove("show");
    }
  });
}
