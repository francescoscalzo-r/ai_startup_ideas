// JavaScript personalizzato per Startup Explorer

document.addEventListener('DOMContentLoaded', function() {
    // Inizializza i tooltip di Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Gestione dei like con AJAX
    const likeButtons = document.querySelectorAll('.like-button');
    if (likeButtons.length > 0) {
        likeButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const form = this.closest('form');
                const url = form.getAttribute('action');
                
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': form.querySelector('input[name="csrfmiddlewaretoken"]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Aggiorna il conteggio dei like
                    const likeCount = this.closest('.idea-item').querySelector('.like-count');
                    if (likeCount) {
                        likeCount.textContent = data.likes_count;
                    }
                    
                    // Aggiorna lo stato del pulsante
                    if (data.user_liked) {
                        this.innerHTML = '<i class="fas fa-thumbs-down"></i> Rimuovi like';
                        this.classList.remove('btn-success');
                        this.classList.add('btn-danger');
                    } else {
                        this.innerHTML = '<i class="fas fa-thumbs-up"></i> Metti like';
                        this.classList.remove('btn-danger');
                        this.classList.add('btn-success');
                    }
                    
                    // Aggiorna il conteggio dei like disponibili nella navbar
                    const likesAvailable = document.querySelector('.likes-available');
                    if (likesAvailable) {
                        likesAvailable.textContent = data.likes_disponibili;
                    }
                    
                    // Mostra un messaggio di feedback
                    const message = data.user_liked ? 
                        'Like aggiunto con successo!' : 
                        'Like rimosso con successo!';
                    
                    showAlert(message, data.user_liked ? 'success' : 'info');
                })
                .catch(error => {
                    console.error('Errore:', error);
                    showAlert('Si è verificato un errore. Riprova più tardi.', 'danger');
                });
            });
        });
    }
    
    // Funzione per mostrare alert
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Rimuovi l'alert dopo 3 secondi
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, 3000);
    }
    
    // Gestione dei filtri dinamici
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        const filterInputs = filterForm.querySelectorAll('select, input');
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }
    
    // Animazione per le card
    const cards = document.querySelectorAll('.card');
    if (cards.length > 0) {
        window.addEventListener('scroll', function() {
            cards.forEach(card => {
                const cardPosition = card.getBoundingClientRect().top;
                const screenPosition = window.innerHeight / 1.3;
                
                if (cardPosition < screenPosition) {
                    card.classList.add('animate__animated', 'animate__fadeInUp');
                }
            });
        });
    }
});
