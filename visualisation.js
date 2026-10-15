const visualisations = [
  { container: "#energy-waffle", specification: "daily_energy_waffle.vg.json" },
  { container: "#macro-parallel", specification: "macronutrient_parallel_coordinates.vg.json" },
  { container: "#nutrient-ridgeline", specification: "food_category_nutrient_ridgeline.vg.json" },
  { container: "#supplement-pictogram", specification: "supplement_use_life_course_pictogram.vg.json" },
  { container: "#beverage-dumbbell", specification: "beverage_consumption_dumbbell.vg.json" },
  { container: "#kids-sugar-heatmap", specification: "kids_prevelance_of_sugar_drink_heatmap.vg.json" },
  { container: "#adult-sugar-heatmap", specification: "adults_prevelance_of_sugar_drink_heatmap.vg.json" },
  { container: "#intake-bullets", specification: "male_female_intake_bullets.vg.json" },
  { container: "#food-security-income", specification: "food_security_income.vg.json" },
  { container: "#discretionary-map", specification: "discret_vs_nondiscret.vg.json" },
  { container: "#sodium-potassium-map", specification: "sodium_potassium_graduated_symbol.vg.json" },
  { container: "#health-cartograms", specification: "health_risk_condition_contiguous_cartograms.vg.json" }
];

const loadedVisualisations = new Set();

function setFrameState(container, state) {
  const frame = container.closest(".chart-frame");
  if (!frame) {
    return;
  }

  frame.setAttribute("aria-busy", "false");
  frame.classList.add(state);
}

function showChartError(container, specification, error) {
  setFrameState(container, "has-error");
  container.innerHTML = `
    <div class="chart-error" role="alert">
      <strong>This chart could not be loaded.</strong>
      <span>Check that <code>${specification}</code> and its data files are available.</span>
    </div>
  `;
  console.error(`Unable to embed ${specification}`, error);
}

function embedVisualisation(visualisation) {
  if (loadedVisualisations.has(visualisation.container)) {
    return;
  }

  const container = document.querySelector(visualisation.container);
  if (!container) {
    console.warn(`Missing chart container: ${visualisation.container}`);
    return;
  }

  loadedVisualisations.add(visualisation.container);

  if (typeof window.vegaEmbed !== "function") {
    showChartError(container, visualisation.specification, new Error("Vega-Embed is unavailable."));
    return;
  }

  window.vegaEmbed(visualisation.container, visualisation.specification, {
    actions: false,
    renderer: "svg",
    tooltip: { theme: "light" }
  })
    .then(() => setFrameState(container, "is-ready"))
    .catch((error) => showChartError(container, visualisation.specification, error));
}

const visualisationByFrame = new Map();

visualisations.forEach((visualisation) => {
  const container = document.querySelector(visualisation.container);
  if (!container) {
    console.warn(`Missing chart container: ${visualisation.container}`);
    return;
  }

  const frame = container.closest(".chart-frame") || container;
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
