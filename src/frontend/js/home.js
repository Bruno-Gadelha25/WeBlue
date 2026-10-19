// ============================================================
// WEBLUE - JAVASCRIPT DA HOME
// ============================================================
//
// Responsabilidades:
//
// 1. Buscar os produtos no backend.
// 2. Mostrar somente produtos ATIVOS.
// 3. Criar os cards automaticamente.
// 4. Formatar preços em Real (R$).
// 5. Pesquisar produtos.
// 6. Filtrar produtos por categoria.
//
// ============================================================


// ============================================================
// ============================================================
// CONFIGURAÇÃO DA API
// ============================================================

// Como frontend e backend estão sendo executados
// pelo mesmo FastAPI, podemos utilizar uma rota relativa.
const API_PRODUTOS = "/api/produtos/catalogo";
const CHAVE_CARRINHO = "weblue-carrinho";


// ============================================================
// ELEMENTOS DO HTML
// ============================================================

// Área onde os cards serão inseridos.
const listaProdutos =
    document.getElementById("listaProdutos");

// Mensagem:
// "Carregando produtos..."
// "Nenhum produto encontrado."
// etc.
const mensagemProdutos =
    document.getElementById("mensagemProdutos");

// Formulário da pesquisa.
const formBusca =
    document.getElementById("formBusca");

// Campo da pesquisa.
const campoBusca =
    document.getElementById("campoBusca");

// Botões que possuem:
// data-categoria="..."
const botoesCategoria =
    document.querySelectorAll("[data-categoria]");

const botaoCarrinho =
    document.getElementById("botaoCarrinho");


// ============================================================
// LISTA LOCAL
// ============================================================

// Depois que buscarmos os produtos da API,
// vamos guardar os produtos ativos aqui.
let produtos = [];

function obterCarrinho() {
    try {
        const carrinhoSalvo = localStorage.getItem(CHAVE_CARRINHO);
        return carrinhoSalvo ? JSON.parse(carrinhoSalvo) : [];
    } catch (erro) {
        console.error("Não foi possível carregar o carrinho.", erro);
        return [];
    }
}

function salvarCarrinho(carrinho) {
    localStorage.setItem(CHAVE_CARRINHO, JSON.stringify(carrinho));
}

function atualizarContadorCarrinho() {
    const contador = document.getElementById("contadorCarrinho");
    if (!contador) {
        return;
    }

    const carrinho = obterCarrinho();
    const totalItens = carrinho.reduce((soma, item) => soma + Number(item.quantidade || 0), 0);
    contador.textContent = String(totalItens);
}

function adicionarAoCarrinho(produto) {
    const carrinho = obterCarrinho();
    const itemExistente = carrinho.find((item) => item.id === produto.id);

    if (itemExistente) {
        itemExistente.quantidade += 1;
    } else {
        carrinho.push({
            id: produto.id,
            nome: produto.nome,
            preco: produto.preco,
            quantidade: 1,
        });
    }

    salvarCarrinho(carrinho);
    atualizarContadorCarrinho();

    if (botaoCarrinho) {
        botaoCarrinho.classList.add("pulse");
        setTimeout(() => botaoCarrinho.classList.remove("pulse"), 250);
    }
}


// ============================================================
// FORMATAR PREÇO
// ============================================================

function formatarPreco(preco) {

    // O backend retorna o preço como string.
    //
    // Exemplo:
    //
    // "64.90"
    //
    // Number transforma em número.
    const valor = Number(preco);


    // Verificação de segurança.
    if (Number.isNaN(valor)) {

        return "Preço indisponível";

    }


    // Formatação para moeda brasileira.
    return new Intl.NumberFormat(
        "pt-BR",
        {
            style: "currency",
            currency: "BRL"
        }
    ).format(valor);

}


// ============================================================
// CRIAR CARD
// ============================================================

function criarCardProduto(produto) {


    // ========================================================
    // CARD
    // ========================================================

    const card =
        document.createElement("article");

    card.classList.add("product-card");


    // ========================================================
    // IMAGEM
    // ========================================================

    const areaImagem =
        document.createElement("div");

    areaImagem.classList.add(
        "product-card__image"
    );


    // Se existir uma imagem cadastrada.
    if (produto.imagem_url) {

        const imagem =
            document.createElement("img");


        imagem.src =
            produto.imagem_url;

        imagem.alt =
            produto.nome;

        imagem.loading =
            "lazy";


        // Se a URL da imagem estiver quebrada,
        // mostramos o placeholder da Weblue.
        imagem.addEventListener(
            "error",
            () => {

                imagem.remove();

                areaImagem.classList.add(
                    "product-card__image--empty"
                );

                areaImagem.textContent =
                    "Weblue";

            }
        );


        areaImagem.appendChild(imagem);

    } else {

        // Produto sem imagem cadastrada.
        areaImagem.classList.add(
            "product-card__image--empty"
        );

        areaImagem.textContent =
            "Weblue";

    }


    // ========================================================
    // CONTEÚDO
    // ========================================================

    const conteudo =
        document.createElement("div");

    conteudo.classList.add(
        "product-card__content"
    );


    // ========================================================
    // CATEGORIA
    // ========================================================

    const categoria =
        document.createElement("span");

    categoria.classList.add(
        "product-card__category"
    );

    categoria.textContent =
        produto.categoria || "Sem categoria";


    // ========================================================
    // NOME
    // ========================================================

    const nome =
        document.createElement("h3");

    nome.classList.add(
        "product-card__name"
    );

    nome.textContent =
        produto.nome || "Produto Weblue";


    // ========================================================
    // MARCA
    // ========================================================

    const marca =
        document.createElement("p");

    marca.classList.add(
        "product-card__brand"
    );

    marca.textContent =
        produto.marca || "Weblue";


    // ========================================================
    // DESCRIÇÃO
    // ========================================================

    const descricao =
        document.createElement("p");

    descricao.classList.add(
        "product-card__description"
    );

    descricao.textContent =
        produto.descricao || "Produto Weblue.";


    // ========================================================
    // PREÇO
    // ========================================================

    const preco =
        document.createElement("strong");

    preco.classList.add(
        "product-card__price"
    );

    preco.textContent =
        formatarPreco(produto.preco);


    // ========================================================
    // ESTOQUE
    // ========================================================

    const estoque =
        document.createElement("span");

    estoque.classList.add(
        "product-card__stock"
    );


    if (produto.estoque > 0) {

        estoque.textContent =
            `${produto.estoque} unidade(s) disponível(is)`;

    } else {

        estoque.textContent =
            "Produto temporariamente indisponível";

        estoque.classList.add(
            "product-card__stock--empty"
        );

    }


    // ========================================================
    // BOTÃO
    // ========================================================

    const botao =
        document.createElement("button");

    botao.type =
        "button";

    botao.classList.add(
        "product-card__button"
    );


    if (produto.estoque > 0) {

        botao.textContent =
            "Adicionar ao carrinho";

    } else {

        botao.textContent =
            "Indisponível";

        botao.disabled =
            true;

    }


    // Quando o botão for clicado, adicionamos o produto
    // ao localStorage para o carrinho funcionar em toda a loja.
    botao.addEventListener(
        "click",
        () => {
            adicionarAoCarrinho(produto);
        }
    );


    // ========================================================
    // MONTAR CONTEÚDO
    // ========================================================

    conteudo.append(
        categoria,
        nome,
        marca,
        descricao,
        preco,
        estoque,
        botao
    );


    // ========================================================
    // MONTAR CARD
    // ========================================================

    card.append(
        areaImagem,
        conteudo
    );


    return card;

}


// ============================================================
// EXIBIR PRODUTOS
// ============================================================

function exibirProdutos(lista) {


    // Segurança caso o elemento não exista.
    if (!listaProdutos) {

        console.error(
            'Elemento com id="listaProdutos" não encontrado.'
        );

        return;

    }


    // Limpa os cards anteriores.
    listaProdutos.innerHTML = "";


    // ========================================================
    // NENHUM PRODUTO
    // ========================================================

    if (lista.length === 0) {

        if (mensagemProdutos) {

            mensagemProdutos.textContent =
                "Nenhum produto encontrado.";

            mensagemProdutos.style.display =
                "block";

        }

        return;

    }


    // Existem produtos.
    if (mensagemProdutos) {

        mensagemProdutos.style.display =
            "none";

    }


    // ========================================================
    // CRIAR CARDS
    // ========================================================

    lista.forEach(
        (produto) => {

            const card =
                criarCardProduto(produto);

            listaProdutos.appendChild(card);

        }
    );

}


// ============================================================
// CARREGAR PRODUTOS
// ============================================================

async function carregarProdutos() {


    // ========================================================
    // VERIFICAR HTML
    // ========================================================

    if (!listaProdutos) {

        console.error(
            'Não foi encontrado o elemento id="listaProdutos".'
        );

        return;

    }


    if (mensagemProdutos) {

        mensagemProdutos.textContent =
            "Carregando produtos...";

        mensagemProdutos.style.display =
            "block";

    }


    try {


        // ====================================================
        // GET /produtos
        // ====================================================

        const resposta =
            await fetch(API_PRODUTOS);


        // ====================================================
        // VERIFICAR HTTP
        // ====================================================

        if (!resposta.ok) {

            throw new Error(
                `Erro HTTP: ${resposta.status}`
            );

        }


        // ====================================================
        // CONVERTER RESPOSTA PARA JSON
        // ====================================================

        const dados =
            await resposta.json();


        console.log(
            "Resposta da API:",
            dados
        );


        // ====================================================
        // VALIDAR PRODUTOS
        // ====================================================

        const produtosRecebidos =
            Array.isArray(dados.produtos)
                ? dados.produtos
                : [];


        console.log(
            "Produtos recebidos:",
            produtosRecebidos
        );


        // ====================================================
        // SOMENTE PRODUTOS ATIVOS
        // ====================================================

        produtos =
            produtosRecebidos.filter(
                (produto) => {

                    return (
                        String(produto.status)
                            .trim()
                            .toUpperCase()
                        === "ATIVO"
                    );

                }
            );


        console.log(
            "Produtos ativos:",
            produtos
        );


        // ====================================================
        // EXIBIR NA HOME
        // ====================================================

        exibirProdutos(produtos);


    } catch (erro) {


        console.error(
            "Erro ao carregar produtos:",
            erro
        );


        if (mensagemProdutos) {

            mensagemProdutos.textContent =
                "Não foi possível carregar os produtos.";

            mensagemProdutos.style.display =
                "block";

        }

    }

}


// ============================================================
// PESQUISAR PRODUTOS
// ============================================================

function pesquisarProdutos(texto) {


    const termo =
        String(texto || "")
            .trim()
            .toLowerCase();


    // Pesquisa vazia:
    // mostra tudo novamente.
    if (!termo) {

        exibirProdutos(produtos);

        return;

    }


    const resultado =
        produtos.filter(
            (produto) => {


                const nome =
                    String(produto.nome || "")
                        .toLowerCase();


                const marca =
                    String(produto.marca || "")
                        .toLowerCase();


                const categoria =
                    String(produto.categoria || "")
                        .toLowerCase();


                const descricao =
                    String(produto.descricao || "")
                        .toLowerCase();


                return (
                    nome.includes(termo) ||
                    marca.includes(termo) ||
                    categoria.includes(termo) ||
                    descricao.includes(termo)
                );

            }
        );


    exibirProdutos(resultado);

}


// ============================================================
// FORMULÁRIO DE PESQUISA
// ============================================================

if (formBusca && campoBusca) {

    formBusca.addEventListener(
        "submit",
        (evento) => {


            // Não deixa o navegador
            // recarregar a página.
            evento.preventDefault();


            pesquisarProdutos(
                campoBusca.value
            );


            // Desce até os produtos.
            const secaoProdutos =
                document.getElementById("produtos");


            if (secaoProdutos) {

                secaoProdutos.scrollIntoView({
                    behavior: "smooth"
                });

            }

        }
    );

}


// ============================================================
// FILTRO POR CATEGORIA
// ============================================================

botoesCategoria.forEach(
    (botao) => {


        botao.addEventListener(
            "click",
            () => {


                const categoriaSelecionada =
                    botao.dataset.categoria;


                if (!categoriaSelecionada) {

                    return;

                }


                const resultado =
                    produtos.filter(
                        (produto) => {


                            return (
                                String(produto.categoria || "")
                                    .trim()
                                    .toLowerCase()
                                ===
                                categoriaSelecionada
                                    .trim()
                                    .toLowerCase()
                            );

                        }
                    );


                exibirProdutos(resultado);


                // Desce até os produtos.
                const secaoProdutos =
                    document.getElementById("produtos");


                if (secaoProdutos) {

                    secaoProdutos.scrollIntoView({
                        behavior: "smooth"
                    });

                }

            }
        );

    }
);


// ============================================================
// INICIAR A HOME
// ============================================================

// Como este arquivo é carregado no final do <body>,
// o HTML normalmente já estará disponível.
//
// Mesmo assim, verificamos o estado do documento
// para deixar o código mais robusto.

if (botaoCarrinho) {
    botaoCarrinho.addEventListener("click", () => {
        window.location.href = "/carrinho";
    });
}

if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        () => {
            atualizarContadorCarrinho();
            carregarProdutos();
        }
    );

} else {

    atualizarContadorCarrinho();
    carregarProdutos();

}