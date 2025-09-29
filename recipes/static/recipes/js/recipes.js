// This script enables interactive star rating and comment AJAX for recipe_detail.html
document.addEventListener('DOMContentLoaded', function () {
    // STAR RATING INPUT (supports -5 to +5)
    const starRatingInput = document.querySelector('.star-rating-input');
    const ratingInput = document.getElementById('rating-input');
    const liveRating = document.getElementById('live-rating');
    const submitRatingBtn = document.getElementById('submit-rating-btn');

    if (starRatingInput && ratingInput && liveRating) {
        const stars = starRatingInput.querySelectorAll('.star');

        function updateStars(selectedValue) {
            stars.forEach(star => {
                const value = parseInt(star.getAttribute('data-value'));
                star.classList.remove('selected');
                if (value === selectedValue) {
                    star.classList.add('selected');
                }
            });
            ratingInput.value = selectedValue;
            liveRating.textContent = selectedValue.toFixed(1);
        }

        stars.forEach(star => {
            star.addEventListener('click', function () {
                const value = parseInt(this.getAttribute('data-value'));
                updateStars(value);
            });
        });

        // Optional: show hover preview
        stars.forEach(star => {
            star.addEventListener('mouseenter', function () {
                const value = parseInt(this.getAttribute('data-value'));
                stars.forEach(s => {
                    s.classList.remove('hovered');
                    if (parseInt(s.getAttribute('data-value')) === value) {
                        s.classList.add('hovered');
                    }
                });
            });
            star.addEventListener('mouseleave', function () {
                stars.forEach(s => s.classList.remove('hovered'));
            });
        });

        // Set initial value
        updateStars(0);

        // Handle rating submission (AJAX or form POST)
        submitRatingBtn.addEventListener('click', function (e) {
            e.preventDefault();
            // TODO: Implement AJAX POST or submit form with ratingInput.value
            alert('Rating submitted: ' + ratingInput.value);
        });
    }

    // COMMENTS AJAX SUBMIT
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function (e) {
            // Check if user is a guest
            if (commentForm.hasAttribute('data-guest')) {
                e.preventDefault();
                document.getElementById('auth-modal').style.display = 'flex';
                return;
            }

            e.preventDefault();
            const url = commentForm.getAttribute('data-url');
            const formData = new FormData(commentForm);

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.comment_html) {
                    // Prepend new comment
                    const commentList = document.getElementById('comment-list');
                    commentList.insertAdjacentHTML('afterbegin', data.comment_html);
                    commentForm.reset();
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(() => {
                alert('Error submitting comment.');
            });
        });
    }

    // Close modal when clicking X or outside
    document.addEventListener('click', function(e) {
        const modal = document.getElementById('auth-modal');
        if (e.target.classList.contains('close-modal') || e.target === modal) {
            modal.style.display = 'none';
        }
    });
});