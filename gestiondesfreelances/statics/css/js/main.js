// Initialisation des tooltips Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // Tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  
    // Faire défiler les messages vers le bas
    const messageContainers = document.querySelectorAll('.message-container');
    messageContainers.forEach(container => {
      container.scrollTop = container.scrollHeight;
    });
  
    // Confirmation des actions critiques
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        const message = button.getAttribute('data-confirm');
        if (!confirm(message)) {
          e.preventDefault();
        }
      });
    });
  });
  
  // Fonction pour afficher les messages toast
  function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
  
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    `;
  
    toastContainer.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
  
    // Supprimer le toast après fermeture
    toastEl.addEventListener('hidden.bs.toast', function () {
      toastEl.remove();
    });
  }
  
  // Gestion des formulaires AJAX
  document.addEventListener('DOMContentLoaded', function() {
    const ajaxForms = document.querySelectorAll('.ajax-form');
    
    ajaxForms.forEach(form => {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const submitBtn = this.querySelector('[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Afficher le loader
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Traitement...';
        submitBtn.disabled = true;
        
        fetch(this.action, {
          method: this.method,
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            showToast(data.message, 'success');
            if (data.redirect) {
              setTimeout(() => {
                window.location.href = data.redirect;
              }, 1500);
            }
          } else {
            showToast(data.message || 'Une erreur est survenue', 'danger');
          }
        })
        .catch(error => {
          showToast('Erreur réseau', 'danger');
          console.error('Error:', error);
        })
        .finally(() => {
          submitBtn.innerHTML = originalText;
          submitBtn.disabled = false;
        });
      });
    });
  });