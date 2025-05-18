document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('search-form');
    const input = document.getElementById('search-input');
    const suggestionLinks = document.querySelectorAll('.suggestion-link');

    // Khi submit form, chuyển hướng sang /jobs?keyword=...
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const keyword = input.value.trim();
        if (keyword) {
            window.location.href = `/jobs?keyword=${encodeURIComponent(keyword)}`;
        }
    });

    // Khi click vào gợi ý, tự động điền vào ô tìm kiếm và submit
    suggestionLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            input.value = this.dataset.keyword;
            form.dispatchEvent(new Event('submit'));
        });
    });
});