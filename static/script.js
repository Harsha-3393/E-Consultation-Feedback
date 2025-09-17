document.addEventListener('DOMContentLoaded', () => {

    const addCommentForm = document.getElementById('add-comment-form');
    const analyzeAllBtn = document.getElementById('analyze-all-btn');
    const clearAllBtn = document.getElementById('clear-all-btn');
    const downloadExcelBtn = document.getElementById('download-excel-btn');

    function updateDashboardStats(stats) {
        document.getElementById('total-comments').textContent = stats.total;
        document.getElementById('positive-sentiment').textContent = stats.positive;
        document.getElementById('negative-sentiment').textContent = stats.negative;
        document.getElementById('neutral-sentiment').textContent = stats.neutral;
    }

    if (addCommentForm) {
        addCommentForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const formData = new FormData(this);
            const commentText = formData.get('comment_text');

            if (!commentText.trim()) {
                alert("Please enter a comment.");
                return;
            }

            fetch('/add_comment', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(`Comment added! Sentiment: ${data.sentiment}, Intent: ${data.intent}`);
                    updateDashboardStats(data.stats);
                    this.reset();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    }

    if (analyzeAllBtn) {
        analyzeAllBtn.addEventListener('click', function() {
            if (confirm("This will analyze all comments from the preprocessed data file and add them to the database. Are you sure?")) {
                analyzeAllBtn.disabled = true;
                analyzeAllBtn.textContent = "Analyzing...";

                fetch('/analyze_all', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert(data.message);
                        updateDashboardStats(data.stats);
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred.');
                })
                .finally(() => {
                    analyzeAllBtn.disabled = false;
                    analyzeAllBtn.textContent = "Analyze All Comments";
                });
            }
        });
    }

    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function() {
            if (confirm("Are you sure you want to clear all comments from the database? This action cannot be undone.")) {
                fetch('/clear_comments', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert(data.message);
                        updateDashboardStats({ total: 0, positive: 0, negative: 0, neutral: 0 });
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while clearing comments.');
                });
            }
        });
    }

    if (downloadExcelBtn) {
        downloadExcelBtn.addEventListener('click', function() {
            const clearAfterDownload = confirm("Do you want to clear the database after downloading?");
            window.location.href = `/download_excel?clear=${clearAfterDownload}`;
        });
    }
});