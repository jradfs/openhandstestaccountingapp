document.addEventListener("DOMContentLoaded", function(event) {
    const showNavbar = (toggleId, navId, bodyId, headerId) => {
        const toggle = document.getElementById(toggleId),
            nav = document.getElementById(navId),
            bodypd = document.getElementById(bodyId),
            headerpd = document.getElementById(headerId)

        if (toggle && nav && bodypd && headerpd) {
            toggle.addEventListener('click', () => {
                nav.classList.toggle('show')
                toggle.classList.toggle('bx-x')
                bodypd.classList.toggle('body-pd')
                headerpd.classList.toggle('body-pd')
            })
        }
    }

    showNavbar('header-toggle', 'nav-bar', 'body-pd', 'header')

    const linkColor = document.querySelectorAll('.nav_link')

    function colorLink() {
        if (linkColor) {
            linkColor.forEach(l => l.classList.remove('active'))
            this.classList.add('active')
        }
    }
    linkColor.forEach(l => l.addEventListener('click', colorLink))
});

// File Upload Handler
document.querySelectorAll('.custom-file-input').forEach(input => {
    input.addEventListener('change', function(e) {
        let fileName = e.target.files[0].name;
        let nextSibling = e.target.nextElementSibling;
        nextSibling.innerText = fileName;
    });
});

// Transaction Form Validation
const transactionForm = document.getElementById('transactionForm');
if (transactionForm) {
    transactionForm.addEventListener('submit', function(e) {
        if (!this.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        this.classList.add('was-validated');
    });
}

// Dynamic Table Sorting
document.querySelectorAll('th[data-sort]').forEach(header => {
    header.addEventListener('click', function() {
        const table = this.closest('table');
        const index = Array.from(this.parentElement.children).indexOf(this);
        const isAsc = this.classList.contains('asc');
        
        sortTableByColumn(table, index, !isAsc);
        
        // Update sort indicators
        this.closest('tr').querySelectorAll('th').forEach(th => {
            th.classList.remove('asc', 'desc');
        });
        this.classList.toggle('asc', !isAsc);
        this.classList.toggle('desc', isAsc);
    });
});

function sortTableByColumn(table, column, asc = true) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const sortedRows = rows.sort((a, b) => {
        const aValue = a.children[column].textContent.trim();
        const bValue = b.children[column].textContent.trim();
        
        return asc ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
    });
    
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    
    tbody.append(...sortedRows);
}

// Initialize tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});