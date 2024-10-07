document.addEventListener('DOMContentLoaded', function() {
    if (typeof $.fn.select2 === 'undefined') {
        console.error("Select2 is not loaded. Please check the CDN or file path.");
        return;
    }

    const searchInput = document.querySelector('input[name=q]');
    if (searchInput) {
        searchInput.setAttribute('id', 'autocomplete-input');
        $('#autocomplete-input').select2({
            ajax: {
                url: '/service/category-autocomplete/',  // آدرس ویو autocomplete
                dataType: 'json',
                delay: 500,  // دیبونس با 500 میلی‌ثانیه
                data: function (params) {
                    return {
                        q: params.term
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.results.slice(0, 100) // محدود به 10 نتیجه
                    };
                }
            },
            minimumInputLength: 1,
            language: {
                noResults: function () {
                    return "No results found";  // پیام در صورت نبود نتیجه
                },
                loadingMore: function () {
                    return 'Loading more results...';  // پیام بارگذاری
                }
            },
            theme: "default",  // تم Select2 (قابل تغییر به bootstrap یا هر تم دیگری)
            multiple: false  // برای انتخاب چندگانه true را تنظیم کنید
        });
        $('#autocomplete-input').css({
            'width': '100%',
            'height': '70px',
            'font-size': '26px'
        });

    }
});
