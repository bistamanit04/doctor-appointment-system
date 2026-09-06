document.addEventListener("DOMContentLoaded", function () {
  /* =========================================
       GET ELEMENTS
    ========================================= */

  const track = document.getElementById("carouselTrack");

  const slides = document.querySelectorAll(".slide");

  const nextButton = document.getElementById("nextBtn");

  const prevButton = document.getElementById("prevBtn");

  const dots = document.querySelectorAll(".dot");

  /* =========================================
       CURRENT SLIDE
    ========================================= */

  let currentSlide = 0;

  /* =========================================
       UPDATE CAROUSEL
    ========================================= */

  function updateCarousel() {
    /*
     * Each slide is 100% width.
     *
     * Slide 0:
     * translateX(0%)
     *
     * Slide 1:
     * translateX(-100%)
     *
     * Slide 2:
     * translateX(-200%)
     *
     * Slide 3:
     * translateX(-300%)
     */

    const position = currentSlide * 100;

    track.style.transform = "translateX(-" + position + "%)";

    /* Update dots */

    dots.forEach(function (dot, index) {
      if (index === currentSlide) {
        dot.classList.add("active");
      } else {
        dot.classList.remove("active");
      }
    });
  }

  /* =========================================
       NEXT BUTTON
    ========================================= */

  nextButton.addEventListener("click", function () {
    console.log("NEXT BUTTON CLICKED");

    currentSlide++;

    if (currentSlide >= slides.length) {
      currentSlide = 0;
    }

    updateCarousel();
  });

  /* =========================================
       PREVIOUS BUTTON
    ========================================= */

  prevButton.addEventListener("click", function () {
    console.log("PREVIOUS BUTTON CLICKED");

    currentSlide--;

    if (currentSlide < 0) {
      currentSlide = slides.length - 1;
    }

    updateCarousel();
  });

  /* =========================================
       DOT BUTTONS
    ========================================= */

  dots.forEach(function (dot) {
    dot.addEventListener("click", function () {
      const slideNumber = Number(dot.getAttribute("data-slide"));

      currentSlide = slideNumber;

      updateCarousel();
    });
  });

  /* =========================================
       LOGIN BUTTON
    ========================================= */

  const loginButton = document.getElementById("loginBtn");

  if (loginButton) {
    loginButton.addEventListener("click", function () {
      window.location.href = "/login";
    });
  }

  /* =========================================
       REGISTER BUTTON
    ========================================= */

  const registerButton = document.getElementById("registerBtn");

  if (registerButton) {
    registerButton.addEventListener("click", function () {
      window.location.href = "/register";
    });
  }

  /* =========================================
       APPOINTMENT BUTTON
    ========================================= */

  const appointmentButton = document.getElementById("appointmentBtn");

  if (appointmentButton) {
    appointmentButton.addEventListener("click", function () {
      window.location.href = "/appointment";
    });
  }

  /* =========================================
       PROFILE BUTTONS
    ========================================= */

  const profileButtons = document.querySelectorAll(".profileBtn");

  profileButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      window.location.href = "/doctors";
    });
  });

  /* =========================================
       KEYBOARD
    ========================================= */

  document.addEventListener("keydown", function (event) {
    if (event.key === "ArrowRight") {
      nextButton.click();
    }

    if (event.key === "ArrowLeft") {
      prevButton.click();
    }
  });

  /* =========================================
       INITIAL STATE
    ========================================= */

  updateCarousel();

  console.log("MedCare carousel initialized successfully");
});
