function changeImage(f) {
    let thumbID = f.id.slice(5, 6);
    $('#fullimage').attr('src', f.src);
}