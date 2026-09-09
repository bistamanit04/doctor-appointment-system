document.addEventListener("DOMContentLoaded", function () {
  wireImagePreview();
  wireAboutCounter();
  wireForm();
});

/*  IMAGE PREVIEW*/

function wireImagePreview() {
  const input = document.getElementById("profile_image");
  const preview = document.getElementById("picPreview");
  const errorEl = document.getElementById("err-image");

  if (!input || !preview) {
    return;
  }

  input.addEventListener("change", function () {
    const file = input.files[0];

    if (!file) {
      return;
    }

    const allowedTypes = ["image/png", "image/jpeg", "image/webp"];

    const maxBytes = 2 * 1024 * 1024;

    /* Check file type */

    if (!allowedTypes.includes(file.type)) {
      errorEl.textContent = "Please choose a JPG, PNG, or WEBP image.";

      errorEl.style.display = "block";

      input.value = "";

      return;
    }

    /* Check file size */

    if (file.size > maxBytes) {
      errorEl.textContent = "Image must be 2MB or smaller.";

      errorEl.style.display = "block";

      input.value = "";

      return;
    }

    /* Clear error */

    errorEl.textContent = "";
    errorEl.style.display = "none";

    /* Preview */

    const reader = new FileReader();

    reader.onload = function (event) {
      preview.src = event.target.result;
    };

    reader.readAsDataURL(file);
  });
}

/* ABOUT CHARACTER COUNTER */

function wireAboutCounter() {
  const textarea = document.getElementById("about");
  const counter = document.getElementById("aboutCount");

  if (!textarea || !counter) {
    return;
  }

  function updateCounter() {
    counter.textContent = textarea.value.length;
  }

  textarea.addEventListener("input", updateCounter);

  updateCounter();
}

/* 
VALIDATION*/

function setRowError(groupId, hasError) {
  const row = document.getElementById(groupId);

  if (row) {
    row.classList.toggle("invalid", hasError);
  }
}

function wireForm() {
  const form = document.getElementById("profileForm");

  if (!form) {
    return;
  }

  form.addEventListener("submit", function (event) {
    const nmc = document.getElementById("nmc_no").value.trim();

    const experience = document.getElementById("experience").value;

    const qualification = document.getElementById("qualification").value.trim();

    const location = document.getElementById("location").value.trim();

    const fee = document.getElementById("consultation_fee").value;

    /* Clear previous errors */

    setRowError("group-nmc", false);

    setRowError("group-experience", false);

    setRowError("group-qualification", false);

    setRowError("group-location", false);

    setRowError("group-fee", false);

    let hasError = false;

    /* NMC */

    if (!nmc) {
      setRowError("group-nmc", true);

      hasError = true;
    }

    /* Experience */

    const expNum = Number(experience);

    if (experience === "" || isNaN(expNum) || expNum < 0 || expNum > 70) {
      setRowError("group-experience", true);

      hasError = true;
    }

    /* Qualification */

    if (!qualification) {
      setRowError("group-qualification", true);

      hasError = true;
    }

    /* Location */

    if (!location) {
      setRowError("group-location", true);

      hasError = true;
    }

    /* Consultation fee */

    const feeNum = Number(fee);

    if (fee === "" || isNaN(feeNum) || feeNum < 0) {
      setRowError("group-fee", true);

      hasError = true;
    }

    /* Stop submission if invalid */

    if (hasError) {
      event.preventDefault();

      return;
    }

    
  });

  /* Remove error when user starts typing */

  form.querySelectorAll("input, textarea, select").forEach(function (element) {
    element.addEventListener("input", function () {
      const row = element.closest(".form-row");

      if (row) {
        row.classList.remove("invalid");
      }
    });
  });
}
