// Fonction pour initialiser le système de messagerie
function initMessaging() {
    // Auto-scroll des conversations
    const messageContainer = document.querySelector('.message-container');
    if (messageContainer) {
      messageContainer.scrollTop = messageContainer.scrollHeight;
    }
  
    // Envoi de message via AJAX
    const messageForm = document.getElementById('messageForm');
    if (messageForm) {
      messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const submitBtn = this.querySelector('[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        submitBtn.disabled = true;
        
        fetch(this.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Ajouter le nouveau message à la conversation
            const messagesContainer = document.querySelector('.message-container');
            if (messagesContainer) {
              const messageDiv = document.createElement('div');
              messageDiv.className = `mb-3 text-end`;
              messageDiv.innerHTML = `
                <div class="d-flex justify-content-end">
                  <div class="bg-primary text-white p-3 rounded-3" style="max-width: 70%;">
                    <div class="d-flex justify-content-between small mb-1">
                      <strong>Vous</strong>
                      <span class="text-white-50">Juste maintenant</span>
                    </div>
                    <p class="mb-0">${data.message.content}</p>
                  </div>
                </div>
              `;
              messagesContainer.appendChild(messageDiv);
              messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            // Réinitialiser le formulaire
            this.reset();
          } else {
            alert(data.message || 'Erreur lors de l\'envoi du message');
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('Erreur réseau');
        })
        .finally(() => {
          submitBtn.innerHTML = originalText;
          submitBtn.disabled = false;
        });
      });
    }
  
    // Actualisation périodique des messages (toutes les 30 secondes)
    if (window.location.pathname.includes('conversation')) {
      setInterval(() => {
        const conversationId = document.querySelector('.message-container')?.dataset?.conversationId;
        if (!conversationId) return;
        
        fetch(`/messaging/get-updates/${conversationId}/`)
          .then(response => response.json())
          .then(data => {
            if (data.messages && data.messages.length > 0) {
              const messagesContainer = document.querySelector('.message-container');
              data.messages.forEach(msg => {
                // Vérifier si le message existe déjà
                if (!document.querySelector(`[data-message-id="${msg.id}"]`)) {
                  const messageDiv = document.createElement('div');
                  messageDiv.className = `mb-3 ${msg.sender_is_current ? 'text-end' : ''}`;
                  messageDiv.setAttribute('data-message-id', msg.id);
                  messageDiv.innerHTML = `
                    <div class="d-flex ${msg.sender_is_current ? 'justify-content-end' : 'justify-content-start'}">
                      <div class="${msg.sender_is_current ? 'bg-primary text-white' : 'bg-light'} p-3 rounded-3" style="max-width: 70%;">
                        <div class="d-flex justify-content-between small mb-1">
                          <strong>${msg.sender_name}</strong>
                          <span class="${msg.sender_is_current ? 'text-white-50' : 'text-muted'}">${msg.timestamp}</span>
                        </div>
                        <p class="mb-0">${msg.content}</p>
                      </div>
                    </div>
                  `;
                  messagesContainer.appendChild(messageDiv);
                }
              });
              messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
          })
          .catch(error => console.error('Error fetching new messages:', error));
      }, 30000);
    }
  }
  
  // Initialiser lorsque le DOM est chargé
  document.addEventListener('DOMContentLoaded', initMessaging);