function form_check(form_id) {
    const data = $(form_id).serializeArray();
    let flag = true
    $.each(data, function (idx, item) {
        if (item.value === "") {
            flag = false;
            return false;
        }
    })
    return {'data': data, 'flag': flag}
}

function submitForm(form_id, url, method) {
    const check_data = form_check(form_id);
    const form_data = check_data['data'];
    $.ajax({
        url: url,
        method: method,
        data: form_data,
        success: function (res) {
            if (res.status) {
                location.reload()
            } else {
                $.each(res.error, function (key, value) {
                    const id_ = $('#id_' + key);
                    setTimeout(function () {
                        id_.popover('hide')
                    }, 3000);
                    id_.attr('data-content', value);
                    id_.popover('show');
                })
            }
        }
    })
}