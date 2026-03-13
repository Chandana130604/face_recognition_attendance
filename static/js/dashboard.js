document.querySelectorAll('.nav-item[data-page]').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        const page = this.dataset.page;
        const pageMap = {
            'dashboard': '/admin-dashboard',
            'camera': '/camera-monitor',
            'employees': '/employees',
            'logs': '/attendance-logs',
            'analytics': '/analytics',
            'reports': '/reports',
            'settings': '/settings'
        };
        if (pageMap[page]) {
            window.location.href = pageMap[page];
        } else {
            console.warn('Unknown page:', page);
        }
    });
});