// ============================================================
// WEBLUE - RECUPERAÇÃO DE SENHA
// ============================================================


// ============================================================
// ELEMENTOS DA PÁGINA
// ============================================================

const form =
    document.getElementById("form-recuperacao");

const mensagem =
    document.getElementById("mensagem");

const campoEmail =
    document.getElementById("email");

const campoToken =
    document.getElementById("token");

const campoNovaSenha =
    document.getElementById("nova-senha");

const campoConfirmarSenha =
    document.getElementById("confirmar-senha");

const botaoSolicitarToken =
    document.getElementById("solicitar-token");

const botaoAlterarSenha =
    form.querySelector(".botao-principal");


// ============================================================
// CONFIGURAÇÃO DA API
// ============================================================

// Rotas centralizadas da Weblue.
const API_SOLICITAR_RECUPERACAO =
    "/api/auth/solicitar-recuperacao";

const API_REDEFINIR_SENHA =
    "/api/auth/redefinir-senha";


// ============================================================
// MOSTRAR / OCULTAR SENHA
// ============================================================

const botoesMostrarSenha =
    document.querySelectorAll(".mostrar-senha");


botoesMostrarSenha.forEach((botao) => {

    botao.addEventListener("click", () => {

        const alvo =
            botao.dataset.alvo;

        const campo =
            document.getElementById(alvo);

        if (!campo) {
            return;
        }


        if (campo.type === "password") {

            campo.type = "text";

            botao.textContent =
                "Ocultar";

        } else {

            campo.type = "password";

            botao.textContent =
                "Mostrar";
        }
    });
});


// ============================================================
// MENSAGENS
// ============================================================

function exibirMensagem(texto, tipo) {

    mensagem.textContent = texto;

    mensagem.className =
        `mensagem ${tipo}`;
}


// ============================================================
// VALIDAR E-MAIL
// ============================================================

function emailValido(email) {

    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
        email
    );
}


// ============================================================
// VALIDIDAR SENHA
// ============================================================

function senhaValida(senha) {

    return (
        senha.length >= 8 &&
        /[A-Z]/.test(senha) &&
        /[a-z]/.test(senha) &&
        /[0-9]/.test(senha) &&
        /[^A-Za-z0-9]/.test(senha)
    );
}


// ============================================================
// ETAPA 1
// SOLICITAR TOKEN DE RECUPERAÇÃO
// ============================================================

if (botaoSolicitarToken) {

    botaoSolicitarToken.addEventListener(
        "click",
        async () => {

            const email =
                campoEmail.value.trim();


            // Limpa mensagens anteriores.
            mensagem.textContent = "";

            mensagem.className =
                "mensagem";


            // =================================================
            // E-MAIL OBRIGATÓRIO
            // =================================================

            if (!email) {

                exibirMensagem(
                    "Informe seu e-mail.",
                    "erro"
                );

                campoEmail.focus();

                return;
            }


            // =================================================
            // VALIDAR FORMATO DO E-MAIL
            // =================================================

            if (!emailValido(email)) {

                exibirMensagem(
                    "Informe um e-mail válido.",
                    "erro"
                );

                campoEmail.focus();

                return;
            }


            // =================================================
            // ESTADO DE CARREGAMENTO
            // =================================================

            botaoSolicitarToken.disabled =
                true;

            botaoSolicitarToken.textContent =
                "Gerando token...";


            try {

                // =============================================
                // POST /api/auth/solicitar-recuperacao
                // =============================================

                const resposta = await fetch(
                    API_SOLICITAR_RECUPERACAO,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            email: email
                        })
                    }
                );


                // =============================================
                // RESPOSTA DA API
                // =============================================

                const dados =
                    await resposta.json();


                // =============================================
                // ERRO
                // =============================================

                if (!resposta.ok) {

                    throw new Error(
                        dados.detail ||
                        "Não foi possível solicitar a recuperação."
                    );
                }


                // =============================================
                // SEGURANÇA
                // =============================================
                //
                // O token de recuperação não deve ser exposto
                // na resposta HTTP. Em produção ele seria enviado
                // por e-mail ou por um canal seguro.
                // =============================================

                // Sem token na resposta, o cliente precisa receber
                // o código por e-mail ou outro canal seguro.
                campoToken.value = "";


                // =============================================
                // SUCESSO
                // =============================================

                exibirMensagem(
                    "Se o e-mail estiver cadastrado, um token de recuperação foi enviado por canal seguro. Verifique seu e-mail e continue com a redefinição da senha.",
                    "sucesso"
                );


                campoToken.focus();


            } catch (erro) {

                console.error(
                    "Erro ao solicitar recuperação:",
                    erro
                );


                exibirMensagem(
                    erro.message === "Failed to fetch"
                        ? "Não foi possível conectar à Weblue."
                        : erro.message,
                    "erro"
                );


            } finally {

                botaoSolicitarToken.disabled =
                    false;

                botaoSolicitarToken.textContent =
                    "Gerar token";
            }
        }
    );
}


// ============================================================
// ETAPA 2
// REDEFINIR SENHA
// ============================================================

form.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        // ====================================================
        // DADOS INFORMADOS PELO CLIENTE
        // ====================================================

        const email =
            campoEmail.value.trim();

        const token =
            campoToken.value.trim();

        const novaSenha =
            campoNovaSenha.value;

        const confirmarSenha =
            campoConfirmarSenha.value;


        // Limpa mensagens anteriores.
        mensagem.className =
            "mensagem";

        mensagem.textContent =
            "";


        // ====================================================
        // CAMPOS OBRIGATÓRIOS
        // ====================================================

        if (
            !email ||
            !token ||
            !novaSenha ||
            !confirmarSenha
        ) {

            exibirMensagem(
                "Preencha todos os campos.",
                "erro"
            );

            return;
        }


        // ====================================================
        // VALIDAR E-MAIL
        // ====================================================

        if (!emailValido(email)) {

            exibirMensagem(
                "Informe um e-mail válido.",
                "erro"
            );

            campoEmail.focus();

            return;
        }


        // ====================================================
        // VALIDAR NOVA SENHA
        // ====================================================

        if (!senhaValida(novaSenha)) {

            exibirMensagem(
                "A nova senha deve ter pelo menos 8 caracteres, com letra maiúscula, minúscula, número e símbolo.",
                "erro"
            );

            campoNovaSenha.focus();

            return;
        }


        // ====================================================
        // CONFIRMAR SENHA
        // ====================================================

        if (novaSenha !== confirmarSenha) {

            exibirMensagem(
                "As senhas não coincidem.",
                "erro"
            );

            campoConfirmarSenha.focus();

            return;
        }


        // ====================================================
        // ESTADO DE CARREGAMENTO
        // ====================================================

        botaoAlterarSenha.disabled =
            true;

        botaoAlterarSenha.textContent =
            "Alterando senha...";


        try {

            // ================================================
            // POST /api/auth/redefinir-senha
            // ================================================

            const resposta = await fetch(
                API_REDEFINIR_SENHA,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        email: email,

                        token: token,

                        nova_senha:
                            novaSenha,

                        confirmar_senha:
                            confirmarSenha
                    })
                }
            );


            // =================================================
            // LER RESPOSTA
            // =================================================

            let dados = {};

            try {

                dados =
                    await resposta.json();

            } catch {

                dados = {};
            }


            // =================================================
            // ERRO
            // =================================================

            if (!resposta.ok) {

                let detalhe =
                    dados.detail;


                // FastAPI pode devolver erros
                // de validação como uma lista.
                if (Array.isArray(detalhe)) {

                    detalhe =
                        detalhe[0]?.msg;
                }


                throw new Error(
                    detalhe ||
                    "Não foi possível alterar a senha."
                );
            }


            // =================================================
            // SENHA ALTERADA
            // =================================================

            exibirMensagem(
                "Senha alterada com sucesso. Redirecionando para o login...",
                "sucesso"
            );


            form.reset();


            // =================================================
            // REDIRECIONAR PARA LOGIN
            // =================================================

            setTimeout(
                () => {

                    window.location.href =
                        "/login";

                },
                1500
            );


        } catch (erro) {

            console.error(
                "Erro ao redefinir senha:",
                erro
            );


            exibirMensagem(
                erro.message === "Failed to fetch"
                    ? "Não foi possível conectar à Weblue."
                    : erro.message,
                "erro"
            );


        } finally {

            // =================================================
            // RESTAURAR BOTÃO
            // =================================================

            botaoAlterarSenha.disabled =
                false;

            botaoAlterarSenha.textContent =
                "Alterar senha";
        }
    }
);