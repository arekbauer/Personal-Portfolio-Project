console.log('Function is running');
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

// Not working, check YouTube vid