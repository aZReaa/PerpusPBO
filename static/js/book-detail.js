/**
 * Book detail page interactivity
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle borrow button click
    const borrowButton = document.querySelector('.borrow-button');
    if (borrowButton) {
        borrowButton.addEventListener('click', function(e) {
            // The confirm dialog is handled by the onclick attribute
            // This is just for additional interactions if needed
        });
    }

    // Add smooth scrolling for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Handle image zoom if needed
    const bookCover = document.querySelector('.book-cover-large');
    if (bookCover) {
        bookCover.addEventListener('click', function() {
            // Implement zoom functionality if desired
            this.classList.toggle('zoomed');
        });
    }
});
