document.addEventListener("DOMContentLoaded", function () {
  toggleEmptyState();
  wireAddForm();
  wireExistingRows();
});

/* --------------------------------
   TOAST HELPER
-------------------------------- */

function showToast(message, type) {
  const toast = document.getElementById("toast");
  const msg = document.getElementById("toastMsg");

  msg.textContent = message;
  toast.className = "toast show" + (type ? " toast-" + type : "");

  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(function () {
    toast.classList.remove("show");
  }, 3000);
}

/* --------------------------------
   SMALL HELPERS
-------------------------------- */

function toFormBody(data) {
  return Object.keys(data)
    .map(function (key) {
      return encodeURIComponent(key) + "=" + encodeURIComponent(data[key]);
    })
    .join("&");
}

async function postForm(url, data) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: toFormBody(data),
  });

  let payload;
  try {
    payload = await response.json();
  } catch (err) {
    payload = {
      success: response.ok,
      message: response.ok ? "" : "Unexpected server response.",
    };
  }

  if (!response.ok && payload.success === undefined) {
    payload.success = false;
  }

  // Server tells us to go elsewhere (e.g. session expired)
  if (payload.redirect) {
    window.location.href = payload.redirect;
  }

  return payload;
}

function toggleEmptyState() {
  const rows = document.querySelectorAll("#slotsTableBody tr");
  const empty = document.getElementById("noSlots");
  const table = document.getElementById("slotsTable");
  const countEl = document.getElementById("slotCount");

  const hasRows = rows.length > 0;
  empty.style.display = hasRows ? "none" : "block";
  table.style.display = hasRows ? "table" : "none";

  if (countEl) {
    countEl.textContent =
      rows.length + (rows.length === 1 ? " slot" : " slots");
  }
}

function setFieldError(groupId, hasError) {
  const group = document.getElementById(groupId);
  if (group) group.classList.toggle("invalid", hasError);
}

/* --------------------------------
   ADD SLOT
-------------------------------- */

function wireAddForm() {
  const form = document.getElementById("addSlotForm");

  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const dateVal = document.getElementById("slot_date").value;
    const startVal = document.getElementById("start_time").value;
    const endVal = document.getElementById("end_time").value;

    setFieldError("group-date", false);
    setFieldError("group-start", false);
    setFieldError("group-end", false);

    let hasError = false;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (!dateVal || new Date(dateVal) < today) {
      setFieldError("group-date", true);
      hasError = true;
    }

    if (!startVal) {
      setFieldError("group-start", true);
      hasError = true;
    }

    if (!endVal) {
      setFieldError("group-end", true);
      hasError = true;
    }

    if (startVal && endVal && startVal >= endVal) {
      setFieldError("group-end", true);
      hasError = true;
    }

    if (hasError) {
      showToast("Please fix the highlighted fields.", "error");
      return;
    }

    const submitBtn = form.querySelector(".slot-add-btn");
    submitBtn.disabled = true;

    try {
      const result = await postForm("/doctor/slots/add", {
        date: dateVal,
        start_time: startVal,
        end_time: endVal,
      });

      if (result.success) {
        addRowToTable({
          slot_id: result.slot_id,
          date: dateVal,
          start_time: startVal,
          end_time: endVal,
          status: "available",
        });

        form.reset();
        toggleEmptyState();
        showToast(result.message || "Time slot added.", "success");
      } else {
        showToast(result.message || "Could not add the time slot.", "error");
      }
    } catch (err) {
      showToast("Network error — could not reach the server.", "error");
    } finally {
      submitBtn.disabled = false;
    }
  });

  document.querySelectorAll("#addSlotForm input").forEach(function (el) {
    el.addEventListener("input", function () {
      const group = el.closest(".slot-field");
      if (group) group.classList.remove("invalid");
    });
  });
}

/* --------------------------------
   BUILD A NEW ROW
-------------------------------- */

function addRowToTable(slot) {
  const tbody = document.getElementById("slotsTableBody");
  const tr = document.createElement("tr");
  tr.dataset.slotId = slot.slot_id;

  tr.innerHTML =
    '<td class="cell-date" data-label="Date">' +
    slot.date +
    "</td>" +
    '<td class="cell-start" data-label="Start">' +
    slot.start_time +
    "</td>" +
    '<td class="cell-end" data-label="End">' +
    slot.end_time +
    "</td>" +
    '<td class="cell-status" data-label="Status">' +
    '<span class="status-badge status-slot-' +
    slot.status +
    '">' +
    slot.status +
    "</span>" +
    "</td>" +
    '<td data-label="Actions">' +
    '<div class="slot-actions">' +
    '<button class="action-btn slot-edit-btn" type="button">✏️ Edit</button>' +
    '<button class="action-btn slot-delete-btn" type="button">🗑️ Delete</button>' +
    "</div>" +
    "</td>";

  tbody.appendChild(tr);
  wireRow(tr);
}

/* --------------------------------
   WIRE UP EXISTING (SERVER-RENDERED) ROWS
-------------------------------- */

function wireExistingRows() {
  document.querySelectorAll("#slotsTableBody tr").forEach(wireRow);
}

function wireRow(row) {
  const editBtn = row.querySelector(".slot-edit-btn");
  const deleteBtn = row.querySelector(".slot-delete-btn");

  // A slot with a booked appointment can't be edited or deleted.
  // (The server enforces this too -- this is just so the buttons
  // don't look clickable.)
  const badge = row.querySelector(".cell-status .status-badge");
  if (badge && badge.textContent.trim().toLowerCase() === "booked") {
    [editBtn, deleteBtn].forEach(function (btn) {
      if (btn) {
        btn.disabled = true;
        btn.title = "This slot has a booked appointment.";
      }
    });
    return;
  }

  if (editBtn) {
    editBtn.addEventListener("click", function () {
      enterEditMode(row);
    });
  }

  if (deleteBtn) {
    deleteBtn.addEventListener("click", function () {
      deleteSlot(row);
    });
  }
}

/* --------------------------------
   EDIT MODE
-------------------------------- */

function enterEditMode(row) {
  const dateCell = row.querySelector(".cell-date");
  const startCell = row.querySelector(".cell-start");
  const endCell = row.querySelector(".cell-end");
  const statusCell = row.querySelector(".cell-status");
  const actionsCell = row.querySelector("td:last-child");

  const currentDate = dateCell.textContent.trim();
  const currentStart = startCell.textContent.trim();
  const currentEnd = endCell.textContent.trim();
  const currentStatus = statusCell
    .querySelector(".status-badge")
    .textContent.trim();

  dateCell.classList.add("editing");
  startCell.classList.add("editing");
  endCell.classList.add("editing");
  statusCell.classList.add("editing");

  dateCell.innerHTML =
    '<input type="date" class="edit-date" value="' + currentDate + '" />';
  startCell.innerHTML =
    '<input type="time" class="edit-start" value="' + currentStart + '" />';
  endCell.innerHTML =
    '<input type="time" class="edit-end" value="' + currentEnd + '" />';

  statusCell.innerHTML =
    '<select class="edit-status">' +
    '<option value="available">available</option>' +
    '<option value="unavailable">unavailable</option>' +
    "</select>";

  const statusSelect = statusCell.querySelector(".edit-status");
  [...statusSelect.options].forEach(function (opt) {
    if (opt.value === currentStatus) opt.selected = true;
  });

  actionsCell.innerHTML =
    '<div class="slot-actions">' +
    '<button class="action-btn slot-save-btn" type="button">💾 Save</button>' +
    '<button class="action-btn slot-cancel-btn" type="button">✖ Cancel</button>' +
    "</div>";

  actionsCell
    .querySelector(".slot-cancel-btn")
    .addEventListener("click", function () {
      restoreRow(row, {
        date: currentDate,
        start_time: currentStart,
        end_time: currentEnd,
        status: currentStatus,
      });
    });

  actionsCell
    .querySelector(".slot-save-btn")
    .addEventListener("click", function () {
      saveEdit(row, {
        date: currentDate,
        start_time: currentStart,
        end_time: currentEnd,
        status: currentStatus,
      });
    });
}

async function saveEdit(row, fallback) {
  const slotId = row.dataset.slotId;
  const newDate = row.querySelector(".edit-date").value;
  const newStart = row.querySelector(".edit-start").value;
  const newEnd = row.querySelector(".edit-end").value;
  const newStatus = row.querySelector(".edit-status").value;

  if (!newDate || !newStart || !newEnd) {
    showToast("All fields are required.", "error");
    return;
  }

  if (newStart >= newEnd) {
    showToast("End time must be after start time.", "error");
    return;
  }

  const saveBtn = row.querySelector(".slot-save-btn");
  saveBtn.disabled = true;

  try {
    const result = await postForm("/doctor/slots/update", {
      slot_id: slotId,
      date: newDate,
      start_time: newStart,
      end_time: newEnd,
      status: newStatus,
    });

    if (result.success) {
      restoreRow(row, {
        date: newDate,
        start_time: newStart,
        end_time: newEnd,
        status: newStatus,
      });
      showToast(result.message || "Time slot updated.", "success");
    } else {
      showToast(result.message || "Could not update the time slot.", "error");
      saveBtn.disabled = false;
    }
  } catch (err) {
    showToast("Network error — could not reach the server.", "error");
    saveBtn.disabled = false;
  }
}

function restoreRow(row, values) {
  const dateCell = row.querySelector(".cell-date");
  const startCell = row.querySelector(".cell-start");
  const endCell = row.querySelector(".cell-end");
  const statusCell = row.querySelector(".cell-status");

  dateCell.classList.remove("editing");
  startCell.classList.remove("editing");
  endCell.classList.remove("editing");
  statusCell.classList.remove("editing");

  dateCell.textContent = values.date;
  startCell.textContent = values.start_time;
  endCell.textContent = values.end_time;
  statusCell.innerHTML =
    '<span class="status-badge status-slot-' +
    values.status +
    '">' +
    values.status +
    "</span>";

  row.querySelector("td:last-child").innerHTML =
    '<div class="slot-actions">' +
    '<button class="action-btn slot-edit-btn" type="button">✏️ Edit</button>' +
    '<button class="action-btn slot-delete-btn" type="button">🗑️ Delete</button>' +
    "</div>";

  wireRow(row);
}

/* --------------------------------
   DELETE
-------------------------------- */

async function deleteSlot(row) {
  if (!confirm("Delete this time slot? This cannot be undone.")) {
    return;
  }

  const slotId = row.dataset.slotId;
  const deleteBtn = row.querySelector(".slot-delete-btn");
  deleteBtn.disabled = true;

  try {
    const result = await postForm("/doctor/slots/delete", { slot_id: slotId });

    if (result.success) {
      row.remove();
      toggleEmptyState();
      showToast(result.message || "Time slot deleted.", "success");
    } else {
      showToast(result.message || "Could not delete the time slot.", "error");
      deleteBtn.disabled = false;
    }
  } catch (err) {
    showToast("Network error — could not reach the server.", "error");
    deleteBtn.disabled = false;
  }
}

