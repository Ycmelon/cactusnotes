function addSidebar() {
  document.querySelector("main>div>div>div:nth-of-type(3)").remove(); // random spacing

  const sidebar = document.createElement("div");
  sidebar.id = "my-sidebar";
  sidebar.classList.add("bootstrap5");
  sidebar.setAttribute("style", "flex:0.75;padding:10px");

  sidebar.innerHTML = `{{ sidebar }}`;
  document.querySelector("main#main>div>div").append(sidebar);
}

function toggleCondensedView() {
  if (document.querySelector("#condensed-styles") == null) {
    const style = document.createElement("style");
    style.setAttribute("id", "condensed-styles");
    style.innerHTML = "body {background-color: green}";
    document.querySelector("head").append(style);
  } else {
    document.querySelector("#condensed-styles").remove();
  }
}

function pasteInChat(text) {
  const textarea = document.querySelector("textarea");
  const reactPropsKey = Object.keys(textarea)
    .filter((i) => i.startsWith("__reactProps"))
    .at(0);
  textarea[reactPropsKey].onChange({ target: { value: text } });
  textarea.focus();
}

function startObserver() {
  // check for change in focused chat
  const targetNode = document.querySelector("a[href^='/u/']");
  const callback = (mutationList, observer) => {
    for (const mutation of mutationList) {
      if (mutation.type === "attributes" && mutation.attributeName == "href") {
        const newUser = mutation.target.href.split("/").at(-2);
        document.querySelector(
          "#iframe"
        ).src = `http://192.168.1.95:5000/extension/get_customer?username=${encodeURIComponent(
          newUser
        )}`;
      }
    }
  };

  const observer = new MutationObserver(callback);
  observer.observe(targetNode, {
    attributes: true,
    childList: false,
    subtree: false,
  });
}

window.addEventListener("load", () => {
  GM_addStyle(GM_getResourceText("bt")); // load isolated bootstrap
  addSidebar();

  // wait for chat interface to load, then grab the username
  const observer = new MutationObserver(function (mutations, mutationInstance) {
    const someDiv = document.querySelector("a[href^='/u/']");
    if (someDiv) {
      const username = someDiv.href.split("/").at(-2);

      document.querySelector(
        "#iframe"
      ).src = `http://192.168.1.95:5000/extension/get_customer?username=${encodeURIComponent(
        username
      )}`;

      startObserver();
      mutationInstance.disconnect();
    }
  });

  observer.observe(document, {
    childList: true,
    subtree: true,
  });

  window.addEventListener(
    "message",
    (event) => {
      if (event.origin == "https://www.carousell.sg") return;
      pasteInChat(event.data);
    },
    false
  );

  document.querySelectorAll("div.copypasta-card").forEach((card) => {
    card.addEventListener("click", (event) => {
      pasteInChat(card.innerText);
    });
  });
});
