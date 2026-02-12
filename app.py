import streamlit as st
import pandas as pd
import numpy as np
import pickle
import time
import json
import os
import re
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="HemaSakula",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Constantes e Dados ---
FICHEIRO_CLIENTES = 'dados_clientes.json'

MUNICIPIOS_LISTA = [
    'Belas', 'Cacuaco', 'Catete', 'Cazenga', 'Icolo e Bengo',
    'Ingombota', 'Kilamba Kiaxi', 'Maianga', 'Rangel', 'Samba',
    'Talatona', 'Viana'
]

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
    'Recém-nascido (0-28 dias)', 'Lactente (1-12 meses)',
    'Criança (1-5 anos)', 'Criança (5-12 anos)',
    'Adolescente (12-18 anos)', 'Adulto jovem (18-45 anos)',
    'Adulto (45-65 anos)', 'Idoso (>65 anos)'
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
    'Malaria': {
        'leve': (
            'Coartem (Arteméter + Lumefantrina): 4 comprimidos de 12/12h '
            'durante 3 dias. Tomar sempre com comida, de preferência com '
            'gordura para absorver melhor. Paracetamol para baixar a febre.'
        ),
        'grave': (
            'Artesunato EV 2,4 mg/kg às 0h, 12h e 24h, depois 1x/dia '
            'até o doente aguentar via oral. Controlar Hb no dia 7 e 14. '
            'Se a parasitemia não baixar em 24h, reavaliar a dose.'
        ),
        'exame': 'Gota espessa ou teste rápido (TDR)',
        'alertas': [
            'Convulsões',
            'Prostração - não come, não bebe, não anda',
            'Vómitos que não param',
            'Urina escura (cor de coca-cola)',
            'Falta de ar',
            'Amarelão nos olhos (icterícia)',
            'Confusão ou perda de consciência'
        ]
    },
    'Dengue': {
        'leve': (
            'Hidratar bem por via oral (60-80 mL/kg/dia). Paracetamol para febre. '
            'Nada de ibuprofeno nem aspirina - pode causar hemorragia.'
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
            '+ soro EV + oxigénio se SpO2 < 95%. '
            'Referenciar ao IHL com urgência.'
        ),
        'exame': 'Electroforese de hemoglobina',
        'alertas': [
            'Febre - num drepanocítico é sempre urgência',
            'Dor no peito - pode ser síndrome torácica aguda',
            'Priapismo',
            'Sinais de AVC - braço ou perna sem força, fala enrolada, boca torta'
        ]
    },
    'Anemia Ferropriva': {
        'leve': (
            'Sulfato ferroso durante 3 a 6 meses. Tomar em jejum com '
            'sumo de limão - a vitamina C ajuda a absorver melhor o ferro. '
            'Avisar que as fezes ficam escuras - é normal, não se preocupar.'
        ),
        'grave': (
            'Se a Hb estiver abaixo de 5 g/dL, pensar em transfusão. '
            'Investigar a causa - parasitose? Hemorragia escondida?'
        ),
        'exame': 'Ferritina sérica',
        'alertas': [
            'Falta de ar mesmo parado',
            'Coração a bater muito rápido',
            'Palidez intensa - ver as palmas das mãos e os olhos'
        ]
    },
    'Colera': {
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
    'Febre Tifoide': {
        'leve': (
            'Ciprofloxacina 500 mg de 12/12h durante 7 a 14 dias. '
            'Em crianças, melhor usar azitromicina. '
            'Hidratar bem e comer leve.'
        ),
        'grave': (
            'Ceftriaxona EV 2 g/dia + internamento. '
            'Ficar atento a sinais de perfuração intestinal - '
            'barriga dura, dor forte, febre em pico.'
        ),
        'exame': 'Hemocultura (de preferência) ou coprocultura',
        'alertas': [
            'Barriga dura como tábua - pode ter perfurado',
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
            'Barriga muito inchada - risco de obstrução',
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
            'Se for HIV+, coordenar com o TARV - cuidado com as interacções.'
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
            'criptocócica - aí esperar 4 a 6 semanas). Referenciar ao CTA.'
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
            'Lavar a ferida com água e sabão durante 15 minutos - '
            'essa medida salva vidas. Vacina anti-rábica nos dias 0, 3, 7 e 14. '
            'Não coser a ferida.'
        ),
        'grave': (
            'Soro anti-rábico + vacina. Não esperar por resultados. '
            'Se o animal morreu ou fugiu, tratar como alto risco. '
            'Cada hora conta.'
        ),
        'exame': 'Não esperar confirmação laboratorial - tratar já',
        'alertas': [
            'Medo de água (hidrofobia)',
            'Medo de vento (aerofobia)',
            'Agitação e desorientação',
            'Se estes sinais já apareceram, o prognóstico é muito reservado'
        ]
    },
    'Saudavel': {
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


# --- Funções de Persistência ---
def carregar_clientes():
    if os.path.exists(FICHEIRO_CLIENTES):
        with open(FICHEIRO_CLIENTES, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def guardar_clientes(dados):
    with open(FICHEIRO_CLIENTES, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def registar_cliente(nome, telefone, municipio, email=''):
    clientes = carregar_clientes()
    tel_limpo = telefone.replace(' ', '').replace('-', '')
    if tel_limpo in clientes:
        clientes[tel_limpo]['nome'] = nome
        clientes[tel_limpo]['municipio'] = municipio
        if email:
            clientes[tel_limpo]['email'] = email
        guardar_clientes(clientes)
        return True, clientes[tel_limpo]
    cliente = {
        'nome': nome,
        'telefone': tel_limpo,
        'municipio': municipio,
        'email': email,
        'data_registo': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'historico': [],
        'plano': None
    }
    clientes[tel_limpo] = cliente
    guardar_clientes(clientes)
    return True, cliente


# --- Funções de Validação e Utilitários ---
def validar_email(email):
    if not email:
        return True
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))


def validar_telefone(telefone):
    numeros = re.sub(r'[^0-9]', '', telefone)
    return len(numeros) == 9 and numeros[0] == '9'


def obter_saudacao():
    hora = datetime.now().hour
    if hora < 12:
        return "Bom dia"
    elif hora < 18:
        return "Boa tarde"
    return "Boa noite"


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
        return "CRITICO"
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
        "CRITICO": "badge-critico"
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


# --- CSS Customizado (Inspirado no "We are OSM") ---
# Estilo: Minimalista, Alto Contraste, Tipografia Bold, Cards Limpos

CSS_GLOBAL = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    :root {
        --bg-color: #FFFFFF;
        --text-color: #0F172A;
        --accent-color: #10B981; /* Verde similar ao OSM */
        --accent-dark: #059669;
        --secondary-bg: #F8FAFC;
        --border-color: #E2E8F0;
        --danger: #EF4444;
        --warning: #F59E0B;
    }

    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
        font-family: 'Inter', sans-serif;
    }

    /* Esconder elementos do Streamlit */
    #MainMenu, footer, .stDeployButton, header[data-testid="stHeader"] {
        visibility: hidden;
        display: none !important;
    }

    /* Tipografia */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        color: var(--text-color) !important;
        letter-spacing: -0.02em;
    }

    p, div, span, label {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-color);
    }

    /* Inputs e Botões */
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 2px solid var(--border-color) !important;
        padding: 10px 14px !important;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2) !important;
    }

    .stButton > button {
        background-color: var(--text-color) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        border: none !important;
        transition: transform 0.1s, background-color 0.2s;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stButton > button:hover {
        background-color: var(--accent-dark) !important;
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Botão Secundário (Outline) */
    .btn-outline > button {
        background-color: transparent !important;
        color: var(--text-color) !important;
        border: 2px solid var(--text-color) !important;
    }
    .btn-outline > button:hover {
        background-color: var(--text-color) !important;
        color: white !important;
    }

    /* Cards */
    .osm-card {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        transition: box-shadow 0.2s;
    }
    .osm-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-leve { background: #D1FAE5; color: #065F46; }
    .badge-moderado { background: #FEF3C7; color: #92400E; }
    .badge-grave { background: #FEE2E2; color: #991B1B; }
    .badge-critico { background: #7F1D1D; color: white; }

    /* Layout Helpers */
    .center-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 1rem;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #64748B;
        max-width: 500px;
        margin-bottom: 2rem;
        line-height: 1.6;
    }

    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out forwards;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        color: #64748B;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: var(--text-color) !important;
        border-bottom: 2px solid var(--text-color) !important;
        background: transparent !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-bg);
        border-right: 1px solid var(--border-color);
    }
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
    }

    /* Alerts */
    .stAlert {
        border-radius: 8px !important;
        border: none !important;
    }
</style>
"""

# --- Telas da Aplicação ---

def tela_boas_vindas():
    st.markdown(CSS_GLOBAL, unsafe_allow_html=True)

    # Container centralizado
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)

        # Logo / Brand
        st.markdown("""
        <div class='center-content animate-fade-in'>
            <div style='width: 80px; height: 80px; background: #0F172A; border-radius: 20px; 
                        display: flex; align-items: center; justify-content: center; 
                        color: white; font-size: 2rem; font-weight: 800; margin-bottom: 24px;'>
                HS
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Título e Subtítulo
        st.markdown(f"""
        <div class='center-content animate-fade-in' style='animation-delay: 0.1s;'>
            <h1 class='hero-title'>Cuidamos da tua saúde.</h1>
            <p class='hero-subtitle'>
                A HemaSakula conecta-te com os melhores hospitais e clínicas de Angola. 
                Tecnologia inteligente ao serviço do bem-estar da tua família.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Formulário
        with st.container():
            st.markdown("<div class='animate-fade-in' style='animation-delay: 0.2s;'>", unsafe_allow_html=True)

            nome = st.text_input("Nome Completo", placeholder="Ex: Maria Silva")
            municipio = st.selectbox("Município", MUNICIPIOS_LISTA, index=None, placeholder="Seleciona onde vives...")
            telefone = st.text_input("Telemóvel", placeholder="9xx xxx xxx")

            if st.button("Começar", use_container_width=True):
                erros = []
                if not nome or not nome.strip():
                    erros.append("Por favor, insere o teu nome.")
                if not municipio:
                    erros.append("Seleciona um município.")
                if not telefone or not validar_telefone(telefone):
                    erros.append("Número de telefone inválido (deve ter 9 dígitos).")

                if erros:
                    for erro in erros:
                        st.error(erro)
                else:
                    sucesso, dados = registar_cliente(nome.strip(), telefone.strip(), municipio)
                    if sucesso:
                        st.session_state['ecra'] = 'cliente'
                        st.session_state['cliente'] = dados
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        # Separador
        st.markdown("<div style='margin: 40px 0; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)

        # Área Profissional
        st.markdown("""
        <div class='center-content animate-fade-in' style='animation-delay: 0.3s;'>
            <p style='color: #64748B; font-size: 0.9rem; margin-bottom: 12px;'>És profissional de saúde?</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Aceder ao Painel Profissional", key="btn_empresa", use_container_width=True):
            st.session_state['ecra'] = 'login_empresa'
            st.rerun()


def tela_login_empresa():
    st.markdown(CSS_GLOBAL, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align: center; margin-bottom: 40px;'>
            <h2 style='font-size: 2rem; margin-bottom: 8px;'>Painel Profissional</h2>
            <p style='color: #64748B;'>Acesso reservado a clínicas e hospitais parceiros.</p>
        </div>
        """, unsafe_allow_html=True)

        usuario = st.text_input("Utilizador", placeholder="nome@clinica.com")
        senha = st.text_input("Palavra-passe", type="password")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Voltar", use_container_width=True):
                st.session_state['ecra'] = 'inicio'
                st.rerun()
        with col_btn2:
            if st.button("Entrar", use_container_width=True):
                if not usuario or not senha:
                    st.error("Preenche todos os campos.")
                else:
                    # Simulação de autenticação
                    try:
                        usuarios_validos = st.secrets.get("usuarios", {"admin": "admin"})
                        if usuario.strip().lower() in usuarios_validos and usuarios_validos[usuario.strip().lower()] == senha:
                            st.session_state['ecra'] = 'empresa'
                            st.session_state['empresa_usuario'] = usuario.strip()
                            st.rerun()
                        else:
                            st.error("Credenciais inválidas.")
                    except Exception:
                        st.error("Erro no sistema de autenticação.")


def tela_painel_cliente():
    st.markdown(CSS_GLOBAL, unsafe_allow_html=True)

    cliente = st.session_state.get('cliente', {})
    nome = cliente.get('nome', 'Amigo')
    municipio = cliente.get('municipio', 'Luanda')
    primeiro_nome = nome.split()[0] if nome else 'Amigo'

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<h1 style='font-size: 1.8rem;'>Olá, {primeiro_nome}!</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748B; margin-top: -10px;'>📍 {municipio}</p>", unsafe_allow_html=True)
    with col2:
        if st.button("Sair", key="btn_sair"):
            for k in ['ecra', 'cliente']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    st.markdown("---")

    # Tabs
    tab_clinicas, tab_alertas, tab_sobre = st.tabs(["🏥 Clínicas", "⚠️ Alertas", "ℹ️ Sobre"])

    with tab_clinicas:
        info_mun = MUNICIPIOS_INFO.get(municipio, {})
        hospital_ref = info_mun.get('hospital', 'Centro de Saúde')

        st.markdown(f"""
        <div class='osm-card' style='border-left: 4px solid #10B981;'>
            <h4 style='margin: 0; font-size: 1rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;'>Hospital de Referência</h4>
            <h3 style='margin: 8px 0 4px 0; font-size: 1.4rem;'>{hospital_ref}</h3>
            <p style='margin: 0; color: #64748B;'>{municipio} • {info_mun.get('provincia', 'Luanda')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Outras Unidades de Saúde")

        parceiros_lista = [
            {'nome': 'Hospital Josina Machel', 'tipo': 'Público', 'local': 'Ingombota'},
            {'nome': 'Clínica Sagrada Esperança', 'tipo': 'Privado', 'local': 'Talatona'},
            {'nome': 'Hospital Geral de Viana', 'tipo': 'Público', 'local': 'Viana'},
        ]

        for p in parceiros_lista:
            st.markdown(f"""
            <div class='osm-card' style='padding: 16px 24px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <strong style='font-size: 1.1rem;'>{p['nome']}</strong>
                        <p style='margin: 4px 0 0 0; color: #64748B; font-size: 0.9rem;'>{p['local']}</p>
                    </div>
                    <span class='badge' style='background: {"#DBEAFE" if p["tipo"] == "Público" else "#FEF3C7"}; 
                                                 color: {"#1E40AF" if p["tipo"] == "Público" else "#92400E"};'>
                        {p['tipo']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_alertas:
        mes_actual = datetime.now().month
        alertas_mes = {
            1: "Época de chuvas. Cuidado com a cólera e a malária.",
            2: "Chuvas fortes. Evita água parada perto de casa.",
            3: "Pico de malária. Se tiveres febre, consulta.",
            6: "Cacimbo. Agasalha-te bem.",
        }
        alerta_txt = alertas_mes.get(mes_actual, "Mantém-te hidratado e segue as normas de higiene.")

        st.markdown(f"""
        <div class='osm-card' style='background: #FFFBEB; border: 1px solid #FEF3C7;'>
            <h4 style='margin: 0 0 8px 0; color: #92400E;'>⚠️ Alerta para {MESES[mes_actual-1]}</h4>
            <p style='margin: 0; color: #78350F;'>{alerta_txt}</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Dicas de Saúde")
        dicas = [
            ("💧", "Bebe água tratada ou fervida."),
            ("🦟", "Dorme sempre debaixo da rede mosquiteira."),
            ("💊", "Desparasita-te de 6 em 6 meses."),
        ]
        for icon, texto in dicas:
            st.markdown(f"<div class='osm-card'>{icon} {texto}</div>", unsafe_allow_html=True)

    with tab_sobre:
        st.markdown("""
        <div class='osm-card' style='text-align: center; padding: 40px;'>
            <div style='width: 60px; height: 60px; background: #0F172A; border-radius: 16px; 
                        display: inline-flex; align-items: center; justify-content: center; 
                        color: white; font-size: 1.5rem; font-weight: 800; margin-bottom: 20px;'>
                HS
            </div>
            <h2>HemaSakula</h2>
            <p style='color: #64748B; max-width: 400px; margin: 0 auto;'>
                Plataforma angolana de apoio à decisão clínica e conexão entre pacientes e unidades de saúde.
            </p>
        </div>
        """, unsafe_allow_html=True)


def tela_painel_empresa():
    st.markdown(CSS_GLOBAL, unsafe_allow_html=True)

    usuario = st.session_state.get('empresa_usuario', 'Profissional')

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Análise Clínica")
        st.markdown("<p style='color: #64748B; margin-top: -10px;'>Sistema de Apoio à Decisão</p>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<p style='text-align: right; color: #94A3B8; font-size: 0.9rem;'>{usuario}<br>{datetime.now().strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)
        if st.button("Sair", key="btn_sair_emp"):
            del st.session_state['ecra']
            del st.session_state['empresa_usuario']
            st.rerun()

    st.info("ℹ️ Este sistema é um auxiliar clínico. A decisão final é sempre do profissional de saúde.")

    modelo, encoders, features = carregar_modelo()
    if modelo is None:
        st.error("❌ Modelo de IA não encontrado. Verifica a instalação.")
        return

    # Layout em Colunas
    col_form, col_result = st.columns([1, 2])

    with col_form:
        st.subheader("Dados do Paciente")

        with st.expander("Identificação", expanded=True):
            faixa_etaria = st.selectbox("Faixa Etária", FAIXAS_ETARIAS, index=5)
            sexo = st.selectbox("Sexo", SEXOS)
            gestante = False
            if sexo == 'Feminino':
                gestante = st.checkbox("Gestante")

        with st.expander("Localização"):
            municipio = st.selectbox("Município", list(MUNICIPIOS_INFO.keys()))
            info_mun = MUNICIPIOS_INFO[municipio]
            st.caption(f"Província: {info_mun['provincia']} | Risco: {info_mun['risco']}")
            mes = st.selectbox("Mês", MESES, index=datetime.now().month - 1)
            estacao = ESTACOES_POR_MES[mes]

        with st.expander("Antecedentes"):
            status_genetico = st.selectbox("Status Genético", STATUS_GENETICO)
            mordedura = st.checkbox("Mordedura recente")

        st.markdown("---")
        st.subheader("Hemograma")

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            hemoglobina = st.number_input("Hemoglobina (g/dL)", 3.0, 22.0, 12.5, 0.1)
            plaquetas = st.number_input("Plaquetas (/mm3)", 5000, 1000000, 250000, 1000)
            leucocitos = st.number_input("Leucócitos (/mm3)", 500, 50000, 7500, 100)
        with col_h2:
            vcm = st.number_input("VCM (fL)", 50.0, 120.0, 88.0, 1.0)
            rdw = st.number_input("RDW (%)", 10.0, 25.0, 13.5, 0.1)
            reticulocitos = st.number_input("Reticulócitos (%)", 0.2, 15.0, 1.2, 0.1)

        analisar = st.button("🚀 Analisar Dados", use_container_width=True, type="primary")

    with col_result:
        if analisar:
            dados = {
                'faixa_etaria': faixa_etaria, 'sexo': sexo, 'gestante': gestante,
                'municipio': municipio, 'provincia': info_mun['provincia'],
                'mes': mes, 'estacao': estacao, 'status_genetico': status_genetico,
                'mordedura_recente': mordedura, 'hemoglobina': hemoglobina,
                'plaquetas': plaquetas, 'leucocitos': leucocitos,
                'vcm': vcm, 'rdw': rdw, 'reticulocitos': reticulocitos
            }

            with st.spinner("A processar análise..."):
                gravidade, resultados, erro = processar_analise(modelo, encoders, features, dados)

            if erro:
                st.error(f"Erro: {erro}")
            else:
                diag_principal = resultados[0][0]

                # Cards de Resultado
                c1, c2, c3 = st.columns(3)
                with c1:
                    classe_css = obter_classe_gravidade(gravidade)
                    st.markdown(f"""
                    <div class='osm-card' style='text-align: center; border-top: 4px solid {"#10B981" if gravidade == "LEVE" else "#F59E0B" if gravidade == "MODERADO" else "#EF4444"};'>
                        <p style='color: #64748B; font-size: 0.8rem; margin: 0;'>GRAVIDADE</p>
                        <span class='badge {classe_css}' style='font-size: 1rem; margin-top: 8px; display: inline-block;'>{gravidade}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class='osm-card' style='text-align: center; border-top: 4px solid #3B82F6;'>
                        <p style='color: #64748B; font-size: 0.8rem; margin: 0;'>DIAGNÓSTICO PRINCIPAL</p>
                        <h3 style='margin: 8px 0 0 0; font-size: 1.2rem;'>{diag_principal}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div class='osm-card' style='text-align: center; border-top: 4px solid #8B5CF6;'>
                        <p style='color: #64748B; font-size: 0.8rem; margin: 0;'>CONFIANÇA</p>
                        <h3 style='margin: 8px 0 0 0; font-size: 1.2rem;'>{resultados[0][1]:.1f}%</h3>
                    </div>
                    """, unsafe_allow_html=True)

                # Conduta
                st.subheader("Conduta Recomendada")
                if diag_principal in CONDUTAS:
                    cond = CONDUTAS[diag_principal]
                    if gravidade in ["GRAVE", "CRITICO"]:
                        st.error(f"**Ação Imediata:** {cond['grave']}")
                    else:
                        st.success(f"**Conduta:** {cond['leve']}")

                    with st.expander("Ver Sinais de Alarme"):
                        for alerta in cond['alertas']:
                            st.markdown(f"- {alerta}")

                # Gráfico de Probabilidades
                st.subheader("Distribuição de Probabilidades")
                chart_data = pd.DataFrame(resultados[:3], columns=['Diagnóstico', 'Probabilidade'])
                st.bar_chart(chart_data.set_index('Diagnóstico'))


# --- Ponto de Entrada ---
def main():
    ecra = st.session_state.get('ecra', 'inicio')

    if ecra == 'inicio':
        tela_boas_vindas()
    elif ecra == 'login_empresa':
        tela_login_empresa()
    elif ecra == 'cliente':
        tela_painel_cliente()
    elif ecra == 'empresa':
        tela_painel_empresa()
    else:
        tela_boas_vindas()


if __name__ == "__main__":
    main()
