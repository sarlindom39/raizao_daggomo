import streamlit as st
import pandas as pd
import numpy as np
import pickle
import time
import json
import os
import re
from datetime import datetime

st.set_page_config(
    page_title="HemaSakula — Angola a Cuidar dos Seus",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
            'Hidratar bem por via oral (60-80 mL/kg/dia). Paracetamol para febre. '
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
            '+ soro EV + oxigénio se SpO2 < 95%. '
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
        dados_paciente['hemoglobina'],
        dados_paciente['plaquetas']
    )
    resultados, erro = fazer_predicao(modelo, encoders, features, dados_paciente)
    progress_bar.empty()
    status_text.empty()
    return gravidade, resultados, erro


def css_global():
    return """<style>
    @import url('https://fonts.googleapis.com/css2?family=Dosis:wght@200;300;400;500;600;700;800&display=swap');

    :root {
        --pri: #15291C;
        --pri-hover: #1E3A28;
        --sec: #D4E7DC;
        --accent: #C9553A;
        --bg: #FAFAF8;
        --surface: #FFFFFF;
        --surface-alt: #F3F2EE;
        --text: #1A1A18;
        --text-secondary: #5A5A52;
        --text-muted: #8A8A82;
        --border: #DDDCD7;
        --border-strong: #1A1A18;
        --success: #1B6B3A;
        --danger: #8B1A1A;
        --radius: 0px;
    }

    /* 2. Aplicação da fonte Dosis em todo o projeto */
    * { font-family: 'Dosis', sans-serif !important; }
    
    .stApp { background: var(--bg) !important; }

    [data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu, footer, .stDeployButton { display: none !important; }

    .stTextInput > label,
    .stSelectbox > label,
    .stNumberInput > label,
    .stCheckbox > label {
        color: var(--text) !important;
        font-size: 0.75rem !important; /* Ajustei ligeiramente pois a Dosis é mais pequena */
        font-weight: 700 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        margin-bottom: 0.5rem !important;
    }

    .stTextInput > div > div > input {
        background: var(--surface) !important;
        border: 2.5px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--text) !important;
        padding: 1rem 1.1rem !important;
        font-size: 1rem !important; /* Dosis lê-se melhor um pouco maior */
        font-weight: 500 !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
        -webkit-appearance: none !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--border-strong) !important;
        box-shadow: none !important;
        background: var(--surface) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #B5B3AD !important;
        font-weight: 400 !important;
    }

    div[data-baseweb="select"] {
        color: var(--text) !important;
    }

    div[data-baseweb="select"] > div {
        background: var(--surface) !important;
        border: 2.5px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--text) !important;
        min-height: 48px !important;
        transition: border-color 0.3s ease !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: var(--text-muted) !important;
    }

    div[data-baseweb="select"] > div:focus-within {
        border-color: var(--border-strong) !important;
        box-shadow: none !important;
    }

    div[data-baseweb="select"] * {
        color: var(--text) !important;
    }

    div[data-baseweb="select"] span {
        color: var(--text) !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }

    div[data-baseweb="select"] [data-testid="stMarkdownContainer"],
    div[data-baseweb="select"] div[class*="ValueContainer"] span,
    div[data-baseweb="select"] div[class*="singleValue"],
    div[data-baseweb="select"] div[class*="SingleValue"],
    div[data-baseweb="select"] div[class*="placeholder"],
    div[data-baseweb="select"] input {
        color: var(--text) !important;
    }

    div[data-baseweb="select"] div[class*="placeholder"] {
        color: #B5B3AD !important;
    }

    div[data-baseweb="select"] svg {
        fill: var(--text-muted) !important;
        color: var(--text-muted) !important;
    }

    div[data-baseweb="popover"] {
        border-radius: var(--radius) !important;
        border: none !important;
        box-shadow: 0 12px 48px rgba(26,26,24,0.12) !important;
    }

    div[data-baseweb="popover"] ul {
        background: var(--surface) !important;
        border: 2px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 6px !important;
    }

    div[data-baseweb="popover"] li {
        color: var(--text) !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        border-radius: var(--radius) !important;
        padding: 10px 14px !important;
        transition: background 0.15s ease !important;
    }

    div[data-baseweb="popover"] li:hover {
        background: var(--surface-alt) !important;
        color: var(--text) !important;
    }

    div[data-baseweb="popover"] li[aria-selected="true"],
    div[data-baseweb="select"] [aria-selected="true"] {
        color: var(--text) !important;
        background: var(--sec) !important;
        font-weight: 700 !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        color: var(--text) !important;
    }

    .stSelectbox [data-baseweb="select"] > div > div {
        color: var(--text) !important;
    }

    .stSelectbox [data-baseweb="select"] > div > div > div {
        color: var(--text) !important;
    }

    *:focus { outline: none !important; }
    input:focus, select:focus, textarea:focus { outline: none !important; }
    input:invalid, input:required { border-color: var(--border) !important; box-shadow: none !important; }

    .stButton > button {
        background: transparent !important;
        color: var(--text) !important;
        border: 3px solid var(--border-strong) !important;
        border-radius: var(--radius) !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        padding: 1rem 2.4rem !important;
        width: 100% !important;
        letter-spacing: 0.13em !important;
        text-transform: uppercase !important;
        transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
        cursor: pointer !important;
    }

    .stButton > button:hover {
        background: var(--pri) !important;
        color: var(--bg) !important;
        border-color: var(--pri) !important;
        transform: none !important;
        box-shadow: none !important;
    }

    .stButton > button:active {
        background: #0D1E13 !important;
        border-color: #0D1E13 !important;
        color: var(--bg) !important;
        transform: none !important;
    }

    .stFormSubmitButton > button {
        background: transparent !important;
        color: var(--text) !important;
        border: 3px solid var(--border-strong) !important;
        border-radius: var(--radius) !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        padding: 1rem 2.4rem !important;
        letter-spacing: 0.13em !important;
        text-transform: uppercase !important;
        transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    }

    .stFormSubmitButton > button:hover {
        background: var(--pri) !important;
        color: var(--bg) !important;
        border-color: var(--pri) !important;
    }

    .stAlert, [data-testid="stNotification"] {
        border-radius: var(--radius) !important;
        border: 2px solid var(--border) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 2px solid var(--border);
        border-radius: 0;
        padding: 0;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-muted) !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        border-radius: 0 !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        padding: 0.9rem 1.6rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        transition: all 0.3s ease !important;
        margin-bottom: -2px !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text) !important;
    }

    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: var(--text) !important;
        font-weight: 800 !important;
        border-bottom: 3px solid var(--text) !important;
        box-shadow: none !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 2px solid var(--border);
        border-radius: var(--radius);
        padding: 1.4rem;
    }

    [data-testid="stMetric"] label {
        color: var(--text-muted) !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-weight: 800 !important;
    }

    .stProgress > div > div {
        background: var(--pri) !important;
        border-radius: 0;
        height: 3px !important;
    }

    .stProgress > div {
        background: var(--border) !important;
        border-radius: 0;
        height: 3px !important;
    }

    .stNumberInput input {
        background: var(--surface) !important;
        border: 2.5px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--text) !important;
        font-weight: 500 !important;
    }

    .stNumberInput input:focus {
        border-color: var(--border-strong) !important;
        box-shadow: none !important;
    }

    .stNumberInput button {
        background: var(--surface-alt) !important;
        border: 2px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--text-muted) !important;
    }

    .stNumberInput button:hover {
        background: var(--border) !important;
        color: var(--text) !important;
    }

    .stCheckbox label span[data-testid="stCheckboxLabel"] {
        color: var(--text) !important;
        font-size: 0.95rem !important;
    }

    [data-testid="stExpander"] {
        border: 2px solid var(--border) !important;
        border-radius: var(--radius) !important;
        background: var(--surface) !important;
    }

    [data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: var(--text) !important;
    }

    div[data-testid="stMarkdownContainer"] p {
        line-height: 1.75 !important;
    }

    </style>"""

def css_tela_inicio():
    return """<style>
    .main .block-container {
        max-width: 480px;
        margin: 0 auto;
        padding-top: 0 !important;
        padding-bottom: 3rem !important;
    }
    </style>"""


def css_painel_cliente():
    return """<style>
    .main .block-container {
        max-width: 780px;
        margin: 0 auto;
        padding: 1.5rem 2rem;
    }
    </style>"""


def css_painel_empresa():
    return """<style>
    .main .block-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem 3rem;
    }

    
    [data-testid="stSidebar"] {
        display: block !important;
        background-color: var(--pri) !important;
        border-right: none;
    }

    header[data-testid="stHeader"] {
        display: block !important;
        background: transparent !important;
    }
    
    div[data-testid="stDecoration"] {
        display: none !important;
    }

    button[data-testid="baseButton-header"] {
        color: #1A1A18 !important;
    }


    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #E8E6E1 !important;
        font-family: 'Dosis', sans-serif !important; /* Fonte Dosis */
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid #2A4435 !important;
        padding-bottom: 0.6rem !important;
        margin-top: 1.5rem !important;
    }

    [data-testid="stSidebar"] label {
        color: #8A9B8E !important;
        font-family: 'Dosis', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #8A9B8E !important;
        font-family: 'Dosis', sans-serif !important;
    }

    [data-testid="stSidebar"] strong {
        color: #B5C4B8 !important;
    }

    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1E3A28 !important;
        border: 2px solid #2A4435 !important;
        border-radius: var(--radius) !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] *,
    [data-testid="stSidebar"] div[data-baseweb="select"] span,
    [data-testid="stSidebar"] div[data-baseweb="select"] div {
        color: #E8E6E1 !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] svg {
        fill: #5A6B5E !important;
        color: #5A6B5E !important;
    }

    [data-testid="stSidebar"] .stNumberInput input {
        background-color: #1E3A28 !important;
        border: 2px solid #2A4435 !important;
        border-radius: var(--radius) !important;
        color: #E8E6E1 !important;
    }

    [data-testid="stSidebar"] .stNumberInput button {
        background-color: #2A4435 !important;
        border-color: #2A4435 !important;
        color: #B5C4B8 !important;
        border-radius: var(--radius) !important;
    }

    [data-testid="stSidebar"] .stCheckbox label span {
        color: #B5C4B8 !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 2.5px solid #2A4435 !important;
        color: #8A9B8E !important;
        border-radius: var(--radius) !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: #1E3A28 !important;
        border-color: #5A6B5E !important;
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: #2A4435 !important;
    }
    
    button[kind="header"] {
        background: transparent !important;
        border: none !important;
        color: #E8E6E1 !important;
    }
    </style>"""

def componente_logo(tamanho="grande"):
    if tamanho == "grande":
        return '''
        <div style="text-align:center;margin-bottom:2rem;">
            <div style="width:80px;height:80px;background:#15291C;
                border-radius:0;display:inline-flex;align-items:center;
                justify-content:center;margin-bottom:1.8rem;">
                <svg width="40" height="40" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="22" cy="22" r="16" stroke="#D4E7DC" stroke-width="2.5" fill="none"/>
                    <circle cx="22" cy="22" r="8" fill="#C9553A"/>
                    <line x1="22" y1="2" x2="22" y2="10" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                    <line x1="22" y1="34" x2="22" y2="42" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                    <line x1="2" y1="22" x2="10" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                    <line x1="34" y1="22" x2="42" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
            <div style="font-size:3rem;font-weight:900;color:#1A1A18;
                letter-spacing:-0.05em;line-height:0.95;">
                Hema<br>Sakula
            </div>
            <div style="font-size:0.68rem;color:#8A8A82;letter-spacing:0.18em;
                text-transform:uppercase;margin-top:1rem;font-weight:600;">
                Angola a Cuidar dos Seus
            </div>
        </div>'''
    else:
        return '''
        <div style="display:flex;align-items:center;gap:0.7rem;">
            <div style="width:38px;height:38px;background:#15291C;
                border-radius:0;display:flex;align-items:center;
                justify-content:center;flex-shrink:0;">
                <svg width="20" height="20" viewBox="0 0 44 44" fill="none">
                    <circle cx="22" cy="22" r="16" stroke="#D4E7DC" stroke-width="2.5" fill="none"/>
                    <circle cx="22" cy="22" r="8" fill="#C9553A"/>
                    <line x1="22" y1="2" x2="22" y2="10" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                    <line x1="22" y1="34" x2="22" y2="42" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                    <line x1="2" y1="22" x2="10" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                    <line x1="34" y1="22" x2="42" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
            <div>
                <div style="font-size:1.1rem;font-weight:800;color:#1A1A18;
                    letter-spacing:-0.03em;">HemaSakula</div>
            </div>
        </div>'''


def componente_linha():
    return '<div style="height:1px;background:var(--border,#DDDCD7);margin:2rem 0;"></div>'


def componente_linha_fina():
    return '''<div style="margin:1rem 0 1.5rem 0;">
        <div style="height:3px;background:#1A1A18;width:48px;"></div>
    </div>'''


def componente_card(conteudo, borda_esquerda=None):
    borda = f"border-left:4px solid {borda_esquerda};" if borda_esquerda else ""
    return f'''<div style="background:#FFFFFF;border:2px solid #DDDCD7;{borda}
        border-radius:0;padding:1.3rem 1.4rem;margin-bottom:0.6rem;
        transition:border-color 0.3s ease;"
        onmouseover="this.style.borderColor='#1A1A18'"
        onmouseout="this.style.borderColor='#DDDCD7'">{conteudo}</div>'''


def componente_badge(texto, tipo="normal"):
    cores = {
        "normal": "background:#F3F2EE;color:#1A1A18;border:2px solid #DDDCD7;",
        "sucesso": "background:#E8F5ED;color:#1B6B3A;border:2px solid #B8D8C4;",
        "alerta": "background:#FDF2E9;color:#C9553A;border:2px solid #F0C9B5;",
        "perigo": "background:#FCEAEA;color:#8B1A1A;border:2px solid #E8B5B5;",
        "critico": "background:#1A1A18;color:#FAFAF8;border:2px solid #1A1A18;",
        "info": "background:#E8EFF7;color:#1E3A6E;border:2px solid #B5CCEB;",
    }
    estilo = cores.get(tipo, cores["normal"])
    return f'''<span style="{estilo}display:inline-block;padding:0.35rem 0.9rem;
        border-radius:0;font-size:0.68rem;font-weight:700;
        letter-spacing:0.1em;text-transform:uppercase;">{texto}</span>'''


def componente_label(texto):
    return f'''<div style="color:#8A8A82;font-size:0.68rem;text-transform:uppercase;
        letter-spacing:0.14em;font-weight:700;margin-bottom:0.8rem;">{texto}</div>'''


def componente_footer():
    return '''
    <div style="text-align:center;padding:3rem 0;margin-top:4rem;
        border-top:2px solid #DDDCD7;">
        <div style="color:#8A8A82;font-size:0.65rem;letter-spacing:0.18em;
            text-transform:uppercase;font-weight:700;margin-bottom:0.5rem;">
            HemaSakula
        </div>
        <div style="color:#B5B3AD;font-size:0.82rem;font-weight:400;">
            A tua saúde importa. Estamos aqui por ti.
        </div>
    </div>'''


def tela_boas_vindas():
    st.markdown(css_global(), unsafe_allow_html=True)
    st.markdown(css_tela_inicio(), unsafe_allow_html=True)

    saudacao = obter_saudacao()

    st.markdown("<div style='height:6vh;'></div>", unsafe_allow_html=True)

    st.markdown(componente_logo("grande"), unsafe_allow_html=True)

    st.markdown(componente_linha(), unsafe_allow_html=True)

    st.markdown(f'''
    <div style="text-align:center;margin-bottom:2.5rem;">
        <div style="font-size:1.8rem;font-weight:800;color:#1A1A18;
            letter-spacing:-0.03em;margin-bottom:0.8rem;">
            {saudacao}.
        </div>
        <div style="font-size:0.95rem;color:#8A8A82;line-height:1.8;
            max-width:360px;margin:0 auto;">
            Encontra clínicas e hospitais perto de ti.
            Cuida da tua saúde com quem te entende.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(componente_linha_fina(), unsafe_allow_html=True)

    nome = st.text_input(
        "NOME",
        placeholder="Como queres que te chamemos?",
        key="nome_cliente"
    )

    municipio = st.selectbox(
        "MUNICÍPIO",
        MUNICIPIOS_LISTA,
        index=None,
        placeholder="Onde vives?",
        key="municipio_cliente"
    )

    telefone = st.text_input(
        "TELEFONE",
        placeholder="9xx xxx xxx",
        key="telefone_cliente"
    )

    email = st.text_input(
        "EMAIL (OPCIONAL)",
        placeholder="exemplo@email.com",
        key="email_cliente"
    )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    if st.button("COMEÇAR →", key="btn_comecar", use_container_width=True):
        erros = []
        if not nome or not nome.strip():
            erros.append("Precisamos do teu nome.")
        if not municipio:
            erros.append("Escolhe o município onde vives.")
        if not telefone:
            erros.append("O número de telefone é obrigatório.")
        elif not validar_telefone(telefone):
            erros.append("O número deve ter 9 dígitos e começar por 9.")
        if email and email.strip() and not validar_email(email.strip()):
            erros.append("O email não parece válido.")

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            sucesso, dados = registar_cliente(
                nome.strip(), telefone.strip(),
                municipio, email.strip() if email else ''
            )
            if sucesso:
                st.session_state['ecra'] = 'cliente'
                st.session_state['cliente'] = dados
                st.rerun()

    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)
    st.markdown(componente_linha(), unsafe_allow_html=True)

    st.markdown('''
    <div style="text-align:center;margin-bottom:1.2rem;">
        <div style="color:#8A8A82;font-size:0.68rem;letter-spacing:0.14em;
            text-transform:uppercase;font-weight:700;">
            Acesso profissional
        </div>
    </div>
    ''', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("ENTRAR COMO EMPRESA", key="btn_empresa", use_container_width=True):
            st.session_state['ecra'] = 'login_empresa'
            st.rerun()

    st.markdown(componente_footer(), unsafe_allow_html=True)


def tela_login_empresa():
    st.markdown(css_global(), unsafe_allow_html=True)
    st.markdown(css_tela_inicio(), unsafe_allow_html=True)

    st.markdown("<div style='height:8vh;'></div>", unsafe_allow_html=True)

    st.markdown('''
    <div style="text-align:center;margin-bottom:2.5rem;">
        <div style="width:56px;height:56px;background:#15291C;border-radius:0;
            display:inline-flex;align-items:center;justify-content:center;
            margin-bottom:1.5rem;">
            <svg width="28" height="28" viewBox="0 0 44 44" fill="none">
                <circle cx="22" cy="22" r="16" stroke="#D4E7DC" stroke-width="2.5" fill="none"/>
                <circle cx="22" cy="22" r="8" fill="#C9553A"/>
                <line x1="22" y1="2" x2="22" y2="10" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                <line x1="22" y1="34" x2="22" y2="42" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                <line x1="2" y1="22" x2="10" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                <line x1="34" y1="22" x2="42" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
            </svg>
        </div>
        <div style="font-size:1.6rem;font-weight:800;color:#1A1A18;
            letter-spacing:-0.03em;">
            Acesso Profissional
        </div>
        <div style="font-size:0.85rem;color:#8A8A82;margin-top:0.5rem;">
            Para clínicas e hospitais parceiros
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(componente_linha_fina(), unsafe_allow_html=True)

    usuario = st.text_input(
        "UTILIZADOR",
        placeholder="O teu utilizador",
        key="emp_usuario"
    )

    senha = st.text_input(
        "PALAVRA-PASSE",
        type="password",
        placeholder="A tua palavra-passe",
        key="emp_senha"
    )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    if st.button("ENTRAR →", key="btn_entrar_empresa", use_container_width=True):
        if not usuario or not senha:
            st.error("Preenche os dois campos.")
        else:
            autenticado = False
            try:
                usuarios_validos = st.secrets["usuarios"]
                if usuario.strip().lower() in usuarios_validos:
                    if usuarios_validos[usuario.strip().lower()] == senha:
                        autenticado = True
            except Exception:
                pass

            if autenticado:
                st.session_state['ecra'] = 'empresa'
                st.session_state['empresa_usuario'] = usuario.strip()
                st.rerun()
            else:
                st.error("Credenciais incorrectas.")

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← VOLTAR", key="btn_voltar_login", use_container_width=True):
            st.session_state['ecra'] = 'inicio'
            st.rerun()

    st.markdown('''
    <div style="text-align:center;margin-top:3rem;color:#B5B3AD;
        font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;">
        Acesso restrito a profissionais autorizados
    </div>
    ''', unsafe_allow_html=True)


def tela_painel_cliente():
    st.markdown(css_global(), unsafe_allow_html=True)
    st.markdown(css_painel_cliente(), unsafe_allow_html=True)

    cliente = st.session_state.get('cliente', {})
    nome = cliente.get('nome', 'Amigo')
    municipio = cliente.get('municipio', 'Luanda')
    primeiro_nome = nome.split()[0] if nome else 'Amigo'
    saudacao = obter_saudacao()

    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(componente_logo("pequeno"), unsafe_allow_html=True)

    with col_h2:
        st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)
        if st.button("SAIR", key="btn_sair_cliente"):
            for k in ['ecra', 'cliente']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    st.markdown(componente_linha(), unsafe_allow_html=True)

    st.markdown(f'''
    <div style="margin-bottom:0.5rem;">
        <div style="font-size:2.2rem;font-weight:900;color:#1A1A18;
            letter-spacing:-0.04em;line-height:1.1;">
            {saudacao},<br>{primeiro_nome}.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(componente_linha_fina(), unsafe_allow_html=True)

    st.markdown(f'''
    <div style="color:#8A8A82;font-size:0.88rem;margin-bottom:2rem;">
        O que precisas hoje?
    </div>
    ''', unsafe_allow_html=True)

    tab_clinicas, tab_alertas, tab_sobre = st.tabs([
        "Clínicas",
        "Alertas",
        "Sobre"
    ])

    with tab_clinicas:
        info_mun = MUNICIPIOS_INFO.get(municipio, {})
        hospital_ref = info_mun.get('hospital', 'Centro de Saúde')

        st.markdown(componente_label(f"Clínicas e hospitais · {municipio}"), unsafe_allow_html=True)

        conteudo_ref = f'''
        <div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;
            letter-spacing:0.12em;font-weight:700;margin-bottom:0.5rem;">
            Hospital de referência
        </div>
        <div style="font-weight:800;color:#1A1A18;font-size:1.15rem;
            letter-spacing:-0.02em;">
            {hospital_ref}
        </div>
        <div style="color:#8A8A82;font-size:0.82rem;margin-top:0.35rem;">
            {municipio} · {info_mun.get('provincia', 'Luanda')}
        </div>'''
        st.markdown(
            componente_card(conteudo_ref, borda_esquerda="#1A1A18"),
            unsafe_allow_html=True
        )

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

        parceiros_lista = [
            {'nome': 'Hospital Josina Machel', 'tipo': 'Hospital Central',
             'local': 'Ingombota', 'horario': '24 horas', 'publico': True},
            {'nome': 'Hospital Américo Boavida', 'tipo': 'Hospital Central',
             'local': 'Maianga', 'horario': '24 horas', 'publico': True},
            {'nome': 'Hospital Pediátrico David Bernardino', 'tipo': 'Hospital Pediátrico',
             'local': 'Maianga', 'horario': '24 horas', 'publico': True},
            {'nome': 'Clínica Sagrada Esperança', 'tipo': 'Clínica Privada',
             'local': 'Talatona', 'horario': '24 horas', 'publico': False},
            {'nome': 'Clínica Multiperfil', 'tipo': 'Clínica Privada',
             'local': 'Talatona', 'horario': '07h–20h', 'publico': False},
            {'nome': 'Hospital Geral de Viana', 'tipo': 'Hospital Geral',
             'local': 'Viana', 'horario': '24 horas', 'publico': True},
        ]

        for p in parceiros_lista:
            badge_tipo = 'Público' if p['publico'] else 'Privado'
            badge_html = componente_badge(
                badge_tipo,
                "sucesso" if p['publico'] else "alerta"
            )

            conteudo = f'''
            <div style="display:flex;align-items:center;gap:1rem;">
                <div style="width:42px;height:42px;background:#1A1A18;
                    border-radius:0;display:flex;align-items:center;
                    justify-content:center;color:white;font-weight:800;
                    font-size:0.65rem;flex-shrink:0;letter-spacing:0.05em;">
                    {p['nome'][:2].upper()}
                </div>
                <div style="flex:1;">
                    <div style="font-weight:700;color:#1A1A18;font-size:0.9rem;
                        letter-spacing:-0.01em;">
                        {p['nome']}
                    </div>
                    <div style="color:#8A8A82;font-size:0.78rem;margin-top:0.2rem;">
                        {p['local']} · {p['horario']}
                    </div>
                </div>
                <div>{badge_html}</div>
            </div>'''
            st.markdown(componente_card(conteudo), unsafe_allow_html=True)

    with tab_alertas:
        info_mun = MUNICIPIOS_INFO.get(municipio, {})
        mes_actual = datetime.now().month
        nomes_meses = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        mes_nome = nomes_meses[mes_actual]
        risco_mun = info_mun.get('risco', 'Médio')

        st.markdown(componente_label(f"Alertas de saúde · {mes_nome}"), unsafe_allow_html=True)

        tipo_badge = {
            'Baixo': 'sucesso', 'Médio': 'alerta',
            'Alto': 'perigo', 'Muito Alto': 'critico'
        }
        badge_risco = componente_badge(risco_mun, tipo_badge.get(risco_mun, 'normal'))

        conteudo_risco = f'''
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;
                    letter-spacing:0.12em;font-weight:700;">Risco na tua zona</div>
                <div style="font-weight:800;color:#1A1A18;font-size:1.05rem;
                    margin-top:0.4rem;letter-spacing:-0.02em;">{municipio}</div>
            </div>
            <div>{badge_risco}</div>
        </div>'''
        st.markdown(
            componente_card(conteudo_risco, borda_esquerda="#1A1A18"),
            unsafe_allow_html=True
        )

        alertas_mes = {
            1: "Época de chuvas. Cuidado com a cólera e a malária. Bebe sempre água tratada.",
            2: "Chuvas fortes. Evita água parada perto de casa. Dorme com rede mosquiteira.",
            3: "Pico de malária. Se tiveres febre, vai ao centro de saúde mais próximo.",
            4: "Ainda há muitos mosquitos. Usa repelente e rede mosquiteira.",
            5: "As chuvas estão a acabar. Boa altura para desparasitar.",
            6: "Cacimbo. Agasalha-te bem. Quem tem drepanocitose: cuidado com o frio.",
            7: "Mês mais frio. Protege as crianças e os idosos.",
            8: "Se tens tosse há mais de 2 semanas, faz exame no centro de saúde.",
            9: "Boa altura para um check-up e desparasitação.",
            10: "As chuvas voltam. Verifica a rede mosquiteira e trata a água.",
            11: "Chuvas. Lembra-te da desparasitação.",
            12: "Prepara-te para a época chuvosa."
        }
        alerta_txt = alertas_mes.get(mes_actual, "Cuida da tua saúde!")

        st.markdown(f'''
        <div style="background:#FFFFFF;border:2px solid #DDDCD7;
            border-left:4px solid #C9553A;border-radius:0;
            padding:1.4rem;margin:1.2rem 0;">
            <div style="font-weight:800;color:#1A1A18;margin-bottom:0.5rem;
                font-size:0.9rem;letter-spacing:-0.01em;">
                Alerta para {mes_nome}
            </div>
            <div style="color:#5A5A52;font-size:0.88rem;line-height:1.8;">
                {alerta_txt}
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown(componente_label("Dicas para ti"), unsafe_allow_html=True)

        dicas = [
            ("Rede mosquiteira",
             "Dorme sempre debaixo de uma rede mosquiteira, mesmo no cacimbo."),
            ("Água tratada",
             "Ferve ou trata a água antes de beber. Protege contra cólera e tifóide."),
            ("Desparasitação",
             "Toma Albendazol de 6 em 6 meses. Para adultos e crianças acima de 2 anos."),
            ("Vacinas",
             "Verifica se as vacinas das crianças estão em dia."),
            ("Drepanocitose",
             "Se há casos na família, faz o teste antes de ter filhos.")
        ]

        for titulo, texto in dicas:
            conteudo = f'''
            <div style="font-weight:700;color:#1A1A18;font-size:0.88rem;
                letter-spacing:-0.01em;">
                {titulo}
            </div>
            <div style="color:#8A8A82;font-size:0.82rem;margin-top:0.3rem;
                line-height:1.7;">
                {texto}
            </div>'''
            st.markdown(componente_card(conteudo), unsafe_allow_html=True)

    with tab_sobre:
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        st.markdown(componente_logo("grande"), unsafe_allow_html=True)

        st.markdown(componente_linha_fina(), unsafe_allow_html=True)

        conteudo_what = f'''
        <div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;
            letter-spacing:0.12em;font-weight:700;margin-bottom:0.8rem;">
            O que é?
        </div>
        <div style="color:#1A1A18;font-size:0.95rem;line-height:1.85;">
            O HemaSakula é uma plataforma angolana que te ajuda a encontrar
            clínicas e hospitais perto de ti. Além disso, as clínicas parceiras
            usam o nosso sistema inteligente para analisar exames de sangue
            e dar melhores diagnósticos.
        </div>'''
        st.markdown(componente_card(conteudo_what), unsafe_allow_html=True)

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            conteudo_paciente = f'''
            <div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;
                letter-spacing:0.12em;font-weight:700;margin-bottom:0.8rem;">
                Para ti
            </div>
            <div style="color:#5A5A52;font-size:0.88rem;line-height:1.85;">
                Encontra clínicas perto da tua zona. Recebe alertas de saúde
                para o teu município. Sabe quando desparasitar, vacinar,
                fazer check-up.
            </div>'''
            st.markdown(
                componente_card(conteudo_paciente, borda_esquerda="#1B6B3A"),
                unsafe_allow_html=True
            )

        with col_p2:
            conteudo_clinica = f'''
            <div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;
                letter-spacing:0.12em;font-weight:700;margin-bottom:0.8rem;">
                Para clínicas
            </div>
            <div style="color:#5A5A52;font-size:0.88rem;line-height:1.85;">
                Apoio à decisão clínica com IA. Análise de hemogramas
                inteligente. Dados epidemiológicos por município.
            </div>'''
            st.markdown(
                componente_card(conteudo_clinica, borda_esquerda="#C9553A"),
                unsafe_allow_html=True
            )

    st.markdown(componente_footer(), unsafe_allow_html=True)


def tela_painel_empresa():
    st.markdown(css_global(), unsafe_allow_html=True)
    st.markdown(css_painel_empresa(), unsafe_allow_html=True)

    usuario = st.session_state.get('empresa_usuario', 'Empresa')

    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown(componente_logo("pequeno"), unsafe_allow_html=True)
    with col_header2:
        st.markdown(f'''
        <div style="text-align:right;padding-top:0.5rem;">
            <span style="color:#8A8A82;font-size:0.75rem;font-weight:600;
                letter-spacing:0.05em;">
                {usuario.capitalize()} · {datetime.now().strftime("%d/%m/%Y")}
            </span>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown(componente_linha(), unsafe_allow_html=True)

    st.markdown(f'''
    <div style="background:#FFFFFF;border:2px solid #DDDCD7;
        border-left:4px solid #8A8A82;border-radius:0;
        padding:1.2rem 1.4rem;margin-bottom:1.5rem;">
        <div style="color:#5A5A52;font-size:0.88rem;line-height:1.7;">
            <strong style="color:#1A1A18;">Atenção:</strong>
            Este sistema serve de apoio à decisão clínica. Não substitui a
            avaliação presencial nem o julgamento do profissional de saúde.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    modelo, encoders, features = carregar_modelo()
    if modelo is None:
        st.error("Modelo não encontrado. Executa primeiro: python modelo_ml.py")
        return

    st.markdown(f'''
    <div style="background:#E8F5ED;border:2px solid #B8D8C4;
        border-left:4px solid #1B6B3A;border-radius:0;
        padding:1rem 1.4rem;margin-bottom:1.5rem;">
        <span style="color:#1B6B3A;font-weight:700;font-size:0.82rem;
            letter-spacing:0.05em;">
            SISTEMA OPERACIONAL — MODELO CARREGADO
        </span>
    </div>
    ''', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f'''
        <div style="text-align:center;padding:1.2rem 0 1.8rem 0;">
            <div style="width:48px;height:48px;background:#1E3A28;border-radius:0;
                display:inline-flex;align-items:center;justify-content:center;
                margin-bottom:0.8rem;">
                <svg width="24" height="24" viewBox="0 0 44 44" fill="none">
                    <circle cx="22" cy="22" r="16" stroke="#D4E7DC" stroke-width="2.5" fill="none"/>
                    <circle cx="22" cy="22" r="8" fill="#C9553A"/>
                    <line x1="22" y1="2" x2="22" y2="10" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                    <line x1="22" y1="34" x2="22" y2="42" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                    <line x1="2" y1="22" x2="10" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                    <line x1="34" y1="22" x2="42" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
            <div style="color:#E8E6E1;font-weight:700;font-size:0.9rem;">
                {usuario.capitalize()}
            </div>
            <div style="color:#5A6B5E;font-size:0.62rem;margin-top:0.2rem;
                letter-spacing:0.12em;text-transform:uppercase;font-weight:600;">
                Conta Profissional
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("---")
        st.header("Identificação")
        faixa_etaria = st.selectbox("Faixa etária", FAIXAS_ETARIAS, index=5)
        sexo = st.selectbox("Sexo biológico", SEXOS)
        gestante = False
        if sexo == 'Feminino' and ('Adulto' in faixa_etaria or 'Adolescente' in faixa_etaria):
            gestante = st.checkbox("Grávida")
        peso = st.number_input("Peso (kg)", 1.0, 200.0, 65.0, 0.5)

        st.header("Localização")
        municipio = st.selectbox("Município", list(MUNICIPIOS_INFO.keys()))
        info_mun = MUNICIPIOS_INFO[municipio]
        provincia = info_mun['provincia']
        st.markdown(f"**Província:** {provincia}")
        st.markdown(f"**Risco:** {info_mun['risco']}")

        st.header("Colheita")
        mes = st.selectbox("Mês", MESES, index=datetime.now().month - 1)
        estacao = ESTACOES_POR_MES[mes]
        st.markdown(f"**Estação:** {estacao}")

        st.header("Antecedentes")
        status_genetico = st.selectbox("Hemoglobina (genética)", STATUS_GENETICO)
        mordedura = st.checkbox("Mordedura animal recente")

        st.markdown("---")
        if st.button("SAIR", key="btn_sair_empresa", use_container_width=True):
            for k in ['ecra', 'empresa_usuario']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    st.markdown(f'''
    <div style="margin-bottom:0.3rem;">
        <div style="font-size:1.6rem;font-weight:900;color:#1A1A18;
            letter-spacing:-0.04em;">
            Hemograma
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown(componente_linha_fina(), unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'''
        <div style="color:#C9553A;font-weight:800;font-size:0.7rem;
            letter-spacing:0.14em;text-transform:uppercase;
            padding-bottom:0.6rem;margin-bottom:1.2rem;
            border-bottom:3px solid #C9553A;">
            Série Vermelha
        </div>
        ''', unsafe_allow_html=True)
        hemoglobina = st.number_input("Hemoglobina (g/dL)", 3.0, 22.0, 12.5, 0.1)
        hematocrito = st.number_input("Hematócrito (%)", 10.0, 70.0, 38.0, 0.5)
        hemacias = st.number_input("Eritrócitos (x10⁶/µL)", 2.0, 7.0, 4.5, 0.1)
        vcm = st.number_input("VCM (fL)", 50.0, 120.0, 88.0, 1.0)
        hcm = st.number_input("HCM (pg)", 15.0, 40.0, 29.0, 0.5)
        chcm = st.number_input("CHCM (g/dL)", 28.0, 40.0, 33.5, 0.5)
        rdw = st.number_input("RDW (%)", 10.0, 25.0, 13.5, 0.1)

    with col2:
        st.markdown(f'''
        <div style="color:#1A1A18;font-weight:800;font-size:0.7rem;
            letter-spacing:0.14em;text-transform:uppercase;
            padding-bottom:0.6rem;margin-bottom:1.2rem;
            border-bottom:3px solid #1A1A18;">
            Série Branca
        </div>
        ''', unsafe_allow_html=True)
        leucocitos = st.number_input("Leucócitos (/mm³)", 500, 50000, 7500, 100)
        neutrofilos = st.number_input("Neutrófilos (%)", 10.0, 90.0, 58.0, 1.0)
        linfocitos = st.number_input("Linfócitos (%)", 5.0, 70.0, 32.0, 1.0)
        monocitos = st.number_input("Monócitos (%)", 0.0, 20.0, 6.0, 0.5)
        eosinofilos = st.number_input("Eosinófilos (%)", 0.0, 25.0, 3.0, 0.5)
        basofilos = st.number_input("Basófilos (%)", 0.0, 3.0, 0.5, 0.1)

        valido, soma = validar_leucograma(
            neutrofilos, linfocitos, monocitos, eosinofilos, basofilos
        )
        if not valido:
            st.warning(
                f"O diferencial soma {soma:.1f}% — o esperado é próximo de 100%."
            )

    with col3:
        st.markdown(f'''
        <div style="color:#15291C;font-weight:800;font-size:0.7rem;
            letter-spacing:0.14em;text-transform:uppercase;
            padding-bottom:0.6rem;margin-bottom:1.2rem;
            border-bottom:3px solid #15291C;">
            Plaquetas e Outros
        </div>
        ''', unsafe_allow_html=True)
        plaquetas = st.number_input("Plaquetas (/mm³)", 5000, 1000000, 250000, 5000)
        vpm = st.number_input("VPM (fL)", 5.0, 15.0, 9.5, 0.5)
        reticulocitos = st.number_input("Reticulócitos (%)", 0.2, 15.0, 1.2, 0.1)

    st.markdown(componente_linha(), unsafe_allow_html=True)

    with st.form(key="form_analise"):
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit = st.form_submit_button(
                "ANALISAR HEMOGRAMA →", use_container_width=True
            )

    if submit:
        dados = {
            'faixa_etaria': faixa_etaria, 'sexo': sexo, 'gestante': gestante,
            'peso_kg': peso, 'municipio': municipio, 'provincia': provincia,
            'mes': mes, 'estacao': estacao, 'status_genetico': status_genetico,
            'mordedura_recente': mordedura, 'hemoglobina': hemoglobina,
            'hematocrito': hematocrito, 'hemacias': hemacias, 'vcm': vcm,
            'hcm': hcm, 'chcm': chcm, 'rdw': rdw, 'leucocitos': leucocitos,
            'neutrofilos': neutrofilos, 'linfocitos': linfocitos,
            'monocitos': monocitos, 'eosinofilos': eosinofilos,
            'basofilos': basofilos, 'plaquetas': plaquetas, 'vpm': vpm,
            'reticulocitos': reticulocitos
        }

        gravidade, resultados, erro = processar_analise(
            modelo, encoders, features, dados
        )

        if erro:
            st.error(f"Erro no processamento: {erro}")
            return

        if not resultados:
            st.error("Não consegui gerar resultados. Confere os dados.")
            return

        diag_principal = resultados[0][0]

        st.markdown(f'''
        <div style="margin-top:2.5rem;">
            <div style="font-size:1.6rem;font-weight:900;color:#1A1A18;
                letter-spacing:-0.04em;">
                Resultados
            </div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown(componente_linha_fina(), unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            tipo_grav = {
                "LEVE": "sucesso", "MODERADO": "alerta",
                "GRAVE": "perigo", "CRITICO": "critico"
            }
            badge_grav = componente_badge(gravidade, tipo_grav.get(gravidade, "normal"))
            conteudo_grav = f'''
            <div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;
                letter-spacing:0.12em;font-weight:700;">Gravidade</div>
            <div style="margin-top:0.8rem;">{badge_grav}</div>'''
            st.markdown(componente_card(conteudo_grav), unsafe_allow_html=True)

        with col_r2:
            conteudo_hosp = f'''
            <div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;
                letter-spacing:0.12em;font-weight:700;">Referenciar para</div>
            <div style="margin-top:0.8rem;font-weight:700;color:#1A1A18;
                font-size:0.95rem;">{info_mun["hospital"]}</div>'''
            st.markdown(componente_card(conteudo_hosp), unsafe_allow_html=True)

        st.markdown(componente_label("Hipóteses diagnósticas"), unsafe_allow_html=True)

        for i, (diag, prob) in enumerate(resultados[:3]):
            if i == 0:
                conteudo = f'''
                <div style="display:flex;justify-content:space-between;
                    align-items:center;">
                    <span style="font-size:1.1rem;font-weight:800;color:#1A1A18;
                        letter-spacing:-0.02em;">
                        01 — {diag}
                    </span>
                    <span style="background:#1A1A18;color:#FAFAF8;
                        padding:0.45rem 1.1rem;border-radius:0;font-weight:800;
                        font-size:0.82rem;letter-spacing:0.02em;">
                        {prob:.1f}%
                    </span>
                </div>'''
                st.markdown(
                    componente_card(conteudo, borda_esquerda="#1A1A18"),
                    unsafe_allow_html=True
                )
                st.progress(prob / 100)
            else:
                num = f"0{i+1}"
                conteudo = f'''
                <div style="display:flex;justify-content:space-between;
                    align-items:center;">
                    <span style="color:#5A5A52;font-weight:600;font-size:0.9rem;">
                        {num} — {diag}
                    </span>
                    <span style="color:#8A8A82;font-weight:700;font-size:0.85rem;">
                        {prob:.1f}%
                    </span>
                </div>'''
                st.markdown(componente_card(conteudo), unsafe_allow_html=True)

        st.markdown(componente_label("Conduta clínica"), unsafe_allow_html=True)

        if diag_principal in CONDUTAS:
            cond = CONDUTAS[diag_principal]

            if gravidade in ["GRAVE", "CRITICO"]:
                st.error(f"**Caso grave:** {cond['grave']}")
            else:
                st.info(f"**Conduta:** {cond['leve']}")

            conteudo_exame = f'''
            <div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;
                letter-spacing:0.12em;font-weight:700;margin-bottom:0.5rem;">
                Exame para confirmar
            </div>
            <div style="color:#1A1A18;font-weight:600;font-size:0.92rem;">
                {cond["exame"]}
            </div>'''
            st.markdown(componente_card(conteudo_exame), unsafe_allow_html=True)

            if cond['alertas']:
                with st.expander("Sinais de alarme — referenciar já"):
                    for a in cond['alertas']:
                        st.markdown(f"· {a}")

        st.markdown(componente_label("Interpretação do hemograma"), unsafe_allow_html=True)

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
                f"**Hemoglobinopatia: {status_genetico}.** "
                "Seguimento no IHL ou centro de drepanocitose. "
                "Ácido fólico 5 mg/dia, beber muita água, "
                "evitar frio e tudo que possa provocar crise."
            )

        if mordedura:
            st.error(
                "**Mordedura animal — risco rábico!** "
                "Lavar a ferida com água e sabão durante 15 minutos. "
                "Iniciar profilaxia anti-rábica sem esperar resultados. "
                "Cada hora conta."
            )

    st.markdown(componente_footer(), unsafe_allow_html=True)


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
