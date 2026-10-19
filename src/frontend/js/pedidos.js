// ============================================================
// WEBLUE - PEDIDOS
// ============================================================
//
// Esta tela consulta o histórico de compras do cliente.
// Como a aplicação ainda é simples, seguimos com busca por e-mail.
// ============================================================

const CHAVE_EMAIL = "weblue-ultimo-email";
const emailPedido = document.getElementById("emailPedido");
const listaPedidos = document.getElementById("listaPedidos");
const mensagemPedidos = document.getElementById("mensagemPedidos");
const botaoBuscarPedidos = document.getElementById("botaoBuscarPedidos");

function formatarPreco(valor) {
    return new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
    }).format(Number(valor || 0));
}

function renderPedido(pedido) {
    const itens = (pedido.itens || [])
        .map((item) => `<li>${item.quantidade}x ${item.nome} — ${formatarPreco(item.subtotal)}</li>`)
        .join("");

    return `
        <article class="pedido">
            <div class="pedido-header">
                <strong>Pedido #${pedido.id}</strong>
                <span class="badge">${pedido.status}</span>
            </div>
            <p>Data: ${pedido.criado_em ? new Date(pedido.criado_em).toLocaleString("pt-BR") : "-"}</p>
            <p>Total: <strong>${formatarPreco(pedido.valor_total)}</strong></p>
            <ul>${itens || "<li>Sem itens registrados.</li>"}</ul>
        </article>
    `;
}

async function buscarPedidos(email) {
    if (!email) {
        if (mensagemPedidos) {
            mensagemPedidos.textContent = "Informe o e-mail para consultar seus pedidos.";
        }
        if (listaPedidos) {
            listaPedidos.innerHTML = "";
        }
        return;
    }

    try {
        const resposta = await fetch(`/api/pedidos/me?email=${encodeURIComponent(email)}`);
        const dados = await resposta.json();

        if (!resposta.ok) {
            throw new Error(dados.detail || "Não foi possível carregar os pedidos.");
        }

        const pedidos = Array.isArray(dados.pedidos) ? dados.pedidos : [];

        if (!pedidos.length) {
            if (listaPedidos) {
                listaPedidos.innerHTML = "";
            }
            if (mensagemPedidos) {
                mensagemPedidos.textContent = "Nenhum pedido encontrado para este e-mail.";
            }
            return;
        }

        if (mensagemPedidos) {
            mensagemPedidos.textContent = "";
        }

        if (listaPedidos) {
            listaPedidos.innerHTML = pedidos.map(renderPedido).join("");
        }
    } catch (erro) {
        console.error("Erro ao buscar pedidos.", erro);
        if (mensagemPedidos) {
            mensagemPedidos.textContent = erro.message || "Erro ao buscar pedidos.";
        }
    }
}

if (emailPedido) {
    const emailSalvo = localStorage.getItem(CHAVE_EMAIL);
    if (emailSalvo) {
        emailPedido.value = emailSalvo;
    }
}

if (botaoBuscarPedidos) {
    botaoBuscarPedidos.addEventListener("click", () => {
        if (emailPedido) {
            const valor = emailPedido.value.trim();
            localStorage.setItem(CHAVE_EMAIL, valor);
            buscarPedidos(valor);
        }
    });
}

if (emailPedido) {
    emailPedido.addEventListener("keydown", (evento) => {
        if (evento.key === "Enter") {
            const valor = emailPedido.value.trim();
            localStorage.setItem(CHAVE_EMAIL, valor);
            buscarPedidos(valor);
        }
    });
}

if (emailPedido && emailPedido.value.trim()) {
    buscarPedidos(emailPedido.value.trim());
} else {
    const emailSalvo = localStorage.getItem(CHAVE_EMAIL);
    if (emailSalvo) {
        emailPedido.value = emailSalvo;
        buscarPedidos(emailSalvo);
    } else if (mensagemPedidos) {
        mensagemPedidos.textContent = "Ainda não há pedidos para consultar. Faça uma compra primeiro.";
    }
}
