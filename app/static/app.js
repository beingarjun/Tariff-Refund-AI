const form = document.getElementById("analyze-form");
const statusEl = document.getElementById("status");
const summaryPanel = document.getElementById("summary-panel");
const resultsPanel = document.getElementById("results-panel");
const summaryGrid = document.getElementById("summary-grid");
const tableBody = document.querySelector("#results-table tbody");
const downloadBtn = document.getElementById("download-report");

function setStatus(message) {
  statusEl.textContent = message || "";
}

function asMoney(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
}

function metric(label, value) {
  const wrapper = document.createElement("div");
  wrapper.className = "metric";
  wrapper.innerHTML = `<span class="label">${label}</span><span class="value">${value}</span>`;
  return wrapper;
}

function buildFormData() {
  const formData = new FormData(form);
  if (!formData.get("exclusions") || formData.get("exclusions").size === 0) {
    formData.delete("exclusions");
  }
  return formData;
}

function renderSummary(summary) {
  summaryGrid.innerHTML = "";
  summaryGrid.appendChild(metric("Shipments", summary.shipment_count));
  summaryGrid.appendChild(metric("Likely Refund Entries", summary.likely_refund_entries));
  summaryGrid.appendChild(metric("Total Duty Paid", asMoney(summary.total_duty_paid)));
  summaryGrid.appendChild(metric("Expected Duty", asMoney(summary.total_expected_duty)));
  summaryGrid.appendChild(metric("Potential Refund", asMoney(summary.total_potential_refund)));
  summaryPanel.classList.remove("hidden");
}

function renderResults(results) {
  tableBody.innerHTML = "";
  results.slice(0, 100).forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.entry_id}</td>
      <td>${row.importer}</td>
      <td>${row.import_date}</td>
      <td>${row.hts_code}</td>
      <td>${asMoney(row.duty_paid)}</td>
      <td>${asMoney(row.expected_duty)}</td>
      <td>${asMoney(row.refundable_amount)}</td>
      <td>${row.confidence_score}</td>
      <td>${row.notes}</td>
    `;
    tableBody.appendChild(tr);
  });
  resultsPanel.classList.remove("hidden");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Analyzing files...");
  summaryPanel.classList.add("hidden");
  resultsPanel.classList.add("hidden");

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: buildFormData(),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Analysis failed");
    }
    renderSummary(payload.summary);
    renderResults(payload.results);
    setStatus("");
  } catch (error) {
    setStatus(error.message);
  }
});

downloadBtn.addEventListener("click", async () => {
  setStatus("Generating report...");
  try {
    const response = await fetch("/api/analyze/report", {
      method: "POST",
      body: buildFormData(),
    });
    if (!response.ok) {
      const payload = await response.json();
      throw new Error(payload.detail || "Unable to generate report");
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "tariff_refund_report.csv";
    a.click();
    URL.revokeObjectURL(url);
    setStatus("");
  } catch (error) {
    setStatus(error.message);
  }
});

