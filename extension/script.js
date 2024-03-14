function addSidebar() {
  document.querySelector("main>div>div>div:nth-of-type(3)").remove(); // random spacing

  const sidebar = document.createElement("div");

  sidebar.id = "my-sidebar";
  sidebar.classList.add("bootstrap5");
  sidebar.setAttribute("style", "flex:0.75; overflow-y: hidden;");
  sidebar.innerHTML = `<iframe id="iframe" style="height: 100%; width: 100%; outline: none;">`;

  document.querySelector("main#main>div>div").append(sidebar);
}

// function toggleCondensedView() {
//   if (document.querySelector("#condensed-styles") == null) {
//     const style = document.createElement("style");
//     style.setAttribute("id", "condensed-styles");
//     style.innerHTML = "body {background-color: green}";
//     document.querySelector("head").append(style);
//   } else {
//     document.querySelector("#condensed-styles").remove();
//   }
// }

function pasteInChat(text) {
  const textarea = document.querySelector("textarea");
  const reactPropsKey = Object.keys(textarea)
    .filter((i) => i.startsWith("__reactProps"))
    .at(0);
  textarea[reactPropsKey].onChange({ target: { value: text } });
  textarea.focus();
}

function changeUser(username) {
  document.querySelector(
    "#iframe"
  ).src = `https://cactusnotes.co/extension/get_customer?username=${encodeURIComponent(
    username
  )}&extension_mode=true`;
}

function startObserver() {
  // check for change in focused chat
  const targetNode = document.querySelector("a[href^='/u/']");
  const callback = (mutationList, _) => {
    for (const mutation of mutationList) {
      if (mutation.type === "attributes" && mutation.attributeName == "href") {
        const newUser = mutation.target.href.split("/").at(-2);
        changeUser(newUser);
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

  // wait for chat interface to load, then grab the username
  const observer = new MutationObserver(function (_, mutationInstance) {
    const someDiv = document.querySelector("a[href^='/u/']");
    if (someDiv) {
      const username = someDiv.href.split("/").at(-2);

      addSidebar(); // only load interface after first user appears
      changeUser(username);

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
});
