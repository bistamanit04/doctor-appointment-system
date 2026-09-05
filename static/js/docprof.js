let activeBooking = null;

function showToast(message) {
    const toast = document.getElementById("toast");
    const msg = document.getElementById("toastMsg");

    if (!toast) return;

    if (msg) {
        msg.textContent = message;
    }

    toast.classList.add("show");

    clearTimeout(window.__toastTimer);

    window.__toastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}


function adjustCount(id, delta) {
    const el = document.getElementById(id);

    if (!el) return;

    const current = parseInt(el.textContent, 10) || 0;

    el.textContent = Math.max(0, current + delta);
}



function showBookingNotice(date, time) {
    const notice = document.getElementById("bookingNotice");
    const noticeText = document.getElementById("noticeDateTime");

    if (!notice) return;

    if (noticeText) {
        noticeText.textContent = `${date}, ${time}`;
    }

    notice.classList.add("show");
}

function hideBookingNotice() {
    const notice = document.getElementById("bookingNotice");

    if (notice) {
        notice.classList.remove("show");
    }
}



function lockOtherSlots(activeRow) {
    document.querySelectorAll(".slot-row").forEach((row) => {
        if (row === activeRow) return;

        row.classList.add("slot-locked");

        const btn = row.querySelector(".book-slot-btn");

        if (btn) {
            btn.disabled = true;
        }
    });
}



function unlockAllSlots() {
    document.querySelectorAll(".slot-row").forEach((row) => {
        row.classList.remove("slot-locked");

        const btn = row.querySelector(".book-slot-btn");

        if (btn) {
            btn.disabled = false;
        }
    });
}



function markRowPending(row, button) {
    row.classList.add("slot-pending");

    button.textContent = "Cancel Appointment";

    button.classList.add("cancel-slot-btn");

    if (!row.querySelector(".status-pill")) {
        const pill = document.createElement("span");

        pill.className = "status-pill status-pending";

        pill.innerHTML = '<i class="dot"></i>Pending';

        row.insertBefore(pill, button);
    }
}


function markRowAvailable(row, button) {
    row.classList.remove("slot-pending");

    row.classList.remove("slot-approved");

    button.textContent = "Book Appointment";

    button.classList.remove("cancel-slot-btn");

    const pill = row.querySelector(".status-pill");

    if (pill) {
        pill.remove();
    }
}



function toggleSlotBooking(button) {
    const row = button.closest(".slot-row");

    if (!row) return;

    const date = row.getAttribute("data-date");

    const time = row.getAttribute("data-time");

    const isThisRowPending = row.classList.contains("slot-pending");

    if (isThisRowPending) {
        markRowAvailable(row, button);

        unlockAllSlots();

        activeBooking = null;

        adjustCount("upcomingCount", -1);

        adjustCount("slotsLeftCount", 1);

        hideBookingNotice();

        showToast(`Appointment for ${date} at ${time} cancelled`);

        return;
    }



    if (activeBooking) {
        showToast("Cancel your current appointment before booking another slot.");

        return;
    }

    markRowPending(row, button);

    lockOtherSlots(row);

    activeBooking = {
        row: row,
        button: button,
        date: date,
        time: time,
    };

    adjustCount("upcomingCount", 1);

    adjustCount("slotsLeftCount", -1);

    showBookingNotice(date, time);

    showToast(`Appointment request sent for ${date} at ${time}`);
}
