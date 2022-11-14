function updateQuery(key, value) {
    const searchParams = new URLSearchParams(window.location.search);
    if (key != '')
        searchParams.set(key, value);
    else
        searchParams.delete(key);
    window.location.search = searchParams.toString();
}
