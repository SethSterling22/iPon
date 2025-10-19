const sidebar = document.getElementById('sidebar')
let isAnimating = false; // Flag to track animation state

const container_footer = document.getElementById('container_footer')

function toggleShow() {

    const overlay = document.querySelector('.overlay');
    const isVisible = sidebar.style.display === 'block';

    overlay.style.display = isVisible ? 'none' : 'block';

    if (isAnimating) return; // Prevent action if an animation is already in progress

    if (sidebar.classList.contains('show')) {
    // If the sidebar is currently shown, hide it
    isAnimating = true; // Set the flag to true
    sidebar.classList.remove('show');
    sidebar.classList.add('hide'); // Trigger hide animation

    // Wait for the animation to complete
    sidebar.addEventListener('animationend', () => {
        sidebar.style.display = 'none'; // Hide it from the document flow
        sidebar.classList.remove('hide'); // Clean up the class
        isAnimating = false; // Reset the flag
    }, { once: true }); // Ensure the listener runs only once
    } else {
    // If the sidebar is currently hidden, show it
    isAnimating = true; // Set the flag to true
    sidebar.style.display = 'block'; // Show the sidebar
    requestAnimationFrame(() => {
        sidebar.classList.add('show'); // Trigger show animation
    });

    // Wait for the animation to complete
    sidebar.addEventListener('animationend', () => {
        isAnimating = false; // Reset the flag
    }, { once: true }); // Ensure the listener runs only once
    }

}

window.addEventListener('resize', () => {
    if (window.innerWidth > 5000) {
        sidebar.style.display = 'block';
    }

});

function toggleShow_make() {
    const popupContainer = document.getElementById('popupContainer');
    
    // Activar el Overlay para hacer efecto de focus
    const overlay = document.querySelector('.overlay_footer');
    const isVisible = popupContainer.style.bottom === '0px';

    overlay.style.display = isVisible ? 'none' : 'block';

    // Verifica el estado actual y ajusta la posición
    if (popupContainer.style.bottom === '0px') {
        popupContainer.style.bottom = '-100%'; // Oculta
    } else {
        popupContainer.style.bottom = '0px'; // Muestra
    }


}

function toggleShow_footer() {
    console.log("holiwi");
    // Activar el Overlay para hacer efecto de focus
    const overlay = document.querySelector('.overlay_footer');
    const isVisible = container_footer.style.display === 'block';

    overlay.style.display = isVisible ? 'none' : 'block';


    // if (isAnimating) return;

    // if (container_footer.classList.contains('show')) {
    // // If the container_footer is currently shown, hide it
    // isAnimating = true; // Set the flag to true
    // container_footer.classList.remove('show');
    // container_footer.classList.add('hide'); // Trigger hide animation

    // // Wait for the animation to complete
    // container_footer.addEventListener('animationend', () => {
    //     container_footer.style.display = 'none'; // Hide it from the document flow
    //     container_footer.classList.remove('hide'); // Clean up the class
    //     isAnimating = false; // Reset the flag
    // }, { once: true }); // Ensure the listener runs only once
    // } else {
    // // If the container_footer is currently hidden, show it
    // isAnimating = true; // Set the flag to true
    // container_footer.style.display = 'block'; // Show the container_footer
    // requestAnimationFrame(() => {
    //     container_footer.classList.add('show'); // Trigger show animation
    // });

    // // Wait for the animation to complete
    // container_footer.addEventListener('animationend', () => {
    //     isAnimating = false; // Reset the flag
    // }, { once: true }); // Ensure the listener runs only once
    // }

}
