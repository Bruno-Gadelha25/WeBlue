// ============================================================
// WEBLUE - LOGIN DO CLIENTE
// ============================================================


// ============================================================
// ELEMENTOS DA PÁGINA
// ============================================================

const formLogin =
    document.getElementById("formLogin");

const campoEmail =
    document.getElementById("email");

const campoSenha =
    document.getElementById("senha");

// Checkbox "Lembrar de mim".
const campoLembrar =
    document.getElementById("lembrar");

const erroEmail =
    document.getElementById("erroEmail");

const erroSenha =
    document.getElementById("erroSenha");

const mensagemLogin =
    document.getElementById("mensagemLogin");

const botaoEntrar =
    document.getElementById("botaoEntrar");

const botaoMostrarSenha =
    document.getElementById("botaoMostrarSenha");


// ============================================================
// CONFIGURAÇÃO DA API
// ============================================================

// Todas as rotas do backend agora utilizam /api.
const API_LOGIN = "/api/auth/login";


// ============================================================
// MOSTRAR / OCULTAR SENHA
// ============================================================

botaoMostrarSenha.addEventListener(
    "click",
    () => {

        const senhaEstaOculta =
            campoSenha.type === "password";

        campoSenha.type =
            senhaEstaOculta
                ? "text"
                : "password";

        botaoMostrarSenha.textContent =
            senhaEstaOculta
                ? "Ocultar"
                : "Mostrar";
    }
);


// ============================================================
// VALIDAR E-MAIL
// ============================================================

function emailValido(email) {

    // Formato básico:
    //
    // usuario@dominio.com
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
        email
    );
}


// ============================================================
// LIMPAR MENSAGENS
// ============================================================

function limparMensagens() {

    erroEmail.textContent = "";
    erroSenha.textContent = "";

    campoEmail.classList.remove(
        "invalido"
    );

    campoSenha.classList.remove(
        "invalido"
    );

    mensagemLogin.textContent = "";

    mensagemLogin.className =
        "mensagem-login";
}


// ============================================================
// VALIDAR FORMULÁRIO
// ============================================================

function validarFormulario() {

    let formularioValido = true;

    const email =
        campoEmail.value.trim();

    const senha =
        campoSenha.value;


    // ========================================================
    // E-MAIL
    // ========================================================

    if (email === "") {

        erroEmail.textContent =
            "Informe seu e-mail.";

        campoEmail.classList.add(
            "invalido"
        );

        formularioValido = false;

    } else if (!emailValido(email)) {

        erroEmail.textContent =
            "Informe um e-mail válido.";

        campoEmail.classList.add(
            "invalido"
        );

        formularioValido = false;
    }


    // ========================================================
    // SENHA
    // ========================================================

    if (senha === "") {

        erroSenha.textContent =
            "Informe sua senha.";

        campoSenha.classList.add(
            "invalido"
        );

        formularioValido = false;

    } else if (senha.length < 8) {

        erroSenha.textContent =
            "A senha deve possuir pelo menos 8 caracteres.";

        campoSenha.classList.add(
            "invalido"
        );

        formularioValido = false;
    }


    return formularioValido;
}


// ============================================================
// REALIZAR LOGIN
// ============================================================

formLogin.addEventListener(
    "submit",
    async (evento) => {

        // Impede o navegador de
        // recarregar a página.
        evento.preventDefault();


        // Limpa mensagens anteriores.
        limparMensagens();


        // ====================================================
        // VALIDAR FORMULÁRIO
        // ====================================================

        if (!validarFormulario()) {

            mensagemLogin.textContent =
                "Verifique os campos destacados.";

            mensagemLogin.className =
                "mensagem-login erro";

            return;
        }


        // ====================================================
        // ESTADO DE CARREGAMENTO
        // ====================================================

        botaoEntrar.disabled = true;

        botaoEntrar.textContent =
            "Entrando...";


        try {

            // =================================================
            // SESSÃO ATIVA
            // =================================================
            //
            // O token nunca deve ser persistido em localStorage.
            // A sessão do cliente fica restrita ao navegador
            // atual e é removida quando a aba for fechada.
            // =================================================

            const lembrar = false;


            // =================================================
            // POST /api/auth/login
            // =================================================

            const resposta = await fetch(
                API_LOGIN,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        email:
                            campoEmail.value.trim(),

                        senha:
                            campoSenha.value,

                        lembrar:
                            lembrar
                    })
                }
            );


            // =================================================
            // RESPOSTA DA API
            // =================================================

            const resultado =
                await resposta.json();


            // =================================================
            // ERRO NO LOGIN
            // =================================================

            if (!resposta.ok) {

                throw new Error(
                    resultado.detail ||
                    "Não foi possível realizar o login."
                );
            }


            // =================================================
            // LOGIN REALIZADO
            // =================================================

            mensagemLogin.textContent =
                `Login realizado com sucesso. Bem-vindo(a), ${resultado.cliente.nome_completo}!`;

            mensagemLogin.className =
                "mensagem-login sucesso";


            // =================================================
            // LIMPAR SESSÃO ANTIGA
            // =================================================

            sessionStorage.removeItem(
                "clienteWeblue"
            );

            sessionStorage.removeItem(
                "tokenWeblue"
            );

            sessionStorage.removeItem(
                "refreshTokenWeblue"
            );

            // Mantém compatibilidade com navegadores que ainda
            // tenham dados antigos em localStorage.
            localStorage.removeItem(
                "clienteWeblue"
            );

            localStorage.removeItem(
                "tokenWeblue"
            );

            localStorage.removeItem(
                "refreshTokenWeblue"
            );


            // =================================================
            // SALVAR SESSÃO
            // =================================================

            sessionStorage.setItem(
                "clienteWeblue",
                JSON.stringify(
                    resultado.cliente
                )
            );

            sessionStorage.setItem(
                "tokenWeblue",
                resultado.access_token
            );

            sessionStorage.setItem(
                "refreshTokenWeblue",
                resultado.refresh_token
            );


            // =================================================
            // REDIRECIONAR PARA ÁREA DO CLIENTE
            // =================================================

            setTimeout(
                () => {

                    window.location.href =
                        "/cliente";

                },
                800
            );


        } catch (erro) {


            // =================================================
            // ERRO DE CONEXÃO / LOGIN
            // =================================================

            mensagemLogin.textContent =
                erro.message === "Failed to fetch"
                    ? "Não foi possível conectar ao servidor."
                    : erro.message;

            mensagemLogin.className =
                "mensagem-login erro";


        } finally {


            // =================================================
            // RESTAURAR BOTÃO
            // =================================================

            botaoEntrar.disabled = false;

            botaoEntrar.textContent =
                "Entrar";
        }
    }
);


// ============================================================
// LIMPAR ERRO DO E-MAIL AO DIGITAR
// ============================================================

campoEmail.addEventListener(
    "input",
    () => {

        erroEmail.textContent = "";

        campoEmail.classList.remove(
            "invalido"
        );
    }
);


// ============================================================
// LIMPAR ERRO DA SENHA AO DIGITAR
// ============================================================

campoSenha.addEventListener(
    "input",
    () => {

        erroSenha.textContent = "";

        campoSenha.classList.remove(
            "invalido"
        );
    }
);