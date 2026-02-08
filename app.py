import streamlit as st
import pandas as pd
import numpy as np
import pickle
import time
from datetime import datetime

st.set_page_config(
    page_title="HemaSakula",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════

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
            'Coartem (Artémer + Lumefantrina): 4 comprimidos de 12/12h '
            'durante 3 dias. Tomar sempre com comida — de preferência com '
            'gordura pra absorver melhor. Paracetamol pra baixar a febre.'
        ),
        'grave': (
            'Artesunato EV 2,4 mg/kg às 0h, 12h e 24h, depois 1×/dia '
            'até o doente aguentar via oral. Controlar Hb no dia 7 e 14. '
            'Se a parasitémia não baixar em 24h, reavaliar a dose.'
        ),
        'exame': 'Gota espessa ou teste rápido (TDR)',
        'alertas': [
            'Convulsões',
            'Prostração — não come, não bebe, não anda',
            'Vómitos que não param',
            'Urina escura (cor de coca-cola)',
            'Falta de ar',
            'Amarelão nos olhos (icterícia)',
            'Confusão ou perda de consciência'
        ]
    },
    'Dengue': {
        'leve': (
            'Hidratar bem por via oral (60–80 mL/kg/dia). Paracetamol pra febre. '
            'Nada de ibuprofeno nem aspirina — pode causar hemorragia.'
        ),
        'grave': (
            'Soro EV e monitorizar o hematócrito de 2 em 2 horas. Se o Ht subir '
            'mais de 20%, aumentar o ritmo da hidratação.'
        ),
        'exame': 'NS1 (fase inicial) ou IgM/IgG (a partir do 5.º dia)',
        'alertas': [
            'Dor de barriga forte que não passa',
            'Vómitos sem parar',
            'Sangramento na gengiva ou pelo nariz',
            'Criança mole demais ou muito irritada'
        ]
    },
    'Drepanocitose (SS)': {
        'leve': (
            'Ácido fólico 5 mg/dia. Beber muita água. '
            'Evitar frio e esforço físico a mais. '
            'Seguimento regular no IHL ou centro de drepanocitose.'
        ),
        'grave': (
            'Crise vaso-oclusiva: analgesia escalonada (tramadol ou morfina) '
            '+ soro EV + oxigénio se SpO₂ < 95%. '
            'Referenciar ao IHL com urgência.'
        ),
        'exame': 'Electroforese de hemoglobina',
        'alertas': [
            'Febre — num drepanocítico é sempre urgência',
            'Dor no peito — pode ser síndrome torácica aguda',
            'Priapismo',
            'Sinais de AVC — braço ou perna sem força, fala enrolada, boca torta'
        ]
    },
    'Anemia Ferropriva': {
        'leve': (
            'Sulfato ferroso durante 3 a 6 meses. Tomar em jejum com '
            'sumo de limão — a vitamina C ajuda a absorver melhor o ferro. '
            'Avisar que as fezes ficam escuras — é normal, não se preocupar.'
        ),
        'grave': (
            'Se a Hb estiver abaixo de 5 g/dL, pensar em transfusão. '
            'Investigar a causa — parasitose? Hemorragia escondida?'
        ),
        'exame': 'Ferritina sérica',
        'alertas': [
            'Falta de ar mesmo parado',
            'Coração a bater muito rápido',
            'Palidez intensa — ver as palmas das mãos e os olhos'
        ]
    },
    'Cólera': {
        'leve': (
            'SRO conforme protocolo da OMS. Preparar 1 saqueta em 1 litro '
            'de água tratada. Dar aos poucos, mas com frequência.'
        ),
        'grave': (
            'Ringer Lactato EV em bólus até estabilizar. '
            'Azitromicina 1 g dose única. Notificação obrigatória à DPS.'
        ),
        'exame': 'Coprocultura',
        'alertas': [
            'Olhos fundos, boca seca',
            'Pele que demora a voltar ao lugar (sinal da prega)',
            'Criança que já não chora com lágrimas',
            'Muito mole ou muito agitado'
        ]
    },
    'Febre Tifóide': {
        'leve': (
            'Ciprofloxacina 500 mg de 12/12h durante 7 a 14 dias. '
            'Em crianças, melhor usar azitromicina. '
            'Hidratar bem e comer leve.'
        ),
        'grave': (
            'Ceftriaxona EV 2 g/dia + internamento. '
            'Ficar atento a sinais de perfuração intestinal — '
            'barriga dura, dor forte, febre em pico.'
        ),
        'exame': 'Hemocultura (de preferência) ou coprocultura',
        'alertas': [
            'Barriga dura como tábua — pode ter perfurado',
            'Confusão mental',
            'Sangue nas fezes'
        ]
    },
    'Parasitose Intestinal': {
        'leve': (
            'Albendazol 400 mg dose única (acima de 2 anos e adultos). '
            'Repetir de 6 em 6 meses. '
            'Reforçar: lavar as mãos e tratar a água.'
        ),
        'grave': (
            'Albendazol 400 mg durante 3 dias + sulfato ferroso '
            'se tiver anemia junto. Quantificar a carga parasitária.'
        ),
        'exame': 'Exame parasitológico de fezes (3 amostras)',
        'alertas': [
            'Barriga muito inchada — risco de obstrução',
            'Desnutrição grave, principalmente nas crianças'
        ]
    },
    'Tuberculose': {
        'leve': (
            'Esquema DOTS: fase intensiva com RHZE durante 2 meses, '
            'depois RH por mais 4 meses. Toma observada directamente. '
            'O doente não pode largar o tratamento no meio.'
        ),
        'grave': (
            'Internamento. Investigar formas fora do pulmão. '
            'Se for HIV+, coordenar com o TARV — cuidado com as interacções.'
        ),
        'exame': 'Baciloscopia (BK) ou GeneXpert',
        'alertas': [
            'Tossir sangue',
            'Perder mais de 10% do peso',
            'Suar muito de noite, a encharcar',
            'Tosse há mais de 2 semanas sem melhorar'
        ]
    },
    'HIV/SIDA': {
        'leve': (
            'TARV 1.ª linha: Dolutegravir + Tenofovir + Lamivudina '
            '(um comprimido por dia). Tomar sempre à mesma hora, sem falhar. '
            'CD4 e carga viral aos 6 meses.'
        ),
        'grave': (
            'Tratar primeiro a infecção oportunista que estiver activa. '
            'Começar o TARV 2 semanas depois (excepto meningite '
            'criptocócica — aí esperar 4 a 6 semanas). Referenciar ao CTA.'
        ),
        'exame': 'Teste rápido HIV + CD4 + carga viral',
        'alertas': [
            'Infecções oportunistas a repetir',
            'Perda de peso sem explicação',
            'Diarreia há mais de 1 mês',
            'Sapinho na boca que não desaparece'
        ]
    },
    'Raiva (Mordedura)': {
        'leve': (
            'Lavar a ferida com água e sabão durante 15 minutos — '
            'essa medida salva vidas. Vacina anti-rábica nos dias 0, 3, 7 e 14. '
            'Não coser a ferida.'
        ),
        'grave': (
            'Soro anti-rábico + vacina. Não esperar por resultados. '
            'Se o animal morreu ou fugiu, tratar como alto risco. '
            'Cada hora conta.'
        ),
        'exame': 'Não esperar confirmação laboratorial — tratar já',
        'alertas': [
            'Medo de água (hidrofobia)',
            'Medo de vento (aerofobia)',
            'Agitação e desorientação',
            'Se estes sinais já apareceram, o prognóstico é muito reservado'
        ]
    },
    'Saudável': {
        'leve': (
            'Hemograma dentro dos valores normais. Orientar prevenção: '
            'rede mosquiteira, água tratada, desparasitação regular, '
            'vacinas em dia.'
        ),
        'grave': 'Não se aplica.',
        'exame': 'Sem necessidade de mais exames',
        'alertas': []
    }
}


# ═══════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════

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
        return "baixo", "⬇ Baixo"
    elif valor > maximo:
        return "alto", "⬆ Alto"
    return "normal", "✓ Normal"


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
        ("A conferir os dados do paciente...", 20),
        ("A analisar os valores do hemograma...", 50),
        ("A cruzar com dados epidemiológicos da zona...", 80),
        ("Quase lá, a finalizar...", 100)
    ]
    for texto, progresso in etapas:
        status_text.text(texto)
        time.sleep(0.2)
        progress_bar.progress(progresso)

    gravidade = determinar_gravidade(
        dados_paciente['hemoglobina'], dados_paciente['plaquetas']
    )
    resultados, erro = fazer_predicao(modelo, encoders, features, dados_paciente)

    progress_bar.empty()
    status_text.empty()

    return gravidade, resultados, erro


# ═══════════════════════════════════════════
# ECRÃ DE LOGIN
# ═══════════════════════════════════════════

def verificar_acesso():
    def processar_login():
        usuario = st.session_state.get("input_usuario", "").strip().lower()
        senha = st.session_state.get("input_senha", "")
        try:
            usuarios_validos = st.secrets["usuarios"]
            if usuario in usuarios_validos and usuarios_validos[usuario] == senha:
                st.session_state["autenticado"] = True
                st.session_state["usuario_atual"] = usuario
            else:
                st.session_state["erro_login"] = True
        except Exception:
            st.session_state["erro_login"] = True

    if st.session_state.get("autenticado", False):
        return True

    # ── CSS DO LOGIN ──
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: #0B0F19 !important;
    }

    [data-testid="stSidebar"],
    header[data-testid="stHeader"],
    #MainMenu, footer,
    .stDeployButton {
        display: none !important;
    }

    .main .block-container {
        max-width: 460px;
        margin: 0 auto;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* ── Inputs ── */
    .stTextInput > label {
        color: rgba(255, 255, 255, 0.45) !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
    }

    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        padding: 0.8rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.25s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 255, 255, 0.35) !important;
        box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.08) !important;
        background: rgba(255, 255, 255, 0.09) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.2) !important;
    }

    /* ── Botão ── */
    .stButton > button {
        background: #FFFFFF !important;
        color: #0B0F19 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.8rem 2rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        margin-top: 0.5rem !important;
    }

    .stButton > button:hover {
        background: #F0F0F0 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Alerta de erro ── */
    .stAlert {
        background: rgba(220, 50, 50, 0.12) !important;
        border: 1px solid rgba(220, 50, 50, 0.25) !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Espaço superior ──
    st.markdown("<div style='height: 6vh;'></div>", unsafe_allow_html=True)

    # ── Cabeçalho visual ──
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <div style="
            width: 72px; height: 72px;
            background: #FFFFFF;
            border-radius: 18px;
            display: flex; align-items: center; justify-content: center;
            font-size: 2rem;
            margin: 0 auto 1.5rem auto;
        ">🩸</div>

        <div style="
            font-size: 2.2rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.03em;
            line-height: 1.1;
        ">HemaSakula</div>

        <div style="
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.3);
            letter-spacing: 0.2em;
            text-transform: uppercase;
            margin-top: 0.6rem;
            font-weight: 400;
        ">Angola a Cuidar dos Seus</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Linha separadora ──
    st.markdown("""
    <div style="
        height: 1px;
        background: rgba(255, 255, 255, 0.08);
        margin: 0 0 2rem 0;
    "></div>
    """, unsafe_allow_html=True)

    # ── Saudação ──
    hora_actual = datetime.now().hour
    if hora_actual < 12:
        saudacao = "Bom dia"
    elif hora_actual < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    st.markdown(f"""
    <div style="margin-bottom: 1.8rem;">
        <div style="
            font-size: 1.3rem;
            font-weight: 600;
            color: #FFFFFF;
            margin-bottom: 0.4rem;
        ">{saudacao} 👋</div>
        <div style="
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.35);
            line-height: 1.5;
        ">Entra com as tuas credenciais pra acessar o sistema.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Campos de login ──
    st.text_input("Utilizador", key="input_usuario", placeholder="O teu nome de utilizador")

    st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)

    st.text_input("Palavra-passe", type="password", key="input_senha", placeholder="A tua palavra-passe")

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    if st.button("Entrar", use_container_width=True):
        processar_login()
        if st.session_state.get("autenticado"):
            st.rerun()

    if st.session_state.get("erro_login", False):
        st.error("Epa, essas credenciais não batem certo. Tenta de novo.")
        st.session_state["erro_login"] = False

    # ── Rodapé ──
    st.markdown("""
    <div style="
        text-align: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    ">
        <div style="
            color: rgba(255, 255, 255, 0.2);
            font-size: 0.75rem;
            letter-spacing: 0.02em;
        ">🔒 Acesso restrito a profissionais autorizados</div>
        <div style="
            color: rgba(255, 255, 255, 0.12);
            font-size: 0.7rem;
            margin-top: 0.6rem;
        ">HemaSakula · Angola 2025</div>
    </div>
    """, unsafe_allow_html=True)

    return False


# ═══════════════════════════════════════════
# CSS GLOBAL (só depois do login)
# ═══════════════════════════════════════════

def aplicar_css_global():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

    .stApp { background-color: #F8FAFC !important; color: #0F172A; }
    .main .block-container {
        padding: 2.5rem 4rem;
        max-width: 1300px;
        margin: 0 auto;
    }

    h1 { color: #0F172A !important; font-weight: 700 !important; font-size: 2rem !important;
         letter-spacing: -0.025em !important; margin-bottom: 0.5rem !important; }
    h2 { color: #1E293B !important; font-weight: 600 !important; font-size: 1.35rem !important;
         margin-top: 2.5rem !important; margin-bottom: 1.25rem !important;
         padding-bottom: 0.75rem !important; border-bottom: 1px solid #E2E8F0 !important; }
    h3 { color: #334155 !important; font-weight: 600 !important; font-size: 1.1rem !important;
         margin-bottom: 1rem !important; }

    label, .stSelectbox label, .stNumberInput label, .stCheckbox label {
        color: #475569 !important; font-weight: 500 !important; font-size: 0.875rem !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0F172A; border-right: 1px solid #1E293B; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #F1F5F9 !important; border-bottom-color: #1E293B !important;
    }
    [data-testid="stSidebar"] label { color: #CBD5E1 !important; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span { color: #94A3B8 !important; }

    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stNumberInput input {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #F1F5F9 !important;
    }

    [data-testid="stSidebar"] .stNumberInput button {
        background-color: #334155 !important;
        border-color: #334155 !important;
        color: #F1F5F9 !important;
    }

    [data-testid="stSidebar"] .stCheckbox label span { color: #CBD5E1 !important; }

    /* Inputs no corpo */
    .stTextInput > label {
        color: #475569 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput input {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        color: #0F172A !important;
    }

    .stNumberInput button {
        background-color: #F1F5F9 !important;
        border: 1px solid #E2E8F0 !important;
        color: #475569 !important;
    }

    /* Botão do formulário */
    .stFormSubmitButton > button {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 2.5rem !important;
        transition: all 0.2s ease !important;
    }

    .stFormSubmitButton > button:hover {
        background-color: #334155 !important;
        transform: translateY(-1px) !important;
    }

    /* Métricas */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    [data-testid="stMetric"] label {
        color: #64748B !important; font-weight: 600 !important; letter-spacing: 0.05em;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0F172A !important; font-weight: 700 !important;
    }

    /* Progress bar */
    .stProgress > div > div { background-color: #1E293B !important; border-radius: 4px; }
    .stProgress > div { background-color: #E2E8F0 !important; border-radius: 4px; }

    /* Cards e badges */
    .card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .badge {
        display: inline-block; padding: 0.35rem 0.85rem; border-radius: 6px;
        font-size: 0.75rem; font-weight: 700; letter-spacing: 0.025em;
    }

    .badge-leve { background-color: #F0FDF4; color: #166534; border: 1px solid #DCFCE7; }
    .badge-moderado { background-color: #FFFBEB; color: #92400E; border: 1px solid #FEF3C7; }
    .badge-grave { background-color: #FEF2F2; color: #991B1B; border: 1px solid #FEE2E2; }
    .badge-critico { background-color: #7F1D1D; color: #FFFFFF; }

    .status-operacional {
        background-color: #F0FDF4; border: 1px solid #DCFCE7;
        border-left: 4px solid #166534; border-radius: 8px;
        padding: 1rem 1.25rem; margin: 1.5rem 0;
    }
    .status-operacional p { margin: 0; color: #166534; font-weight: 600; }

    .aviso-institucional {
        background-color: #F8FAFC; border: 1px solid #E2E8F0;
        border-left: 4px solid #475569; border-radius: 8px;
        padding: 1.25rem; margin: 1.5rem 0;
    }
    .aviso-institucional p { margin: 0; color: #334155; font-size: 0.9rem; line-height: 1.6; }

    .serie-vermelha-header {
        color: #B91C1C !important; font-weight: 700 !important; font-size: 1rem !important;
        border-bottom: 2px solid #B91C1C; padding-bottom: 0.5rem; margin-bottom: 1.5rem !important;
    }

    .serie-branca-header {
        color: #475569 !important; font-weight: 700 !important; font-size: 1rem !important;
        border-bottom: 2px solid #475569; padding-bottom: 0.5rem; margin-bottom: 1.5rem !important;
    }

    .serie-plaquetas-header {
        color: #4338CA !important; font-weight: 700 !important; font-size: 1rem !important;
        border-bottom: 2px solid #4338CA; padding-bottom: 0.5rem; margin-bottom: 1.5rem !important;
    }

    hr { border: none; height: 1px; background-color: #E2E8F0; margin: 2rem 0; }
    .text-muted { color: #64748B; font-size: 0.875rem; }
    .text-small { font-size: 0.8125rem; }

    .footer {
        text-align: center; padding: 2rem 0; margin-top: 3rem;
        border-top: 1px solid #E2E8F0; color: #94A3B8; font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# APP PRINCIPAL
# ═══════════════════════════════════════════

def main():
    if not verificar_acesso():
        st.stop()

    aplicar_css_global()

    # Cabeçalho
    col_header1, col_header2 = st.columns([3, 1])

    with col_header1:
        st.title("🩸 HemaSakula")
        st.markdown(
            f'<p style="color: #64748B; font-size: 1rem; margin-top: -0.5rem; '
            f'font-style: italic;">{SLOGAN}</p>',
            unsafe_allow_html=True
        )

    with col_header2:
        usuario = st.session_state.get("usuario_atual", "")
        st.markdown(f"""
        <div style="text-align: right; padding-top: 0.8rem;">
            <span style="color: #94A3B8; font-size: 0.85rem;">
                👤 {usuario.capitalize()} · {datetime.now().strftime("%d/%m/%Y")}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="aviso-institucional">
        <p><strong>⚠️ Atenção:</strong> Este sistema serve de apoio à decisão clínica.
        Não substitui a avaliação presencial nem o julgamento do profissional de saúde.
        Interpreta sempre os resultados dentro do contexto clínico do doente.</p>
    </div>
    """, unsafe_allow_html=True)

    modelo, encoders, features = carregar_modelo()

    if modelo is None:
        st.error("⚠️ Modelo não encontrado. Executa primeiro: `python modelo_ml.py`")
        return

    st.markdown("""
    <div class="status-operacional">
        <p>✅ Tudo a funcionar — modelo carregado com sucesso</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.header("📋 Dados do Paciente")

        st.subheader("Identificação")
        faixa_etaria = st.selectbox("Faixa etária", FAIXAS_ETARIAS, index=5)
        sexo = st.selectbox("Sexo biológico", SEXOS)

        gestante = False
        if sexo == 'Feminino' and ('Adulto' in faixa_etaria or 'Adolescente' in faixa_etaria):
            gestante = st.checkbox("Grávida")

        peso = st.number_input("Peso (kg)", 1.0, 200.0, 65.0, 0.5)

        st.subheader("📍 Localização")
        municipio = st.selectbox("Município", list(MUNICIPIOS_INFO.keys()))
        info_mun = MUNICIPIOS_INFO[municipio]
        provincia = info_mun['provincia']
        st.markdown(f"**Província:** {provincia}")
        st.markdown(f"**Risco epidemiológico:** {info_mun['risco']}")

        st.subheader("📅 Data da colheita")
        mes = st.selectbox("Mês", MESES, index=datetime.now().month - 1)
        estacao = ESTACOES_POR_MES[mes]
        st.markdown(f"**Estação:** {estacao}")

        st.subheader("🧬 Antecedentes")
        status_genetico = st.selectbox("Hemoglobina (genética)", STATUS_GENETICO)
        mordedura = st.checkbox("Mordedura animal recente")

    # ── Hemograma ──
    st.header("🔬 Hemograma")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<p class="serie-vermelha-header">🔴 Série Vermelha</p>', unsafe_allow_html=True)
        hemoglobina = st.number_input("Hemoglobina (g/dL)", 3.0, 22.0, 12.5, 0.1)
        hematocrito = st.number_input("Hematócrito (%)", 10.0, 70.0, 38.0, 0.5)
        hemacias = st.number_input("Eritrócitos (×10⁶/µL)", 2.0, 7.0, 4.5, 0.1)
        vcm = st.number_input("VCM (fL)", 50.0, 120.0, 88.0, 1.0)
        hcm = st.number_input("HCM (pg)", 15.0, 40.0, 29.0, 0.5)
        chcm = st.number_input("CHCM (g/dL)", 28.0, 40.0, 33.5, 0.5)
        rdw = st.number_input("RDW (%)", 10.0, 25.0, 13.5, 0.1)

    with col2:
        st.markdown('<p class="serie-branca-header">⚪ Série Branca</p>', unsafe_allow_html=True)
        leucocitos = st.number_input("Leucócitos (/mm³)", 500, 50000, 7500, 100)
        neutrofilos = st.number_input("Neutrófilos (%)", 10.0, 90.0, 58.0, 1.0)
        linfocitos = st.number_input("Linfócitos (%)", 5.0, 70.0, 32.0, 1.0)
        monocitos = st.number_input("Monócitos (%)", 0.0, 20.0, 6.0, 0.5)
        eosinofilos = st.number_input("Eosinófilos (%)", 0.0, 25.0, 3.0, 0.5)
        basofilos = st.number_input("Basófilos (%)", 0.0, 3.0, 0.5, 0.1)

        valido, soma = validar_leucograma(neutrofilos, linfocitos, monocitos, eosinofilos, basofilos)
        if not valido:
            st.warning(f"⚠️ O diferencial soma {soma:.1f}% — o esperado é ≈ 100%. Confere os valores.")

    with col3:
        st.markdown('<p class="serie-plaquetas-header">🟣 Plaquetas e Outros</p>', unsafe_allow_html=True)
        plaquetas = st.number_input("Plaquetas (/mm³)", 5000, 1000000, 250000, 5000)
        vpm = st.number_input("VPM (fL)", 5.0, 15.0, 9.5, 0.5)
        reticulocitos = st.number_input("Reticulócitos (%)", 0.2, 15.0, 1.2, 0.1)

    st.markdown("---")

    # ── Análise ──
    with st.form(key="form_analise"):
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit = st.form_submit_button("🔍 Analisar Hemograma", use_container_width=True)

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

            gravidade, resultados, erro = processar_analise(modelo, encoders, features, dados)

            if erro:
                st.error(f"❌ Erro no processamento: {erro}")
                return

            if not resultados:
                st.error("❌ Não consegui gerar resultados. Confere os dados que meteste.")
                return

            diag_principal = resultados[0][0]

            # ── Resultados ──
            st.header("📊 Resultados")

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
                    <div style="margin-top: 0.75rem; font-weight: 600; color: #0F172A;">
                        🏥 {info_mun['hospital']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.subheader("🎯 Hipóteses diagnósticas")

            for i, (diag, prob) in enumerate(resultados[:3]):
                if i == 0:
                    st.markdown(f"""
                    <div class="card" style="border-left: 4px solid #1E293B;">
                        <div style="display: flex; justify-content: space-between;
                             align-items: center;">
                            <span style="font-size: 1.1rem; font-weight: 600;
                                  color: #0F172A;">
                                1.º {diag}
                            </span>
                            <span style="background: #1E293B; color: white;
                                  padding: 0.4rem 1rem; border-radius: 6px;
                                  font-weight: 600;">
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
                                {i+1}.º {diag}
                            </span>
                            <span style="color: #64748B; font-weight: 600;">
                                {prob:.1f}%
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.subheader("💊 O que fazer agora")

            if diag_principal in CONDUTAS:
                cond = CONDUTAS[diag_principal]
                if gravidade in ["GRAVE", "CRÍTICO"]:
                    st.error(f"**🚨 Caso grave:** {cond['grave']}")
                else:
                    st.info(f"**💡 Conduta:** {cond['leve']}")

                st.markdown(
                    f'<div class="card"><strong>🧪 Exame pra confirmar:</strong> '
                    f'{cond["exame"]}</div>',
                    unsafe_allow_html=True
                )

                if cond['alertas']:
                    with st.expander("🚩 Sinais de alarme — referenciar já"):
                        for a in cond['alertas']:
                            st.markdown(f"- {a}")

            st.subheader("📈 Interpretação do hemograma")

            col_l1, col_l2 = st.columns(2)

            with col_l1:
                _, hb_l = classificar_valor(hemoglobina, 11.5, 16.5)
                st.metric("Hemoglobina", f"{hemoglobina} g/dL", hb_l)
                _, plt_l = classificar_valor(plaquetas, 140000, 400000)
                st.metric("Plaquetas", f"{formatar_numero(plaquetas)}/mm³", plt_l)
                _, leu_l = classificar_valor(leucocitos, 4000, 10000)
                st.metric("Leucócitos", f"{formatar_numero(leucocitos)}/mm³", leu_l)

            with col_l2:
                _, vcm_l = classificar_valor(vcm, 80, 98)
                st.metric("VCM", f"{vcm} fL", vcm_l)
                _, eos_l = classificar_valor(eosinofilos, 1, 5)
                st.metric("Eosinófilos", f"{eosinofilos}%", eos_l)
                _, ret_l = classificar_valor(reticulocitos, 0.5, 2.5)
                st.metric("Reticulócitos", f"{reticulocitos}%", ret_l)

            if status_genetico in ['Traço falciforme (AS)', 'Drepanocitose (SS)']:
                st.warning(
                    f"**🧬 Hemoglobinopatia: {status_genetico}.** "
                    f"Seguimento no IHL ou centro de drepanocitose. "
                    f"Ácido fólico 5 mg/dia, beber muita água, "
                    f"evitar frio e tudo que possa provocar crise."
                )

            if mordedura:
                st.error(
                    "**🐕 Mordedura animal — risco rábico!** "
                    "Lavar a ferida com água e sabão durante 15 minutos. "
                    "Iniciar profilaxia anti-rábica sem esperar resultados. "
                    "Cada hora conta."
                )

    # Footer
    st.markdown(f"""
    <div class="footer">
        <strong>🩸 HemaSakula</strong><br>
        {SLOGAN}<br>
        <span style="font-size: 0.75rem;">Feito com ❤️ pra Angola</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
