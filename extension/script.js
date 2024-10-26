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
  document
    .querySelector("#iframe")
    .setAttribute(
      "src",
      `{{ domain }}/extension/get_customer?username=${encodeURIComponent(
        username
      )}&extension_mode=true`
    );
}

function startObserver() {
  // check for change in focused chat
  const targetNode = document.querySelector("p[data-testid]");
  const callback = (mutationList, _) => {
    for (const mutation of mutationList) {
      if (mutation.type === "characterData") {
        const newUser = mutation.target.data.trim();
        changeUser(newUser);
      }
    }
  };

  const observer = new MutationObserver(callback);
  observer.observe(targetNode, {
    characterData: true,
    attributes: false,
    childList: false,
    subtree: true,
  });
}

window.addEventListener("load", () => {
  GM_addStyle(GM_getResourceText("bt")); // load isolated bootstrap

  // wait for chat interface to load, then grab the username
  const observer = new MutationObserver(function (_, mutationInstance) {
    const someDiv = document.querySelector("p[data-testid]");
    if (someDiv) {
      mutationInstance.disconnect();

      const username = someDiv.innerText.trim();
      addSidebar(); // only load interface after first user appears
      changeUser(username);

      startObserver();
    }
  });

  observer.observe(document, {
    childList: true,
    subtree: true,
  });

  window.addEventListener(
    "message",
    (event) => {
      // console.log("ORIGIN", event.origin);
      // if (event.origin == "https://www.carousell.sg") return;

      if (event.origin == "{{ domain }}") pasteInChat(event.data);
    },
    false
  );
});
