import { annotate, annotationGroup  } from './rough-notation.esm.js';

const colours = {
    darkestBlue: '#0A192F',
    midBlue: '#112240',
    lightBlue: '#8892B0',
    lighterBlue: '#CCD6F6',
    lightestBlue: '#E6F1FF',
    clearBlue: '#94A3B8',
    cream: '#64FFDA',
    bluey: '#ccd6f6',
    blueClear: '#233554'
};

let lightmode = localStorage.getItem('lightmode')
const themeSwitch = document.getElementById('theme-switch')

const enableLightmode = () => {
    document.body.classList.add('lightmode')
    localStorage.setItem('lightmode', 'active')
}

const disableLightmode = () => {
    document.body.classList.remove('lightmode')
    localStorage.setItem('lightmode', null)
}

if(lightmode === "active") enableLightmode()

themeSwitch.addEventListener("click", () => {
    lightmode = localStorage.getItem('lightmode')
    lightmode !== "active" ? enableLightmode() : disableLightmode()
})

function roughNotionFunction() {
    // Define variables
    const textAnnotations = [];

    const title = document.querySelector('.highlight');
    const elements = document.querySelectorAll('.about-me span');

    // Define animations
    elements.forEach(element => {
        
        const annotation = annotate(element, { 
            type: 'highlight', 
            color: colours.blueClear,
            iterations: 1,
        });
        textAnnotations.push(annotation);
    });

    const a1 = annotate(title, { 
        type: 'underline', 
        color: colours.lighterBlue, 
        padding: 0
    });

    // Combine all annotations into one group
    const allAnnotations = [a1, ...textAnnotations ];

    // Show the annotation group with animation
    const ag = annotationGroup(allAnnotations);
    //ag.show(); 
}

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

window.addEventListener('load', roughNotionFunction);
window.addEventListener('load', projectsFunction);