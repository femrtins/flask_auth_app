document.getElementById('botao-editar-perfil').addEventListener('click', function() {
    var content = document.getElementById('editar-perfil');
    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
    } else {
        content.style.display = 'none';
    }
});

