function typeWriter(element, text, i, interval, callback) {
    if (i < text.length) {
        element.innerHTML += text.charAt(i);
        i++;
        setTimeout(function() {
            typeWriter(element, text, i, interval, callback);
        }, interval);
    } else if (callback) {
        callback(); // Call the callback function if provided
    }
}

function animateHealthMessage() {
    var typewriterHealthMessage = document.getElementById('typewriter-health-message');
    if (typewriterHealthMessage) {
        var healthText = typewriterHealthMessage.getAttribute('data-text');
        typeWriter(typewriterHealthMessage, healthText, 0, 25, function() {
            // Typing is done, remove the cursor
            typewriterHealthMessage.style.borderRight = 'none';
        });
    }
}

// Start the animation when the document is fully loaded
document.addEventListener('DOMContentLoaded', animateHealthMessage);
