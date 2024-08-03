import { annotate, annotationGroup  } from './rough-notation.esm.js';

const colours = {
    darkestBlue: '#0A192F',
    midBlue: '#112240',
    lightBlue: '#8892B0',
    lighterBlue: '#CCD6F6',
    lightestBlue: '#E6F1FF',
    clearBlue: '#94A3B8',
    cream: '#64FFDA'
};

document.addEventListener('DOMContentLoaded', () => {
    const elements = document.querySelectorAll('.about-me span');
    const title = document.querySelector('.left h3');
    const annotations = [];

    elements.forEach(element => {
        const annotation = annotate(element, { type: 'underline', color: colours.cream });
        annotations.push(annotation);
    });

    const a1 = annotate(title, { type: 'highlight', color: colours.cream });
    const ag = annotationGroup(annotations);

    // Show the annotation group with animation
    a1.show();
    ag.show();
});