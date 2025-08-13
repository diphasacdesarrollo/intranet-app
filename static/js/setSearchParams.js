function setParams(elementId, params, url) {
    function addParams(url) {
        if (window.location.search === '') {
            return url + '?' + params
        } else {
            if (window.location.search.startsWith('?page')) {
                return url + '?' + params
            } else {
                if (window.location.search.includes('page')) {
                    let params_list = window.location.search.split('&')
                    let page = params_list[params_list.length - 1]
                    return url + window.location.search.replace(page, params)
                } else {
                    return url + window.location.search + '&' + params
                }
            }
        }
    }
    document.getElementById(elementId).setAttribute('href', addParams(url))
}