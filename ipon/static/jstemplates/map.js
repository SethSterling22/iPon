let map, directionsService, directionsRenderer;

function initMap() {
    const mapOptions = {
        zoom: 8,
        center: { lat: 18.2208, lng: -66.5901 }, // Puerto Rico coordinates
    };

    // Initialize the map
    map = new google.maps.Map(document.getElementById("map"), mapOptions);

    // Initialize Directions Service and Renderer
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);

    // Set the user's location as the default for "Original Location"
    setUserLocation();
}

function calculateRoute() {
    const source = document.getElementById("source").value;
    const destination = document.getElementById("destination").value;
    const output = document.getElementById("route-info"); // Element to display route info

    if (source && destination) {
        const request = {
            origin: source,
            destination: destination,
            travelMode: google.maps.TravelMode.DRIVING, // Options: DRIVING, WALKING, BICYCLING, TRANSIT
        };

        directionsService.route(request, function (result, status) {
            if (status === google.maps.DirectionsStatus.OK) {
                directionsRenderer.setDirections(result);

                // Get travel time and distance from the first route leg
                const route = result.routes[0].legs[0];
                const duration = route.duration.text; 
                const distanceKm = route.distance.value / 1000; // Convert meters to kilometers
                const distanceMiles = (distanceKm * 0.621371).toFixed(2);

                // Display the route time and distance
                output.innerHTML = `<p>Travel Time: ${duration}</p><p>Distance: ${distanceMiles} mi</p>`;
                output.style.display = "flex"; // Ensure it's visible
            } else {
                alert("Could not calculate route: " + status);
                output.innerHTML = ""; // Clear output on failure
                output.style.display = "none"; // Hide the element
            }
        });
    } else {
        alert("Please enter both source and destination!");
        output.style.display = "none"; // Hide the element
    }
}

function setUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;

                // Use reverse geocoding to convert coordinates to an address
                const geocoder = new google.maps.Geocoder();
                const latlng = { lat: lat, lng: lng };

                geocoder.geocode({ location: latlng }, (results, status) => {
                    if (status === google.maps.GeocoderStatus.OK) {
                        if (results[0]) {
                            document.getElementById("source").value = results[0].formatted_address;
                        } else {
                            console.log("No results found for the location.");
                        }
                    } else {
                        console.log("Geocoder failed due to: " + status);
                    }
                });
            },
            (error) => {
                console.log("Error retrieving location: " + error.message);
            }
        );
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

document.getElementById("route-btn").addEventListener("click", calculateRoute);

// Initialize the map after the page loads
window.onload = initMap;

