function form_check(form_id) {
        const data = $(form_id).serializeArray();
        let flag = true
        $.each(data,function (idx,item) {
            if(item.value==="")
            {
                flag = false;
                return false;
            }
        })
        return {'data':data,'flag':flag}
    }