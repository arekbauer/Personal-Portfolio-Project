document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.experience-card');
    
    cards.forEach(card => {
      card.addEventListener('click', () => {
        // Collapse any expanded card
        const expandedCard = document.querySelector('.experience-card.expanded');
          if (expandedCard && expandedCard !== card) {
              expandedCard.classList.remove('expanded');
          }
    
        // Toggle the clicked card
        card.classList.toggle('expanded');
        });
      });
    });