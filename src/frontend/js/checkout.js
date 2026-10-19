// ============================================================
// WEBLUE - CHECKOUT
// ============================================================
//
// Este script consolida o carrinho em uma compra real,
// coleta os dados do cliente e envia a compra para a API.
// O resultado é um pedido pago com simulação de aprovação.
// ============================================================

const CHAVE_CARRINHO = "weblue-carrinho";
const CHAVE_EMAIL = "weblue-ultimo-email";
const resumoCheckout = document.getElementById("resumoCheckout");
const totalCheckout = document.getElementById("totalCheckout");
const formCheckout = document.getElementById("formCheckout");
const metodoPagamento = document.getElementById("metodoPagamento");
const campoCartao = document.getElementById("campoCartao");

function obterCarrinho() {
    try {
        const valor = localStorage.getItem(CHAVE_CARRINHO);
        return valor ? JSON.parse(valor) : [];
    } catch (erro) {
        console.error("Erro ao ler carrinho.", erro);
        return [];
    }
}

function formatarPreco(valor) {
    return new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
    }).format(Number(valor || 0));
}

function renderResumo() {
    const carrinho = obterCarrinho();
    if (!resumoCheckout) {
        return;
    }

    if (!carrinho.length) {
        resumoCheckout.innerHTML = "<p>Seu carrinho está vazio.</p>";
        if (totalCheckout) {
            totalCheckout.textContent = "R$ 0,00";
        }
        return;
    }

    let total = 0;
    resumoCheckout.innerHTML = carrinho
        .map((item) => {
            const subtotal = Number(item.preco || 0) * Number(item.quantidade || 0);
            total += subtotal;
            return `
                <div class="resumo-item">
                    <span>${item.quantidade}x ${item.nome}</span>
                    <strong>${formatarPreco(subtotal)}</strong>
                </div>
            `;
        })
        .join("");

    if (totalCheckout) {
        totalCheckout.textContent = formatarPreco(total);
    }
}

if (metodoPagamento) {
    const atualizarCampoCartao = () => {
        if (campoCartao) {
            campoCartao.classList.toggle("hidden", metodoPagamento.value !== "CARTAO");
        }
    };

    metodoPagamento.addEventListener("change", atualizarCampoCartao);
    atualizarCampoCartao();
}

if (formCheckout) {
    formCheckout.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const carrinho = obterCarrinho();
        if (!carrinho.length) {
            alert("Adicione pelo menos um produto ao carrinho antes de finalizar.");
            return;
        }

        const body = {
            nome: document.getElementById("nome").value.trim(),
            email: document.getElementById("email").value.trim(),
            telefone: document.getElementById("telefone").value.trim(),
            endereco: document.getElementById("endereco").value.trim(),
            metodo_pagamento: metodoPagamento.value,
            numero_cartao: document.getElementById("numeroCartao").value.trim(),
            itens: carrinho.map((item) => ({
                produto_id: Number(item.id),
                quantidade: Number(item.quantidade || 1),
            })),
        };

        localStorage.setItem(CHAVE_EMAIL, body.email);

        try {
            const resposta = await fetch("/api/pedidos/checkout", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(body),
            });

            const dados = await resposta.json();

            if (!resposta.ok) {
                throw new Error(dados.detail || "Não foi possível confirmar a compra.");
            }

            localStorage.removeItem(CHAVE_CARRINHO);
            window.location.href = "/pedidos";
        } catch (erro) {
            console.error("Erro ao confirmar compra.", erro);
            alert(erro.message || "Erro ao confirmar a compra.");
        }
    });
}

renderResumo();
