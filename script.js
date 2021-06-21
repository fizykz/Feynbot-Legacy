//Scroll Anim
ScrollReveal().reveal("nav h1", { distance: "10px", duration: 1000 });
ScrollReveal().reveal(".prompt button", { distance: "10px", delay: 1000 });

// Init vars
var player;
var tag = document.createElement("script");
tag.id = "iframe-demo";
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName("script")[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
prompt = document.querySelector(".prompt");
text = document.querySelector(".verifyingText");
vid = document.querySelector("#videoFrame");
const urlParams = new URLSearchParams(window.location.search);
const verifyCode = urlParams.get("verificationCode");
document.getElementById("instructions").textContent = ">verify " + verifyCode;

function onYouTubeIframeAPIReady() {
  player = new YT.Player("videoFrame", {
    events: {},
  });
}

// On Button Click, user is shown the youtube video. During that a http request is sent to the discord bot which returns a code that you can type in the server.
prompt.addEventListener("click", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const verifyCode = urlParams.get("verificationCode");

  player.seekTo(0);
  player.unMute();
  prompt.classList.add("hidden");
  text.classList.remove("hidden");
  vid.classList.remove("hidden");

  if (verifyCode) {
    request = new XMLHttpRequest();
    request.open(
      "GET",
      "http://99.197.208.116:5000/api/verify/" + verifyCode,
      false
    );
    console.log(verifyCode);
    request.send();
    console.log("end");
  }

  // POST
});

function onClick(event) {
  event.target.unMute();
}
