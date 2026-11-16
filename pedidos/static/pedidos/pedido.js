/* Mostra, antes do envio, quantas fotos o cliente precisa selecionar. */
(function () {
  var dadosEl = document.getElementById("dados-kits");
  var resumo = document.getElementById("resumo-fotos");
  var kit = document.getElementById("id_produto");
  var qtd = document.getElementById("id_quantidade");
  var fotos = document.getElementById("id_fotos");
  if (!dadosEl || !resumo || !kit || !qtd || !fotos) {
    return;
  }
  var kits = JSON.parse(dadosEl.textContent);

  function plural(n) {
    return n === 1 ? "foto" : "fotos";
  }

  function atualizar() {
    var escolhido = kits.find(function (k) {
      return String(k.id) === kit.value;
    });
    var q = parseInt(qtd.value, 10);
    if (!escolhido || !q || q < 1) {
      resumo.textContent = "Escolha o kit e a quantidade para ver quantas fotos enviar.";
      return;
    }
    var total = escolhido.fotos * q;
    var texto = "Você precisa enviar " + total + " " + plural(total) + " (" + q + " × " + escolhido.fotos + ").";
    var enviadas = fotos.files.length;
    if (enviadas === total) {
      texto += " ✔ Você selecionou " + enviadas + " " + plural(enviadas) + ". Está certo!";
    } else if (enviadas > 0 && enviadas < total) {
      texto += " ⚠ Você selecionou " + enviadas + ". Faltam " + (total - enviadas) + ".";
    } else if (enviadas > total) {
      texto += " ⚠ Você selecionou " + enviadas + ". Tire " + (enviadas - total) + ".";
    }
    resumo.textContent = texto;
  }

  kit.addEventListener("change", atualizar);
  qtd.addEventListener("input", atualizar);
  fotos.addEventListener("change", atualizar);
  atualizar();
})();
