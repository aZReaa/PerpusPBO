/**
 * Blue-White Theme custom JavaScript
 * For iPusnos Library System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Apply theme colors to dynamic elements
    applyThemeColors();
    
    // Add interaction effects
    addInteractionEffects();
});

/**
 * Apply theme colors to dynamic elements that can't be styled with CSS alone
 */
function applyThemeColors() {
    // Primary color: #1a73e8
    // Secondary color: #e8f0fe
    
    // Apply to card headers if they exist
    document.querySelectorAll('.card-header').forEach(header => {
        header.style.backgroundColor = '#1a73e8';
        header.style.color = 'white';
    });
    
    // Add border to buttons
    document.querySelectorAll('.btn-detail-modern').forEach(btn => {
        btn.style.border = '1px solid #1a73e8';
        btn.style.color = '#1a73e8';
    });
    
    // Style borrow buttons
    document.querySelectorAll('.btn-borrow-modern, .borrow-button').forEach(btn => {
        btn.style.backgroundColor = '#1a73e8';
        btn.style.color = 'white';
    });
    
    // Style book titles
    document.querySelectorAll('.book-title-modern, .book-title-detail').forEach(title => {
        title.style.color = '#1a73e8';
    });
}

/**
 * Add interaction effects to elements
 */
function addInteractionEffects() {
    // Add hover effects to book cards
    document.querySelectorAll('.book-card-modern').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        });
    });
    
    // Add ripple effect to buttons
    document.querySelectorAll('.btn-borrow-modern, .btn-detail-modern, .borrow-button').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

/**
 * Handle book detail page specific behaviors
 */
function setupBookDetailPage() {
    // Zoom effect for book cover
    const bookCover = document.querySelector('.book-cover-large');
    if (bookCover) {
        bookCover.addEventListener('click', function() {
            this.classList.toggle('zoomed');
            if (this.classList.contains('zoomed')) {
                this.style.transform = 'scale(1.5)';
                this.style.cursor = 'zoom-out';
                this.style.zIndex = '100';
            } else {
                this.style.transform = 'scale(1)';
                this.style.cursor = 'zoom-in';
                this.style.zIndex = '1';
            }
        });
        
        // Add zoom-in cursor by default
        bookCover.style.cursor = 'zoom-in';
    }
}

// Call setup for book detail page if we're on that page
if (document.querySelector('.book-detail-container')) {
    setupBookDetailPage();
}
