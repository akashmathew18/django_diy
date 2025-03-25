// Like/Dislike functionality
function handleLikeDislike(postSlug, action) {
    const url = action === 'like' ? `/post/${postSlug}/like/` : `/post/${postSlug}/dislike/`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const likeBtn = document.querySelector(`#like-btn-${postSlug}`);
    const dislikeBtn = document.querySelector(`#dislike-btn-${postSlug}`);
    const likesCount = document.querySelector(`#likes-count-${postSlug}`);
    const dislikesCount = document.querySelector(`#dislikes-count-${postSlug}`);

    // Add loading state
    const actionBtn = action === 'like' ? likeBtn : dislikeBtn;
    actionBtn.classList.add('loading');
    actionBtn.disabled = true;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (action === 'like') {
            likeBtn.classList.toggle('liked', data.liked);
            dislikeBtn.classList.remove('disliked');
        } else {
            dislikeBtn.classList.toggle('disliked', data.disliked);
            likeBtn.classList.remove('liked');
        }

        likesCount.textContent = data.likes_count;
        dislikesCount.textContent = data.dislikes_count;

        // Show success message
        showToast('success', action === 'like' ? 
            (data.liked ? 'Post liked!' : 'Like removed!') : 
            (data.disliked ? 'Post disliked!' : 'Dislike removed!'));
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('error', 'Something went wrong. Please try again.');
    })
    .finally(() => {
        // Remove loading state
        actionBtn.classList.remove('loading');
        actionBtn.disabled = false;
    });
}

// Toast notification function
function showToast(type, message) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 1050;';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();

    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Comment reply functionality
function showReplyForm(commentId) {
    const replyForm = document.querySelector(`#reply-form-${commentId}`);
    replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
}

// Profile image preview
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.querySelector('#profile-image-preview').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Post image preview
function previewPostImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.querySelector('#post-image-preview').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Search functionality
const searchForm = document.querySelector('#search-form');
if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
        const searchInput = document.querySelector('#search-input');
        if (!searchInput.value.trim()) {
            e.preventDefault();
        }
    });
}

// Infinite scroll for posts
let loading = false;
let page = 2;

window.addEventListener('scroll', function() {
    if (loading) return;

    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
        loading = true;
        
        fetch(`?page=${page}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const posts = doc.querySelector('#posts-container');
            
            if (posts) {
                document.querySelector('#posts-container').insertAdjacentHTML('beforeend', posts.innerHTML);
                page++;
                loading = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loading = false;
        });
    }
});

// Bootstrap tooltips initialization
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}); 