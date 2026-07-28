/* SPDX-License-Identifier: AGPL-3.0-or-later */
((_w, d, aperion) => {
  if (aperion.endpoint !== "preferences") {
    return;
  }

  aperion.ready(() => {
    let engine_descriptions = null;

    function load_engine_descriptions() {
      if (engine_descriptions == null) {
        aperion.http("GET", "engine_descriptions.json").then((content) => {
          engine_descriptions = JSON.parse(content);
          for (const [engine_name, description] of Object.entries(engine_descriptions)) {
            const elements = d.querySelectorAll(`[data-engine-name="${engine_name}"] .engine-description`);
            for (const element of elements) {
              const source = ` (<i>${aperion.settings.translations.Source}:&nbsp;${description[1]}</i>)`;
              element.innerHTML = description[0] + source;
            }
          }
        });
      }
    }

    for (const el of d.querySelectorAll("[data-engine-name]")) {
      aperion.on(el, "mouseenter", load_engine_descriptions);
    }

    const enableAllEngines = d.querySelectorAll(".enable-all-engines");
    const disableAllEngines = d.querySelectorAll(".disable-all-engines");
    const engineToggles = d.querySelectorAll("tbody input[type=checkbox][class~=checkbox-onoff]");
    const toggleEngines = (enable) => {
      for (const el of engineToggles) {
        // check if element visible, so that only engines of the current category are modified
        if (el.offsetParent !== null) el.checked = !enable;
      }
    };
    for (const el of enableAllEngines) {
      aperion.on(el, "click", () => toggleEngines(true));
    }
    for (const el of disableAllEngines) {
      aperion.on(el, "click", () => toggleEngines(false));
    }

    const copyHashButton = d.querySelector("#copy-hash");
    aperion.on(copyHashButton, "click", (e) => {
      e.preventDefault();
      navigator.clipboard.writeText(copyHashButton.dataset.hash);
      copyHashButton.innerText = copyHashButton.dataset.copiedText;
    });
  });
})(window, document, window.aperion);
