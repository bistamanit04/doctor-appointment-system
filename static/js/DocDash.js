

let pendingCount = 3;
let approvedCount = 1;
let rejectedCount = 0;

/* ----- Toast helper ----- */
function showToast(message, isError) {
  const toast = document.getElementById("toast");
  const msg = document.getElementById("toastMsg");
  if (!toast) return;

  if (msg) msg.textContent = message;
  toast.classList.toggle("toast-error", !!isError);
  toast.classList.add("show");

  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

/* ----- Sync stat cards + side summary panel ----- */
function refreshCounts() {
  const pendingEl = document.getElementById("pendingCount");
  const remainingEl = document.getElementById("requestsRemaining");
  const summaryPending = document.getElementById("summaryPending");
  const summaryAccepted = document.getElementById("summaryAccepted");
  const summaryRejected = document.getElementById("summaryRejected");
  const noRequests = document.getElementById("noRequests");

  if (pendingEl) pendingEl.textContent = pendingCount;
  if (remainingEl) remainingEl.textContent = `${pendingCount} pending`;
  if (summaryPending) summaryPending.textContent = `${pendingCount} Pending`;
  if (summaryAccepted) summaryAccepted.textContent = `${approvedCount} Accepted`;
  if (summaryRejected) summaryRejected.textContent = `${rejectedCount} Rejected`;

  if (noRequests) noRequests.classList.toggle("show", pendingCount === 0);
}

/* ----- Main handler for Approve / Reject buttons ----- */
function handleRequest(button, action) {
  const row = button.closest("tr");
  if (!row || row.classList.contains("request-resolved")) return;

  const patient = row.getAttribute("data-patient");
  const date = row.getAttribute("data-date");
  const time = row.getAttribute("data-time");

  const statusCell = row.children[3];
  const actionCell = row.children[4];

  row.classList.add("request-resolved");
  pendingCount = Math.max(0, pendingCount - 1);

  if (action === "approve") {
    row.classList.add("request-approved-row");
    statusCell.innerHTML = '<span class="status-badge status-approved">Approved</span>';
    actionCell.innerHTML = '<button class="action-btn">View</button>';
    approvedCount++;

    // Bump today's appointment count
    const todayEl = document.getElementById("todayCount");
    if (todayEl) {
      const current = parseInt(todayEl.textContent, 10) || 0;
      todayEl.textContent = current + 1;
    }

    showToast(`Approved ${patient}'s appointment for ${date}, ${time}`);
  } else {
    row.classList.add("request-rejected-row");
    statusCell.innerHTML = '<span class="status-badge status-cancelled">Rejected</span>';
    actionCell.innerHTML = '<button class="action-btn">View</button>';
    rejectedCount++;

    showToast(`Rejected ${patient}'s request for ${date}, ${time}`, true);
  }

  refreshCounts();
}

refreshCounts();