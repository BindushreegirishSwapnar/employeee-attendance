/* ============================================================
   Employee Attendance & Salary Processing System
   Global JavaScript
   ============================================================ */

'use strict';

// ── Auto-dismiss flash alerts after 5 seconds ────────────────
(function autoDissmissAlerts() {
  document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(function (alert) {
      setTimeout(function () {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
      }, 5000);
    });
  });
})();


// ── Activate Bootstrap tooltips globally ─────────────────────
(function initTooltips() {
  document.addEventListener('DOMContentLoaded', function () {
    const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(function (el) {
      new bootstrap.Tooltip(el, { trigger: 'hover' });
    });
  });
})();


// ── Highlight active nav link ─────────────────────────────────
(function highlightNav() {
  document.addEventListener('DOMContentLoaded', function () {
    const path = window.location.pathname;
    document.querySelectorAll('.navbar .nav-link').forEach(function (link) {
      if (link.getAttribute('href') === path) {
        link.classList.add('active');
      }
    });
  });
})();


// ── Employee table: client-side instant search (optional UX boost) ──
// Filters the visible rows while the user types, without a round-trip.
// The form still submits for a proper server-side filter on Enter/button click.
(function liveTableSearch() {
  document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('input[name="search"]');
    const table       = document.getElementById('employeeTable');
    if (!searchInput || !table) return;

    searchInput.addEventListener('input', function () {
      const term = this.value.toLowerCase().trim();
      const rows = table.querySelectorAll('tbody tr');

      rows.forEach(function (row) {
        const text = row.textContent.toLowerCase();
        row.style.display = (term === '' || text.includes(term)) ? '' : 'none';
      });
    });
  });
})();


// ── Indian Rupee formatter (shared utility) ──────────────────
function formatINR(amount) {
  if (isNaN(amount)) return '₹0.00';
  const neg = amount < 0;
  amount = Math.abs(amount);
  const paise = amount.toFixed(2).split('.')[1];
  let intPart = Math.floor(amount).toString();
  let result  = '';
  if (intPart.length <= 3) {
    result = intPart;
  } else {
    result  = intPart.slice(-3);
    intPart = intPart.slice(0, -3);
    while (intPart.length > 0) {
      result  = intPart.slice(-2) + ',' + result;
      intPart = intPart.slice(0, -2);
    }
  }
  return (neg ? '-' : '') + '₹' + result + '.' + paise;
}


// ── Number-input: prevent negative values via keyboard ───────
(function preventNegativeInputs() {
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[type="number"][min="0"]').forEach(function (el) {
      el.addEventListener('input', function () {
        if (parseFloat(this.value) < 0) this.value = 0;
      });
    });
  });
})();


// ── Form validation: highlight empty required fields ─────────
(function clientValidation() {
  document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(function (form) {
      form.addEventListener('submit', function (e) {
        let valid = true;
        form.querySelectorAll('[required]').forEach(function (field) {
          if (!field.value.trim()) {
            field.classList.add('is-invalid');
            valid = false;
          } else {
            field.classList.remove('is-invalid');
          }
        });
        if (!valid) e.preventDefault();
      });

      // Remove invalid class on input
      form.querySelectorAll('[required]').forEach(function (field) {
        field.addEventListener('input', function () {
          if (this.value.trim()) this.classList.remove('is-invalid');
        });
      });
    });
  });
})();


// ── Confirm-delete helper (used on employee list & detail) ───
// The templates call this function directly; it lives here so it
// can also be used from any other page that needs the same pattern.
window.confirmDelete = window.confirmDelete || function (empId, empName) {
  const modal  = document.getElementById('deleteModal');
  const nameEl = document.getElementById('deleteEmpName');
  const btn    = document.getElementById('confirmDeleteBtn');
  if (!modal) return;
  if (nameEl) nameEl.textContent = empName;
  btn && btn.addEventListener('click', function handler() {
    const form = document.getElementById('delete-form-' + empId);
    if (form) form.submit();
    btn.removeEventListener('click', handler);
  }, { once: true });
  new bootstrap.Modal(modal).show();
};


// ── Smooth scroll-to-top on page load (after flash message) ──
(function scrollToFlash() {
  document.addEventListener('DOMContentLoaded', function () {
    const flash = document.querySelector('.alert.alert-dismissible');
    if (flash) flash.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });
})();
