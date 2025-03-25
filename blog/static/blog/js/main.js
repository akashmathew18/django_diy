// Function to preview profile image before upload
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            document.getElementById('profile-image-preview').src = e.target.result;
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Fetch all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');

    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Password match validation
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');

    if (password1 && password2) {
        password2.addEventListener('input', function() {
            if (password1.value !== password2.value) {
                password2.setCustomValidity("Passwords do not match");
            } else {
                password2.setCustomValidity("");
            }
        });

        password1.addEventListener('input', function() {
            if (password1.value !== password2.value) {
                password2.setCustomValidity("Passwords do not match");
            } else {
                password2.setCustomValidity("");
            }
        });
    }
}); 