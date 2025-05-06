
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const langLinks = document.querySelectorAll('.lang-link');
        langLinks.forEach(link => {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                const currentHash = window.location.hash;
                const targetPage = this.getAttribute('href');
                let newUrl = targetPage;
                if (currentHash) {
                    newUrl += currentHash;
                }
                window.location.href = newUrl;
            });
        });

        // Mobile menu toggle script (copied from original)
        const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
        const nav = document.querySelector('nav');
        
        if (mobileMenuToggle && nav) { // Ensure elements exist
            mobileMenuToggle.addEventListener('click', function() {
                nav.classList.toggle('active');
            });
        }
        
        // Close mobile menu on link click (copied from original)
        const navLinks = document.querySelectorAll('nav ul li a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (nav) { // Ensure nav exists
                    nav.classList.remove('active');
                }
            });
        });
    });

    // Calculation script (placeholder, as original content is unknown)
    function navigateToCalculation(param) {
        console.log("Navigate to calculation with: ", param);
        // Placeholder for actual navigation or modal logic
    }
</script>

