import streamlit as st
import pandas as pd
import numpy as np
import pickle
import time
import json
import hashlib
from datetime import datetime

st.set_page_config(
    page_title="HemaSakula",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────

SLOGAN = "Angola a Cuidar dos Seus"

MUNICIPIOS_INFO = {
    'Ingombota': {'provincia': 'Luanda', 'risco': 'Baixo', 'hospital': 'Hospital Josina Machel'},
    'Talatona': {'provincia': 'Luanda', 'risco': 'Baixo', 'hospital': 'Clínica Sagrada Esperança'},
    'Belas': {'provincia': 'Luanda', 'risco': 'Médio', 'hospital': 'Hospital Américo Boavida'},
    'Viana': {'provincia': 'Luanda', 'risco': 'Médio', 'hospital': 'Hospital Geral de Viana'},
    'Cacuaco': {'provincia': 'Luanda', 'risco': 'Alto', 'hospital': 'Hospital Geral de Cacuaco'},
    'Cazenga': {'provincia': 'Luanda', 'risco': 'Muito Alto', 'hospital': 'Hospital Municipal do Cazenga'},
    'Kilamba Kiaxi': {'provincia': 'Luanda', 'risco': 'Médio', 'hospital': 'Hospital Geral de Luanda'},
    'Rangel': {'provincia': 'Luanda', 'risco': 'Alto', 'hospital': 'Hospital Américo Boavida'},
    'Maianga': {'provincia': 'Luanda', 'risco': 'Médio', 'hospital': 'Hospital Josina Machel'},
    'Samba': {'provincia': 'Luanda', 'risco': 'Médio', 'hospital': 'Hospital Américo Boavida'},
    'Catete': {'provincia': 'Icolo e Bengo', 'risco': 'Alto', 'hospital': 'Hospital Municipal de Catete'},
    'Icolo e Bengo': {'provincia': 'Icolo e Bengo', 'risco': 'Alto', 'hospital': 'Centro de Saúde'}
}

FAIXAS_ETARIAS = [
    'Recém-nascido (0–28 dias)',
    'Lactente (1–12 meses)',
    'Criança (1–5 anos)',
    'Criança (5–12 anos)',
    'Adolescente (12–18 anos)',
    'Adulto jovem (18–45 anos)',
    'Adulto (45–65 anos)',
    'Idoso (>65 anos)'
]

MESES = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

ESTACOES_POR_MES = {
    'Janeiro': 'Chuvas', 'Fevereiro': 'Chuvas (pico)',
    'Março': 'Chuvas (pico)', 'Abril': 'Chuvas (pico)',
    'Maio': 'Chuvas (a acabar)', 'Junho': 'Cacimbo',
    'Julho': 'Cacimbo', 'Agosto': 'Cacimbo',
    'Setembro': 'Transição', 'Outubro': 'Chuvas (início)',
    'Novembro': 'Chuvas', 'Dezembro': 'Chuvas'
}

STATUS_GENETICO = ['Normal', 'Traço falciforme (AS)', 'Drepanocitose (SS)']
SEXOS = ['Masculino', 'Feminino']

CONDUTAS = {
    'Malária': {
        'leve': (
            'Coartem (Arteméter + Lumefantrina): 4 comprimidos de 12/12h '
            'durante 3 dias. Tomar sempre com comida — de preferência com '
            'gordura para melhor absorção. Paracetamol para a febre.'
        ),
        'grave': (
            'Artesunato EV 2,4 mg/kg às 0h, 12h e 24h, depois 1×/dia '
            'até tolerar via oral. Controlar Hb no dia 7 e 14. '
            'Se a parasitémia não baixar em 24h, reavaliar dose.'
        ),
        'exame': 'Gota espessa ou teste rápido (TDR)',
        'alertas': [
            'Convulsões',
            'Prostração — não come, não bebe, não anda',
            'Vómitos persistentes',
            'Urina escura (cor de coca-cola)',
            'Dispneia',
            'Icterícia',
            'Alteração do estado de consciência'
        ]
    },
    'Dengue': {
        'leve': (
            'Hidratação oral (60–80 mL/kg/dia). Paracetamol para a febre. '
            'Não administrar ibuprofeno nem aspirina — risco hemorrágico.'
        ),
        'grave': (
            'Soro EV com monitorização do hematócrito de 2/2h. Se o Ht subir '
            'mais de 20%, aumentar o ritmo da hidratação.'
        ),
        'exame': 'NS1 (fase inicial) ou IgM/IgG (a partir do 5.º dia)',
        'alertas': [
            'Dor abdominal intensa e persistente',
            'Vómitos incoercíveis',
            'Hemorragia gengival ou nasal',
            'Letargia ou irritabilidade extrema'
        ]
    },
    'Drepanocitose (SS)': {
        'leve': (
            'Ácido fólico 5 mg/dia. Hidratação abundante. '
            'Evitar frio e esforço físico excessivo. '
            'Seguimento regular no IHL ou centro de drepanocitose.'
        ),
        'grave': (
            'Crise vaso-oclusiva: analgesia escalonada (tramadol ou morfina) '
            '+ soro EV + oxigénio se SpO₂ < 95%. '
            'Referenciar ao IHL com urgência.'
        ),
        'exame': 'Electroforese de hemoglobina',
        'alertas': [
            'Febre (num drepanocítico é sempre urgência)',
            'Dor torácica — possível síndrome torácica aguda',
            'Priapismo',
            'Sinais de AVC — défice motor, disartria, desvio facial'
        ]
    },
    'Anemia Ferropriva': {
        'leve': (
            'Sulfato ferroso durante 3 a 6 meses. Tomar em jejum com '
            'sumo de limão (vitamina C melhora a absorção). '
            'Informar que as fezes ficam escuras — é esperado.'
        ),
        'grave': (
            'Se Hb < 5 g/dL, ponderar transfusão. '
            'Investigar causa — parasitose? Hemorragia oculta?'
        ),
        'exame': 'Ferritina sérica',
        'alertas': [
            'Dispneia em repouso',
            'Taquicardia marcada',
            'Palidez intensa — verificar palmas e conjuntivas'
        ]
    },
    'Cólera': {
        'leve': (
            'SRO conforme protocolo OMS. Preparar 1 saqueta em 1 litro '
            'de água tratada. Administrar em pequenas quantidades, com frequência.'
        ),
        'grave': (
            'Ringer Lactato EV em bólus até estabilização hemodinâmica. '
            'Azitromicina 1 g dose única. Notificação obrigatória à DPS.'
        ),
        'exame': 'Coprocultura',
        'alertas': [
            'Olhos encovados, mucosas secas',
            'Sinal da prega positivo',
            'Criança sem lágrimas',
            'Letargia ou agitação extrema'
        ]
    },
    'Febre Tifóide': {
        'leve': (
            'Ciprofloxacina 500 mg 12/12h durante 7–14 dias. '
            'Em crianças, preferir azitromicina. '
            'Hidratação e alimentação leve.'
        ),
        'grave': (
            'Ceftriaxona EV 2 g/dia + internamento. '
            'Vigiar sinais de perfuração intestinal — '
            'defesa abdominal, dor intensa, febre em pico.'
        ),
        'exame': 'Hemocultura (preferencial) ou coprocultura',
        'alertas': [
            'Abdómen em tábua — possível perfuração',
            'Confusão mental',
            'Rectorragia'
        ]
    },
    'Parasitose Intestinal': {
        'leve': (
            'Albendazol 400 mg dose única (> 2 anos e adultos). '
            'Repetir de 6/6 meses. '
            'Reforçar higiene das mãos e tratamento da água.'
        ),
        'grave': (
            'Albendazol 400 mg durante 3 dias + sulfato ferroso '
            'se anemia associada. Quantificar carga parasitária.'
        ),
        'exame': 'Exame parasitológico de fezes (3 amostras)',
        'alertas': [
            'Distensão abdominal intensa — risco de obstrução',
            'Desnutrição grave, sobretudo em crianças'
        ]
    },
    'Tuberculose': {
        'leve': (
            'Esquema DOTS: fase intensiva RHZE 2 meses, '
            'depois RH 4 meses. Toma observada directamente. '
            'O doente não pode abandonar o tratamento.'
        ),
        'grave': (
            'Internamento. Investigar formas extrapulmonares. '
            'Se HIV+, coordenar com TARV — atenção às interacções.'
        ),
        'exame': 'Baciloscopia (BK) ou GeneXpert',
        'alertas': [
            'Hemoptise',
            'Perda ponderal > 10%',
            'Sudorese nocturna profusa',
            'Tosse > 2 semanas sem melhoria'
        ]
    },
    'HIV/SIDA': {
        'leve': (
            'TARV 1.ª linha: Dolutegravir + Tenofovir + Lamivudina '
            '(comprimido único diário). Adesão rigorosa — mesma hora todos os dias. '
            'CD4 e carga viral aos 6 meses.'
        ),
        'grave': (
            'Tratar infecção oportunista activa primeiro. '
            'Iniciar TARV 2 semanas depois (excepto meningite '
            'criptocócica — esperar 4–6 semanas). Referenciar ao CTA.'
        ),
        'exame': 'Teste rápido HIV + CD4 + carga viral',
        'alertas': [
            'Infecções oportunistas de repetição',
            'Perda ponderal inexplicada',
            'Diarreia > 1 mês',
            'Candidíase oral persistente'
        ]
    },
    'Raiva (Mordedura)': {
        'leve': (
            'Lavar a ferida com água e sabão durante 15 minutos — '
            'medida que salva vidas. Vacina antirrábica nos dias 0, 3, 7 e 14. '
            'Não suturar a ferida.'
        ),
        'grave': (
            'Soro antirrábico + vacina. Não aguardar resultados. '
            'Se o animal morreu ou desapareceu, tratar como alto risco. '
            'Cada hora conta.'
        ),
        'exame': 'Não aguardar confirmação laboratorial — tratar de imediato',
        'alertas': [
            'Hidrofobia',
            'Aerofobia',
            'Agitação e desorientação',
            'Se estes sinais já surgiram, o prognóstico é reservado'
        ]
    },
    'Saudável': {
        'leve': (
            'Hemograma dentro dos parâmetros normais. Orientar prevenção: '
            'rede mosquiteira, água tratada, desparasitação regular, '
            'vacinação actualizada.'
        ),
        'grave': 'Não aplicável.',
        'exame': 'Sem necessidade de exames adicionais',
        'alertas': []
    }
}

# ─────────────────────────────────────────────
# PERFIS DE EMPRESA (novo sistema)
# ─────────────────────────────────────────────

PERFIS_USUARIO = {
    'admin': 'Administrador',
    'medico': 'Médico',
    'tecnico': 'Técnico de Laboratório',
    'enfermeiro': 'Enfermeiro'
}


# ─────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────

@st.cache_resource
def carregar_modelo():
    try:
        with open('models/modelo_angogen.pkl', 'rb') as f:
            modelo = pickle.load(f)
        with open('models/encoders.pkl', 'rb') as f:
            encoders = pickle.load(f)
        with open('models/features.pkl', 'rb') as f:
            features = pickle.load(f)
        return modelo, encoders, features
    except FileNotFoundError:
        return None, None, None


def formatar_numero(valor):
    return f"{valor:,.0f}".replace(",", ".")


def classificar_valor(valor, minimo, maximo):
    if valor < minimo:
        return "baixo", "Baixo"
    elif valor > maximo:
        return "alto", "Alto"
    return "normal", "Normal"


def determinar_gravidade(hb, plt):
    if hb < 5 or plt < 20000:
        return "CRÍTICO"
    elif hb < 7 or plt < 50000:
        return "GRAVE"
    elif hb < 10 or plt < 100000:
        return "MODERADO"
    return "LEVE"


def obter_classe_gravidade(gravidade):
    return {
        "LEVE": "badge-leve",
        "MODERADO": "badge-moderado",
        "GRAVE": "badge-grave",
        "CRÍTICO": "badge-critico"
    }.get(gravidade, "badge-leve")


def validar_leucograma(neutrofilos, linfocitos, monocitos, eosinofilos, basofilos):
    soma = neutrofilos + linfocitos + monocitos + eosinofilos + basofilos
    return (abs(soma - 100) <= 5, soma)


def fazer_predicao(modelo, encoders, features, dados):
    try:
        df_temp = pd.DataFrame([dados])
        for col in ['faixa_etaria', 'sexo', 'municipio', 'provincia',
                     'mes', 'estacao', 'status_genetico']:
            if col in dados and col in encoders:
                le = encoders[col]
                valor = dados[col]
                if valor in le.classes_:
                    df_temp[col + '_cod'] = le.transform([valor])[0]
                else:
                    df_temp[col + '_cod'] = 0
            else:
                df_temp[col + '_cod'] = 0

        df_temp['gestante_int'] = int(dados.get('gestante', False))
        df_temp['mordedura_int'] = int(dados.get('mordedura_recente', False))

        for feat in features:
            if feat not in df_temp.columns:
                df_temp[feat] = 0

        X_pred = df_temp[features]
        probas = modelo.predict_proba(X_pred)[0]
        le_diag = encoders['diagnostico']

        resultados = []
        for idx, prob in enumerate(probas):
            diag = le_diag.inverse_transform([idx])[0]
            resultados.append((diag, prob * 100))

        resultados.sort(key=lambda x: x[1], reverse=True)
        return resultados[:5], None

    except Exception as e:
        return None, str(e)


def processar_analise(modelo, encoders, features, dados_paciente):
    progress_bar = st.progress(0)
    status_text = st.empty()

    etapas = [
        ("A validar dados do paciente...", 20),
        ("A analisar parâmetros do hemograma...", 50),
        ("A cruzar dados epidemiológicos...", 80),
        ("A finalizar...", 100)
    ]
    for texto, progresso in etapas:
        status_text.text(texto)
        time.sleep(0.2)
        progress_bar.progress(progresso)

    gravidade = determinar_gravidade(
        dados_paciente['hemoglobina'], dados_paciente['plaquetas']
    )
    resultados, erro = fazer_predicao(
        modelo, encoders, features, dados_paciente
    )

    progress_bar.empty()
    status_text.empty()

    return gravidade, resultados, erro


def obter_dados_empresa(usuario):
    """Busca dados da empresa vinculada ao utilizador."""
    try:
        empresas = st.secrets.get("empresas", {})
        vinculos = st.secrets.get("vinculos", {})

        empresa_id = vinculos.get(usuario, None)
        if empresa_id and empresa_id in empresas:
            return empresas[empresa_id]
        return None
    except Exception:
        return None


def obter_perfil_usuario(usuario):
    """Busca o perfil/papel do utilizador."""
    try:
        perfis = st.secrets.get("perfis", {})
        return perfis.get(usuario, "tecnico")
    except Exception:
        return "tecnico"


# ─────────────────────────────────────────────
# CSS DO LOGIN (isolado, só aparece antes de autenticar)
# ─────────────────────────────────────────────

def aplicar_css_login():
    st.markdown("""
    <style>
    /* ── Reset total da página para o login ── */
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 40%, #312E81 100%);
        overflow: hidden;
    }

    /* Esconder TUDO do Streamlit */
    [data-testid="stSidebar"],
    header[data-testid="stHeader"],
    footer,
    #MainMenu,
    [data-testid="stToolbar"],
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }

    /* Remover padding excessivo */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ── Wrapper de fundo com partículas decorativas ── */
    .login-page-wrapper {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }

    .login-page-wrapper::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .login-page-wrapper::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.06) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    /* ── Card de login ── */
    .login-card {
        width: 100%;
        max-width: 440px;
        background: #FFFFFF;
        border-radius: 24px;
        padding: 2.75rem 2.5rem 2.25rem 2.5rem;
        box-shadow:
            0 4px 6px rgba(0, 0, 0, 0.05),
            0 20px 60px rgba(0, 0, 0, 0.15),
            0 0 0 1px rgba(255, 255, 255, 0.05);
        position: relative;
        z-index: 10;
        animation: loginSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes loginSlideUp {
        from { opacity: 0; transform: translateY(30px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Ícone do topo ── */
    .login-brand-icon {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #312E81 0%, #4338CA 100%);
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin: 0 auto 1.5rem auto;
        box-shadow: 0 8px 24px rgba(49, 46, 129, 0.3);
        color: white;
    }

    /* ── Título e subtítulo ── */
    .login-brand-name {
        text-align: center;
        font-size: 2rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.03em;
        margin-bottom: 0.25rem;
        line-height: 1.2;
    }

    .login-brand-slogan {
        text-align: center;
        font-size: 0.925rem;
        color: #64748B;
        font-style: italic;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* ── Separador elegante ── */
    .login-separator {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.75rem;
    }

    .login-separator::before,
    .login-separator::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, #E2E8F0, transparent);
    }

    .login-separator-text {
        font-size: 0.7rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
        white-space: nowrap;
    }

    /* ── Labels dos inputs ── */
    .login-label {
        display: block;
        font-size: 0.8rem;
        font-weight: 600;
        color: #475569;
        margin-bottom: 0.4rem;
        letter-spacing: 0.02em;
    }

    /* ── Estilo dos inputs Streamlit dentro do login ── */
    .login-fields-area [data-testid="stTextInput"] > div > div > input {
        background-color: #F8FAFC !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 12px !important;
        color: #0F172A !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.925rem !important;
        transition: all 0.2s ease !important;
        font-weight: 400 !important;
    }

    .login-fields-area [data-testid="stTextInput"] > div > div > input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
        background-color: #FFFFFF !important;
    }

    .login-fields-area [data-testid="stTextInput"] > div > div > input::placeholder {
        color: #94A3B8 !important;
        font-weight: 400 !important;
    }

    /* Esconder labels padrão do Streamlit nos inputs */
    .login-fields-area [data-testid="stTextInput"] > label {
        display: none !important;
    }

    /* ── Espaçamento entre campos ── */
    .login-spacer {
        height: 1rem;
    }

    .login-spacer-lg {
        height: 1.5rem;
    }

    /* ── Botão de entrar ── */
    .login-fields-area .stButton > button {
        background: linear-gradient(135deg, #312E81 0%, #4338CA 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.85rem 2rem !important;
        width: 100% !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 16px rgba(49, 46, 129, 0.35) !important;
        letter-spacing: 0.02em !important;
        cursor: pointer !important;
    }

    .login-fields-area .stButton > button:hover {
        background: linear-gradient(135deg, #3730A3 0%, #4F46E5 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(49, 46, 129, 0.45) !important;
    }

    .login-fields-area .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 8px rgba(49, 46, 129, 0.3) !important;
    }

    /* ── Erro de login ── */
    .login-fields-area .stAlert {
        border-radius: 10px !important;
        font-size: 0.85rem !important;
        margin-top: 0.75rem !important;
    }

    /* ── Rodapé do login ── */
    .login-footer-text {
        text-align: center;
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 2rem;
        line-height: 1.8;
        letter-spacing: 0.01em;
    }

    .login-footer-text strong {
        color: #64748B;
    }

    /* ── Indicador de segurança ── */
    .login-security {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.4rem;
        margin-top: 1.25rem;
        font-size: 0.7rem;
        color: #94A3B8;
        letter-spacing: 0.03em;
    }

    .login-security-dot {
        width: 6px;
        height: 6px;
        background: #22C55E;
        border-radius: 50%;
        display: inline-block;
        animation: securityPulse 2s infinite;
    }

    @keyframes securityPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ECRÃ DE LOGIN (reconstruído de raiz)
# ─────────────────────────────────────────────

def verificar_acesso():
    def processar_login():
        usuario = st.session_state.get("input_usuario", "").strip().lower()
        senha = st.session_state.get("input_senha", "")
        try:
            usuarios_validos = st.secrets["usuarios"]
            if usuario in usuarios_validos and usuarios_validos[usuario] == senha:
                st.session_state["autenticado"] = True
                st.session_state["usuario_atual"] = usuario
                st.session_state["perfil"] = obter_perfil_usuario(usuario)
                st.session_state["empresa"] = obter_dados_empresa(usuario)
            else:
                st.session_state["erro_login"] = True
        except Exception:
            st.session_state["erro_login"] = True

    if st.session_state.get("autenticado", False):
        return True

    # Aplicar CSS exclusivo do login
    aplicar_css_login()

    # Estrutura visual — tudo dentro de colunas para centrar
    spacer_left, col_login, spacer_right = st.columns([1, 1.4, 1])

    with col_login:
        # Parte superior do card (HTML puro)
        st.markdown(f"""
        <div class="login-page-wrapper">
        <div class="login-card">
            <div class="login-brand-icon">🩺</div>
            <div class="login-brand-name">HemaSakula</div>
            <div class="login-brand-slogan">{SLOGAN}</div>

            <div class="login-separator">
                <span class="login-separator-text">Acesso ao sistema</span>
            </div>

            <span class="login-label">Utilizador</span>
        """, unsafe_allow_html=True)

        # Campo utilizador — integrado visualmente
        st.markdown('<div class="login-fields-area">', unsafe_allow_html=True)
        st.text_input(
            "Utilizador",
            key="input_usuario",
            placeholder="Introduza o seu nome de utilizador",
            label_visibility="collapsed"
        )

        st.markdown(
            '<div class="login-spacer"></div>'
            '<span class="login-label">Palavra-passe</span>',
            unsafe_allow_html=True
        )

        st.text_input(
            "Senha",
            type="password",
            key="input_senha",
            placeholder="Introduza a sua palavra-passe",
            label_visibility="collapsed"
        )

        st.markdown('<div class="login-spacer-lg"></div>', unsafe_allow_html=True)

        # Botão
        if st.button("Entrar no Sistema", use_container_width=True):
            processar_login()
            if st.session_state.get("autenticado"):
                st.rerun()

        # Erro de login
        if st.session_state.get("erro_login", False):
            st.error("Credenciais inválidas. Verifique o utilizador e a palavra-passe.")
            st.session_state["erro_login"] = False

        st.markdown('</div>', unsafe_allow_html=True)  # fecha login-fields-area

        # Rodapé do card
        st.markdown("""
            <div class="login-security">
                <span class="login-security-dot"></span>
                Conexão segura
            </div>

            <div class="login-footer-text">
                Acesso restrito a profissionais autorizados<br>
                <strong>HemaSakula</strong> · Angola 2026
            </div>
        </div><!-- fecha login-card -->
        </div><!-- fecha login-page-wrapper -->
        """, unsafe_allow_html=True)

    return False


# ─────────────────────────────────────────────
# CSS GLOBAL (aplicado APENAS após login)
# ─────────────────────────────────────────────

def aplicar_css_global():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

    .stApp { background-color: #F8FAFC; color: #0F172A; }
    .main .block-container { padding: 2rem 3.5rem; max-width: 1300px; }

    /* ── Tipografia ── */
    h1 {
        color: #0F172A !important; font-weight: 800 !important; font-size: 2rem !important;
        letter-spacing: -0.03em !important; margin-bottom: 0.25rem !important;
    }
    h2 {
        color: #1E293B !important; font-weight: 700 !important; font-size: 1.3rem !important;
        margin-top: 2.5rem !important; margin-bottom: 1.25rem !important;
        padding-bottom: 0.75rem !important; border-bottom: 1px solid #E2E8F0 !important;
    }
    h3 {
        color: #334155 !important; font-weight: 600 !important; font-size: 1.05rem !important;
        margin-bottom: 1rem !important;
    }

    label, .stSelectbox label, .stNumberInput label, .stCheckbox label {
        color: #475569 !important; font-weight: 500 !important; font-size: 0.85rem !important;
    }

    /* ── Barra do topo (user bar) ── */
    .user-bar {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 0.85rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    .user-bar-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .user-avatar {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #312E81, #4338CA);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        color: white;
        font-weight: 700;
    }

    .user-name {
        font-weight: 600;
        color: #0F172A;
        font-size: 0.9rem;
    }

    .user-role {
        font-size: 0.75rem;
        color: #64748B;
    }

    .user-bar-right {
        display: flex;
        align-items: center;
        gap: 1.25rem;
    }

    .empresa-badge {
        background: #F0FDF4;
        border: 1px solid #DCFCE7;
        color: #166534;
        padding: 0.3rem 0.75rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .data-badge {
        color: #94A3B8;
        font-size: 0.8rem;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #F1F5F9 !important;
        border-bottom-color: #1E293B !important;
    }

    [data-testid="stSidebar"] label { color: #CBD5E1 !important; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span { color: #94A3B8 !important; }

    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stNumberInput input {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        color: #F1F5F9 !important;
    }

    [data-testid="stSidebar"] .stNumberInput button {
        background-color: #334155 !important;
        border-color: #334155 !important;
        color: #F1F5F9 !important;
    }

    [data-testid="stSidebar"] .stCheckbox label span {
        color: #CBD5E1 !important;
    }

    /* Botão de logout na sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: #EF4444 !important;
        border: 1px solid #7F1D1D !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
        margin-top: 1rem !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #7F1D1D !important;
        color: #FFFFFF !important;
    }

    /* ── Inputs no corpo principal ── */
    .stNumberInput input {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 10px !important;
        color: #0F172A !important;
        transition: border-color 0.2s ease !important;
    }

    .stNumberInput input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }

    .stNumberInput button {
        background-color: #F1F5F9 !important;
        border: 1px solid #E2E8F0 !important;
        color: #475569 !important;
        border-radius: 8px !important;
    }

    /* ── Botão do formulário ── */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #312E81 0%, #4338CA 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.85rem 2.5rem !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 16px rgba(49, 46, 129, 0.3) !important;
        letter-spacing: 0.01em !important;
    }

    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #3730A3 0%, #4F46E5 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(49, 46, 129, 0.4) !important;
    }

    /* ── Métricas ── */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    [data-testid="stMetric"] label {
        color: #64748B !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em;
        font-size: 0.75rem !important;
        text-transform: uppercase;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    /* ── Progress bar ── */
    .stProgress > div > div {
        background: linear-gradient(90deg, #312E81, #4338CA) !important;
        border-radius: 6px;
    }
    .stProgress > div {
        background-color: #E2E8F0 !important;
        border-radius: 6px;
    }

    /* ── Cards e badges ── */
    .card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s ease;
    }

    .card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .badge {
        display: inline-block;
        padding: 0.4rem 0.9rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }

    .badge-leve {
        background-color: #F0FDF4;
        color: #166534;
        border: 1px solid #DCFCE7;
    }
    .badge-moderado {
        background-color: #FFFBEB;
        color: #92400E;
        border: 1px solid #FEF3C7;
    }
    .badge-grave {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FEE2E2;
    }
    .badge-critico {
        background-color: #7F1D1D;
        color: #FFFFFF;
        border: 1px solid #991B1B;
    }

    .status-operacional {
        background-color: #F0FDF4;
        border: 1px solid #DCFCE7;
        border-left: 4px solid #166534;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin: 1.25rem 0;
    }
    .status-operacional p {
        margin: 0;
        color: #166534;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .aviso-institucional {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #475569;
        border-radius: 10px;
        padding: 1.25rem;
        margin: 1rem 0 1.5rem 0;
    }
    .aviso-institucional p {
        margin: 0;
        color: #334155;
        font-size: 0.875rem;
        line-height: 1.7;
    }

    /* ── Headers de série ── */
    .serie-vermelha-header {
        color: #DC2626 !important; font-weight: 700 !important; font-size: 0.95rem !important;
        border-bottom: 2px solid #DC2626; padding-bottom: 0.5rem;
        margin-bottom: 1.5rem !important; letter-spacing: 0.02em;
    }
    .serie-branca-header {
        color: #475569 !important; font-weight: 700 !important; font-size: 0.95rem !important;
        border-bottom: 2px solid #475569; padding-bottom: 0.5rem;
        margin-bottom: 1.5rem !important; letter-spacing: 0.02em;
    }
    .serie-plaquetas-header {
        color: #4338CA !important; font-weight: 700 !important; font-size: 0.95rem !important;
        border-bottom: 2px solid #4338CA; padding-bottom: 0.5rem;
        margin-bottom: 1.5rem !important; letter-spacing: 0.02em;
    }

    /* ── Utilidades ── */
    hr { border: none; height: 1px; background-color: #E2E8F0; margin: 2rem 0; }
    .text-muted { color: #64748B; font-size: 0.85rem; }
    .text-small { font-size: 0.8rem; }

    .footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 1px solid #E2E8F0;
        color: #94A3B8;
        font-size: 0.8rem;
        line-height: 1.8;
    }

    .footer strong {
        color: #64748B;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: #334155 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BARRA DE UTILIZADOR (empresa + perfil)
# ─────────────────────────────────────────────

def mostrar_barra_usuario():
    """Mostra a barra superior com dados do utilizador e empresa."""
    usuario = st.session_state.get("usuario_atual", "utilizador")
    perfil = st.session_state.get("perfil", "tecnico")
    empresa = st.session_state.get("empresa", None)

    perfil_nome = PERFIS_USUARIO.get(perfil, "Utilizador")
    iniciais = usuario[:2].upper()

    empresa_html = ""
    if empresa:
        nome_empresa = empresa if isinstance(empresa, str) else empresa.get("nome", "Instituição")
        empresa_html = f'<span class="empresa-badge">🏥 {nome_empresa}</span>'

    st.markdown(f"""
    <div class="user-bar">
        <div class="user-bar-left">
            <div class="user-avatar">{iniciais}</div>
            <div>
                <div class="user-name">{usuario.capitalize()}</div>
                <div class="user-role">{perfil_nome}</div>
            </div>
        </div>
        <div class="user-bar-right">
            {empresa_html}
            <span class="data-badge">{datetime.now().strftime("%d/%m/%Y · %H:%M")}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────

def main():
    if not verificar_acesso():
        st.stop()

    # Após login, aplicar CSS da app
    aplicar_css_global()

    # Barra de utilizador no topo
    mostrar_barra_usuario()

    # Cabeçalho
    st.title("🩺 HemaSakula")
    st.markdown(
        f'<p style="color: #64748B; font-size: 0.95rem; margin-top: -0.75rem; '
        f'font-style: italic; margin-bottom: 0.5rem;">{SLOGAN}</p>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="aviso-institucional">
        <p><strong>Nota:</strong> Este sistema é uma ferramenta de apoio à decisão clínica.
        Não substitui a avaliação presencial nem o julgamento do profissional de saúde.
        Os resultados devem ser interpretados no contexto clínico do doente.</p>
    </div>
    """, unsafe_allow_html=True)

    modelo, encoders, features = carregar_modelo()

    if modelo is None:
        st.error(
            "Modelo não encontrado. Execute primeiro: `python modelo_ml.py`"
        )
        return

    st.markdown("""
    <div class="status-operacional">
        <p>✓ Sistema operacional — modelo carregado com sucesso</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar: dados do paciente ──
    with st.sidebar:
        st.header("Dados do Paciente")

        st.subheader("Identificação")
        faixa_etaria = st.selectbox("Faixa etária", FAIXAS_ETARIAS, index=5)
        sexo = st.selectbox("Sexo biológico", SEXOS)

        gestante = False
        if sexo == 'Feminino' and (
            'Adulto' in faixa_etaria or 'Adolescente' in faixa_etaria
        ):
            gestante = st.checkbox("Grávida")

        peso = st.number_input("Peso (kg)", 1.0, 200.0, 65.0, 0.5)

        st.subheader("Localização")
        municipio = st.selectbox("Município", list(MUNICIPIOS_INFO.keys()))
        info_mun = MUNICIPIOS_INFO[municipio]
        provincia = info_mun['provincia']
        st.markdown(f"**Província:** {provincia}")
        st.markdown(f"**Risco epidemiológico:** {info_mun['risco']}")

        st.subheader("Data da colheita")
        mes = st.selectbox("Mês", MESES, index=datetime.now().month - 1)
        estacao = ESTACOES_POR_MES[mes]
        st.markdown(f"**Estação:** {estacao}")

        st.subheader("Antecedentes")
        status_genetico = st.selectbox(
            "Hemoglobina (genética)", STATUS_GENETICO
        )
        mordedura = st.checkbox("Mordedura animal recente")

        # Separador visual
        st.markdown("---")

        # Botão de logout
        if st.button("🚪 Terminar Sessão"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # ── Corpo: hemograma ──
    st.header("Hemograma")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<p class="serie-vermelha-header">Série Vermelha</p>',
            unsafe_allow_html=True
        )
        hemoglobina = st.number_input(
            "Hemoglobina (g/dL)", 3.0, 22.0, 12.5, 0.1
        )
        hematocrito = st.number_input(
            "Hematócrito (%)", 10.0, 70.0, 38.0, 0.5
        )
        hemacias = st.number_input(
            "Eritrócitos (×10⁶/µL)", 2.0, 7.0, 4.5, 0.1
        )
        vcm = st.number_input("VCM (fL)", 50.0, 120.0, 88.0, 1.0)
        hcm = st.number_input("HCM (pg)", 15.0, 40.0, 29.0, 0.5)
        chcm = st.number_input("CHCM (g/dL)", 28.0, 40.0, 33.5, 0.5)
        rdw = st.number_input("RDW (%)", 10.0, 25.0, 13.5, 0.1)

    with col2:
        st.markdown(
            '<p class="serie-branca-header">Série Branca</p>',
            unsafe_allow_html=True
        )
        leucocitos = st.number_input(
            "Leucócitos (/mm³)", 500, 50000, 7500, 100
        )
        neutrofilos = st.number_input(
            "Neutrófilos (%)", 10.0, 90.0, 58.0, 1.0
        )
        linfocitos = st.number_input(
            "Linfócitos (%)", 5.0, 70.0, 32.0, 1.0
        )
        monocitos = st.number_input(
            "Monócitos (%)", 0.0, 20.0, 6.0, 0.5
        )
        eosinofilos = st.number_input(
            "Eosinófilos (%)", 0.0, 25.0, 3.0, 0.5
        )
        basofilos = st.number_input(
            "Basófilos (%)", 0.0, 3.0, 0.5, 0.1
        )

        valido, soma = validar_leucograma(
            neutrofilos, linfocitos, monocitos, eosinofilos, basofilos
        )
        if not valido:
            st.warning(
                f"Diferencial leucocitário soma {soma:.1f}% — esperado ≈ 100%."
            )

    with col3:
        st.markdown(
            '<p class="serie-plaquetas-header">Plaquetas e Outros</p>',
            unsafe_allow_html=True
        )
        plaquetas = st.number_input(
            "Plaquetas (/mm³)", 5000, 1000000, 250000, 5000
        )
        vpm = st.number_input("VPM (fL)", 5.0, 15.0, 9.5, 0.5)
        reticulocitos = st.number_input(
            "Reticulócitos (%)", 0.2, 15.0, 1.2, 0.1
        )

    st.markdown("---")

    # ── Formulário de análise ──
    with st.form(key="form_analise"):
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit = st.form_submit_button(
                "Analisar Hemograma", use_container_width=True
            )

        if submit:
            dados = {
                'faixa_etaria': faixa_etaria,
                'sexo': sexo,
                'gestante': gestante,
                'peso_kg': peso,
                'municipio': municipio,
                'provincia': provincia,
                'mes': mes,
                'estacao': estacao,
                'status_genetico': status_genetico,
                'mordedura_recente': mordedura,
                'hemoglobina': hemoglobina,
                'hematocrito': hematocrito,
                'hemacias': hemacias,
                'vcm': vcm,
                'hcm': hcm,
                'chcm': chcm,
                'rdw': rdw,
                'leucocitos': leucocitos,
                'neutrofilos': neutrofilos,
                'linfocitos': linfocitos,
                'monocitos': monocitos,
                'eosinofilos': eosinofilos,
                'basofilos': basofilos,
                'plaquetas': plaquetas,
                'vpm': vpm,
                'reticulocitos': reticulocitos
            }

            gravidade, resultados, erro = processar_analise(
                modelo, encoders, features, dados
            )

            if erro:
                st.error(f"Erro no processamento: {erro}")
                return

            if not resultados:
                st.error(
                    "Não foi possível gerar resultados. "
                    "Verifique os dados introduzidos."
                )
                return

            diag_principal = resultados[0][0]

            # ── Resultados ──
            st.header("Resultados")

            col_r1, col_r2 = st.columns(2)

            with col_r1:
                classe = obter_classe_gravidade(gravidade)
                st.markdown(f"""
                <div class="card">
                    <div class="text-muted text-small"
                         style="text-transform: uppercase; letter-spacing: 0.05em;">
                        Gravidade
                    </div>
                    <div style="margin-top: 0.75rem;">
                        <span class="badge {classe}"
                              style="font-size: 0.9rem; padding: 0.5rem 1rem;">
                            {gravidade}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_r2:
                st.markdown(f"""
                <div class="card">
                    <div class="text-muted text-small"
                         style="text-transform: uppercase; letter-spacing: 0.05em;">
                        Referenciar para
                    </div>
                    <div style="margin-top: 0.75rem; font-weight: 600;
                         color: #0F172A;">
                        {info_mun['hospital']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.subheader("Hipóteses diagnósticas")

            for i, (diag, prob) in enumerate(resultados[:3]):
                if i == 0:
                    st.markdown(f"""
                    <div class="card" style="border-left: 4px solid #312E81;">
                        <div style="display: flex; justify-content: space-between;
                             align-items: center;">
                            <span style="font-size: 1.1rem; font-weight: 700;
                                  color: #0F172A;">
                                1. {diag}
                            </span>
                            <span style="background: linear-gradient(135deg, #312E81, #4338CA);
                                  color: white; padding: 0.4rem 1rem;
                                  border-radius: 8px; font-weight: 700;
                                  font-size: 0.9rem;">
                                {prob:.1f}%
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(prob / 100)
                else:
                    st.markdown(f"""
                    <div class="card" style="padding: 1rem 1.25rem;">
                        <div style="display: flex; justify-content: space-between;
                             align-items: center;">
                            <span style="color: #334155; font-weight: 500;">
                                {i+1}. {diag}
                            </span>
                            <span style="color: #64748B; font-weight: 600;">
                                {prob:.1f}%
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.subheader("Conduta recomendada")

            if diag_principal in CONDUTAS:
                cond = CONDUTAS[diag_principal]
                if gravidade in ["GRAVE", "CRÍTICO"]:
                    st.error(f"**Conduta:** {cond['grave']}")
                else:
                    st.info(f"**Conduta:** {cond['leve']}")

                st.markdown(
                    f'<div class="card">'
                    f'<strong>Exame confirmatório:</strong> {cond["exame"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                if cond['alertas']:
                    with st.expander(
                        "⚠ Sinais de alarme — referenciar imediatamente"
                    ):
                        for a in cond['alertas']:
                            st.markdown(f"- {a}")

            st.subheader("Interpretação do hemograma")

            col_l1, col_l2 = st.columns(2)

            with col_l1:
                _, hb_l = classificar_valor(hemoglobina, 11.5, 16.5)
                st.metric("Hemoglobina", f"{hemoglobina} g/dL", hb_l)
                _, plt_l = classificar_valor(plaquetas, 140000, 400000)
                st.metric(
                    "Plaquetas",
                    f"{formatar_numero(plaquetas)}/mm³",
                    plt_l
                )
                _, leu_l = classificar_valor(leucocitos, 4000, 10000)
                st.metric(
                    "Leucócitos",
                    f"{formatar_numero(leucocitos)}/mm³",
                    leu_l
                )

            with col_l2:
                _, vcm_l = classificar_valor(vcm, 80, 98)
                st.metric("VCM", f"{vcm} fL", vcm_l)
                _, eos_l = classificar_valor(eosinofilos, 1, 5)
                st.metric("Eosinófilos", f"{eosinofilos}%", eos_l)
                _, ret_l = classificar_valor(reticulocitos, 0.5, 2.5)
                st.metric("Reticulócitos", f"{reticulocitos}%", ret_l)

            if status_genetico in [
                'Traço falciforme (AS)', 'Drepanocitose (SS)'
            ]:
                st.warning(
                    f"**Hemoglobinopatia: {status_genetico}.** "
                    f"Seguimento no IHL ou centro de drepanocitose. "
                    f"Ácido fólico 5 mg/dia, hidratação abundante, "
                    f"evitar frio e factores precipitantes de crise."
                )

            if mordedura:
                st.error(
                    "**Mordedura animal — risco rábico.** "
                    "Lavar a ferida com água e sabão durante 15 minutos. "
                    "Iniciar profilaxia antirrábica sem aguardar resultados. "
                    "Cada hora conta."
                )

    # Footer
    st.markdown(f"""
    <div class="footer">
        <strong>HemaSakula</strong> · {SLOGAN}<br>
        Angola 2026
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
