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
    const commentTextarea = commentForm?.querySelector('textarea[name="content"]');
    const parentInput = document.getElementById('comment-parent-id');
    
    // Set initial placeholder
    if (commentTextarea) {
        commentTextarea.placeholder = "Write a comment...";
    }

    // Handle reply button clicks
    document.body.addEventListener('click', function(e) {
        if (e.target.classList.contains('reply-toggle')) {
            const commentEl = e.target.closest('.comment');
            const author = commentEl.dataset.authorUsername;
            const commentId = commentEl.dataset.commentId;
            
            parentInput.value = commentId;
            commentTextarea.placeholder = `Replying to @${author}...`;
            commentTextarea.focus();
        }
    });

    // Handle form submission
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            // Guest users: show modal
            if (commentForm.hasAttribute('data-guest')) {
                e.preventDefault();
                document.getElementById('auth-modal').style.display = 'flex';
                return;
            }

            e.preventDefault();
            const url = parentInput.value 
                ? commentForm.dataset.url.replace(/\/comment\/$/, `/comment/${parentInput.value}/reply/`)
                : commentForm.dataset.url;

            const formData = new FormData(commentForm);
            
            fetch(url, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.html) {
                    const parentId = parentInput.value;                    

                    // Reset form
                    commentTextarea.value = '';
                    parentInput.value = '';
                    commentTextarea.placeholder = "Share your thoughts...";

                    // Insert comment in correct place
                    if (parentId) {
                        // Find parent and append to its replies
                        const parentComment = document.querySelector(`.comment[data-comment-id="${parentInput.value}"]`);
                        if (parentComment) {
                            const repliesDiv = parentComment.querySelector('.replies');
                            repliesDiv.insertAdjacentHTML('beforeend', data.html);
                        }
                    } else {
                        // Add to top of main comment list
                        document.getElementById('comment-list').insertAdjacentHTML('afterbegin', data.html);
                    }
                }
            })
            .catch(err => {
                console.error('Comment error:', err);
                alert('Failed to post comment. Please try again.');;
            });
        });
    }

    // Close modal
    document.addEventListener('click', function(e) {
        const modal = document.getElementById('auth-modal');
        if (e.target.classList.contains('close-modal') || e.target === modal) {
            modal.style.display = 'none';
        }
    });
});