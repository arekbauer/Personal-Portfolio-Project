import { annotate, annotationGroup  } from './rough-notation.esm.js';

let blueClear = '#233554';
let lighterBlue = '#CCD6F6';
let annotationGroupInstance = null;

let lightmode = localStorage.getItem('lightmode')
const themeSwitch = document.getElementById('theme-switch')

// Runs when lightmode is enabled
const enableLightmode = () => {
    document.body.classList.add('lightmode')
    localStorage.setItem('lightmode', 'active')
    blueClear = '#4ed3c1';
    lighterBlue = '#000000';
}

// Runs when lightmode is disabled
const disableLightmode = () => {
    document.body.classList.remove('lightmode')
    localStorage.setItem('lightmode', null)
    blueClear = '#233554';
    lighterBlue = '#CCD6F6';
}

// Checks memory if lightmode was active last
if(lightmode === "active") enableLightmode()


// When my lightmode/darkmode button is clicked...
themeSwitch.addEventListener("click", () => {
    lightmode = localStorage.getItem('lightmode')
    lightmode !== "active" ? enableLightmode() : disableLightmode()
    removeAnnotations();
    roughNotionFunction();
})

// My Rough Notation handler
function roughNotionFunction() {
    // Define variables
    const textAnnotations = [];

    const title = document.querySelector('.highlight');
    const elements = document.querySelectorAll('.about-me span');

    // Define animations
    elements.forEach(element => {
        
        const annotation = annotate(element, { 
            type: 'highlight', 
            color: blueClear,
            iterations: 1,
        });
        textAnnotations.push(annotation);
    });

    const a1 = annotate(title, { 
        type: 'underline', 
        color: lighterBlue, 
        padding: 0
    });

    // Combine all annotations into one group
    const allAnnotations = [a1, ...textAnnotations ];

    // Show the annotation group with animation
    annotationGroupInstance = annotationGroup(allAnnotations);
    annotationGroupInstance.show(); 
}

// Checks if there are any current active annotations
function removeAnnotations() {
    if (annotationGroupInstance) {
        annotationGroupInstance.hide();
        annotationGroupInstance = null;
    }
}

// Controls the filter buttons on my projects section
function projectsFunction() {
    const iso = new Isotope('.projects-grid');
    const filterButtons = Array.prototype.slice.call(document.querySelectorAll('.filter-button'));

    filterButtons.map(button => {
        button.addEventListener('click', function() {
        filterButtons.map(button => button.classList.remove('active-filter'));
        const type = this.getAttribute('data-filter');
        this.classList.add('active-filter');
        iso.arrange({
            // item element provided as argument
            filter: type && `.${type}`
        });
        iso.layout();
        });
    });
}

window.addEventListener('load', () => {
    roughNotionFunction();
    projectsFunction();
})
