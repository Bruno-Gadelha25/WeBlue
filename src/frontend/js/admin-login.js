// ============================================================
// WEBLUE - LOGIN ADMINISTRATIVO
// ============================================================
//
// Responsabilidades:
//
// 1. Capturar e-mail e senha.
// 2. Validar os campos.
// 3. Enviar o login para o backend.
// 4. Receber o JWT administrativo.
// 5. Salvar o token.
// 6. Redirecionar para o painel de produtos.
//
// Endpoint utilizado:
//
// POST /api/admin/auth/login
//
// ============================================================


// ============================================================
// CONFIGURAÇÃO DA API
// ============================================================

const API_ADMIN_LOGIN = "/api/admin/auth/login";


// ============================================================
// CHAVE UTILIZADA PARA SALVAR O TOKEN
// ============================================================
//
// O token administrativo fica separado do token do cliente.
//
// Isso evita misturar:
//
// tokenWeblue
//
// com:
//
// tokenAdminWeblue
//

const TOKEN_ADMIN_KEY = "tokenAdminWeblue";
const REFRESH_TOKEN_ADMIN_KEY = "refreshTokenAdminWeblue";


// ============================================================
// ELEMENTOS DA PÁGINA
// ============================================================

const formAdminLogin =
    document.getElementById("formAdminLogin");

const campoEmail =
    document.getElementById("email");

const campoSenha =
    document.getElementById("senha");

const btnEntrar =
    document.getElementById("btnEntrar");

const textoBtnEntrar =
    document.getElementById("textoBtnEntrar");

const btnMostrarSenha =
    document.getElementById("btnMostrarSenha");

const mensagemLogin =
    document.getElementById("mensagemLogin");

const paramsUrl = new URLSearchParams(window.location.search);
const mensagemExpirada = paramsUrl.get("expirada") === "1";
const mensagemUrl = paramsUrl.get("msg") || "Sua sessão administrativa expirou. Faça login novamente.";

if (mensagemExpirada) {
    sessionStorage.removeItem(TOKEN_ADMIN_KEY);
    sessionStorage.removeItem(REFRESH_TOKEN_ADMIN_KEY);
    sessionStorage.removeItem("administradorWeblue");
    localStorage.removeItem(TOKEN_ADMIN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_ADMIN_KEY);
    localStorage.removeItem("administradorWeblue");
    mostrarMensagem(mensagemUrl, "info");
}


// ============================================================
// MOSTRAR MENSAGEM
// ============================================================

function mostrarMensagem(
    mensagem,
    tipo = "error"
) {

    mensagemLogin.textContent = mensagem;

    mensagemLogin.className =
        `login-message ${tipo}`;
}


// ============================================================
// LIMPAR MENSAGEM
// ============================================================

function limparMensagem() {

    mensagemLogin.textContent = "";

    mensagemLogin.className =
        "login-message";
}


// ============================================================
// ESTADO DO BOTÃO
// ============================================================

function alterarEstadoBotao(carregando) {

    if (carregando) {

        btnEntrar.disabled = true;

        textoBtnEntrar.textContent =
            "Entrando...";

        return;
    }

    btnEntrar.disabled = false;

    textoBtnEntrar.textContent =
        "Entrar no painel";
}


// ============================================================
// MOSTRAR / OCULTAR SENHA
// ============================================================

btnMostrarSenha.addEventListener(
    "click",
    function () {

        const senhaEstaOculta =
            campoSenha.type === "password";


        if (senhaEstaOculta) {

            campoSenha.type = "text";

            btnMostrarSenha.textContent =
                "Ocultar";

            btnMostrarSenha.setAttribute(
                "aria-label",
                "Ocultar senha"
            );

        } else {

            campoSenha.type = "password";

            btnMostrarSenha.textContent =
                "Mostrar";

            btnMostrarSenha.setAttribute(
                "aria-label",
                "Mostrar senha"
            );
        }
    }
);


// ============================================================
// VALIDAR E-MAIL
// ============================================================

function emailValido(email) {

    const regexEmail =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return regexEmail.test(email);
}


// ============================================================
// REALIZAR LOGIN
// ============================================================

async function realizarLogin(
    email,
    senha
) {

    // --------------------------------------------------------
    // ENVIAR LOGIN PARA O BACKEND
    // --------------------------------------------------------

    const resposta = await fetch(
        API_ADMIN_LOGIN,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                senha: senha
            })
        }
    );


    // --------------------------------------------------------
    // TENTAR LER RESPOSTA JSON
    // --------------------------------------------------------

    let dados = {};

    try {

        dados = await resposta.json();

    } catch (erro) {

        dados = {};
    }


    // --------------------------------------------------------
    // LOGIN NÃO AUTORIZADO
    // --------------------------------------------------------

    if (!resposta.ok) {

        const mensagemErro =
            dados.detail ||
            "Não foi possível realizar o login.";

        throw new Error(mensagemErro);
    }


    // --------------------------------------------------------
    // VALIDAR TOKEN RECEBIDO
    // --------------------------------------------------------

    if (!dados.access_token) {

        throw new Error(
            "O servidor não retornou o token administrativo."
        );
    }


    return dados;
}


// ============================================================
// ENVIO DO FORMULÁRIO
// ============================================================

formAdminLogin.addEventListener(
    "submit",
    async function (event) {

        // Impede o formulário de recarregar a página.
        event.preventDefault();


        // ----------------------------------------------------
        // LIMPAR MENSAGEM ANTERIOR
        // ----------------------------------------------------

        limparMensagem();


        // ----------------------------------------------------
        // PEGAR VALORES
        // ----------------------------------------------------

        const email =
            campoEmail.value
                .trim()
                .toLowerCase();

        const senha =
            campoSenha.value;


        // ----------------------------------------------------
        // VALIDAR E-MAIL
        // ----------------------------------------------------

        if (!email) {

            mostrarMensagem(
                "Informe o e-mail do administrador."
            );

            campoEmail.focus();

            return;
        }


        if (!emailValido(email)) {

            mostrarMensagem(
                "Informe um e-mail válido."
            );

            campoEmail.focus();

            return;
        }


        // ----------------------------------------------------
        // VALIDAR SENHA
        // ----------------------------------------------------

        if (!senha) {

            mostrarMensagem(
                "Informe a senha do administrador."
            );

            campoSenha.focus();

            return;
        }


        // ----------------------------------------------------
        // INICIAR LOGIN
        // ----------------------------------------------------

        alterarEstadoBotao(true);


        try {

            const dados =
                await realizarLogin(
                    email,
                    senha
                );


            // ------------------------------------------------
            // SALVAR TOKEN ADMINISTRATIVO
            // ------------------------------------------------

            sessionStorage.setItem(
                TOKEN_ADMIN_KEY,
                dados.access_token
            );

            if (dados.refresh_token) {
                sessionStorage.setItem(
                    REFRESH_TOKEN_ADMIN_KEY,
                    dados.refresh_token
                );
            }


            // ------------------------------------------------
            // SALVAR DADOS BÁSICOS DO ADMINISTRADOR
            // ------------------------------------------------

            if (dados.administrador) {

                sessionStorage.setItem(
                    "administradorWeblue",
                    JSON.stringify(
                        dados.administrador
                    )
                );
            }


            // ------------------------------------------------
            // LOGIN REALIZADO
            // ------------------------------------------------

            mostrarMensagem(
                "Login realizado com sucesso.",
                "success"
            );


            // ------------------------------------------------
            // REDIRECIONAR PARA O PAINEL
            // ------------------------------------------------

            setTimeout(
                function () {

                    window.location.href =
                        "/admin-produtos.html";

                },
                500
            );


        } catch (erro) {

            // ------------------------------------------------
            // ERRO NO LOGIN
            // ------------------------------------------------

            mostrarMensagem(
                erro.message ||
                "Não foi possível realizar o login."
            );


            // Por segurança, limpa a senha.
            campoSenha.value = "";

            campoSenha.focus();


        } finally {

            alterarEstadoBotao(false);
        }
    }
);


// ============================================================
// LIMPAR MENSAGEM AO DIGITAR NOVAMENTE
// ============================================================

campoEmail.addEventListener(
    "input",
    limparMensagem
);

campoSenha.addEventListener(
    "input",
    limparMensagem
);