/* ============================================================
   WEBLUE - ADMIN-PRODUTOS.JS
   Painel administrativo de produtos

   Funções principais:
   - Listar produtos
   - Pesquisar produtos
   - Filtrar por status
   - Cadastrar produto
   - Buscar produto por ID
   - Editar produto
   - Desativar produto
   - Reativar produto
   - Atualizar estatísticas
   ============================================================ */


/* ============================================================
   1. ENDPOINT DA API
   ============================================================ */

/*
   Como frontend e backend estão sendo servidos
   pelo mesmo endereço:

   http://127.0.0.1:8000

   podemos usar uma URL relativa.
*/
const API_PRODUTOS = "/api/produtos";
const API_PEDIDOS = "/api/pedidos";
const TOKEN_ADMIN_KEY = "tokenAdminWeblue";
const REFRESH_TOKEN_ADMIN_KEY = "refreshTokenAdminWeblue";
const listaPedidosRecentes = document.getElementById("listaPedidosRecentes");
const listaEstoqueBaixo = document.getElementById("listaEstoqueBaixo");

function limparSessaoAdmin() {
   sessionStorage.removeItem(TOKEN_ADMIN_KEY);
   sessionStorage.removeItem(REFRESH_TOKEN_ADMIN_KEY);
   sessionStorage.removeItem("administradorWeblue");
   localStorage.removeItem(TOKEN_ADMIN_KEY);
   localStorage.removeItem(REFRESH_TOKEN_ADMIN_KEY);
   localStorage.removeItem("administradorWeblue");
}

function redirecionarParaLoginAdmin(mensagem = "Sua sessão administrativa expirou. Faça login novamente.") {
   limparSessaoAdmin();
   window.location.href = `/admin-login.html?expirada=1&msg=${encodeURIComponent(mensagem)}`;
}

async function logoutAdminNoServidor() {
   const accessToken = sessionStorage.getItem(TOKEN_ADMIN_KEY);
   const refreshToken = sessionStorage.getItem(REFRESH_TOKEN_ADMIN_KEY);

   if (!accessToken && !refreshToken) {
       return;
   }

   try {
       await fetch("/api/admin/auth/logout", {
           method: "POST",
           headers: {
               "Content-Type": "application/json",
           },
           body: JSON.stringify({
               access_token: accessToken,
               refresh_token: refreshToken,
           }),
       });
   } catch (erro) {
       console.warn("Logout administrativo falhou no servidor:", erro);
   }
}

async function requisitarComRefreshAdmin(url, opcoes = {}) {
   const accessToken = sessionStorage.getItem(TOKEN_ADMIN_KEY);
   const refreshToken = sessionStorage.getItem(REFRESH_TOKEN_ADMIN_KEY);

   if (!accessToken) {
       redirecionarParaLoginAdmin("Sessão administrativa expirada. Faça login novamente.");
       throw new Error("Sessão administrativa expirada.");
   }

   const headers = {
       ...(opcoes.headers || {}),
       "Authorization": `Bearer ${accessToken}`
   };

   const resposta = await fetch(url, {
       ...opcoes,
       headers,
   });

   if (resposta.status !== 401 || !refreshToken) {
       return resposta;
   }

   try {
       const refreshResposta = await fetch("/api/admin/auth/refresh", {
           method: "POST",
           headers: {
               "Content-Type": "application/json",
           },
           body: JSON.stringify({ refresh_token: refreshToken }),
       });

       if (!refreshResposta.ok) {
           throw new Error("Refresh token inválido.");
       }

       const novosTokens = await refreshResposta.json();
       sessionStorage.setItem(TOKEN_ADMIN_KEY, novosTokens.access_token);

       if (novosTokens.refresh_token) {
           sessionStorage.setItem(REFRESH_TOKEN_ADMIN_KEY, novosTokens.refresh_token);
       }

       return fetch(url, {
           ...opcoes,
           headers: {
               ...(opcoes.headers || {}),
               "Authorization": `Bearer ${novosTokens.access_token}`
           },
       });
   } catch (erro) {
       redirecionarParaLoginAdmin("Sua sessão administrativa expirou. Faça login novamente.");
       throw erro;
   }
}


/* ============================================================
   2. ELEMENTOS DA PÁGINA
   ============================================================ */

// Botões principais.
const botaoNovoProduto = document.getElementById("botaoNovoProduto");
const botaoFecharModal = document.getElementById("botaoFecharModal");
const botaoCancelar = document.getElementById("botaoCancelar");
const botaoSalvar = document.getElementById("botaoSalvar");
const btnSairAdmin = document.getElementById("btnSairAdmin");

// Modal.
const modalProduto = document.getElementById("modalProduto");
const modalOverlay = document.getElementById("modalOverlay");
const tituloModal = document.getElementById("tituloModal");

// Formulário.
const formProduto = document.getElementById("formProduto");

// Campos.
const produtoId = document.getElementById("produtoId");
const campoNome = document.getElementById("nome");
const campoDescricao = document.getElementById("descricao");
const campoPreco = document.getElementById("preco");
const campoEstoque = document.getElementById("estoque");
const campoCategoria = document.getElementById("categoria");
const campoMarca = document.getElementById("marca");
const campoImagemUrl = document.getElementById("imagemUrl");
const campoStatus = document.getElementById("status");

// Pesquisa e filtro.
const pesquisaProduto = document.getElementById("pesquisaProduto");
const filtroStatus = document.getElementById("filtroStatus");

// Área da listagem.
const listaProdutos = document.getElementById("listaProdutos");

// Mensagens.
const mensagem = document.getElementById("mensagem");

// Estatísticas.
const totalProdutos = document.getElementById("totalProdutos");
const totalAtivos = document.getElementById("totalAtivos");
const totalInativos = document.getElementById("totalInativos");
const totalEstoque = document.getElementById("totalEstoque");


/* ============================================================
   3. ESTADO LOCAL
   ============================================================ */

/*
   Guardamos aqui todos os produtos retornados pela API.

   Depois usamos este array para:
   - pesquisar;
   - filtrar;
   - calcular estatísticas;
   - renderizar os cards.
*/
let produtos = [];


/* ============================================================
   4. ESCAPAR HTML
   ============================================================ */

/*
   Como alguns valores vêm do banco de dados,
   não devemos inseri-los diretamente no HTML.

   Esta função transforma caracteres especiais em texto seguro.
*/
function escaparHtml(valor) {

    if (valor === null || valor === undefined) {
        return "";
    }

    return String(valor)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* ============================================================
   5. FORMATAR PREÇO
   ============================================================ */

function formatarPreco(valor) {

    const numero = Number(valor);

    /*
       Se por algum motivo o preço recebido não for válido,
       exibimos R$ 0,00.
    */
    if (Number.isNaN(numero)) {
        return "R$ 0,00";
    }

    return numero.toLocaleString(
        "pt-BR",
        {
            style: "currency",
            currency: "BRL"
        }
    );
}


/* ============================================================
   6. MOSTRAR MENSAGEM
   ============================================================ */

function mostrarMensagem(texto, tipo = "info") {

    mensagem.textContent = texto;

    /*
       Remove classes anteriores.
    */
    mensagem.classList.remove(
        "sucesso",
        "erro",
        "info"
    );

    /*
       Adiciona a nova classe.
    */
    mensagem.classList.add(tipo);

    mensagem.hidden = false;


    /*
       Após alguns segundos, escondemos a mensagem.
    */
    window.clearTimeout(mostrarMensagem.timeout);

    mostrarMensagem.timeout = window.setTimeout(
        () => {
            mensagem.hidden = true;
        },
        5000
    );
}


/* ============================================================
   7. TRATAR ERROS DA API
   ============================================================ */

async function obterMensagemErro(response) {

    try {

        const dados = await response.json();

        /*
           FastAPI normalmente retorna:

           {
               "detail": "Mensagem do erro"
           }
        */
        if (dados.detail) {

            /*
               Alguns erros de validação podem vir
               como uma lista.
            */
            if (Array.isArray(dados.detail)) {

                return dados.detail
                    .map((erro) => erro.msg || "Erro de validação.")
                    .join(" ");

            }

            return String(dados.detail);
        }

        if (dados.mensagem) {
            return String(dados.mensagem);
        }

    } catch (erro) {

        console.error(
            "Não foi possível interpretar o erro da API:",
            erro
        );
    }

    return `Erro na requisição. Código HTTP: ${response.status}`;
}


/* ============================================================
   8. CARREGAR PRODUTOS
   ============================================================ */

async function carregarProdutos() {

    listaProdutos.innerHTML = `
        <p class="carregando">
            Carregando produtos...
        </p>
    `;

    try {
       const response = await requisitarComRefreshAdmin(API_PRODUTOS, {
           method: "GET",
           headers: {
               "Accept": "application/json"
           }
       });

       if (!response.ok) {
           const erroApi = await obterMensagemErro(response);
           throw new Error(erroApi);
       }

       const dados = await response.json();
       produtos = Array.isArray(dados.produtos) ? dados.produtos : [];

       atualizarEstatisticas();
       aplicarFiltros();

    } catch (erro) {
       console.error("Erro ao carregar produtos:", erro);
       listaProdutos.innerHTML = `
            <p class="sem-produtos">
                Não foi possível carregar os produtos.
            </p>
       `;

       mostrarMensagem(
           erro.message || "Não foi possível carregar os produtos.",
           "erro"
       );
    }
}

async function carregarResumoAdmin() {
    try {
       const [pedidosResposta, estoqueResposta] = await Promise.all([
           requisitarComRefreshAdmin(`${API_PEDIDOS}`, {
               method: "GET",
               headers: { "Accept": "application/json" },
           }),
           requisitarComRefreshAdmin(`${API_PEDIDOS}/estoque`, {
               method: "GET",
               headers: { "Accept": "application/json" },
           }),
       ]);

       if (!pedidosResposta.ok || !estoqueResposta.ok) {
           throw new Error("Não foi possível carregar o resumo administrativo.");
       }

       const pedidosDados = await pedidosResposta.json();
       const estoqueDados = await estoqueResposta.json();

       const pedidos = Array.isArray(pedidosDados.pedidos) ? pedidosDados.pedidos : [];
       const estoque = Array.isArray(estoqueDados.produtos) ? estoqueDados.produtos : [];

       const itensRecentes = pedidos.slice(0, 3);
       if (listaPedidosRecentes) {
           if (!itensRecentes.length) {
               listaPedidosRecentes.innerHTML = '<p class="sem-produtos">Nenhum pedido registrado.</p>';
           } else {
               listaPedidosRecentes.innerHTML = itensRecentes.map((pedido) => {
                   const valor = Number(pedido.valor_total || 0);
                   const data = pedido.criado_em ? new Date(pedido.criado_em).toLocaleString("pt-BR") : "-";
                   const itens = (pedido.itens || [])
                       .slice(0, 2)
                       .map((item) => `${item.quantidade}x ${item.nome}`).join(", ");
                   return `
                       <div class="admin-item-resumo">
                           <strong>#${pedido.id}</strong>
                           <span>${pedido.status}</span>
                           <small>${data}</small>
                           <small>${itens || "Sem itens"}</small>
                           <strong>${valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}</strong>
                       </div>
                   `;
               }).join("");
           }
       }

       const estoqueBaixo = estoque
           .filter((produto) => Number(produto.estoque) <= 3)
           .slice(0, 4);

       if (listaEstoqueBaixo) {
           if (!estoqueBaixo.length) {
               listaEstoqueBaixo.innerHTML = '<p class="sem-produtos">Estoque saudável para todos os produtos.</p>';
           } else {
               listaEstoqueBaixo.innerHTML = estoqueBaixo.map((produto) => `
                   <div class="admin-item-resumo">
                       <strong>${escaparHtml(produto.nome)}</strong>
                       <span>Disponível: ${produto.estoque}</span>
                       <small>${escaparHtml(produto.categoria || "Sem categoria")}</small>
                   </div>
               `).join("");
           }
       }
    } catch (erro) {
       console.error("Erro ao carregar resumo administrativo:", erro);
       if (listaPedidosRecentes) {
           listaPedidosRecentes.innerHTML = '<p class="sem-produtos">Não foi possível carregar os pedidos.</p>';
       }
       if (listaEstoqueBaixo) {
           listaEstoqueBaixo.innerHTML = '<p class="sem-produtos">Não foi possível carregar o estoque.</p>';
       }
    }
}


/* ============================================================
   9. ATUALIZAR ESTATÍSTICAS
   ============================================================ */

function atualizarEstatisticas() {

    /*
       Quantidade total.
    */
    const quantidadeTotal = produtos.length;


    /*
       Produtos ativos.
    */
    const quantidadeAtivos = produtos.filter(
        (produto) => produto.status === "ATIVO"
    ).length;


    /*
       Produtos inativos.
    */
    const quantidadeInativos = produtos.filter(
        (produto) => produto.status === "INATIVO"
    ).length;


    /*
       Soma de todas as unidades em estoque.

       Number(produto.estoque) garante que o valor
       seja tratado como número.
    */
    const quantidadeEstoque = produtos.reduce(
        (total, produto) => {

            const estoque = Number(produto.estoque);

            return total + (
                Number.isNaN(estoque)
                    ? 0
                    : estoque
            );
        },
        0
    );


    /*
       Atualizamos os quatro cards.
    */
    totalProdutos.textContent = quantidadeTotal;
    totalAtivos.textContent = quantidadeAtivos;
    totalInativos.textContent = quantidadeInativos;
    totalEstoque.textContent = quantidadeEstoque;
}


/* ============================================================
   10. APLICAR FILTROS
   ============================================================ */

function aplicarFiltros() {

    /*
       Texto pesquisado.
    */
    const termo = pesquisaProduto.value
        .trim()
        .toLowerCase();


    /*
       Status selecionado.
    */
    const statusSelecionado = filtroStatus.value;


    /*
       Criamos um novo array apenas com os produtos
       que atendem aos filtros.
    */
    const produtosFiltrados = produtos.filter(
        (produto) => {

            const nome = String(
                produto.nome || ""
            ).toLowerCase();

            const categoria = String(
                produto.categoria || ""
            ).toLowerCase();

            const marca = String(
                produto.marca || ""
            ).toLowerCase();


            /*
               Pesquisa por:
               - nome;
               - categoria;
               - marca.
            */
            const correspondePesquisa =
                !termo ||
                nome.includes(termo) ||
                categoria.includes(termo) ||
                marca.includes(termo);


            /*
               Se nenhum status foi selecionado,
               qualquer status é aceito.
            */
            const correspondeStatus =
                !statusSelecionado ||
                produto.status === statusSelecionado;


            return (
                correspondePesquisa &&
                correspondeStatus
            );
        }
    );


    renderizarProdutos(produtosFiltrados);
}


/* ============================================================
   11. RENDERIZAR PRODUTOS
   ============================================================ */

function renderizarProdutos(lista) {

    /*
       Caso não existam produtos.
    */
    if (!lista.length) {

        listaProdutos.innerHTML = `
            <p class="sem-produtos">
                Nenhum produto encontrado.
            </p>
        `;

        return;
    }


    /*
       Limpamos o container antes de criar os cards.
    */
    listaProdutos.innerHTML = "";


    lista.forEach(
        (produto) => {

            const card = document.createElement("article");

            card.className = "admin-produto-card";


            /*
               Verifica se existe URL de imagem.
            */
            const possuiImagem =
                produto.imagem_url &&
                String(produto.imagem_url).trim() !== "";


            /*
               Define classe visual do status.
            */
            const classeStatus =
                produto.status === "ATIVO"
                    ? "ativo"
                    : "inativo";


            /*
               Define o texto do botão.

               Produto ativo:
               Desativar

               Produto inativo:
               Reativar
            */
            const textoBotaoStatus =
                produto.status === "ATIVO"
                    ? "Desativar"
                    : "Reativar";


            /*
               Conteúdo da imagem.
            */
            const htmlImagem = possuiImagem

                ? `
                    <img
                        src="${escaparHtml(produto.imagem_url)}"
                        alt="${escaparHtml(produto.nome)}"
                    >
                `

                : `
                    <span class="admin-produto-sem-imagem">
                        Weblue
                    </span>
                `;


            /*
               Montamos o card completo.
            */
            card.innerHTML = `

                <div class="admin-produto-imagem">

                    ${htmlImagem}

                    <span
                        class="status-produto ${classeStatus}"
                    >
                        ${escaparHtml(produto.status)}
                    </span>

                </div>


                <div class="admin-produto-conteudo">

                    <span class="admin-produto-categoria">
                        ${escaparHtml(produto.categoria)}
                    </span>


                    <h3 class="admin-produto-nome">
                        ${escaparHtml(produto.nome)}
                    </h3>


                    <p class="admin-produto-marca">
                        ${escaparHtml(produto.marca || "Sem marca")}
                    </p>


                    <p class="admin-produto-descricao">
                        ${
                            escaparHtml(
                                produto.descricao ||
                                "Produto sem descrição."
                            )
                        }
                    </p>


                    <div class="admin-produto-dados">

                        <strong class="admin-produto-preco">
                            ${formatarPreco(produto.preco)}
                        </strong>


                        <span class="admin-produto-estoque">
                            ${escaparHtml(produto.estoque)}
                            unidade(s)
                        </span>

                    </div>


                    <div class="admin-produto-acoes">

                        <button
                            type="button"
                            class="botao-editar"
                            data-id="${produto.id}"
                        >
                            Editar
                        </button>


                        <button
                            type="button"
                            class="botao-status"
                            data-id="${produto.id}"
                            data-status="${escaparHtml(produto.status)}"
                        >
                            ${textoBotaoStatus}
                        </button>

                    </div>

                </div>
            `;


            listaProdutos.appendChild(card);
        }
    );
}


/* ============================================================
   12. ABRIR MODAL PARA NOVO PRODUTO
   ============================================================ */

function abrirModalNovoProduto() {

    /*
       Limpa todos os campos.
    */
    formProduto.reset();


    /*
       Sem ID significa cadastro.
    */
    produtoId.value = "";


    /*
       Produto novo começa ativo.
    */
    campoStatus.value = "ATIVO";


    tituloModal.textContent = "Novo produto";

    botaoSalvar.textContent = "Salvar produto";


    abrirModal();
}


/* ============================================================
   13. ABRIR MODAL
   ============================================================ */

function abrirModal() {

    modalProduto.hidden = false;

    document.body.classList.add(
        "modal-aberto"
    );


    /*
       Coloca o cursor no nome.
    */
    window.setTimeout(
        () => {
            campoNome.focus();
        },
        50
    );
}


/* ============================================================
   14. FECHAR MODAL
   ============================================================ */

function fecharModal() {

    modalProduto.hidden = true;

    document.body.classList.remove(
        "modal-aberto"
    );


    /*
       Limpa o formulário para evitar que
       dados antigos permaneçam na próxima abertura.
    */
    formProduto.reset();

    produtoId.value = "";
}


/* ============================================================
   15. BUSCAR PRODUTO POR ID
   ============================================================ */

async function buscarProdutoPorId(id) {

    const response = await requisitarComRefreshAdmin(
        `${API_PRODUTOS}/${id}`,
        {
            method: "GET",
            headers: {
                "Accept": "application/json"
            }
        }
    );


    if (!response.ok) {

        const erroApi = await obterMensagemErro(response);

        throw new Error(erroApi);
    }


    const dados = await response.json();


    /*
       Nosso endpoint retorna:

       {
           "produto": {...}
       }
    */
    return dados.produto;
}


/* ============================================================
   16. ABRIR PRODUTO PARA EDIÇÃO
   ============================================================ */

async function editarProduto(id) {

    try {

        /*
           Buscamos novamente na API para garantir
           que estamos editando os dados mais recentes.
        */
        const produto = await buscarProdutoPorId(id);


        /*
           Preenchemos os campos.
        */
        produtoId.value = produto.id;

        campoNome.value = produto.nome || "";
        campoDescricao.value = produto.descricao || "";
        campoPreco.value = produto.preco || "";
        campoEstoque.value = produto.estoque ?? 0;
        campoCategoria.value = produto.categoria || "";
        campoMarca.value = produto.marca || "";
        campoImagemUrl.value = produto.imagem_url || "";
        campoStatus.value = produto.status || "ATIVO";


        tituloModal.textContent = "Editar produto";

        botaoSalvar.textContent = "Salvar alterações";


        abrirModal();

    } catch (erro) {

        console.error(
            "Erro ao buscar produto:",
            erro
        );

        mostrarMensagem(
            erro.message || "Não foi possível abrir o produto.",
            "erro"
        );
    }
}


/* ============================================================
   17. PREPARAR DADOS DO FORMULÁRIO
   ============================================================ */

function obterDadosFormulario() {

    /*
       trim() remove espaços desnecessários
       no começo e no fim.
    */
    const nome = campoNome.value.trim();

    const descricao = campoDescricao.value.trim();

    const preco = Number(campoPreco.value);

    const estoque = Number(campoEstoque.value);

    const categoria = campoCategoria.value;

    const marca = campoMarca.value.trim();

    const imagemUrl = campoImagemUrl.value.trim();

    const status = campoStatus.value;


    /*
       Validações adicionais no frontend.
    */
    if (!nome) {
        throw new Error(
            "Informe o nome do produto."
        );
    }


    if (
        Number.isNaN(preco) ||
        preco < 0
    ) {
        throw new Error(
            "Informe um preço válido."
        );
    }


    if (
        !Number.isInteger(estoque) ||
        estoque < 0
    ) {
        throw new Error(
            "Informe um estoque válido."
        );
    }


    if (!categoria) {
        throw new Error(
            "Selecione uma categoria."
        );
    }


    /*
       Criamos o objeto enviado para a API.
    */
    return {

        nome: nome,

        /*
           Campos opcionais vazios são enviados como null.
        */
        descricao:
            descricao || null,

        preco: preco,

        estoque: estoque,

        categoria: categoria,

        marca:
            marca || null,

        imagem_url:
            imagemUrl || null,

        status: status
    };
}


/* ============================================================
   18. SALVAR PRODUTO
   ============================================================ */

async function salvarProduto(event) {

    /*
       Impede o navegador de recarregar a página.
    */
    event.preventDefault();


    try {

        const dadosProduto = obterDadosFormulario();


        /*
           Verificamos se estamos:
           - cadastrando;
           - editando.
        */
        const id = produtoId.value;


        const editando = Boolean(id);


        /*
           Cadastro:
           POST /produtos

           Edição:
           PUT /produtos/{id}
        */
        const url = editando
            ? `${API_PRODUTOS}/${id}`
            : API_PRODUTOS;


        const metodo = editando
            ? "PUT"
            : "POST";


        /*
           Evita vários cliques enquanto salva.
        */
        botaoSalvar.disabled = true;

        botaoSalvar.textContent = editando
            ? "Salvando alterações..."
            : "Salvando produto...";


        const response = await requisitarComRefreshAdmin(
            url,
            {
                method: metodo,

                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },

                body: JSON.stringify(
                    dadosProduto
                )
            }
        );


        if (!response.ok) {

            const erroApi = await obterMensagemErro(response);

            throw new Error(erroApi);
        }


        /*
           Lemos a resposta para concluir corretamente
           a requisição.
        */
        await response.json();


        fecharModal();


        mostrarMensagem(
            editando
                ? "Produto atualizado com sucesso."
                : "Produto cadastrado com sucesso.",
            "sucesso"
        );


        /*
           Atualizamos a listagem usando dados
           novos diretamente do banco.
        */
        await carregarProdutos();

    } catch (erro) {

        console.error(
            "Erro ao salvar produto:",
            erro
        );

        mostrarMensagem(
            erro.message || "Não foi possível salvar o produto.",
            "erro"
        );

    } finally {

        botaoSalvar.disabled = false;

        botaoSalvar.textContent = produtoId.value
            ? "Salvar alterações"
            : "Salvar produto";
    }
}


/* ============================================================
   19. ALTERAR STATUS
   ============================================================ */

async function alterarStatusProduto(id, statusAtual) {

    /*
       Se está ativo:
       usamos DELETE para desativar.

       Se está inativo:
       usamos PUT para reativar.
    */
    const estaAtivo =
        statusAtual === "ATIVO";


    const mensagemConfirmacao = estaAtivo

        ? "Deseja realmente desativar este produto?"

        : "Deseja reativar este produto?";


    const confirmou = window.confirm(
        mensagemConfirmacao
    );


    if (!confirmou) {
        return;
    }


    try {

        let response;


        /* ====================================================
           DESATIVAR
           ==================================================== */

        if (estaAtivo) {

            response = await requisitarComRefreshAdmin(
                `${API_PRODUTOS}/${id}`,
                {
                    method: "DELETE",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

        }


        /* ====================================================
           REATIVAR
           ==================================================== */

        else {

            response = await requisitarComRefreshAdmin(
                `${API_PRODUTOS}/${id}`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },

                    body: JSON.stringify(
                        {
                            status: "ATIVO"
                        }
                    )
                }
            );
        }


        if (!response.ok) {

            const erroApi = await obterMensagemErro(response);

            throw new Error(erroApi);
        }


        await response.json();


        mostrarMensagem(
            estaAtivo
                ? "Produto desativado com sucesso."
                : "Produto reativado com sucesso.",
            "sucesso"
        );


        await carregarProdutos();

    } catch (erro) {

        console.error(
            "Erro ao alterar status:",
            erro
        );

        mostrarMensagem(
            erro.message || "Não foi possível alterar o status.",
            "erro"
        );
    }
}


/* ============================================================
   20. CLIQUES NOS CARDS
   ============================================================ */

/*
   Usamos delegação de eventos.

   Assim não precisamos adicionar um listener
   separado para cada produto.
*/
listaProdutos.addEventListener(
    "click",
    (event) => {

        /*
           Procura o botão Editar mais próximo.
        */
        const botaoEditar = event.target.closest(
            ".botao-editar"
        );


        if (botaoEditar) {

            const id = Number(
                botaoEditar.dataset.id
            );

            editarProduto(id);

            return;
        }


        /*
           Procura o botão de status.
        */
        const botaoStatus = event.target.closest(
            ".botao-status"
        );


        if (botaoStatus) {

            const id = Number(
                botaoStatus.dataset.id
            );

            const statusAtual =
                botaoStatus.dataset.status;


            alterarStatusProduto(
                id,
                statusAtual
            );
        }
    }
);


/* ============================================================
   21. EVENTOS DO MODAL
   ============================================================ */

botaoNovoProduto.addEventListener(
    "click",
    abrirModalNovoProduto
);


botaoFecharModal.addEventListener(
    "click",
    fecharModal
);


botaoCancelar.addEventListener(
    "click",
    fecharModal
);


modalOverlay.addEventListener(
    "click",
    fecharModal
);


/*
   ESC também fecha o modal.
*/
document.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Escape" &&
            !modalProduto.hidden
        ) {
            fecharModal();
        }
    }
);


/* ============================================================
   22. EVENTO DO FORMULÁRIO
   ============================================================ */

formProduto.addEventListener(
    "submit",
    salvarProduto
);


/* ============================================================
   23. EVENTOS DOS FILTROS
   ============================================================ */

pesquisaProduto.addEventListener(
    "input",
    aplicarFiltros
);


filtroStatus.addEventListener(
    "change",
    aplicarFiltros
);


/* ============================================================
   24. ERRO DE IMAGEM
   ============================================================ */

/*
   Caso uma URL de imagem cadastrada deixe de funcionar,
   escondemos a imagem quebrada e mostramos "Weblue".
*/
listaProdutos.addEventListener(
    "error",
    (event) => {

        if (
            event.target.tagName !== "IMG"
        ) {
            return;
        }


        const container =
            event.target.closest(
                ".admin-produto-imagem"
            );


        event.target.remove();


        /*
           Evita criar o placeholder duas vezes.
        */
        if (
            container &&
            !container.querySelector(
                ".admin-produto-sem-imagem"
            )
        ) {

            const placeholder =
                document.createElement("span");


            placeholder.className =
                "admin-produto-sem-imagem";


            placeholder.textContent =
                "Weblue";


            /*
               Inserimos antes do status.
            */
            const status =
                container.querySelector(
                    ".status-produto"
                );


            if (status) {

                container.insertBefore(
                    placeholder,
                    status
                );

            } else {

                container.appendChild(
                    placeholder
                );
            }
        }

    },
    true
);


/* ============================================================
   25. LOGOUT DO ADMINISTRADOR
   ============================================================ */

if (btnSairAdmin) {
   btnSairAdmin.addEventListener("click", async () => {
       btnSairAdmin.disabled = true;
       btnSairAdmin.textContent = "Saindo...";

       try {
           await logoutAdminNoServidor();
       } finally {
           limparSessaoAdmin();
           window.location.href = "/admin-login.html";
       }
   });
}

/* ============================================================
   26. INICIALIZAÇÃO
   ============================================================ */

const tokenAdminAtivo = sessionStorage.getItem(TOKEN_ADMIN_KEY);

if (!tokenAdminAtivo) {
   redirecionarParaLoginAdmin("Você precisa estar autenticado para acessar o painel administrativo.");
} else {
   carregarProdutos();
   carregarResumoAdmin();
}