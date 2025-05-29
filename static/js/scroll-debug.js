// Mobile scroll testing and debugging script
(function() {
    'use strict';
    
    // Add this script to run on page load
    window.addEventListener('load', function() {
        console.log('Mobile scroll testing script loaded');
        
        // Find all scrollable containers
        const scrollContainers = document.querySelectorAll(
            '.table-container, .admin-book-table, .loans-table-container-member, .table-wrapper-member'
        );
        
        // Add debug information to page
        const debugInfo = document.createElement('div');
        debugInfo.id = 'scroll-debug-info';
        debugInfo.style.cssText = 'position: fixed; bottom: 10px; left: 10px; background: rgba(0,0,0,0.7); color: white; padding: 10px; font-size: 12px; z-index: 9999; border-radius: 5px; max-width: 80%; display: none;';
        document.body.appendChild(debugInfo);
        
        // Toggle debug info display
        let debugVisible = false;
        const toggleDebug = document.createElement('button');
        toggleDebug.innerText = 'Debug Scroll';
        toggleDebug.style.cssText = 'position: fixed; bottom: 10px; right: 10px; z-index: 9999; background: #5D78FF; color: white; border: none; padding: 5px 10px; border-radius: 5px; font-size: 12px;';
        document.body.appendChild(toggleDebug);
        
        toggleDebug.addEventListener('click', function() {
            debugVisible = !debugVisible;
            debugInfo.style.display = debugVisible ? 'block' : 'none';
            updateDebugInfo();
        });
        
        // Update debug info
        function updateDebugInfo() {
            if (!debugVisible) return;
            
            let info = '<strong>Scroll Containers:</strong><br>';
            
            scrollContainers.forEach((container, i) => {
                const table = container.querySelector('table');
                const tableWidth = table ? table.offsetWidth : 0;
                const containerWidth = container.offsetWidth;
                const scrollWidth = container.scrollWidth;
                const scrollLeft = container.scrollLeft;
                const maxScroll = scrollWidth - containerWidth;
                
                info += `<div style="margin-top:5px;border-top:1px solid #999;padding-top:5px;">
                    <strong>Container ${i+1}:</strong><br>
                    - Table width: ${tableWidth}px<br>
                    - Container width: ${containerWidth}px<br>
                    - Scroll width: ${scrollWidth}px<br>
                    - Current scroll: ${scrollLeft}px / ${maxScroll}px<br>
                    - Is scrollable: ${maxScroll > 0 ? 'YES' : 'NO'}<br>
                    - overflow-x: ${getComputedStyle(container).overflowX}<br>
                    - touch-action: ${getComputedStyle(container).touchAction}<br>
                </div>`;
            });
            
            debugInfo.innerHTML = info;
        }
        
        // Update on scroll
        scrollContainers.forEach(container => {
            container.addEventListener('scroll', updateDebugInfo);
            
            // Manually test ability to scroll programmatically
            setTimeout(() => {
                const originalScroll = container.scrollLeft;
                container.scrollLeft = 10;
                setTimeout(() => {
                    if (container.scrollLeft === 10) {
                        console.log('Container is programmatically scrollable');
                        container.scrollLeft = originalScroll;
                    } else {
                        console.log('Container is NOT programmatically scrollable');
                        // Force scroll mode
                        container.style.overflowX = 'scroll';
                    }
                    updateDebugInfo();
                }, 50);
            }, 1000);
        });
        
        // Device info
        const deviceInfo = `
            <div style="margin-top:10px;border-top:1px solid white;padding-top:10px;">
                <strong>Device Info:</strong><br>
                - Window inner: ${window.innerWidth} x ${window.innerHeight}<br>
                - User agent: ${navigator.userAgent}<br>
                - Touch points: ${navigator.maxTouchPoints}<br>
            </div>
        `;
        
        // Add to debug info
        debugInfo.innerHTML += deviceInfo;
    });
})();
