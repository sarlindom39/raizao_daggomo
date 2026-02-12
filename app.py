# app.py
# HemaSakula - Angola a Cuidar dos Seus
# v3.0 - Tela principal acolhedora focada no cliente
# Login de empresa discreto

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import time
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="HemaSakula",
    page_icon="ðŸ©¸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

SLOGAN = "Angola a Cuidar dos Seus"

# ficheiros de dados locais
FICHEIRO_CLIENTES = 'dados_clientes.json'
FICHEIRO_EMPRESAS = 'dados_empresas.json'

# municipios disponiveis
MUNICIPIOS_LISTA = [
    'Ingombota', 'Talatona', 'Belas', 'Viana', 'Cacuaco',
    'Cazenga', 'Kilamba Kiaxi', 'Rangel', 'Maianga', 'Samba',
    'Catete', 'Icolo e Bengo'
]

MUNICIPIOS_INFO = {
    'Ingombota': {'provincia': 'Luanda', 'risco': 'Baixo', 'hospital': 'Hospital Josina Machel'},
    'Talatona': {'provincia': 'Luanda', 'risco': 'Baixo', 'hospital': 'Clinica Sagrada Esperanca'},
    'Belas': {'provincia': 'Luanda', 'risco': 'Medio', 'hospital': 'Hospital Americo Boavida'},
    'Viana': {'provincia': 'Luanda', 'risco': 'Medio', 'hospital': 'Hospital Geral de Viana'},
    'Cacuaco': {'provincia': 'Luanda', 'risco': 'Alto', 'hospital': 'Hospital Geral de Cacuaco'},
    'Cazenga': {'provincia': 'Luanda', 'risco': 'Muito Alto', 'hospital': 'Hospital Municipal do Cazenga'},
    'Kilamba Kiaxi': {'provincia': 'Luanda', 'risco': 'Medio', 'hospital': 'Hospital Geral de Luanda'},
    'Rangel': {'provincia': 'Luanda', 'risco': 'Alto', 'hospital': 'Hospital Americo Boavida'},
    'Maianga': {'provincia': 'Luanda', 'risco': 'Medio', 'hospital': 'Hospital Josina Machel'},
    'Samba': {'provincia': 'Luanda', 'risco': 'Medio', 'hospital': 'Hospital Americo Boavida'},
    'Catete': {'provincia': 'Icolo e Bengo', 'risco': 'Alto', 'hospital': 'Hospital Municipal de Catete'},
    'Icolo e Bengo': {'provincia': 'Icolo e Bengo', 'risco': 'Alto', 'hospital': 'Centro de Saude'}
}

FAIXAS_ETARIAS = [
    'Recem-nascido (0-28 dias)', 'Lactente (1-12 meses)',
    'Crianca (1-5 anos)', 'Crianca (5-12 anos)',
    'Adolescente (12-18 anos)', 'Adulto jovem (18-45 anos)',
    'Adulto (45-65 anos)', 'Idoso (>65 anos)'
]

MESES = [
    'Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

ESTACOES_POR_MES = {
    'Janeiro': 'Chuvas', 'Fevereiro': 'Chuvas (pico)',
    'Marco': 'Chuvas (pico)', 'Abril': 'Chuvas (pico)',
    'Maio': 'Chuvas (a acabar)', 'Junho': 'Cacimbo',
    'Julho': 'Cacimbo', 'Agosto': 'Cacimbo',
    'Setembro': 'Transicao', 'Outubro': 'Chuvas (inicio)',
    'Novembro': 'Chuvas', 'Dezembro': 'Chuvas'
}

STATUS_GENETICO = ['Normal', 'Traco falciforme (AS)', 'Drepanocitose (SS)']
SEXOS = ['Masculino', 'Feminino']

CONDUTAS = {
    'Malaria': {
        'leve': (
            'Coartem (Artemer + Lumefantrina): 4 comprimidos de 12/12h '
            'durante 3 dias. Tomar sempre com comida, de preferencia com '
            'gordura pra absorver melhor. Paracetamol pra baixar a febre.'
        ),
        'grave': (
            'Artesunato EV 2,4 mg/kg as 0h, 12h e 24h, depois 1x/dia '
            'ate o doente aguentar via oral. Controlar Hb no dia 7 e 14. '
            'Se a parasitemia nao baixar em 24h, reavaliar a dose.'
        ),
        'exame': 'Gota espessa ou teste rapido (TDR)',
        'alertas': [
            'Convulsoes',
            'Prostracao - nao come, nao bebe, nao anda',
            'Vomitos que nao param',
            'Urina escura (cor de coca-cola)',
            'Falta de ar',
            'Amarelao nos olhos (ictericia)',
            'Confusao ou perda de consciencia'
        ]
    },
    'Dengue': {
        'leve': (
            'Hidratar bem por via oral (60-80 mL/kg/dia). Paracetamol pra febre. '
            'Nada de ibuprofeno nem aspirina - pode causar hemorragia.'
        ),
        'grave': (
            'Soro EV e monitorizar o hematocrito de 2 em 2 horas. Se o Ht subir '
            'mais de 20%, aumentar o ritmo da hidratacao.'
        ),
        'exame': 'NS1 (fase inicial) ou IgM/IgG (a partir do 5o dia)',
        'alertas': [
            'Dor de barriga forte que nao passa',
            'Vomitos sem parar',
            'Sangramento na gengiva ou pelo nariz',
            'Crianca mole demais ou muito irritada'
        ]
    },
    'Drepanocitose (SS)': {
        'leve': (
            'Acido folico 5 mg/dia. Beber muita agua. '
            'Evitar frio e esforco fisico a mais. '
            'Seguimento regular no IHL ou centro de drepanocitose.'
        ),
        'grave': (
            'Crise vaso-oclusiva: analgesia escalonada (tramadol ou morfina) '
            '+ soro EV + oxigenio se SpO2 < 95%. '
            'Referenciar ao IHL com urgencia.'
        ),
        'exame': 'Electroforese de hemoglobina',
        'alertas': [
            'Febre - num drepanocitico e sempre urgencia',
            'Dor no peito - pode ser sindrome toracica aguda',
            'Priapismo',
            'Sinais de AVC - braco ou perna sem forca, fala enrolada, boca torta'
        ]
    },
    'Anemia Ferropriva': {
        'leve': (
            'Sulfato ferroso durante 3 a 6 meses. Tomar em jejum com '
            'sumo de limao - a vitamina C ajuda a absorver melhor o ferro. '
            'Avisar que as fezes ficam escuras - e normal, nao se preocupar.'
        ),
        'grave': (
            'Se a Hb estiver abaixo de 5 g/dL, pensar em transfusao. '
            'Investigar a causa - parasitose? Hemorragia escondida?'
        ),
        'exame': 'Ferritina serica',
        'alertas': [
            'Falta de ar mesmo parado',
            'Coracao a bater muito rapido',
            'Palidez intensa - ver as palmas das maos e os olhos'
        ]
    },
    'Colera': {
        'leve': (
            'SRO conforme protocolo da OMS. Preparar 1 saqueta em 1 litro '
            'de agua tratada. Dar aos poucos, mas com frequencia.'
        ),
        'grave': (
            'Ringer Lactato EV em bolus ate estabilizar. '
            'Azitromicina 1 g dose unica. Notificacao obrigatoria a DPS.'
        ),
        'exame': 'Coprocultura',
        'alertas': [
            'Olhos fundos, boca seca',
            'Pele que demora a voltar ao lugar (sinal da prega)',
            'Crianca que ja nao chora com lagrimas',
            'Muito mole ou muito agitado'
        ]
    },
    'Febre Tifoide': {
        'leve': (
            'Ciprofloxacina 500 mg de 12/12h durante 7 a 14 dias. '
            'Em criancas, melhor usar azitromicina. '
            'Hidratar bem e comer leve.'
        ),
        'grave': (
            'Ceftriaxona EV 2 g/dia + internamento. '
            'Ficar atento a sinais de perfuracao intestinal - '
            'barriga dura, dor forte, febre em pico.'
        ),
        'exame': 'Hemocultura (de preferencia) ou coprocultura',
        'alertas': [
            'Barriga dura como tabua - pode ter perfurado',
            'Confusao mental',
            'Sangue nas fezes'
        ]
    },
    'Parasitose Intestinal': {
        'leve': (
            'Albendazol 400 mg dose unica (acima de 2 anos e adultos). '
            'Repetir de 6 em 6 meses. '
            'Reforcar: lavar as maos e tratar a agua.'
        ),
        'grave': (
            'Albendazol 400 mg durante 3 dias + sulfato ferroso '
            'se tiver anemia junto. Quantificar a carga parasitaria.'
        ),
        'exame': 'Exame parasitologico de fezes (3 amostras)',
        'alertas': [
            'Barriga muito inchada - risco de obstrucao',
            'Desnutricao grave, principalmente nas criancas'
        ]
    },
    'Tuberculose': {
        'leve': (
            'Esquema DOTS: fase intensiva com RHZE durante 2 meses, '
            'depois RH por mais 4 meses. Toma observada directamente. '
            'O doente nao pode largar o tratamento no meio.'
        ),
        'grave': (
            'Internamento. Investigar formas fora do pulmao. '
            'Se for HIV+, coordenar com o TARV - cuidado com as interaccoes.'
        ),
        'exame': 'Baciloscopia (BK) ou GeneXpert',
        'alertas': [
            'Tossir sangue',
            'Perder mais de 10% do peso',
            'Suar muito de noite, a encharcar',
            'Tosse ha mais de 2 semanas sem melhorar'
        ]
    },
    'HIV/SIDA': {
        'leve': (
            'TARV 1a linha: Dolutegravir + Tenofovir + Lamivudina '
            '(um comprimido por dia). Tomar sempre a mesma hora, sem falhar. '
            'CD4 e carga viral aos 6 meses.'
        ),
        'grave': (
            'Tratar primeiro a infeccao oportunista que estiver activa. '
            'Comecar o TARV 2 semanas depois (excepto meningite '
            'criptococica - ai esperar 4 a 6 semanas). Referenciar ao CTA.'
        ),
        'exame': 'Teste rapido HIV + CD4 + carga viral',
        'alertas': [
            'Infeccoes oportunistas a repetir',
            'Perda de peso sem explicacao',
            'Diarreia ha mais de 1 mes',
            'Sapinho na boca que nao desaparece'
        ]
    },
    'Raiva (Mordedura)': {
        'leve': (
            'Lavar a ferida com agua e sabao durante 15 minutos - '
            'essa medida salva vidas. Vacina anti-rabica nos dias 0, 3, 7 e 14. '
            'Nao coser a ferida.'
        ),
        'grave': (
            'Soro anti-rabico + vacina. Nao esperar por resultados. '
            'Se o animal morreu ou fugiu, tratar como alto risco. '
            'Cada hora conta.'
        ),
        'exame': 'Nao esperar confirmacao laboratorial - tratar ja',
        'alertas': [
            'Medo de agua (hidrofobia)',
            'Medo de vento (aerofobia)',
            'Agitacao e desorientacao',
            'Se estes sinais ja apareceram, o prognostico e muito reservado'
        ]
    },
    'Saudavel': {
        'leve': (
            'Hemograma dentro dos valores normais. Orientar prevencao: '
            'rede mosquiteira, agua tratada, desparasitacao regular, '
            'vacinas em dia.'
        ),
        'grave': 'Nao se aplica.',
        'exame': 'Sem necessidade de mais exames',
        'alertas': []
    }
}


# =============================================
# FUNCOES DE DADOS (clientes e empresas)
# =============================================

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
        # cliente ja existe, actualizar e deixar entrar
        clientes[tel_limpo]['nome'] = nome
        clientes[tel_limpo]['municipio'] = municipio
        if email:
            clientes[tel_limpo]['email'] = email
        guardar_clientes(clientes)
        return True, clientes[tel_limpo], "Bem-vindo de volta!"
    
    # novo cliente
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
    return True, cliente, f"Bem-vindo ao HemaSakula, {nome.split()[0]}!"


# =============================================
# FUNCOES DO MODELO ML
# =============================================

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
        ("A cruzar com dados epidemiologicos da zona...", 80),
        ("Quase la, a finalizar...", 100)
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


# =============================================
# CSS
# =============================================

def css_tela_principal():
    """CSS da tela de boas-vindas - branca, limpa, acolhedora"""
    return """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
* { font-family: 'Inter', -apple-system, sans-serif; }
.stApp { background: #FFFFFF !important; }
[data-testid="stSidebar"], header[data-testid="stHeader"],
#MainMenu, footer, .stDeployButton { display: none !important; }
.main .block-container {
    max-width: 520px; margin: 0 auto;
    padding-top: 0 !important; padding-bottom: 2rem !important;
}

/* inputs */
.stTextInput > label, .stSelectbox > label {
    color: #64748B !important; font-size: 0.82rem !important;
    font-weight: 600 !important; letter-spacing: 0.02em !important;
    text-transform: none !important;
}
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: #F8FAFC !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 12px !important;
    color: #0F172A !important;
    padding: 0.85rem 1rem !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #0F172A !important;
    box-shadow: 0 0 0 3px rgba(15,23,42,0.06) !important;
    background: #FFFFFF !important;
}
.stTextInput > div > div > input::placeholder {
    color: #94A3B8 !important;
}

/* botao principal */
.stButton > button {
    background: #0F172A !important; color: #FFFFFF !important;
    border: none !important; border-radius: 12px !important;
    font-weight: 600 !important; font-size: 1rem !important;
    padding: 0.9rem 2rem !important; width: 100% !important;
    transition: all 0.2s ease !important; margin-top: 0.5rem !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: #1E293B !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(15,23,42,0.12) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* alertas */
.stAlert { border-radius: 12px !important; }
</style>"""


def css_painel_cliente():
    """CSS do painel do cliente depois de entrar"""
    return """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', -apple-system, sans-serif; }
.stApp { background-color: #F8FAFC !important; color: #0F172A; }
[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
.main .block-container {
    max-width: 800px; margin: 0 auto;
    padding: 1.5rem 2rem;
}

h1 { color: #0F172A !important; font-weight: 700 !important; font-size: 1.6rem !important; }
h2 {
    color: #1E293B !important; font-weight: 600 !important;
    font-size: 1.15rem !important; margin-top: 1.5rem !important;
    margin-bottom: 0.8rem !important; padding-bottom: 0.5rem !important;
    border-bottom: 1px solid #E2E8F0 !important;
}

/* tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0; background: #F1F5F9; border-radius: 12px; padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #64748B !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 500 !important; font-size: 0.85rem !important;
    padding: 0.6rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important; color: #0F172A !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}

/* botoes */
.stButton > button {
    background: #0F172A !important; color: #FFFFFF !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.88rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #1E293B !important;
}
</style>"""


def css_painel_empresa():
    """CSS do painel da empresa (sistema clinico)"""
    return """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
.stApp { background-color: #F8FAFC !important; color: #0F172A; }
.main .block-container { padding: 2.5rem 4rem; max-width: 1300px; margin: 0 auto; }
h1 { color: #0F172A !important; font-weight: 700 !important; font-size: 2rem !important; letter-spacing: -0.025em !important; margin-bottom: 0.5rem !important; }
h2 { color: #1E293B !important; font-weight: 600 !important; font-size: 1.35rem !important; margin-top: 2.5rem !important; margin-bottom: 1.25rem !important; padding-bottom: 0.75rem !important; border-bottom: 1px solid #E2E8F0 !important; }
h3 { color: #334155 !important; font-weight: 600 !important; font-size: 1.1rem !important; margin-bottom: 1rem !important; }
label, .stSelectbox label, .stNumberInput label, .stCheckbox label { color: #475569 !important; font-weight: 500 !important; font-size: 0.875rem !important; }
[data-testid="stSidebar"] { background-color: #0F172A; border-right: 1px solid #1E293B; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #F1F5F9 !important; border-bottom-color: #1E293B !important; }
[data-testid="stSidebar"] label { color: #CBD5E1 !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #94A3B8 !important; }
[data-testid="stSidebar"] .stSelectbox > div > div, [data-testid="stSidebar"] .stNumberInput input { background-color: #1E293B !important; border: 1px solid #334155 !important; border-radius: 8px !important; color: #F1F5F9 !important; }
[data-testid="stSidebar"] .stNumberInput button { background-color: #334155 !important; border-color: #334155 !important; color: #F1F5F9 !important; }
[data-testid="stSidebar"] .stCheckbox label span { color: #CBD5E1 !important; }
.stTextInput > label { color: #475569 !important; font-size: 0.875rem !important; font-weight: 500 !important; letter-spacing: normal !important; text-transform: none !important; }
.stTextInput > div > div > input, .stNumberInput input { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; color: #0F172A !important; }
.stNumberInput button { background-color: #F1F5F9 !important; border: 1px solid #E2E8F0 !important; color: #475569 !important; }
.stFormSubmitButton > button { background-color: #1E293B !important; color: #FFFFFF !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; font-size: 0.95rem !important; padding: 0.75rem 2.5rem !important; transition: all 0.2s ease !important; }
.stFormSubmitButton > button:hover { background-color: #334155 !important; transform: translateY(-1px) !important; }
[data-testid="stMetric"] { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
[data-testid="stMetric"] label { color: #64748B !important; font-weight: 600 !important; letter-spacing: 0.05em; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #0F172A !important; font-weight: 700 !important; }
.stProgress > div > div { background-color: #1E293B !important; border-radius: 4px; }
.stProgress > div { background-color: #E2E8F0 !important; border-radius: 4px; }
.card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.badge { display: inline-block; padding: 0.35rem 0.85rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.025em; }
.badge-leve { background-color: #F0FDF4; color: #166534; border: 1px solid #DCFCE7; }
.badge-moderado { background-color: #FFFBEB; color: #92400E; border: 1px solid #FEF3C7; }
.badge-grave { background-color: #FEF2F2; color: #991B1B; border: 1px solid #FEE2E2; }
.badge-critico { background-color: #7F1D1D; color: #FFFFFF; }
.status-operacional { background-color: #F0FDF4; border: 1px solid #DCFCE7; border-left: 4px solid #166534; border-radius: 8px; padding: 1rem 1.25rem; margin: 1.5rem 0; }
.status-operacional p { margin: 0; color: #166534; font-weight: 600; }
.aviso-institucional { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #475569; border-radius: 8px; padding: 1.25rem; margin: 1.5rem 0; }
.aviso-institucional p { margin: 0; color: #334155; font-size: 0.9rem; line-height: 1.6; }
.serie-vermelha-header { color: #B91C1C !important; font-weight: 700 !important; font-size: 1rem !important; border-bottom: 2px solid #B91C1C; padding-bottom: 0.5rem; margin-bottom: 1.5rem !important; }
.serie-branca-header { color: #475569 !important; font-weight: 700 !important; font-size: 1rem !important; border-bottom: 2px solid #475569; padding-bottom: 0.5rem; margin-bottom: 1.5rem !important; }
.serie-plaquetas-header { color: #4338CA !important; font-weight: 700 !important; font-size: 1rem !important; border-bottom: 2px solid #4338CA; padding-bottom: 0.5rem; margin-bottom: 1.5rem !important; }
hr { border: none; height: 1px; background-color: #E2E8F0; margin: 2rem 0; }
.footer { text-align: center; padding: 2rem 0; margin-top: 3rem; border-top: 1px solid #E2E8F0; color: #94A3B8; font-size: 0.85rem; }
</style>"""


# =============================================
# TELA 1 - BOAS-VINDAS (tela principal)
# =============================================

def tela_boas_vindas():
    """
    Tela principal - acolhedora, focada no cliente
    Pergunta simples: nome, municipio, telefone, email (opcional)
    Link discreto para empresas
    """
    st.markdown(css_tela_principal(), unsafe_allow_html=True)

    # saudacao por hora do dia
    hora = datetime.now().hour
    if hora < 12:
        saudacao = "Bom dia"
        emoji = "â˜€ï¸"
    elif hora < 18:
        saudacao = "Boa tarde"
        emoji = "ðŸŒ¤ï¸"
    else:
        saudacao = "Boa noite"
        emoji = "ðŸŒ™"

    st.markdown("<div style='height: 4vh;'></div>", unsafe_allow_html=True)

    # logo e marca
    st.markdown('''
    <div style="text-align:center;margin-bottom:2rem;">
        <div style="width:80px;height:80px;background:#0F172A;border-radius:20px;
                    display:inline-flex;align-items:center;justify-content:center;
                    font-size:1.7rem;font-weight:800;color:#FFFFFF;margin-bottom:1.2rem;
                    box-shadow:0 8px 24px rgba(15,23,42,0.12);">
            HS
        </div>
        <div style="font-size:2.2rem;font-weight:800;color:#0F172A;letter-spacing:-0.03em;
                    line-height:1.1;">
            HemaSakula
        </div>
        <div style="font-size:0.82rem;color:#94A3B8;letter-spacing:0.12em;
                    text-transform:uppercase;margin-top:0.5rem;font-weight:500;">
            Angola a Cuidar dos Seus
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # separador suave
    st.markdown('''
    <div style="height:1px;background:linear-gradient(90deg,transparent,#E2E8F0,transparent);
                margin:0.5rem 0 2rem 0;"></div>
    ''', unsafe_allow_html=True)

    # saudacao calorosa
    st.markdown(f'''
    <div style="text-align:center;margin-bottom:2rem;">
        <div style="font-size:1.5rem;font-weight:600;color:#0F172A;margin-bottom:0.5rem;">
            {saudacao}! {emoji}
        </div>
        <div style="font-size:1rem;color:#64748B;line-height:1.6;max-width:380px;margin:0 auto;">
            Encontra clinicas e hospitais perto de ti.
            Cuida da tua saude com quem te entende.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # formulario simples
    st.markdown('''
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:16px;
                padding:1.8rem;margin-bottom:1.5rem;">
        <div style="font-size:0.95rem;font-weight:600;color:#0F172A;margin-bottom:1.2rem;">
            Diz-nos um pouco sobre ti
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # usar container para os campos ficarem dentro do "card" visual
    nome = st.text_input(
        "Como queres que te chamemos?",
        placeholder="Ex: Maria, Joao, Kika...",
        key="nome_cliente"
    )

    municipio = st.selectbox(
        "Onde vives?",
        MUNICIPIOS_LISTA,
        key="municipio_cliente"
    )

    telefone = st.text_input(
        "O teu numero de telefone",
        placeholder="Ex: 923 456 789",
        key="telefone_cliente"
    )

    email = st.text_input(
        "Email (se tiveres, nao e obrigatorio)",
        placeholder="exemplo@email.com",
        key="email_cliente"
    )

    # botao principal
    if st.button("Comecar", key="btn_comecar", use_container_width=True):
        # validacoes simples
        if not nome or not nome.strip():
            st.error("Precisamos do teu nome para te chamar.")
        elif not telefone or len(telefone.replace(' ', '').replace('-', '')) < 9:
            st.error("Mete o teu numero de telefone. Precisamos dele para te contactar.")
        else:
            # registar e entrar
            sucesso, dados, msg = registar_cliente(
                nome.strip(), telefone.strip(), municipio, email.strip()
            )
            if sucesso:
                st.session_state['ecra'] = 'cliente'
                st.session_state['cliente'] = dados
                st.success(msg)
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Algo correu mal. Tenta de novo.")

    # espaco antes do link de empresa
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)

    # separador
    st.markdown('''
    <div style="height:1px;background:linear-gradient(90deg,transparent,#E2E8F0,transparent);
                margin:0 0 1.5rem 0;"></div>
    ''', unsafe_allow_html=True)

    # link discreto para empresas
    st.markdown('''
    <div style="text-align:center;">
        <div style="color:#CBD5E1;font-size:0.78rem;margin-bottom:0.5rem;">
            Es uma clinica ou hospital?
        </div>
    </div>
    ''', unsafe_allow_html=True)

    col_emp1, col_emp2, col_emp3 = st.columns([1, 2, 1])
    with col_emp2:
        if st.button("Entrar como Empresa", key="btn_empresa", use_container_width=True):
            st.session_state['ecra'] = 'login_empresa'
            st.rerun()

    # rodape
    st.markdown('''
    <div style="text-align:center;margin-top:2.5rem;color:#CBD5E1;font-size:0.72rem;">
        HemaSakula &middot; Angola 2025
    </div>
    ''', unsafe_allow_html=True)


# =============================================
# TELA 2 - LOGIN DA EMPRESA (discreto)
# =============================================

def tela_login_empresa():
    """Login da empresa - simples, discreto"""
    st.markdown(css_tela_principal(), unsafe_allow_html=True)

    st.markdown("<div style='height: 6vh;'></div>", unsafe_allow_html=True)

    # logo pequeno
    st.markdown('''
    <div style="text-align:center;margin-bottom:2rem;">
        <div style="width:56px;height:56px;background:#0F172A;border-radius:14px;
                    display:inline-flex;align-items:center;justify-content:center;
                    font-size:1.2rem;font-weight:800;color:#FFFFFF;margin-bottom:1rem;">
            HS
        </div>
        <div style="font-size:1.3rem;font-weight:700;color:#0F172A;">
            Acesso Profissional
        </div>
        <div style="font-size:0.82rem;color:#94A3B8;margin-top:0.3rem;">
            Para clinicas e hospitais parceiros
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div style="height:1px;background:linear-gradient(90deg,transparent,#E2E8F0,transparent);
                margin:0 0 2rem 0;"></div>
    ''', unsafe_allow_html=True)

    usuario = st.text_input(
        "Utilizador",
        placeholder="O teu utilizador",
        key="emp_usuario"
    )

    senha = st.text_input(
        "Palavra-passe",
        type="password",
        placeholder="A tua palavra-passe",
        key="emp_senha"
    )

    if st.button("Entrar", key="btn_entrar_empresa", use_container_width=True):
        if not usuario or not senha:
            st.error("Preenche os dois campos.")
        else:
            # tentar autenticar via secrets
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
                st.success("Bem-vindo!")
                time.sleep(0.3)
                st.rerun()
            else:
                st.error("Credenciais incorrectas. Verifica e tenta de novo.")

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    # voltar para tela principal
    col_v1, col_v2, col_v3 = st.columns([1, 2, 1])
    with col_v2:
        if st.button("Voltar", key="btn_voltar_login", use_container_width=True):
            st.session_state['ecra'] = 'inicio'
            st.rerun()

    st.markdown('''
    <div style="text-align:center;margin-top:2rem;color:#CBD5E1;font-size:0.72rem;">
        Acesso restrito a profissionais autorizados
    </div>
    ''', unsafe_allow_html=True)


# =============================================
# TELA 3 - PAINEL DO CLIENTE
# =============================================

def tela_painel_cliente():
    """Painel do cliente - depois de se identificar"""
    st.markdown(css_painel_cliente(), unsafe_allow_html=True)

    cliente = st.session_state.get('cliente', {})
    nome = cliente.get('nome', 'Amigo')
    municipio = cliente.get('municipio', 'Luanda')
    primeiro_nome = nome.split()[0] if nome else 'Amigo'

    hora = datetime.now().hour
    if hora < 12:
        saudacao = "Bom dia"
    elif hora < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    # header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f'''
        <div style="margin-bottom:0.5rem;">
            <span style="font-size:1.4rem;font-weight:700;color:#0F172A;">
                {saudacao}, {primeiro_nome}!
            </span>
        </div>
        <div style="color:#64748B;font-size:0.88rem;">
            O que precisas hoje?
        </div>
        ''', unsafe_allow_html=True)
    with col_h2:
        if st.button("Sair", key="btn_sair_cliente"):
            for k in ['ecra', 'cliente']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    # tabs
    tab_clinicas, tab_alertas, tab_sobre = st.tabs([
        "Clinicas perto de mim", "Alertas de saude", "Sobre"
    ])

    # === TAB CLINICAS ===
    with tab_clinicas:
        st.markdown(f'''
        <div style="color:#64748B;font-size:0.88rem;margin-bottom:1rem;">
            Clinicas e hospitais perto de <strong>{municipio}</strong>
        </div>
        ''', unsafe_allow_html=True)

        # mostrar hospital de referencia do municipio
        info_mun = MUNICIPIOS_INFO.get(municipio, {})
        hospital_ref = info_mun.get('hospital', 'Centro de Saude')

        st.markdown(f'''
        <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid #0F172A;
                    border-radius:12px;padding:1.2rem;margin-bottom:1rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="color:#94A3B8;font-size:0.72rem;text-transform:uppercase;
                        letter-spacing:0.05em;margin-bottom:0.4rem;">
                Hospital de referencia
            </div>
            <div style="font-weight:600;color:#0F172A;font-size:1.05rem;">
                {hospital_ref}
            </div>
            <div style="color:#64748B;font-size:0.82rem;margin-top:0.3rem;">
                {municipio} &middot; {info_mun.get('provincia', 'Luanda')}
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # lista de parceiros (simplificada)
        parceiros_exemplo = [
            {
                'nome': 'Hospital Josina Machel',
                'tipo': 'Hospital Central',
                'local': 'Ingombota',
                'horario': '24 horas',
                'cor': '#1E40AF'
            },
            {
                'nome': 'Hospital Americo Boavida',
                'tipo': 'Hospital Central',
                'local': 'Maianga',
                'horario': '24 horas',
                'cor': '#047857'
            },
            {
                'nome': 'Hospital Pediatrico David Bernardino',
                'tipo': 'Hospital Pediatrico',
                'local': 'Maianga',
                'horario': '24 horas',
                'cor': '#DC2626'
            },
            {
                'nome': 'Clinica Sagrada Esperanca',
                'tipo': 'Clinica Privada',
                'local': 'Talatona',
                'horario': '24 horas',
                'cor': '#0369A1'
            },
            {
                'nome': 'Clinica Multiperfil',
                'tipo': 'Clinica Privada',
                'local': 'Talatona',
                'horario': '07h-20h',
                'cor': '#1D4ED8'
            },
            {
                'nome': 'Hospital Geral de Viana',
                'tipo': 'Hospital Geral',
                'local': 'Viana',
                'horario': '24 horas',
                'cor': '#7C3AED'
            }
        ]

        for p in parceiros_exemplo:
            badge_tipo = 'Publico' if 'Hospital' in p['tipo'] and 'Clinica' not in p['tipo'] else 'Privado'
            badge_cor = '#DBEAFE;color:#1E40AF' if badge_tipo == 'Publico' else '#FEF3C7;color:#92400E'

            st.markdown(f'''
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;
                        padding:1rem 1.2rem;margin-bottom:0.6rem;
                        box-shadow:0 1px 2px rgba(0,0,0,0.03);">
                <div style="display:flex;align-items:center;gap:0.7rem;">
                    <div style="width:36px;height:36px;background:{p['cor']};
                                border-radius:8px;display:flex;align-items:center;
                                justify-content:center;color:white;font-weight:700;
                                font-size:0.7rem;flex-shrink:0;">
                        {p['nome'][:2].upper()}
                    </div>
                    <div style="flex:1;">
                        <div style="font-weight:600;color:#0F172A;font-size:0.92rem;">
                            {p['nome']}
                        </div>
                        <div style="color:#64748B;font-size:0.78rem;margin-top:0.15rem;">
                            {p['local']} &middot; {p['horario']}
                        </div>
                    </div>
                    <div>
                        <span style="background:{badge_cor};padding:0.2rem 0.5rem;
                                     border-radius:5px;font-size:0.68rem;font-weight:600;">
                            {badge_tipo}
                        </span>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    # === TAB ALERTAS ===
    with tab_alertas:
        mes_actual = datetime.now().month
        meses_nome = [
            '', 'Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        mes_nome = meses_nome[mes_actual]

        risco_mun = info_mun.get('risco', 'Medio')
        cor_risco = {
            'Baixo': '#059669', 'Medio': '#D97706',
            'Alto': '#DC2626', 'Muito Alto': '#7F1D1D'
        }

        st.markdown(f'''
        <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;
                    padding:1.2rem;margin-bottom:1rem;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="color:#94A3B8;font-size:0.72rem;text-transform:uppercase;
                                letter-spacing:0.05em;">Risco na tua zona</div>
                    <div style="font-weight:600;color:#0F172A;font-size:1rem;margin-top:0.3rem;">
                        {municipio}
                    </div>
                </div>
                <div style="background:{cor_risco.get(risco_mun, '#64748B')};color:white;
                            padding:0.3rem 0.8rem;border-radius:6px;font-size:0.78rem;
                            font-weight:600;">
                    {risco_mun}
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # alertas sazonais
        alertas_mes = {
            1: "Epoca de chuvas. Cuidado com a colera e a malaria. Bebe sempre agua tratada.",
            2: "Chuvas fortes. Evita agua parada perto de casa. Dorme com rede mosquiteira.",
            3: "Pico de malaria. Se tiveres febre, vai ao centro de saude mais proximo.",
            4: "Ainda ha muitos mosquitos. Usa repelente e rede mosquiteira.",
            5: "As chuvas estao a acabar. Boa altura para desparasitar.",
            6: "Cacimbo. Agasalha-te bem. Quem tem drepanocitose: cuidado com o frio.",
            7: "Mes mais frio. Protege as criancas e os idosos.",
            8: "Se tens tosse ha mais de 2 semanas, faz exame no centro de saude.",
            9: "Boa altura para um check-up e desparasitacao.",
            10: "As chuvas voltam. Verifica a rede mosquiteira e trata a agua.",
            11: "Chuvas. Lembra-te da desparasitacao.",
            12: "Prepara-te para a epoca chuvosa."
        }

        alerta_txt = alertas_mes.get(mes_actual, "Cuida da tua saude!")

        st.markdown(f'''
        <div style="background:#FFFBEB;border:1px solid #FEF3C7;border-left:4px solid #F59E0B;
                    border-radius:10px;padding:1.2rem;margin-bottom:1rem;">
            <div style="font-weight:600;color:#0F172A;margin-bottom:0.4rem;">
                Alerta para {mes_nome}
            </div>
            <div style="color:#475569;font-size:0.88rem;line-height:1.6;">
                {alerta_txt}
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # dicas gerais
        dicas = [
            ("Rede mosquiteira", "Dorme sempre debaixo de uma rede mosquiteira, mesmo no cacimbo."),
            ("Agua tratada", "Ferve ou trata a agua antes de beber. Protege contra colera e tifoide."),
            ("Desparasitacao", "Toma Albendazol de 6 em 6 meses. Para adultos e criancas acima de 2 anos."),
            ("Vacinas", "Verifica se as vacinas das criancas estao em dia."),
            ("Drepanocitose", "Se ha casos na familia, faz o teste antes de ter filhos.")
        ]

        for titulo, texto in dicas:
            st.markdown(f'''
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;
                        padding:1rem;margin-bottom:0.5rem;">
                <div style="font-weight:600;color:#0F172A;font-size:0.88rem;">{titulo}</div>
                <div style="color:#64748B;font-size:0.82rem;margin-top:0.2rem;">{texto}</div>
            </div>
            ''', unsafe_allow_html=True)

    # === TAB SOBRE ===
    with tab_sobre:
        st.markdown('''
        <div style="text-align:center;padding:2rem 0;">
            <div style="width:64px;height:64px;background:#0F172A;border-radius:16px;
                        display:inline-flex;align-items:center;justify-content:center;
                        font-size:1.3rem;font-weight:800;color:#FFFFFF;margin-bottom:1rem;">
                HS
            </div>
            <div style="font-size:1.5rem;font-weight:700;color:#0F172A;margin-bottom:0.3rem;">
                HemaSakula
            </div>
            <div style="color:#64748B;font-size:0.88rem;margin-bottom:1.5rem;">
                Angola a Cuidar dos Seus
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;
                    padding:1.5rem;line-height:1.8;color:#475569;font-size:0.9rem;">
            <strong style="color:#0F172A;">O que e o HemaSakula?</strong><br><br>
            O HemaSakula e uma plataforma angolana que te ajuda a encontrar
            clinicas e hospitais perto de ti. Alem disso, as clinicas parceiras
            usam o nosso sistema inteligente para analisar exames de sangue
            e dar melhores diagnosticos.<br><br>
            <strong style="color:#0F172A;">Para ti (paciente):</strong><br>
            &bull; Encontra clinicas e hospitais perto da tua zona<br>
            &bull; Recebe alertas de saude para o teu municipio<br>
            &bull; Sabe quando e altura de desparasitar, vacinar, fazer check-up<br><br>
            <strong style="color:#0F172A;">Para clinicas e hospitais:</strong><br>
            &bull; Sistema inteligente de apoio a decisao clinica<br>
            &bull; Analise de hemogramas com inteligencia artificial<br>
            &bull; Dados epidemiologicos por municipio e estacao<br><br>
            <em>Feito com dedicacao para Angola.</em>
        </div>
        ''', unsafe_allow_html=True)

    # footer
    st.markdown('''
    <div style="text-align:center;padding:1.5rem 0;margin-top:2rem;
                border-top:1px solid #E2E8F0;color:#94A3B8;font-size:0.78rem;">
        <strong>HemaSakula</strong> &middot; Angola a Cuidar dos Seus
    </div>
    ''', unsafe_allow_html=True)


# =============================================
# TELA 4 - PAINEL DA EMPRESA (sistema clinico)
# =============================================

def tela_painel_empresa():
    """Painel da empresa - sistema de apoio a decisao clinica"""
    st.markdown(css_painel_empresa(), unsafe_allow_html=True)

    usuario = st.session_state.get('empresa_usuario', 'Empresa')

    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.title("HemaSakula")
        st.markdown(
            f'<p style="color:#64748B;font-size:1rem;margin-top:-0.5rem;'
            f'font-style:italic;">{SLOGAN}</p>',
            unsafe_allow_html=True
        )
    with col_header2:
        st.markdown(
            f'<div style="text-align:right;padding-top:0.8rem;">'
            f'<span style="color:#94A3B8;font-size:0.85rem;">'
            f'{usuario.capitalize()} | {datetime.now().strftime("%d/%m/%Y")}'
            f'</span></div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="aviso-institucional"><p><strong>Atencao:</strong> '
        'Este sistema serve de apoio a decisao clinica. Nao substitui a '
        'avaliacao presencial nem o julgamento do profissional de saude.'
        '</p></div>',
        unsafe_allow_html=True
    )

    modelo, encoders, features = carregar_modelo()

    if modelo is None:
        st.error("Modelo nao encontrado. Executa primeiro: python modelo_ml.py")
        return

    st.markdown(
        '<div class="status-operacional">'
        '<p>Sistema operacional - modelo carregado com sucesso</p></div>',
        unsafe_allow_html=True
    )

    # sidebar com dados do paciente
    with st.sidebar:
        st.markdown(f'''
        <div style="text-align:center;padding:0.8rem 0 1rem 0;">
            <div style="width:48px;height:48px;background:#1E293B;border-radius:12px;
                        display:inline-flex;align-items:center;justify-content:center;
                        font-size:1rem;font-weight:700;color:#FFFFFF;margin-bottom:0.6rem;">
                HS
            </div>
            <div style="color:#F1F5F9;font-weight:600;font-size:0.9rem;">
                {usuario.capitalize()}
            </div>
            <div style="color:#475569;font-size:0.72rem;margin-top:0.15rem;">
                Conta Profissional
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("---")

        st.header("Dados do Paciente")

        st.subheader("Identificacao")
        faixa_etaria = st.selectbox("Faixa etaria", FAIXAS_ETARIAS, index=5)
        sexo = st.selectbox("Sexo biologico", SEXOS)

        gestante = False
        if sexo == 'Feminino' and ('Adulto' in faixa_etaria or 'Adolescente' in faixa_etaria):
            gestante = st.checkbox("Gravida")

        peso = st.number_input("Peso (kg)", 1.0, 200.0, 65.0, 0.5)

        st.subheader("Localizacao")
        municipio = st.selectbox("Municipio", list(MUNICIPIOS_INFO.keys()))
        info_mun = MUNICIPIOS_INFO[municipio]
        provincia = info_mun['provincia']
        st.markdown(f"**Provincia:** {provincia}")
        st.markdown(f"**Risco epidemiologico:** {info_mun['risco']}")

        st.subheader("Data da colheita")
        mes = st.selectbox("Mes", MESES, index=datetime.now().month - 1)
        estacao = ESTACOES_POR_MES[mes]
        st.markdown(f"**Estacao:** {estacao}")

        st.subheader("Antecedentes")
        status_genetico = st.selectbox("Hemoglobina (genetica)", STATUS_GENETICO)
        mordedura = st.checkbox("Mordedura animal recente")

        st.markdown("---")

        if st.button("Sair", key="btn_sair_empresa", use_container_width=True):
            for k in ['ecra', 'empresa_usuario']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    # hemograma
    st.header("Hemograma")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<p class="serie-vermelha-header">Serie Vermelha</p>', unsafe_allow_html=True)
        hemoglobina = st.number_input("Hemoglobina (g/dL)", 3.0, 22.0, 12.5, 0.1)
        hematocrito = st.number_input("Hematocrito (%)", 10.0, 70.0, 38.0, 0.5)
        hemacias = st.number_input("Eritrocitos (x10^6/uL)", 2.0, 7.0, 4.5, 0.1)
        vcm = st.number_input("VCM (fL)", 50.0, 120.0, 88.0, 1.0)
        hcm = st.number_input("HCM (pg)", 15.0, 40.0, 29.0, 0.5)
        chcm = st.number_input("CHCM (g/dL)", 28.0, 40.0, 33.5, 0.5)
        rdw = st.number_input("RDW (%)", 10.0, 25.0, 13.5, 0.1)

    with col2:
        st.markdown('<p class="serie-branca-header">Serie Branca</p>', unsafe_allow_html=True)
        leucocitos = st.number_input("Leucocitos (/mm3)", 500, 50000, 7500, 100)
        neutrofilos = st.number_input("Neutrofilos (%)", 10.0, 90.0, 58.0, 1.0)
        linfocitos = st.number_input("Linfocitos (%)", 5.0, 70.0, 32.0, 1.0)
        monocitos = st.number_input("Monocitos (%)", 0.0, 20.0, 6.0, 0.5)
        eosinofilos = st.number_input("Eosinofilos (%)", 0.0, 25.0, 3.0, 0.5)
        basofilos = st.number_input("Basofilos (%)", 0.0, 3.0, 0.5, 0.1)

        valido, soma = validar_leucograma(neutrofilos, linfocitos, monocitos, eosinofilos, basofilos)
        if not valido:
            st.warning(f"O diferencial soma {soma:.1f}% - o esperado e proximo de 100%.")

    with col3:
        st.markdown('<p class="serie-plaquetas-header">Plaquetas e Outros</p>', unsafe_allow_html=True)
        plaquetas = st.number_input("Plaquetas (/mm3)", 5000, 1000000, 250000, 5000)
        vpm = st.number_input("VPM (fL)", 5.0, 15.0, 9.5, 0.5)
        reticulocitos = st.number_input("Reticulocitos (%)", 0.2, 15.0, 1.2, 0.1)

    st.markdown("---")

    with st.form(key="form_analise"):
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit = st.form_submit_button("Analisar Hemograma", use_container_width=True)

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
                'basofilos': basofilos, 'plaquetas': plaquetas,
                'vpm': vpm, 'reticulocitos': reticulocitos
            }

            gravidade, resultados, erro = processar_analise(
                modelo, encoders, features, dados
            )

            if erro:
                st.error(f"Erro no processamento: {erro}")
                return

            if not resultados:
                st.error("Nao consegui gerar resultados. Confere os dados.")
                return

            diag_principal = resultados[0][0]

            st.header("Resultados")

            col_r1, col_r2 = st.columns(2)

            with col_r1:
                classe = obter_classe_gravidade(gravidade)
                st.markdown(
                    f'<div class="card"><div style="color:#64748B;font-size:0.78rem;'
                    f'text-transform:uppercase;letter-spacing:0.05em;">'
                    f'Gravidade</div><div style="margin-top:0.75rem;">'
                    f'<span class="badge {classe}" '
                    f'style="font-size:0.9rem;padding:0.5rem 1rem;">'
                    f'{gravidade}</span></div></div>',
                    unsafe_allow_html=True
                )

            with col_r2:
                st.markdown(
                    f'<div class="card"><div style="color:#64748B;font-size:0.78rem;'
                    f'text-transform:uppercase;letter-spacing:0.05em;">'
                    f'Referenciar para</div><div style="margin-top:0.75rem;'
                    f'font-weight:600;color:#0F172A;">{info_mun["hospital"]}'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

            st.subheader("Hipoteses diagnosticas")

            for i, (diag, prob) in enumerate(resultados[:3]):
                if i == 0:
                    st.markdown(
                        f'<div class="card" style="border-left:4px solid #1E293B;">'
                        f'<div style="display:flex;justify-content:space-between;'
                        f'align-items:center;"><span style="font-size:1.1rem;'
                        f'font-weight:600;color:#0F172A;">1. {diag}</span>'
                        f'<span style="background:#1E293B;color:white;'
                        f'padding:0.4rem 1rem;border-radius:6px;font-weight:600;">'
                        f'{prob:.1f}%</span></div></div>',
                        unsafe_allow_html=True
                    )
                    st.progress(prob / 100)
                else:
                    st.markdown(
                        f'<div class="card" style="padding:1rem 1.25rem;">'
                        f'<div style="display:flex;justify-content:space-between;'
                        f'align-items:center;"><span style="color:#334155;'
                        f'font-weight:500;">{i+1}. {diag}</span>'
                        f'<span style="color:#64748B;font-weight:600;">'
                        f'{prob:.1f}%</span></div></div>',
                        unsafe_allow_html=True
                    )

            st.subheader("O que fazer agora")

            if diag_principal in CONDUTAS:
                cond = CONDUTAS[diag_principal]
                if gravidade in ["GRAVE", "CRITICO"]:
                    st.error(f"**Caso grave:** {cond['grave']}")
                else:
                    st.info(f"**Conduta:** {cond['leve']}")

                st.markdown(
                    f'<div class="card"><strong>Exame pra confirmar:</strong> '
                    f'{cond["exame"]}</div>',
                    unsafe_allow_html=True
                )

                if cond['alertas']:
                    with st.expander("Sinais de alarme - referenciar ja"):
                        for a in cond['alertas']:
                            st.markdown(f"- {a}")

            st.subheader("Interpretacao do hemograma")

            col_l1, col_l2 = st.columns(2)

            with col_l1:
                _, hb_l = classificar_valor(hemoglobina, 11.5, 16.5)
                st.metric("Hemoglobina", f"{hemoglobina} g/dL", hb_l)
                _, plt_l = classificar_valor(plaquetas, 140000, 400000)
                st.metric("Plaquetas", f"{formatar_numero(plaquetas)}/mm3", plt_l)
                _, leu_l = classificar_valor(leucocitos, 4000, 10000)
                st.metric("Leucocitos", f"{formatar_numero(leucocitos)}/mm3", leu_l)

            with col_l2:
                _, vcm_l = classificar_valor(vcm, 80, 98)
                st.metric("VCM", f"{vcm} fL", vcm_l)
                _, eos_l = classificar_valor(eosinofilos, 1, 5)
                st.metric("Eosinofilos", f"{eosinofilos}%", eos_l)
                _, ret_l = classificar_valor(reticulocitos, 0.5, 2.5)
                st.metric("Reticulocitos", f"{reticulocitos}%", ret_l)

            if status_genetico in ['Traco falciforme (AS)', 'Drepanocitose (SS)']:
                st.warning(
                    f"**Hemoglobinopatia: {status_genetico}.** "
                    f"Seguimento no IHL ou centro de drepanocitose. "
                    f"Acido folico 5 mg/dia, beber muita agua, "
                    f"evitar frio e tudo que possa provocar crise."
                )

            if mordedura:
                st.error(
                    "**Mordedura animal - risco rabico!** "
                    "Lavar a ferida com agua e sabao durante 15 minutos. "
                    "Iniciar profilaxia anti-rabica sem esperar resultados. "
                    "Cada hora conta."
                )

    st.markdown(
        f'<div class="footer"><strong>HemaSakula</strong><br>{SLOGAN}<br>'
        f'<span style="font-size:0.75rem;">Feito com dedicacao pra Angola | '
        f'v3.0</span></div>',
        unsafe_allow_html=True
    )


# =============================================
# MAIN - NAVEGACAO POR ECRAS
# =============================================

def main():
    # determinar ecra actual
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
