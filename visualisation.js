//all of the created visualisations and their respective container ID used in the index.html
// and their respective .vg.json files
const visualisations = [
  { container: "#energy-waffle", specification: "daily_energy_waffle.vg.json" },
  { container: "#macro-deviation", specification: "macronutrient_age_deviation.vg.json" },
  { container: "#nutrient-ridgeline", specification: "food_category_nutrient_ridgeline.vg.json" },
  { container: "#supplement-pictogram", specification: "supplement_use_life_course_pictogram.vg.json" },
  { container: "#beverage-dumbbell", specification: "beverage_consumption_dumbbell.vg.json" },
  { container: "#kids-sugar-heatmap", specification: "kids_prevelance_of_sugar_drink_heatmap.vg.json" },
  { container: "#adult-sugar-heatmap", specification: "adults_prevelance_of_sugar_drink_heatmap.vg.json" },
  { container: "#intake-bullets", specification: "male_female_intake_bullets.vg.json" },
  { container: "#food-security-income", specification: "food_security_income.vg.json" },
  { container: "#discretionary-map", specification: "discret_vs_nondiscret.vg.json" },
  { container: "#sodium-map", specification: "sodium_graduated_symbol.vg.json" },
  { container: "#potassium-map", specification: "potassium_graduated_symbol.vg.json" },
  { container: "#health-cartograms", specification: "health_risk_condition_contiguous_cartograms.vg.json" }
];

//a  set to keep track of already loaded charts so that the browser doesnt load them multiple times
const loadedVisualisations = new Set();

/**
 * 
 * Helper function that updates the outer <div class="chart-frame" wrapper
 * once a chart finishes loading or fails
 */
function setFrameState(container, state) {
  //finds outer box wrapping the chart
  const frame = container.closest(".chart-frame");
  if (!frame) {
    return;
  }

  //tells css its done loading
  frame.setAttribute("aria-busy", "false");
  //add css class to the outer box, essentially giving CSS green light to 
  // display it once its done loading
  frame.classList.add(state);
}

/*
* helper function to prevent page from failing if theres an error, and will just show an error
* for that section
*/
function showChartError(container, specification, error) {
  //markts the outer frame state as has error, so css will handle the error stylinh
  setFrameState(container, "has-error");
  container.innerHTML = `
    <div class="chart-error" role="alert">
      <strong>This chart could not be loaded.</strong>
      <span>Check that <code>${specification}</code> and its data files are available.</span>
    </div>
  `;
  console.error(`Unable to embed ${specification}`, error);
}

/**
 * the chart builder function
 * @param {*} visualisation to be built
 * @returns 
 */
function embedVisualisation(visualisation) {
  //checks and stops if chart has already been loaded
  if (loadedVisualisations.has(visualisation.container)) {
    return;
  }

  //uses document.querySelector to find the <div id="..."> in the html for this specific vis
  const container = document.querySelector(visualisation.container);
  if (!container) {
    console.warn(`Missing chart container: ${visualisation.container}`);
    return;
  }

  //vis has been loaded, can add it to the checklist
  loadedVisualisations.add(visualisation.container);

  //safety check if the vega embed library from the internet loaded correctly
  if (typeof window.vegaEmbed !== "function") {
    showChartError(container, visualisation.specification, new Error("Vega-Embed is unavailable."));
    return;
  }

  //tells vega  to put the chart inside visu.container using the vis.specification 
  // file with a few visual settings
  window.vegaEmbed(visualisation.container, visualisation.specification, {
    actions: false, // hides the "..." button vega puts in the corner
    renderer: "svg", //draw it using svg fr better clarity
    tooltip: { theme: "light" } //light coloured pop up box
  })
    //marks the state as is ready for the CSS to do its thing
    .then(() => setFrameState(container, "is-ready"))
    .catch((error) => showChartError(container, visualisation.specification, error));
}

const visualisationByFrame = new Map();

// loop through the entire visualisation JavaScript array
visualisations.forEach((visualisation) => {
  //gets the container of each visualisation
  //and searches the dom built by the index.html for the container of the current vis
  const container = document.querySelector(visualisation.container);
  //throw an error if none found for a vis in the DOM
  if (!container) {
    console.warn(`Missing chart container: ${visualisation.container}`);
    return;
  }

  //once it find the container of the vis, it looks for the defined chart frame in the DOM/html
  const frame = container.closest(".chart-frame") || container;
  // map this specific chart frame container found near this visualisations id/cont to its specification
  visualisationByFrame.set(frame, visualisation);
});

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        const visualisation = visualisationByFrame.get(entry.target);
        if (visualisation) {
          embedVisualisation(visualisation);
        }
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "700px 0px", threshold: 0.01 }
  );

  visualisationByFrame.forEach((_visualisation, frame) => observer.observe(frame));
} else {
  visualisations.forEach(embedVisualisation);
}

window.addEventListener("beforeprint", () => {
  visualisations.forEach(embedVisualisation);
});
