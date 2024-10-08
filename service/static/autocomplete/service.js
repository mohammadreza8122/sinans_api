document.addEventListener('DOMContentLoaded', function() {
    if (typeof $.fn.select2 === 'undefined') {
        console.error("Select2 is not loaded. Please check the CDN or file path.");
        return;
    }
    let searchValue = ''
    console.log(window.location.pathname)
    console.log('*********************88')
    const page_path  = window.location.pathname
    if (page_path.includes('homecarecategory')) {
                end_point = '/service/category-autocomplete/';
    } else {
         end_point = '/service/service-autocomplete/';
    }
    console.log(end_point)
    const searchInput = document.querySelector('input[name=q]');
    if (searchInput) {
        searchInput.setAttribute('id', 'autocomplete-input');
        $('#autocomplete-input').select2({
            ajax: {
                url: end_point,  // آدرس ویو autocomplete
                dataType: 'json',
                delay: 500,  // دیبونس با 500 میلی‌ثانیه
                data: function (params) {
                    return {
                        q: params.term
                    };
                },
                processResults: function (data) {
                    searchValue = data.query
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
            'font-size': '206px'
        });
        $('#autocomplete-input').on('select2:select', function (e) {
            const selectedValue = e.params.data.id;
            const searchUrl = window.location.origin + window.location.pathname + selectedValue + '/change/';
            window.location.href = searchUrl;
        });

        const searchButton = document.getElementsByClassName('btn btn-outline-primary');
        for (let i = 0; i < searchButton.length; i++) {
        searchButton[i].addEventListener('click', function() {
            event.preventDefault();
            const searchUrl = window.location.origin + window.location.pathname + '?q=' + searchValue ;
            window.location.href = searchUrl;
        });
    }
}
});


