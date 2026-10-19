// ============================================================
// WEBLUE - CARRINHO DE COMPRAS
// ============================================================
//
// Este script gerencia a lista de itens que o cliente adicionou
// na home e calcula o total para o checkout.
// O carrinho é persistido no localStorage do navegador.
// ============================================================

const CHAVE_CARRINHO = "weblue-carrinho";
const listaCarrinho = document.getElementById("listaCarrinho");
const mensagemCarrinho = document.getElementById("mensagemCarrinho");
const quantidadeItens = document.getElementById("quantidadeItens");
const totalCarrinho = document.getElementById("totalCarrinho");

function obterCarrinho() {
    try {
        const carrinhoSalvo = localStorage.getItem(CHAVE_CARRINHO);
        return carrinhoSalvo ? JSON.parse(carrinhoSalvo) : [];
    } catch (erro) {
        console.error("Não foi possível ler o carrinho.", erro);
        return [];
    }
}

function salvarCarrinho(carrinho) {
    localStorage.setItem(CHAVE_CARRINHO, JSON.stringify(carrinho));
}

function formatarPreco(valor) {
    return new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
    }).format(Number(valor || 0));
}

function atualizarContadorCarrinho() {
    const carrinho = obterCarrinho();
    const total = carrinho.reduce((soma, item) => soma + Number(item.quantidade || 0), 0);
    const contador = document.getElementById("contadorCarrinho");
    if (contador) {
        contador.textContent = String(total);
    }
}

function alterarQuantidade(produtoId, delta) {
    const carrinho = obterCarrinho();
    const item = carrinho.find((produto) => produto.id === produtoId);

    if (!item) {
        return;
    }

    item.quantidade = Math.max(1, Number(item.quantidade || 1) + delta);
    salvarCarrinho(carrinho);
    renderCarrinho();
}

function removerDoCarrinho(produtoId) {
    const carrinho = obterCarrinho().filter((produto) => produto.id !== produtoId);
    salvarCarrinho(carrinho);
    renderCarrinho();
}

function renderCarrinho() {
    const carrinho = obterCarrinho();
    atualizarContadorCarrinho();

    if (!listaCarrinho) {
        return;
    }

    if (!carrinho.length) {
        listaCarrinho.innerHTML = "";
        if (mensagemCarrinho) {
            mensagemCarrinho.textContent = "Seu carrinho está vazio. Adicione produtos antes de continuar.";
        }
        if (quantidadeItens) {
            quantidadeItens.textContent = "0 itens";
        }
        if (totalCarrinho) {
            totalCarrinho.textContent = "R$ 0,00";
        }
        return;
    }

    if (mensagemCarrinho) {
        mensagemCarrinho.textContent = "";
    }

    let total = 0;
    let quantidadeTotal = 0;

    listaCarrinho.innerHTML = carrinho
        .map((item) => {
            const subtotal = Number(item.preco || 0) * Number(item.quantidade || 0);
            total += subtotal;
            quantidadeTotal += Number(item.quantidade || 0);

            return `
                <article class="item">
                    <div>
                        <h3>${item.nome || "Produto Weblue"}</h3>
                        <p>${formatarPreco(item.preco || 0)} cada</p>
                        <div class="controls">
                            <button type="button" data-acao="diminuir" data-id="${item.id}">-</button>
                            <span>${item.quantidade}</span>
                            <button type="button" data-acao="aumentar" data-id="${item.id}">+</button>
                            <button type="button" data-acao="remover" data-id="${item.id}" style="background:#f9d3d3;">Remover</button>
                        </div>
                    </div>
                    <strong>${formatarPreco(subtotal)}</strong>
                </article>
            `;
        })
        .join("");

    if (quantidadeItens) {
        quantidadeItens.textContent = `${quantidadeTotal} item${quantidadeTotal === 1 ? "" : "s"}`;
    }

    if (totalCarrinho) {
        totalCarrinho.textContent = formatarPreco(total);
    }

    document.querySelectorAll("[data-acao]").forEach((botao) => {
        const acao = botao.dataset.acao;
        const produtoId = Number(botao.dataset.id);

        botao.addEventListener("click", () => {
            if (acao === "aumentar") {
                alterarQuantidade(produtoId, 1);
            }

            if (acao === "diminuir") {
                alterarQuantidade(produtoId, -1);
            }

            if (acao === "remover") {
                removerDoCarrinho(produtoId);
            }
        });
    });
}

renderCarrinho();
