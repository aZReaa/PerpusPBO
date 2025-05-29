// Enhanced Touch scroll script with visual feedback
document.addEventListener('DOMContentLoaded', function() {
    // Find all scrollable tables
    const scrollableTables = document.querySelectorAll('.table-container, .admin-book-table, .loans-table-container-member, .table-wrapper-member');
    
    scrollableTables.forEach(function(container) {
        // Force scroll mode for all containers
        container.style.overflowX = 'scroll';
        container.style.webkitOverflowScrolling = 'touch';
        
        // Check if table is wider than container (needs scrolling)
        const table = container.querySelector('table');
        if (table && container.clientWidth < table.clientWidth) {
            // Add visual indicators for scrolling
            const indicator = document.createElement('div');
            indicator.className = 'scroll-indicator';
            indicator.innerHTML = '⟷ Geser untuk melihat lebih banyak';
            indicator.style.cssText = 'position: absolute; top: -25px; left: 0; width: 100%; text-align: center; font-size: 12px; color: #667eea; animation: fadeInOut 2s infinite; opacity: 1; transition: opacity 0.3s;';
            container.style.position = 'relative';
            container.appendChild(indicator);
            
            // Create gradient overlays to indicate scrollability
            const leftOverlay = document.createElement('div');
            leftOverlay.className = 'scroll-overlay-left';
            leftOverlay.style.cssText = 'position: absolute; left: 0; top: 0; height: 100%; width: 15px; background: linear-gradient(to right, rgba(255,255,255,0.7), transparent); pointer-events: none; opacity: 0; transition: opacity 0.3s; z-index: 1;';
            
            const rightOverlay = document.createElement('div');
            rightOverlay.className = 'scroll-overlay-right';
            rightOverlay.style.cssText = 'position: absolute; right: 0; top: 0; height: 100%; width: 15px; background: linear-gradient(to left, rgba(255,255,255,0.7), transparent); pointer-events: none; opacity: 0.7; transition: opacity 0.3s; z-index: 1;';
            
            container.appendChild(leftOverlay);
            container.appendChild(rightOverlay);
            
            // Update overlay visibility based on scroll position
            const updateOverlays = function() {
                // Show left overlay if scrolled
                leftOverlay.style.opacity = container.scrollLeft > 0 ? '0.7' : '0';
                
                // Show right overlay if more to scroll
                const maxScroll = container.scrollWidth - container.clientWidth;
                rightOverlay.style.opacity = container.scrollLeft >= maxScroll - 5 ? '0' : '0.7';
                
                // Hide indicator when user has scrolled
                indicator.style.opacity = container.scrollLeft > 0 ? '0' : '1';
            };
            
            // Initial update
            updateOverlays();
            
            // Update on scroll
            container.addEventListener('scroll', updateOverlays);
            
            // Add pulse animation to right overlay to encourage scrolling
            setTimeout(function() {
                rightOverlay.style.animation = 'pulse 2s infinite';
            }, 1000);
        }
        
        // Add touch feedback
        container.addEventListener('touchstart', function() {
            this.classList.add('touching');
        });
        
        container.addEventListener('touchend', function() {
            this.classList.remove('touching');
        });
    });
    
    // Create keyframes animation for indicator if it doesn't exist
    if (!document.querySelector('#scroll-indicator-keyframes')) {
        const style = document.createElement('style');
        style.id = 'scroll-indicator-keyframes';
        style.textContent = `
            @keyframes fadeInOut {
                0% { opacity: 0.3; }
                50% { opacity: 1; }
                100% { opacity: 0.3; }
            }
            
            @keyframes pulse {
                0% { opacity: 0.4; }
                50% { opacity: 0.8; }
                100% { opacity: 0.4; }
            }
            
            .touching {
                cursor: grabbing !important;
            }
            
            /* Force scroll on touch devices */
            @media (hover: none) and (pointer: coarse) {
                .table-container, .admin-book-table, 
                .loans-table-container-member, .table-wrapper-member {
                    -ms-overflow-style: none !important;  /* IE and Edge */
                    scrollbar-width: none !important;  /* Firefox */
                    overflow-x: scroll !important;
                }
                
                /* Hide scrollbar for Chrome, Safari and Opera */
                .table-container::-webkit-scrollbar,
                .admin-book-table::-webkit-scrollbar,
                .loans-table-container-member::-webkit-scrollbar,
                .table-wrapper-member::-webkit-scrollbar {
                    display: none !important;
                }
            }
        `;
        document.head.appendChild(style);
    }
});
