// ao clicar em editar perfil: caixa de edição surge
document.getElementById('botao-editar-perfil').addEventListener('click', function() {
    var conteudo = document.getElementById('editar-perfil');
    if (conteudo.style.display === 'none' || conteudo.style.display === '') {
        conteudo.style.display = 'block';
    } else {
        conteudo.style.display = 'none';
    }
});

// mudar fundo do botao da search page

function apareceDiv(int){

    var div = document.getElementById();
}

// Ao clica no botao editar
document.addEventListener('DOMContentLoaded', function() {
    var editarButtons = document.querySelectorAll('.editar-post');

    editarButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var postPedido = this.closest('.post-pedido');

            var blocoPostMain = postPedido.querySelector('.bloco-post-main');
            var editPostMain = postPedido.querySelector('.edit-post-main');
            var editButton = postPedido.querySelector('.editar-post');

            blocoPostMain.style.display = 'none';
            editButton.style.display = 'none';
            editPostMain.style.display = 'block';
        });
    });
});



// mensagem do flash desaparece em 3 segundos
window.onload = function() {
    var flashMessage = document.getElementById('flash-message');
    if (flashMessage) {
        flashMessage.style.display = 'block';
        setTimeout(function() {
            flashMessage.style.display = 'none';
        }, 3000);
    }
    
};


// caixa de comentário aumenta conforme seu conteudo
document.addEventListener('DOMContentLoaded', function() {
    const caixas = document.querySelectorAll('.post');

    caixas.forEach(function(caixa) {
        caixa.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });

        // Inicializa a altura
        caixa.style.height = caixa.scrollHeight + 'px';
    });
});


function irPara(url) {
    window.location.href = url;
}
