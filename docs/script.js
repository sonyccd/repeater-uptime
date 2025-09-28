// Copy code functionality
function copyCode() {
    const codeElement = document.getElementById('install-code');
    const textArea = document.createElement('textarea');
    textArea.value = codeElement.textContent;
    document.body.appendChild(textArea);
    textArea.select();

    try {
        document.execCommand('copy');
        const copyBtn = document.querySelector('.copy-btn');
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        copyBtn.style.background = '#28ca42';

        setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.style.background = '#667eea';
        }, 2000);
    } catch (err) {
        console.error('Failed to copy text: ', err);
    }

    document.body.removeChild(textArea);
}

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for internal links
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add entrance animations when elements come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.feature-card, .step, .requirement-card, .flow-step');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Add staggered animation delay to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.style.transitionDelay = `${index * 0.1}s`;
    });

    // Add hover effect to GitHub link
    const githubLink = document.querySelector('a[href*="github.com"]');
    if (githubLink) {
        githubLink.addEventListener('mouseenter', function() {
            const svg = this.querySelector('svg');
            if (svg) {
                svg.style.transform = 'scale(1.1) rotate(5deg)';
                svg.style.transition = 'transform 0.3s ease';
            }
        });

        githubLink.addEventListener('mouseleave', function() {
            const svg = this.querySelector('svg');
            if (svg) {
                svg.style.transform = 'scale(1) rotate(0deg)';
            }
        });
    }

    // Dynamic spectrum animation enhancement
    const spectrumLines = document.querySelectorAll('.spectrum-line');
    if (spectrumLines.length > 0) {
        setInterval(() => {
            spectrumLines.forEach((line, index) => {
                const randomHeight = Math.random() * 80 + 20; // 20-100%
                line.style.height = randomHeight + '%';
                line.style.animationDelay = (Math.random() * 2) + 's';
            });
        }, 3000);
    }

    // Add parallax effect to hero section
    const hero = document.querySelector('.hero');
    const heroContent = document.querySelector('.hero-content');

    if (hero && heroContent) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;

            if (scrolled < hero.offsetHeight) {
                heroContent.style.transform = `translateY(${rate}px)`;
            }
        });
    }

    // Add typing effect to hero title (optional enhancement)
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const text = heroTitle.textContent;
        heroTitle.textContent = '';

        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };

        // Start typing effect after a short delay
        setTimeout(typeWriter, 500);
    }

    // Add click tracking for analytics (placeholder)
    document.addEventListener('click', function(e) {
        const target = e.target;

        // Track button clicks
        if (target.classList.contains('btn')) {
            console.log(`Button clicked: ${target.textContent.trim()}`);
            // Add analytics tracking here if needed
        }

        // Track feature card interactions
        if (target.closest('.feature-card')) {
            const featureTitle = target.closest('.feature-card').querySelector('h3').textContent;
            console.log(`Feature card viewed: ${featureTitle}`);
            // Add analytics tracking here if needed
        }
    });

    // Add keyboard navigation support
    document.addEventListener('keydown', function(e) {
        // Support Escape key to close any modals or overlays
        if (e.key === 'Escape') {
            // Close any open modals here if implemented
        }

        // Support Tab navigation enhancement
        if (e.key === 'Tab') {
            // Add visible focus indicators for accessibility
            document.body.classList.add('keyboard-navigation');
        }
    });

    // Remove keyboard navigation class on mouse use
    document.addEventListener('mousedown', function() {
        document.body.classList.remove('keyboard-navigation');
    });
});