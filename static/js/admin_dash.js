document.addEventListener("DOMContentLoaded", function () {
    wireSidebarToggle();
    toggleEmptyStates();
    wireSearch();
    wireConfirmations();
});

/* SIDEBAR TOGGLE */

function wireSidebarToggle() {
    const toggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");

    if (toggle && sidebar) {
        toggle.addEventListener("click", function () {
            sidebar.classList.toggle("open");
        });
    }
}

/* EMPTY STATES + NOTIFICATION DOT */

function toggleEmptyStates() {
    const pendingRows = document.querySelectorAll("#pendingTableBody tr");

    const pendingEmpty = document.getElementById("noPending");

    const pendingTable = document.getElementById("pendingTable");

    if (pendingEmpty && pendingTable) {
        const hasPending = pendingRows.length > 0;

        pendingEmpty.style.display = hasPending ? "none" : "block";

        pendingTable.style.display = hasPending ? "table" : "none";
    }

    /* NOTIFICATION DOT */

    const dot = document.getElementById("notifDot");

    if (dot) {
        dot.style.display = pendingRows.length > 0 ? "block" : "none";
    }

    /* CERTIFIED EMPTY STATE */

    const noCertifiedEl = document.getElementById("noCertified");

    if (noCertifiedEl) {
        const table = noCertifiedEl.previousElementSibling;

        if (table && table.tagName === "TABLE") {
            const rows = table.querySelectorAll("tbody tr");

            const hasRows = rows.length > 0;

            noCertifiedEl.style.display = hasRows ? "none" : "block";

            table.style.display = hasRows ? "table" : "none";
        }
    }
}

/* REJECTED EMPTY STATE */

const noRejectedEl =
    document.getElementById("noRejected");

if (noRejectedEl) {

    const table =
        noRejectedEl.previousElementSibling;

    if (table && table.tagName === "TABLE") {

        const rows =
            table.querySelectorAll("tbody tr");

        const hasRows =
            rows.length > 0;

        noRejectedEl.style.display =
            hasRows ? "none" : "block";

        table.style.display =
            hasRows ? "table" : "none";
    }
}

/* DOCTOR SEARCH */

function wireSearch() {
    const input = document.getElementById("doctorSearch");

    if (!input) {
        return;
    }

    input.addEventListener("input", function () {
        const term = input.value.trim().toLowerCase();

        document.querySelectorAll(".admin-table tbody tr").forEach(function (row) {
            const text = row.textContent.toLowerCase();

            if (text.includes(term)) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    });
}

/* CONFIRM BEFORE CERTIFY */

function wireConfirmations() {
    document.querySelectorAll(".certify-btn").forEach(function (btn) {
        btn.addEventListener("click", function (event) {
            const confirmed = confirm(
                "Certify this doctor? They will become visible to patients.",
            );

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });

    /* CONFIRM BEFORE REJECT */

    document.querySelectorAll(".reject-btn").forEach(function (btn) {
        btn.addEventListener("click", function (event) {
            const confirmed = confirm("Reject this doctor's registration?");

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
}
