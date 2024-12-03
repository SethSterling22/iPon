// JavaScript to handle modal display and functionality
document.addEventListener('DOMContentLoaded', function() {
    // Handle route button click
    const routeButton = document.getElementById('route-btn');
    if (routeButton) {
        routeButton.addEventListener('click', function() {
            const fromLocation = document.getElementById('source').value;
            const toLocation = document.getElementById('destination').value;

            if (fromLocation && toLocation) {
                document.getElementById('from-location').innerText = fromLocation;
                document.getElementById('to-location').innerText = toLocation;
                document.getElementById('ride-popup').style.display = 'block'; // Show the modal
            } else {
                alert('Please enter both locations.');
            }
        });
    }

    // Close modal function
    function closePopup() {
        const modal = document.getElementById('ride-popup');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    // Close button event listener
    const closeButton = document.querySelector('.close');
    if (closeButton) {
        closeButton.addEventListener('click', closePopup);
    }

    // Publish button event listener
    const publishButton = document.getElementById('publish-btn');
    if (publishButton) {
        publishButton.addEventListener('click', function() {
            const from = document.getElementById('from-location').innerText;
            const to = document.getElementById('to-location').innerText;
            const numberOfPeople = document.getElementById('num-people').value;

            // Send data to the server using fetch
            const data = {
                from_location: from,
                to_location: to,
                number_of_people: numberOfPeople,
            };

            fetch("{% url 'publish_pon' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}',  // Include CSRF token for security
                },
                body: JSON.stringify(data),
            })
            .then(response => {
                if (response.ok) {
                    alert('Ride published successfully!');
                    closePopup(); // Close the modal after publishing
                } else {
                    return response.json().then(errorData => {
                        alert('Failed to publish ride: ' + errorData.error);
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while publishing the ride.');
            });
        });
    }
});