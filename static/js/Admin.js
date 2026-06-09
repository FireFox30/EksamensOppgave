// Enkel klient-side filtrering av sakstabellen
document.getElementById('statusFilter').addEventListener('change', function () {
    const filter = this.value.toLowerCase();
    const rows = document.querySelectorAll('#ticketTable tbody tr');

    rows.forEach(row => {
        const status = row.dataset.status.toLowerCase();
        row.style.display = (!filter || status === filter) ? '' : 'none';
    });
});