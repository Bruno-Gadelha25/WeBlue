// ============================================================
// WEBLUE - DASHBOARD ADMINISTRATIVO
// ============================================================

const API_BASE = "";

const token =
    sessionStorage.getItem(
        "tokenAdminWeblue"
    ) ||
    localStorage.getItem(
        "tokenAdminWeblue"
    );

if (!token) {
    window.location.href =
        "/admin-login";
}
// ============================================================
// TOKEN ADMIN
// ============================================================

function obterToken() {

    return (
        sessionStorage.getItem("tokenAdminWeblue") ||
        localStorage.getItem("tokenAdminWeblue")
    );

}

function obterHeaders() {
    const token = obterToken();

    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

// ============================================================
// FORMATAÇÃO
// ============================================================

function formatarMoeda(valor) {
    return new Intl.NumberFormat(
        "pt-BR",
        {
            style: "currency",
            currency: "BRL"
        }
    ).format(Number(valor || 0));
}

// ============================================================
// RESUMO DE VENDAS
// ============================================================

async function carregarResumoVendas() {

    try {

        const response = await fetch(
            `${API_BASE}/pedidos/relatorios/vendas`,
            {
                headers: obterHeaders()
            }
        );

        if (!response.ok) {
            throw new Error("Erro ao carregar relatório.");
        }

        const dados = await response.json();

        document.getElementById(
            "faturamentoTotal"
        ).textContent = formatarMoeda(
            dados.faturamento_total
        );

        document.getElementById(
            "totalPedidos"
        ).textContent =
            dados.quantidade_pedidos;

        document.getElementById(
            "ticketMedio"
        ).textContent =
            formatarMoeda(
                dados.ticket_medio
            );

    } catch (erro) {

        console.error(
            "Erro ao carregar vendas:",
            erro
        );

    }
}

// ============================================================
// ESTOQUE
// ============================================================

async function carregarEstoque() {

    try {

        const response = await fetch(
            `${API_BASE}/pedidos/estoque`,
            {
                headers: obterHeaders()
            }
        );

        if (!response.ok) {
            throw new Error("Erro ao carregar estoque.");
        }

        const dados = await response.json();

        let estoqueTotal = 0;

        const containerBaixoEstoque =
            document.getElementById(
                "listaEstoqueBaixo"
            );

        if (containerBaixoEstoque) {
            containerBaixoEstoque.innerHTML = "";
        }

        dados.produtos.forEach(produto => {

            estoqueTotal += produto.estoque;

            if (
                produto.estoque <= 10 &&
                containerBaixoEstoque
            ) {

                containerBaixoEstoque.innerHTML += `
                    <div class="alerta-produto">
                        <strong>${produto.nome}</strong>
                        <span>
                            ${produto.estoque} unidade(s)
                        </span>
                    </div>
                `;
            }

        });

        document.getElementById(
            "estoqueTotal"
        ).textContent = estoqueTotal;

    } catch (erro) {

        console.error(
            "Erro ao carregar estoque:",
            erro
        );

    }
}

// ============================================================
// PRODUTOS MAIS VENDIDOS
// ============================================================

async function carregarProdutosMaisVendidos() {

    try {

        const response = await fetch(
            `${API_BASE}/pedidos/relatorios/produtos`,
            {
                headers: obterHeaders()
            }
        );

        if (!response.ok) {
            return;
        }

        const produtos = await response.json();

        const tabela =
            document.getElementById(
                "tabelaProdutos"
            );

        if (!tabela) {
            return;
        }

        tabela.innerHTML = "";

        produtos.forEach(produto => {

            tabela.innerHTML += `
                <tr>
                    <td>${produto.produto}</td>
                    <td>${produto.quantidade_vendida}</td>
                </tr>
            `;

        });

    } catch (erro) {

        console.error(
            "Erro ao carregar produtos:",
            erro
        );

    }
}

// ============================================================
// ÚLTIMOS PEDIDOS
// ============================================================

async function carregarUltimosPedidos() {

    try {

        const response = await fetch(
            `${API_BASE}/pedidos`,
            {
                headers: obterHeaders()
            }
        );

        if (!response.ok) {
            throw new Error(
                "Erro ao carregar pedidos."
            );
        }

        const dados = await response.json();

        const container =
            document.getElementById(
                "ultimasVendas"
            );

        if (!container) {
            return;
        }

        container.innerHTML = "";

        dados.pedidos
            .slice(0, 5)
            .forEach(pedido => {

                container.innerHTML += `
                    <div class="venda">

                        <div>
                            <strong>
                                Pedido #${pedido.id}
                            </strong>
                            <br>
                            ${pedido.status}
                        </div>

                        <div>
                            ${formatarMoeda(
                                pedido.valor_total
                            )}
                        </div>

                    </div>
                `;

            });

    } catch (erro) {

        console.error(
            "Erro ao carregar pedidos:",
            erro
        );

    }
}

// ============================================================
// LOGOUT ADMIN
// ============================================================

function configurarLogout() {

    const botao =
        document.getElementById(
            "btnLogout"
        );

    if (!botao) {
        return;
    }

    botao.addEventListener(
        "click",
        () => {

            sessionStorage.removeItem(
    "tokenAdminWeblue"
);

            localStorage.removeItem(
    "tokenAdminWeblue"
);

            window.location.href =
                "admin-login.html";

        }
    );
}

// ============================================================
// INICIALIZAÇÃO
// ============================================================

async function iniciarDashboard() {

    await carregarResumoVendas();

    await carregarEstoque();

    await carregarProdutosMaisVendidos();

    await carregarUltimosPedidos();

    configurarLogout();
}

document.addEventListener(
    "DOMContentLoaded",
    iniciarDashboard
);

// ======================================
// LOGOUT
// ======================================

function realizarLogout() {

    sessionStorage.removeItem(
        "tokenAdminWeblue"
    );

    sessionStorage.removeItem(
        "refreshTokenAdminWeblue"
    );

    sessionStorage.removeItem(
        "administradorWeblue"
    );

    localStorage.removeItem(
        "tokenAdminWeblue"
    );

    localStorage.removeItem(
        "refreshTokenAdminWeblue"
    );

    localStorage.removeItem(
        "administradorWeblue"
    );

    window.location.href =
        "/admin-login";
}

document
    .getElementById("btnLogout")
    ?.addEventListener(
        "click",
        realizarLogout
    );