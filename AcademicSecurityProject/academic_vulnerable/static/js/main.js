// Notifications toast automatiques
document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss des alertes après 5s
    document.querySelectorAll('.alert-dismissible').forEach(el => {
        setTimeout(() => {
            const alert = bootstrap.Alert.getOrCreateInstance(el);
            alert.close();
        }, 5000);
    });

    // Confirmation sur actions sensibles
    document.querySelectorAll('form[data-confirm]').forEach(form => {
        form.addEventListener('submit', e => {
            if (!confirm(form.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // Recherche globale (démo)
    const search = document.getElementById('globalSearch');
    if (search) {
        search.addEventListener('keypress', e => {
            if (e.key === 'Enter') {
                window.location = '/courses/?q=' + encodeURIComponent(search.value);
            }
        });
    }
});