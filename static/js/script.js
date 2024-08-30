
document.getElementById('depositar').addEventListener('click', function() {
    realizarTransacao('Depósito', document.getElementById('valor_deposito').value);
});

document.getElementById('sacar').addEventListener('click', function() {
    realizarTransacao('Saque', document.getElementById('valor_saque').value);
});

function realizarTransacao(tipo, valor) {
    if (valor && valor > 0) {
        var mensagem = tipo + " de R$ " + parseFloat(valor).toFixed(2) + " realizado com sucesso!";
        document.getElementById('mensagem').innerText = mensagem;

        // Adiciona ao histórico
        var historico = document.getElementById('historico');
        var novaTransacao = document.createElement('li');
        var dataHora = new Date().toLocaleString();

        novaTransacao.textContent = tipo + " de R$ " + parseFloat(valor).toFixed(2) + " em " + dataHora;
        historico.appendChild(novaTransacao);
    } else {
        document.getElementById('mensagem').innerText = "Por favor, insira um valor válido.";
    }
}
