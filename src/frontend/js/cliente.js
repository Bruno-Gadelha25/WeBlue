// ============================================================
// AGUARDAR O HTML SER CARREGADO
// ============================================================

// Todo o código da área do cliente só será executado depois
// que o navegador terminar de montar os elementos do HTML.
document.addEventListener("DOMContentLoaded", async () => {


    // ========================================================
    // ELEMENTOS DE VISUALIZAÇÃO DO PERFIL
    // ========================================================

    // Nome exibido no cabeçalho da página.
    const nomeCliente =
        document.getElementById("nomeCliente");

    // Dados exibidos na seção "Meus dados".
    const clienteNome =
        document.getElementById("clienteNome");

    const clienteEmail =
        document.getElementById("clienteEmail");

    const clienteCpf =
        document.getElementById("clienteCpf");

    const clienteTelefone =
        document.getElementById("clienteTelefone");

    // Status da conta.
    const clienteStatus =
        document.getElementById("clienteStatus");

    // Avatar com a primeira letra do nome.
    const avatarCliente =
        document.getElementById("avatarCliente");


    // ========================================================
    // ELEMENTOS RESPONSÁVEIS PELA EDIÇÃO
    // ========================================================

    // Botão que ativa o modo de edição.
    const btnEditarDados =
        document.getElementById("btnEditarDados");

    // Área que mostra os dados normalmente.
    const visualizacaoDados =
        document.getElementById("visualizacaoDados");

    // Formulário utilizado para editar os dados.
    const formEditarPerfil =
        document.getElementById("formEditarPerfil");

    // Campos do formulário.
    const inputNome =
        document.getElementById("inputNome");

    const inputEmail =
        document.getElementById("inputEmail");

    const inputCpf =
        document.getElementById("inputCpf");

    const inputTelefone =
        document.getElementById("inputTelefone");

    // Botão utilizado para cancelar a edição.
    const btnCancelarEdicao =
        document.getElementById("btnCancelarEdicao");

    // Botão utilizado para salvar as alterações.
    const btnSalvarPerfil =
        document.getElementById("btnSalvarPerfil");

    // Área onde serão exibidas mensagens de sucesso ou erro.
    const mensagemPerfil =
        document.getElementById("mensagemPerfil");


    // ========================================================
    // OUTROS BOTÕES
    // ========================================================

    // Botão responsável por encerrar a sessão.
    const btnSair =
        document.getElementById("btnSair");

    // Botão "Começar a comprar".
    const btnComprar =
        document.getElementById("btnComprar");


    // ========================================================
    // VARIÁVEL COM OS DADOS ATUAIS DO CLIENTE
    // ========================================================

    /*
        Esta variável guarda os dados mais recentes do cliente.

        Ela será preenchida pelo GET /perfil.

        Depois de uma atualização pelo PUT /perfil,
        também será atualizada.
    */
    let clienteAtual = null;


    // ========================================================
    // PROCURAR TOKEN JWT
    // ========================================================

    /*
        A autenticação do cliente usa apenas a sessão ativa do navegador.

        Isso evita persistência insegura do JWT em localStorage,
        reduzindo a superfície de ataque por XSS.
    */
    const token =
        sessionStorage.getItem("tokenWeblue");


    // ========================================================
    // VERIFICAR SE EXISTE SESSÃO
    // ========================================================

    /*
        Sem token não existe sessão autenticada.

        Nesse caso:
        1. limpamos possíveis dados antigos;
        2. enviamos o usuário para o login;
        3. interrompemos a execução do código.
    */
    if (!token) {

        limparSessao();

        window.location.href = "/login";

        return;
    }


    // ========================================================
    // FUNÇÃO: LIMPAR SESSÃO
    // ========================================================

    function limparSessao() {

        /*
            Remove apenas a sessão ativa do cliente.
            Mantém compatibilidade limpando também qualquer dado
            antigo que ainda tenha ficado em localStorage.
        */

        sessionStorage.removeItem("clienteWeblue");
        sessionStorage.removeItem("tokenWeblue");
        sessionStorage.removeItem("refreshTokenWeblue");

        localStorage.removeItem("clienteWeblue");
        localStorage.removeItem("tokenWeblue");
        localStorage.removeItem("refreshTokenWeblue");
    }

    async function logoutClienteNoServidor() {
        const accessToken = sessionStorage.getItem("tokenWeblue");
        const refreshToken = sessionStorage.getItem("refreshTokenWeblue");

        if (!accessToken && !refreshToken) {
            return;
        }

        try {
            await fetch("/api/auth/logout", {
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
            console.warn("Logout do servidor falhou:", erro);
        }
    }

    async function requisitarComRefresh(url, opcoes = {}) {
        const accessToken = sessionStorage.getItem("tokenWeblue");
        const refreshToken = sessionStorage.getItem("refreshTokenWeblue");

        if (!accessToken) {
            limparSessao();
            window.location.href = "/login";
            throw new Error("Sessão expirada.");
        }

        const headers = {
            ...(opcoes.headers || {}),
            "Authorization": `Bearer ${accessToken}`,
        };

        const resposta = await fetch(url, {
            ...opcoes,
            headers,
        });

        if (resposta.status !== 401 || !refreshToken) {
            return resposta;
        }

        try {
            const refreshResposta = await fetch("/api/auth/refresh", {
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
            sessionStorage.setItem("tokenWeblue", novosTokens.access_token);
            if (novosTokens.refresh_token) {
                sessionStorage.setItem("refreshTokenWeblue", novosTokens.refresh_token);
            }

            return fetch(url, {
                ...opcoes,
                headers: {
                    ...(opcoes.headers || {}),
                    "Authorization": `Bearer ${novosTokens.access_token}`,
                },
            });
        } catch (erro) {
            limparSessao();
            window.location.href = "/login";
            throw erro;
        }
    }


    // ========================================================
    // FUNÇÃO: SALVAR CLIENTE NO NAVEGADOR
    // ========================================================

    function salvarClienteLocalmente(cliente) {

        /*
            Os dados do cliente ficam junto com a sessão atual,
            não em armazenamento persistente.
        */
        sessionStorage.setItem(
            "clienteWeblue",
            JSON.stringify(cliente)
        );
    }


    // ========================================================
    // FUNÇÃO: MOSTRAR MENSAGEM
    // ========================================================

    function mostrarMensagem(texto, tipo = "") {

        // Verificação de segurança.
        if (!mensagemPerfil) {
            return;
        }


        // Define o texto da mensagem.
        mensagemPerfil.textContent = texto;


        /*
            Removemos classes anteriores para evitar
            que uma mensagem de erro mantenha a aparência
            depois de uma mensagem de sucesso.
        */
        mensagemPerfil.classList.remove(
            "sucesso",
            "erro"
        );


        /*
            O tipo poderá ser:
            "sucesso"
            "erro"
        */
        if (tipo) {

            mensagemPerfil.classList.add(tipo);
        }
    }


    // ========================================================
    // FUNÇÃO: ATUALIZAR INTERFACE
    // ========================================================

    function atualizarInterface(cliente) {

        /*
            Guardamos os dados mais recentes do cliente.
        */
        clienteAtual = cliente;


        // ====================================================
        // NOME DO CABEÇALHO
        // ====================================================

        if (nomeCliente) {

            nomeCliente.textContent =
                cliente.nome_completo ||
                "Cliente Weblue";
        }


        // ====================================================
        // NOME DA SEÇÃO "MEUS DADOS"
        // ====================================================

        if (clienteNome) {

            clienteNome.textContent =
                cliente.nome_completo ||
                "Não informado";
        }


        // ====================================================
        // E-MAIL
        // ====================================================

        if (clienteEmail) {

            clienteEmail.textContent =
                cliente.email ||
                "Não informado";
        }


        // ====================================================
        // CPF
        // ====================================================

        if (clienteCpf) {

            clienteCpf.textContent =
                cliente.cpf ||
                "Não informado";
        }


        // ====================================================
        // TELEFONE
        // ====================================================

        if (clienteTelefone) {

            clienteTelefone.textContent =
                cliente.telefone ||
                "Não informado";
        }


        // ====================================================
        // STATUS
        // ====================================================

        if (clienteStatus) {

            /*
                Mostra o status retornado pelo backend.
            */
            clienteStatus.textContent =
                cliente.status ||
                "Não informado";


            /*
                Primeiro removemos todas as possíveis
                classes de status.
            */
            clienteStatus.classList.remove(
                "status-ativo",
                "status-inativo",
                "status-bloqueado"
            );


            /*
                Depois adicionamos a classe correspondente
                ao status atual.
            */
            if (cliente.status === "ATIVA") {

                clienteStatus.classList.add(
                    "status-ativo"
                );

            } else if (cliente.status === "INATIVA") {

                clienteStatus.classList.add(
                    "status-inativo"
                );

            } else if (cliente.status === "BLOQUEADA") {

                clienteStatus.classList.add(
                    "status-bloqueado"
                );
            }
        }


        // ====================================================
        // AVATAR
        // ====================================================

        if (avatarCliente) {

            /*
                Se existir nome, utilizamos a primeira letra.
            */
            if (cliente.nome_completo) {

                avatarCliente.textContent =
                    cliente.nome_completo
                        .trim()
                        .charAt(0)
                        .toUpperCase();

            } else {

                // Caso não exista nome, utilizamos W de Weblue.
                avatarCliente.textContent = "W";
            }
        }
    }


    // ========================================================
    // FUNÇÃO: CARREGAR PERFIL
    // ========================================================

    async function carregarPerfil() {

        try {

            /*
                Enviamos GET /perfil.

                O JWT vai no cabeçalho Authorization.
            */
            const resposta = await requisitarComRefresh(
                "/api/perfil",
                {
                    method: "GET",

                    headers: {
                        "Accept": "application/json",
                    }
                }
            );


            // =================================================
            // TOKEN INVÁLIDO OU EXPIRADO
            // =================================================

            if (resposta.status === 401) {

                limparSessao();

                window.location.href = "/login";

                return;
            }


            // =================================================
            // CONTA SEM PERMISSÃO
            // =================================================

            if (resposta.status === 403) {

                /*
                    Uma conta bloqueada ou inativa não deve
                    continuar acessando normalmente o perfil.
                */

                limparSessao();

                alert(
                    "Sua conta não possui permissão de acesso."
                );

                window.location.href = "/login";

                return;
            }


            // =================================================
            // OUTROS ERROS
            // =================================================

            if (!resposta.ok) {

                throw new Error(
                    "Não foi possível carregar os dados do perfil."
                );
            }


            // =================================================
            // CONVERTER JSON
            // =================================================

            const cliente =
                await resposta.json();


            // =================================================
            // SALVAR DADOS NO NAVEGADOR
            // =================================================

            salvarClienteLocalmente(cliente);


            // =================================================
            // ATUALIZAR A INTERFACE
            // =================================================

            atualizarInterface(cliente);


        } catch (erro) {

            console.error(
                "Erro ao carregar perfil:",
                erro
            );

            alert(
                "Não foi possível carregar os dados da sua conta."
            );
        }
    }


    // ========================================================
    // CARREGAR PERFIL AO ABRIR A PÁGINA
    // ========================================================

    /*
        Como carregarPerfil() é assíncrona,
        aguardamos o GET terminar antes de continuar.
    */
    await carregarPerfil();


    // ========================================================
    // BOTÃO EDITAR DADOS
    // ========================================================

    if (btnEditarDados) {

        btnEditarDados.addEventListener(
            "click",
            () => {

                /*
                    Só permitimos abrir o formulário depois
                    que os dados do cliente forem carregados.
                */
                if (!clienteAtual) {
                    return;
                }


                // =============================================
                // PREENCHER FORMULÁRIO
                // =============================================

                /*
                    Os inputs recebem os dados atuais.

                    Assim o cliente não precisa digitar tudo
                    novamente.
                */

                if (inputNome) {

                    inputNome.value =
                        clienteAtual.nome_completo || "";
                }


                if (inputEmail) {

                    inputEmail.value =
                        clienteAtual.email || "";
                }


                if (inputCpf) {

                    inputCpf.value =
                        clienteAtual.cpf || "";
                }


                if (inputTelefone) {

                    inputTelefone.value =
                        clienteAtual.telefone || "";
                }


                // =============================================
                // LIMPAR MENSAGEM ANTIGA
                // =============================================

                mostrarMensagem("");


                // =============================================
                // ESCONDER VISUALIZAÇÃO
                // =============================================

                if (visualizacaoDados) {

                    visualizacaoDados.hidden = true;
                }


                // =============================================
                // MOSTRAR FORMULÁRIO
                // =============================================

                if (formEditarPerfil) {

                    formEditarPerfil.hidden = false;
                }


                // =============================================
                // ESCONDER BOTÃO EDITAR
                // =============================================

                /*
                    Enquanto o formulário estiver aberto,
                    não precisamos mostrar novamente
                    "Editar dados".
                */
                btnEditarDados.hidden = true;


                // =============================================
                // FOCO NO NOME
                // =============================================

                /*
                    Coloca o cursor automaticamente
                    no primeiro campo.
                */
                if (inputNome) {

                    inputNome.focus();
                }
            }
        );
    }


    // ========================================================
    // BOTÃO CANCELAR EDIÇÃO
    // ========================================================

    if (btnCancelarEdicao) {

        btnCancelarEdicao.addEventListener(
            "click",
            () => {

                // Limpa qualquer mensagem exibida.
                mostrarMensagem("");


                // Esconde o formulário.
                if (formEditarPerfil) {

                    formEditarPerfil.hidden = true;
                }


                // Mostra novamente os dados.
                if (visualizacaoDados) {

                    visualizacaoDados.hidden = false;
                }


                // Mostra novamente "Editar dados".
                if (btnEditarDados) {

                    btnEditarDados.hidden = false;
                }
            }
        );
    }


    // ========================================================
    // ENVIAR FORMULÁRIO DE EDIÇÃO
    // ========================================================

    if (formEditarPerfil) {

        formEditarPerfil.addEventListener(
            "submit",
            async (evento) => {

                /*
                    Impede o comportamento padrão do formulário,
                    que recarregaria a página.
                */
                evento.preventDefault();


                // =============================================
                // PEGAR VALORES DOS CAMPOS
                // =============================================

                const nome =
                    inputNome.value.trim();

                const email =
                    inputEmail.value
                        .trim()
                        .toLowerCase();

                const telefone =
                    inputTelefone.value.trim();


                // =============================================
                // VALIDAÇÃO DO NOME
                // =============================================

                if (nome.length < 3) {

                    mostrarMensagem(
                        "Informe um nome com pelo menos 3 caracteres.",
                        "erro"
                    );

                    inputNome.focus();

                    return;
                }


                // =============================================
                // VALIDAÇÃO DO E-MAIL
                // =============================================

                /*
                    O input type="email" já faz uma validação
                    básica pelo navegador.

                    Ainda assim verificamos se não está vazio.
                */
                if (!email) {

                    mostrarMensagem(
                        "Informe um e-mail válido.",
                        "erro"
                    );

                    inputEmail.focus();

                    return;
                }


                // =============================================
                // VALIDAÇÃO DO TELEFONE
                // =============================================

                if (
                    telefone.length < 10 ||
                    telefone.length > 20
                ) {

                    mostrarMensagem(
                        "Informe um telefone válido.",
                        "erro"
                    );

                    inputTelefone.focus();

                    return;
                }


                // =============================================
                // MONTAR JSON
                // =============================================

                /*
                    Enviamos SOMENTE os campos aceitos pelo
                    AtualizarPerfilRequest do backend.

                    Não enviamos:
                    - id
                    - CPF
                    - status
                    - senha
                */
                const dadosAtualizados = {

                    nome_completo: nome,

                    email: email,

                    telefone: telefone
                };


                // =============================================
                // PREPARAR BOTÃO SALVAR
                // =============================================

                /*
                    Desabilitamos o botão enquanto a requisição
                    estiver sendo processada.

                    Isso evita vários PUTs causados por
                    cliques repetidos.
                */
                btnSalvarPerfil.disabled = true;

                btnSalvarPerfil.textContent =
                    "Salvando...";


                // Remove mensagens anteriores.
                mostrarMensagem("");


                try {

                    // =========================================
                    // PUT /perfil
                    // =========================================

                    const resposta = await requisitarComRefresh(
                        "/api/perfil",
                        {
                            method: "PUT",

                            headers: {

                                "Accept":
                                    "application/json",

                                "Content-Type":
                                    "application/json",
                            },

                            /*
                                JSON.stringify transforma
                                o objeto JavaScript em JSON.
                            */
                            body: JSON.stringify(
                                dadosAtualizados
                            )
                        }
                    );


                    // =========================================
                    // TOKEN EXPIRADO
                    // =========================================

                    if (resposta.status === 401) {

                        limparSessao();

                        window.location.href = "/login";

                        return;
                    }


                    // =========================================
                    // CONTA SEM PERMISSÃO
                    // =========================================

                    if (resposta.status === 403) {

                        limparSessao();

                        alert(
                            "Sua conta não possui permissão de acesso."
                        );

                        window.location.href = "/login";

                        return;
                    }


                    // =========================================
                    // LER RESPOSTA DO BACKEND
                    // =========================================

                    /*
                        Mesmo quando ocorre erro, o FastAPI
                        normalmente devolve JSON.

                        Por isso lemos a resposta antes
                        de verificar resposta.ok.
                    */
                    const resultado =
                        await resposta.json();


                    // =========================================
                    // E-MAIL JÁ CADASTRADO
                    // =========================================

                    if (resposta.status === 409) {

                        mostrarMensagem(
                            resultado.detail ||
                            "Este e-mail já está cadastrado.",
                            "erro"
                        );

                        inputEmail.focus();

                        return;
                    }


                    // =========================================
                    // ERRO DE VALIDAÇÃO DO FASTAPI
                    // =========================================

                    if (resposta.status === 422) {

                        mostrarMensagem(
                            "Verifique os dados informados.",
                            "erro"
                        );

                        return;
                    }


                    // =========================================
                    // OUTROS ERROS
                    // =========================================

                    if (!resposta.ok) {

                        mostrarMensagem(
                            resultado.detail ||
                            "Não foi possível atualizar o perfil.",
                            "erro"
                        );

                        return;
                    }


                    // =========================================
                    // ATUALIZAÇÃO REALIZADA
                    // =========================================

                    /*
                        Nosso PUT retorna:

                        {
                            "mensagem": "...",
                            "cliente": {...}
                        }

                        Portanto, os dados atualizados estão
                        dentro de resultado.cliente.
                    */
                    clienteAtual =
                        resultado.cliente;


                    // =========================================
                    // ATUALIZAR ARMAZENAMENTO
                    // =========================================

                    salvarClienteLocalmente(
                        clienteAtual
                    );


                    // =========================================
                    // ATUALIZAR A TELA
                    // =========================================

                    atualizarInterface(
                        clienteAtual
                    );


                    // =========================================
                    // MOSTRAR SUCESSO
                    // =========================================

                    mostrarMensagem(
                        resultado.mensagem ||
                        "Perfil atualizado com sucesso.",
                        "sucesso"
                    );


                    /*
                        Mantemos o formulário visível por um
                        pequeno momento para o cliente enxergar
                        a mensagem de sucesso.
                    */
                    await new Promise(
                        (resolver) =>
                            setTimeout(resolver, 900)
                    );


                    // =========================================
                    // VOLTAR PARA VISUALIZAÇÃO
                    // =========================================

                    formEditarPerfil.hidden = true;

                    visualizacaoDados.hidden = false;

                    btnEditarDados.hidden = false;


                    /*
                        Limpamos a mensagem depois que voltamos
                        para a visualização normal.
                    */
                    mostrarMensagem("");


                } catch (erro) {

                    // =========================================
                    // ERRO DE REDE OU SERVIDOR
                    // =========================================

                    console.error(
                        "Erro ao atualizar perfil:",
                        erro
                    );


                    mostrarMensagem(
                        "Não foi possível atualizar o perfil. Tente novamente.",
                        "erro"
                    );


                } finally {

                    // =========================================
                    // RESTAURAR BOTÃO
                    // =========================================

                    /*
                        O finally executa tanto em caso
                        de sucesso quanto de erro.
                    */
                    btnSalvarPerfil.disabled = false;

                    btnSalvarPerfil.textContent =
                        "Salvar alterações";
                }
            }
        );
    }


    // ========================================================
    // BOTÃO COMEÇAR A COMPRAR
    // ========================================================

    if (btnComprar) {

        btnComprar.addEventListener(
            "click",
            () => {

                /*
                    Volta para a Home da Weblue.

                    Como index.html é servido na raiz,
                    utilizamos "/".
                */
                window.location.href = "/";
            }
        );
    }


    // ========================================================
    // BOTÃO SAIR
    // ========================================================

    if (btnSair) {

        btnSair.addEventListener(
            "click",
            async () => {

                await logoutClienteNoServidor();

                // Remove token e dados do cliente.
                limparSessao();


                // Redireciona para a página de login.
                window.location.href = "/login";
            }
        );
    }

});