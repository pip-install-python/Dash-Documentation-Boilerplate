/**
 * LLM Copy, TOON, and Page JSON Button Functionality
 * Copies the current page's /llms.txt, /llms.toon, or /page.json URL to clipboard
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('LLM Copy, TOON, and Page JSON handler loaded');

    // Function to copy text using fallback methods
    async function copyToClipboard(text) {
        // Try modern clipboard API first
        if (navigator.clipboard && navigator.clipboard.writeText) {
            try {
                await navigator.clipboard.writeText(text);
                return true;
            } catch (err) {
                console.warn('Clipboard API failed, trying fallback:', err);
            }
        }

        // Fallback for non-secure contexts (HTTP)
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.top = '0';
        textarea.style.left = '0';
        textarea.style.width = '2em';
        textarea.style.height = '2em';
        textarea.style.padding = '0';
        textarea.style.border = 'none';
        textarea.style.outline = 'none';
        textarea.style.boxShadow = 'none';
        textarea.style.background = 'transparent';
        textarea.style.opacity = '0';

        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();

        try {
            const success = document.execCommand('copy');
            document.body.removeChild(textarea);
            return success;
        } catch (err) {
            console.error('execCommand failed:', err);
            document.body.removeChild(textarea);
            return false;
        }
    }

    // Function to setup copy buttons
    function setupCopyButtons() {
        // Find all LLM copy buttons by class and by ID prefix
        const buttonsByClass = document.querySelectorAll('.llms-copy-button');
        const buttonsById = document.querySelectorAll('[id^="llm-copy-button-"]');

        // Combine both selections
        const allButtons = new Set([...buttonsByClass, ...buttonsById]);

        console.log(`Found ${allButtons.size} copy buttons to setup`);

        allButtons.forEach(button => {
            // Skip if already setup
            if (button.dataset.copySetup) return;
            button.dataset.copySetup = 'true';

            // Add click handler
            button.addEventListener('click', async function(e) {
                e.preventDefault();
                e.stopPropagation();

                try {
                    // Get current page URL
                    const currentPath = window.location.pathname;

                    // Construct llms.txt URL
                    // Remove trailing slash if present
                    const cleanPath = currentPath.endsWith('/')
                        ? currentPath.slice(0, -1)
                        : currentPath;

                    // Build full URL
                    const llmsUrl = `${window.location.origin}${cleanPath}/llms.txt`;

                    // Copy to clipboard
                    const copySuccess = await copyToClipboard(llmsUrl);

                    if (copySuccess) {
                        // Update button text
                        const originalText = button.textContent;
                        button.textContent = '✓ Copied! ✓';
                        button.style.color = 'var(--mantine-color-teal-6)';

                        // Restore original text after 2 seconds
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.style.color = '';
                        }, 2000);

                        console.log('URL copied to clipboard:', llmsUrl);
                    } else {
                        throw new Error('All copy methods failed');
                    }
                } catch (err) {
                    console.error('Failed to copy:', err);

                    // Show error feedback
                    const originalText = button.textContent;
                    button.textContent = '❌ Failed';
                    button.style.color = 'var(--mantine-color-red-6)';

                    setTimeout(() => {
                        button.textContent = originalText;
                        button.style.color = '';
                    }, 2000);
                }
            });

            console.log('Copy button setup for:', button.id);
        });
    }

    // Function to setup llms.toon buttons
    function setupToonButtons() {
        // Find all TOON buttons by class and by ID prefix
        const buttonsByClass = document.querySelectorAll('.llms-toon-button');
        const buttonsById = document.querySelectorAll('[id^="llms-toon-button-"]');

        // Combine both selections
        const allButtons = new Set([...buttonsByClass, ...buttonsById]);

        console.log(`Found ${allButtons.size} TOON buttons to setup`);

        allButtons.forEach(button => {
            // Skip if already setup
            if (button.dataset.toonSetup) return;
            button.dataset.toonSetup = 'true';

            // Add click handler
            button.addEventListener('click', async function(e) {
                e.preventDefault();
                e.stopPropagation();

                try {
                    // Get current page URL
                    const currentPath = window.location.pathname;

                    // Construct llms.toon URL
                    // Remove trailing slash if present
                    const cleanPath = currentPath.endsWith('/')
                        ? currentPath.slice(0, -1)
                        : currentPath;

                    // Build full URL
                    const toonUrl = `${window.location.origin}${cleanPath}/llms.toon`;

                    // Copy to clipboard
                    const copySuccess = await copyToClipboard(toonUrl);

                    if (copySuccess) {
                        // Update button text
                        const originalText = button.textContent;
                        button.textContent = '✓ Copied! ✓';
                        button.style.color = 'var(--mantine-color-teal-6)';

                        // Restore original text after 2 seconds
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.style.color = '';
                        }, 2000);

                        console.log('URL copied to clipboard:', toonUrl);
                    } else {
                        throw new Error('All copy methods failed');
                    }
                } catch (err) {
                    console.error('Failed to copy:', err);

                    // Show error feedback
                    const originalText = button.textContent;
                    button.textContent = '❌ Failed';
                    button.style.color = 'var(--mantine-color-red-6)';

                    setTimeout(() => {
                        button.textContent = originalText;
                        button.style.color = '';
                    }, 2000);
                }
            });

            console.log('TOON button setup for:', button.id);
        });
    }

    // Function to setup page.json buttons
    function setupPageJsonButtons() {
        // Find all page.json buttons by class and by ID prefix
        const buttonsByClass = document.querySelectorAll('.page-json-button');
        const buttonsById = document.querySelectorAll('[id^="page-json-button-"]');

        // Combine both selections
        const allButtons = new Set([...buttonsByClass, ...buttonsById]);

        console.log(`Found ${allButtons.size} page.json buttons to setup`);

        allButtons.forEach(button => {
            // Skip if already setup
            if (button.dataset.jsonSetup) return;
            button.dataset.jsonSetup = 'true';

            // Add click handler
            button.addEventListener('click', async function(e) {
                e.preventDefault();
                e.stopPropagation();

                try {
                    // Get current page URL
                    const currentPath = window.location.pathname;

                    // Construct page.json URL
                    // Remove trailing slash if present
                    const cleanPath = currentPath.endsWith('/')
                        ? currentPath.slice(0, -1)
                        : currentPath;

                    // Build full URL
                    const pageJsonUrl = `${window.location.origin}${cleanPath}/page.json`;

                    // Copy to clipboard
                    const copySuccess = await copyToClipboard(pageJsonUrl);

                    if (copySuccess) {
                        // Update button text
                        const originalText = button.textContent;
                        button.textContent = '✓ Copied! ✓';
                        button.style.color = 'var(--mantine-color-teal-6)';

                        // Restore original text after 2 seconds
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.style.color = '';
                        }, 2000);

                        console.log('URL copied to clipboard:', pageJsonUrl);
                    } else {
                        throw new Error('All copy methods failed');
                    }
                } catch (err) {
                    console.error('Failed to copy:', err);

                    // Show error feedback
                    const originalText = button.textContent;
                    button.textContent = '❌ Failed';
                    button.style.color = 'var(--mantine-color-red-6)';

                    setTimeout(() => {
                        button.textContent = originalText;
                        button.style.color = '';
                    }, 2000);
                }
            });

            console.log('Page JSON button setup for:', button.id);
        });
    }

    // Initial setup for all button types
    setupCopyButtons();
    setupToonButtons();
    setupPageJsonButtons();

    // Delayed setup for Dash-rendered content
    setTimeout(() => {
        setupCopyButtons();
        setupToonButtons();
        setupPageJsonButtons();
    }, 500);
    setTimeout(() => {
        setupCopyButtons();
        setupToonButtons();
        setupPageJsonButtons();
    }, 1000);
    setTimeout(() => {
        setupCopyButtons();
        setupToonButtons();
        setupPageJsonButtons();
    }, 2000);

    // Re-run setup when Dash updates the page (for navigation)
    const observer = new MutationObserver(function(mutations) {
        // Debounce the setup calls
        clearTimeout(window.llmsCopyTimeout);
        window.llmsCopyTimeout = setTimeout(() => {
            setupCopyButtons();
            setupToonButtons();
            setupPageJsonButtons();
        }, 100);
    });

    // Observe the main content area for changes
    const targetNode = document.getElementById('_pages_content') || document.body;
    observer.observe(targetNode, {
        childList: true,
        subtree: true
    });

    console.log('LLM Copy, TOON, and Page JSON buttons observer active');
});
