// JavaScript per gestire i like con AJAX
document.addEventListener('DOMContentLoaded', function() {
    // Seleziona tutti i pulsanti di like
    const likeButtons = document.querySelectorAll('.like-button');
    
    if (likeButtons.length > 0) {
        likeButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Ottieni il form e l'URL
                const form = this.closest('form');
                const url = form.getAttribute('action');
                const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;
                
                // Effettua la richiesta AJAX
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Aggiorna il conteggio dei like
                    const likeCountElements = document.querySelectorAll(`.like-count-${form.dataset.ideaId}`);
                    likeCountElements.forEach(el => {
                        el.textContent = data.likes_count;
                    });
                    
                    // Aggiorna lo stato del pulsante
                    if (data.user_liked) {
                        button.innerHTML = '<i class="fas fa-thumbs-down"></i> Rimuovi like';
                        button.classList.remove('btn-success');
                        button.classList.add('btn-danger');
                    } else {
                        button.innerHTML = '<i class="fas fa-thumbs-up"></i> Metti like';
                        button.classList.remove('btn-danger');
                        button.classList.add('btn-success');
                    }
                    
                    // Aggiorna il conteggio dei like disponibili nella navbar
                    const likesAvailable = document.querySelector('.likes-available');
                    if (likesAvailable) {
                        likesAvailable.textContent = data.likes_disponibili;
                    }
                    
                    // Mostra un messaggio di feedback
                    showAlert(data.message, data.user_liked ? 'success' : 'info');
                    
                    // Aggiorna eventuali elementi che mostrano i like disponibili
                    const likesDisponibiliElements = document.querySelectorAll('.likes-disponibili');
                    likesDisponibiliElements.forEach(el => {
                        el.textContent = data.likes_disponibili;
                    });
                    
                    // Disabilita il pulsante se non ci sono più like disponibili
                    if (data.likes_disponibili === 0 && !data.user_liked) {
                        const allLikeButtons = document.querySelectorAll('.like-button:not(.liked)');
                        allLikeButtons.forEach(btn => {
                            btn.disabled = true;
                            btn.classList.add('disabled');
                            btn.title = 'Hai esaurito i tuoi 5 like disponibili';
                        });
                    } else {
                        // Riabilita i pulsanti se ci sono like disponibili
                        const allLikeButtons = document.querySelectorAll('.like-button.disabled');
                        allLikeButtons.forEach(btn => {
                            btn.disabled = false;
                            btn.classList.remove('disabled');
                            btn.title = 'Metti like a questa idea';
                        });
                    }
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
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Rimuovi l'alert dopo 3 secondi
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, 3000);
    }
});
