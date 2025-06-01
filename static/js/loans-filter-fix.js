// Loans Filter Fix - Mengatasi masalah filter setelah kelola denda

// Force refresh stats dan filter saat halaman dimuat atau setelah perubahan
function forceRefreshStats() {
    const today = new Date().toISOString().split('T')[0];
    let dueTodayCount = 0;
    let overdueCount = 0;
    let dipinjamCount = 0;
    let dikembalikanCount = 0;
    let allCount = 0;

    document.querySelectorAll('.loan-row').forEach(row => {
        const status = row.dataset.status;
        const dueDate = row.dataset.dueDate;
        
        allCount++;
        
        if (status === 'dipinjam') {
            dipinjamCount++;
            
            // Update status badge secara paksa
            const statusBadge = row.querySelector('.status-badge');
            if (statusBadge) {
                if (dueDate < today) {
                    statusBadge.textContent = '🚨 Terlambat';
                    statusBadge.className = 'status-badge status-overdue';
                    overdueCount++;
                    row.classList.add('overdue');
                    row.classList.remove('due-today');
                } else if (dueDate === today) {
                    statusBadge.textContent = '⏰ Jatuh Tempo Hari Ini';
                    statusBadge.className = 'status-badge status-due-today';
                    dueTodayCount++;
                    row.classList.add('due-today');
                    row.classList.remove('overdue');
                } else {
                    statusBadge.textContent = '📖 Dipinjam';
                    statusBadge.className = 'status-badge status-active';
                    row.classList.remove('overdue', 'due-today');
                }
            }
        } else if (status === 'dikembalikan') {
            dikembalikanCount++;
            row.classList.remove('overdue', 'due-today');
        }
    });

    // Update semua count dengan force
    const elements = {
        'due-today-count': dueTodayCount,
        'overdue-count': overdueCount,
        'count-all': allCount,
        'count-dipinjam': dipinjamCount,
        'count-dikembalikan': dikembalikanCount,
        'count-terlambat': overdueCount
    };

    Object.entries(elements).forEach(([id, count]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = count;
        }
    });

    console.log('Stats refreshed:', {
        all: allCount,
        dipinjam: dipinjamCount,
        dikembalikan: dikembalikanCount,
        terlambat: overdueCount,
        dueToday: dueTodayCount
    });
}

// Force reset filter ke "Semua" dan pastikan berfungsi
function resetFiltersToAll() {
    const filterButtons = document.querySelectorAll('.filter-btn-modern');
    const allButton = document.querySelector('.filter-btn-modern[data-filter="all"]');
    
    // Reset semua tombol
    filterButtons.forEach(btn => btn.classList.remove('active'));
    
    // Aktifkan tombol "Semua"
    if (allButton) {
        allButton.classList.add('active');
    }
    
    // Tampilkan semua rows
    document.querySelectorAll('.loan-row').forEach(row => {
        row.style.display = '';
        
        // Set action buttons untuk filter "semua"
        const dipinjamActions = row.querySelector('.dipinjam-actions');
        const statusOnly = row.querySelector('.status-only');
        
        if (dipinjamActions && statusOnly) {
            dipinjamActions.style.display = 'none';
            statusOnly.style.display = 'block';
        }
    });
    
    console.log('Filter reset to "Semua"');
}

// Setup filter yang lebih robust
function setupRobustFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn-modern');
    const today = new Date().toISOString().split('T')[0];
    
    console.log('Setting up robust filters, found buttons:', filterButtons.length);
    
    filterButtons.forEach(btn => {
        // Hapus event listener lama
        btn.removeEventListener('click', btn._filterHandler);
        
        // Buat handler baru
        btn._filterHandler = function() {
            console.log('Filter clicked:', this.dataset.filter);
            
            // Force refresh stats dulu
            forceRefreshStats();
            
            // Remove active class dari semua tombol
            filterButtons.forEach(b => b.classList.remove('active'));
            
            // Add active class ke tombol yang diklik
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            let visibleCount = 0;
            
            document.querySelectorAll('.loan-row').forEach(row => {
                const status = row.dataset.status;
                const dueDate = row.dataset.dueDate;
                let show = false;
                
                switch(filter) {
                    case 'all':
                        show = true;
                        toggleActionButtons(row, 'all');
                        break;
                    case 'dipinjam':
                        show = status === 'dipinjam';
                        toggleActionButtons(row, 'dipinjam');
                        break;
                    case 'dikembalikan':
                        show = status === 'dikembalikan';
                        toggleActionButtons(row, 'dikembalikan');
                        break;
                    case 'terlambat':
                        show = status === 'dipinjam' && dueDate < today;
                        toggleActionButtons(row, 'terlambat');
                        break;
                }
                
                if (show) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });
            
            console.log('Filter applied:', filter, 'Visible rows:', visibleCount);
            
            // Show notification
            showFilterNotification(filter, visibleCount);
        };
        
        // Tambah event listener baru
        btn.addEventListener('click', btn._filterHandler);
    });
}

// Toggle action buttons based on active filter
function toggleActionButtons(row, filterType) {
    const dipinjamActions = row.querySelector('.dipinjam-actions');
    const dikembalikanActions = row.querySelector('.dikembalikan-actions');
    const statusOnly = row.querySelector('.status-only');
    const kembalikanBtn = row.querySelector('.btn-kembalikan');
    const kelolaDendaBtn = row.querySelector('.btn-kelola-denda');
    
    // Hide all action containers first
    if (dipinjamActions) dipinjamActions.style.display = 'none';
    if (dikembalikanActions) dikembalikanActions.style.display = 'none';
    if (statusOnly) statusOnly.style.display = 'none';
    
    if (filterType === 'all') {
        // Untuk filter "semua", tampilkan status saja
        if (statusOnly) statusOnly.style.display = 'block';
    } else if (filterType === 'dipinjam') {
        // Untuk filter "dipinjam", tampilkan tombol kembalikan saja
        if (dipinjamActions) {
            dipinjamActions.style.display = 'flex';
            if (kembalikanBtn) kembalikanBtn.style.display = 'inline-block';
            if (kelolaDendaBtn) kelolaDendaBtn.style.display = 'none';
        }
    } else if (filterType === 'dikembalikan') {
        // Untuk filter "dikembalikan", tampilkan tombol selesai
        if (dikembalikanActions) dikembalikanActions.style.display = 'block';
    } else if (filterType === 'terlambat') {
        // Untuk filter "terlambat", hanya tampilkan tombol kelola denda
        if (dipinjamActions) {
            dipinjamActions.style.display = 'flex';
            if (kembalikanBtn) kembalikanBtn.style.display = 'none';
            if (kelolaDendaBtn) kelolaDendaBtn.style.display = 'inline-block';
        }
    } else {
        // Default case
        if (dipinjamActions) dipinjamActions.style.display = 'flex';
        if (dikembalikanActions) dikembalikanActions.style.display = 'block';
    }
}

// Show filter notification
function showFilterNotification(filter, count) {
    // Hapus notifikasi yang ada
    const existingNotification = document.querySelector('.filter-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const filterNames = {
        'all': 'Semua Peminjaman',
        'dipinjam': 'Sedang Dipinjam',
        'dikembalikan': 'Sudah Dikembalikan',
        'terlambat': 'Terlambat'
    };
    
    const notification = document.createElement('div');
    notification.className = 'filter-notification';
    notification.innerHTML = `
        <span class="notification-icon">📊</span>
        <span class="notification-text">Menampilkan ${count} ${filterNames[filter]}</span>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(72, 187, 120, 0.3);
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 600;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Inisialisasi saat DOM ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Loans Filter Fix loaded');
    
    // Force refresh stats pertama kali
    setTimeout(() => {
        forceRefreshStats();
        setupRobustFilters();
        resetFiltersToAll();
    }, 500);
});

// Export functions untuk digunakan secara global
window.loansFilterFix = {
    forceRefreshStats,
    resetFiltersToAll,
    setupRobustFilters
};
