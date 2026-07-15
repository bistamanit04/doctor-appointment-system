function login() {
  alert("Login Page Coming Soon.");
}

function signin() {
  alert("Sign In Button Clicked.");
}

function scrollDown() {
  const carousel = document.getElementById("carousel");

  carousel.scrollBy({
    left: carousel.clientWidth,
    behavior: "smooth",
  });
}

function scrollUp() {
  const carousel = document.getElementById("carousel");

  carousel.scrollBy({
    left: -carousel.clientWidth,
    behavior: "smooth",
  });
}
