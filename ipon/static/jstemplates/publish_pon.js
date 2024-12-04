// JavaScript to handle modal display and functionality
document.addEventListener('DOMContentLoaded', function() {
    // Show the modal when the publish button is clicked
    document.getElementById('route-btn').addEventListener('click', function() {
        const fromLocation = document.getElementById('source').value;  // Adjust to match form fields
        const toLocation = document.getElementById('destination').value;  // Adjust to match form fields
        
        if (fromLocation && toLocation) {
            // Set the modal details
            document.getElementById('from-location').innerText = fromLocation;
            document.getElementById('to-location').innerText = toLocation;

            // Show the modal
            document.getElementById('ride-popup').style.display = 'block';
        } else {
            alert("Please enter both 'From' and 'To' locations.");
        }
    });

    // Confirm and publish ride
    document.getElementById('confirm-publish-btn').addEventListener('click', function() {
        const numberOfPeople = document.getElementById('num-people').value;
        const fromLocation = document.getElementById('source').value;
        const toLocation = document.getElementById('destination').value;

        // Send data to the server using fetch
        const data = {
            from_location: fromLocation,
            to_location: toLocation,
            number_of_people: numberOfPeople,
        };

        console.log("ride data: ", data);

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
                document.getElementById('ride-form').reset(); // Reset the form if needed
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

    // Close modal functionality
    document.querySelector('.close').addEventListener('click', closePopup);

    function closePopup() {
        document.getElementById('ride-popup').style.display = 'none';
    }
});