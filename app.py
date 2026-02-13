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
FICHEIRO_MENSAGENS = 'mensagens_chat.json'
FICHEIRO_ESTADO = 'conversas_estado.json'
FICHEIRO_DIGITANDO = 'digitando_estado.json'

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
        'leve': 'Coartem (Artemeter + Lumefantrina): 4 comprimidos de 12/12h durante 3 dias. Tomar sempre com comida, de preferencia com gordura para absorver melhor. Paracetamol para baixar a febre.',
        'grave': 'Artesunato EV 2,4 mg/kg as 0h, 12h e 24h, depois 1x/dia ate o doente aguentar via oral. Controlar Hb no dia 7 e 14. Se a parasitemia nao baixar em 24h, reavaliar a dose.',
        'exame': 'Gota espessa ou teste rapido (TDR)',
        'alertas': ['Convulsoes', 'Prostracao', 'Vomitos que nao param', 'Urina escura', 'Falta de ar', 'Amarelao nos olhos', 'Confusao ou perda de consciencia']
    },
    'Dengue': {
        'leve': 'Hidratar bem por via oral (60-80 mL/kg/dia). Paracetamol para febre. Nada de ibuprofeno nem aspirina.',
        'grave': 'Soro EV e monitorizar o hematocrito de 2 em 2 horas. Se o Ht subir mais de 20%, aumentar o ritmo da hidratacao.',
        'exame': 'NS1 (fase inicial) ou IgM/IgG (a partir do 5. dia)',
        'alertas': ['Dor de barriga forte', 'Vomitos sem parar', 'Sangramento na gengiva ou pelo nariz', 'Crianca mole demais']
    },
    'Drepanocitose (SS)': {
        'leve': 'Acido folico 5 mg/dia. Beber muita agua. Evitar frio e esforco fisico a mais. Seguimento regular no IHL.',
        'grave': 'Crise vaso-oclusiva: analgesia escalonada (tramadol ou morfina) + soro EV + oxigenio se SpO2 menor que 95%. Referenciar ao IHL com urgencia.',
        'exame': 'Electroforese de hemoglobina',
        'alertas': ['Febre', 'Dor no peito', 'Priapismo', 'Sinais de AVC']
    },
    'Anemia Ferropriva': {
        'leve': 'Sulfato ferroso durante 3 a 6 meses. Tomar em jejum com sumo de limao. Avisar que as fezes ficam escuras.',
        'grave': 'Se a Hb estiver abaixo de 5 g/dL, pensar em transfusao. Investigar a causa.',
        'exame': 'Ferritina serica',
        'alertas': ['Falta de ar mesmo parado', 'Coracao a bater muito rapido', 'Palidez intensa']
    },
    'Colera': {
        'leve': 'SRO conforme protocolo da OMS. Preparar 1 saqueta em 1 litro de agua tratada. Dar aos poucos.',
        'grave': 'Ringer Lactato EV em bolus ate estabilizar. Azitromicina 1 g dose unica. Notificacao obrigatoria.',
        'exame': 'Coprocultura',
        'alertas': ['Olhos fundos, boca seca', 'Sinal da prega', 'Crianca que ja nao chora com lagrimas']
    },
    'Febre Tifoide': {
        'leve': 'Ciprofloxacina 500 mg de 12/12h durante 7 a 14 dias. Em criancas, melhor usar azitromicina.',
        'grave': 'Ceftriaxona EV 2 g/dia + internamento. Ficar atento a sinais de perfuracao intestinal.',
        'exame': 'Hemocultura ou coprocultura',
        'alertas': ['Barriga dura', 'Confusao mental', 'Sangue nas fezes']
    },
    'Parasitose Intestinal': {
        'leve': 'Albendazol 400 mg dose unica (acima de 2 anos). Repetir de 6 em 6 meses.',
        'grave': 'Albendazol 400 mg durante 3 dias + sulfato ferroso se tiver anemia.',
        'exame': 'Exame parasitologico de fezes (3 amostras)',
        'alertas': ['Barriga muito inchada', 'Desnutricao grave']
    },
    'Tuberculose': {
        'leve': 'Esquema DOTS: fase intensiva com RHZE durante 2 meses, depois RH por mais 4 meses.',
        'grave': 'Internamento. Investigar formas fora do pulmao. Se for HIV+, coordenar com o TARV.',
        'exame': 'Baciloscopia (BK) ou GeneXpert',
        'alertas': ['Tossir sangue', 'Perder mais de 10% do peso', 'Suar muito de noite', 'Tosse ha mais de 2 semanas']
    },
    'HIV/SIDA': {
        'leve': 'TARV 1. linha: Dolutegravir + Tenofovir + Lamivudina (um comprimido por dia). CD4 e carga viral aos 6 meses.',
        'grave': 'Tratar primeiro a infeccao oportunista. Comecar o TARV 2 semanas depois. Referenciar ao CTA.',
        'exame': 'Teste rapido HIV + CD4 + carga viral',
        'alertas': ['Infeccoes oportunistas a repetir', 'Perda de peso', 'Diarreia ha mais de 1 mes', 'Sapinho na boca']
    },
    'Raiva (Mordedura)': {
        'leve': 'Lavar a ferida com agua e sabao durante 15 minutos. Vacina anti-rabica nos dias 0, 3, 7 e 14. Nao coser a ferida.',
        'grave': 'Soro anti-rabico + vacina. Nao esperar por resultados. Cada hora conta.',
        'exame': 'Nao esperar confirmacao laboratorial',
        'alertas': ['Medo de agua', 'Medo de vento', 'Agitacao e desorientacao']
    },
    'Saudavel': {
        'leve': 'Hemograma dentro dos valores normais. Orientar prevencao: rede mosquiteira, agua tratada, desparasitacao regular, vacinas em dia.',
        'grave': 'Nao se aplica.',
        'exame': 'Sem necessidade de mais exames',
        'alertas': []
    }
}


def carregar_json(ficheiro):
    if os.path.exists(ficheiro):
        try:
            with open(ficheiro, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def guardar_json(ficheiro, dados):
    with open(ficheiro, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_clientes():
    return carregar_json(FICHEIRO_CLIENTES)


def guardar_clientes(dados):
    guardar_json(FICHEIRO_CLIENTES, dados)


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


def carregar_mensagens():
    return carregar_json(FICHEIRO_MENSAGENS)


def guardar_mensagens(dados):
    guardar_json(FICHEIRO_MENSAGENS, dados)


def carregar_estados():
    return carregar_json(FICHEIRO_ESTADO)


def guardar_estados(dados):
    guardar_json(FICHEIRO_ESTADO, dados)


def carregar_digitando():
    return carregar_json(FICHEIRO_DIGITANDO)


def guardar_digitando(dados):
    guardar_json(FICHEIRO_DIGITANDO, dados)


def marcar_digitando(telefone, quem, ativo):
    dados = carregar_digitando()
    chave = telefone + '___' + quem
    if ativo:
        dados[chave] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        if chave in dados:
            del dados[chave]
    guardar_digitando(dados)


def verificar_digitando(telefone, quem):
    dados = carregar_digitando()
    chave = telefone + '___' + quem
    if chave not in dados:
        return False
    try:
        momento = datetime.strptime(dados[chave], '%Y-%m-%d %H:%M:%S')
        diferenca = (datetime.now() - momento).total_seconds()
        if diferenca > 10:
            del dados[chave]
            guardar_digitando(dados)
            return False
        return True
    except (ValueError, KeyError):
        return False


def obter_estado_conversa(telefone):
    estados = carregar_estados()
    return estados.get(telefone, {
        'status': 'sem_contacto',
        'atendido_por': '',
        'hora_atendimento': ''
    })


def definir_estado_conversa(telefone, status, atendido_por=''):
    estados = carregar_estados()
    estados[telefone] = {
        'status': status,
        'atendido_por': atendido_por,
        'hora_atendimento': datetime.now().strftime('%H:%M') if status == 'atendido' else ''
    }
    guardar_estados(estados)


def obter_conversa(telefone_cliente):
    mensagens = carregar_mensagens()
    return mensagens.get(telefone_cliente, [])


def enviar_mensagem_cliente(telefone_cliente, nome_cliente, texto):
    mensagens = carregar_mensagens()
    if telefone_cliente not in mensagens:
        mensagens[telefone_cliente] = []
    mensagens[telefone_cliente].append({
        'remetente': 'cliente',
        'nome': nome_cliente,
        'texto': texto,
        'hora': datetime.now().strftime('%H:%M'),
        'data': datetime.now().strftime('%d/%m/%Y'),
    })
    guardar_mensagens(mensagens)
    estado = obter_estado_conversa(telefone_cliente)
    if estado['status'] == 'sem_contacto':
        definir_estado_conversa(telefone_cliente, 'aguardando')
    marcar_digitando(telefone_cliente, 'cliente', False)


def enviar_mensagem_empresa(telefone_cliente, nome_atendente, texto):
    mensagens = carregar_mensagens()
    if telefone_cliente not in mensagens:
        mensagens[telefone_cliente] = []
    mensagens[telefone_cliente].append({
        'remetente': 'empresa',
        'nome': nome_atendente,
        'texto': texto,
        'hora': datetime.now().strftime('%H:%M'),
        'data': datetime.now().strftime('%d/%m/%Y'),
    })
    guardar_mensagens(mensagens)
    marcar_digitando(telefone_cliente, 'empresa', False)


def contar_nao_lidas_empresa(telefone_cliente):
    conversa = obter_conversa(telefone_cliente)
    cont = 0
    for msg in reversed(conversa):
        if msg['remetente'] == 'cliente':
            cont += 1
        else:
            break
    return cont


def obter_conversas_pendentes():
    mensagens = carregar_mensagens()
    estados = carregar_estados()
    pendentes = []
    for tel, msgs in mensagens.items():
        if not msgs:
            continue
        estado = estados.get(tel, {'status': 'aguardando', 'atendido_por': '', 'hora_atendimento': ''})
        clientes = carregar_clientes()
        nome = clientes.get(tel, {}).get('nome', 'Desconhecido')
        municipio = clientes.get(tel, {}).get('municipio', '')
        ultima = msgs[-1]
        nao_lidas = contar_nao_lidas_empresa(tel)
        pendentes.append({
            'telefone': tel,
            'nome': nome,
            'municipio': municipio,
            'ultima_msg': ultima['texto'],
            'ultima_hora': ultima['hora'],
            'ultima_data': ultima['data'],
            'nao_lidas': nao_lidas,
            'status': estado['status'],
            'atendido_por': estado.get('atendido_por', ''),
        })
    pendentes.sort(key=lambda x: x['nao_lidas'], reverse=True)
    return pendentes


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


def guardar_sessao_url():
    params = {}
    if 'ecra' in st.session_state:
        params['e'] = st.session_state['ecra']
    if 'cliente' in st.session_state and st.session_state['cliente']:
        params['t'] = st.session_state['cliente'].get('telefone', '')
    if 'empresa_usuario' in st.session_state:
        params['u'] = st.session_state['empresa_usuario']
    if 'conversa_activa' in st.session_state:
        params['ca'] = st.session_state['conversa_activa']
    st.query_params.update(params)


def restaurar_sessao_url():
    params = st.query_params
    if 'ecra' not in st.session_state:
        ecra = params.get('e', 'inicio')
        st.session_state['ecra'] = ecra
        if ecra == 'cliente' and 't' in params:
            tel = params['t']
            clientes = carregar_clientes()
            if tel in clientes:
                st.session_state['cliente'] = clientes[tel]
            else:
                st.session_state['ecra'] = 'inicio'
        if ecra == 'empresa' and 'u' in params:
            st.session_state['empresa_usuario'] = params['u']
        if 'ca' in params:
            st.session_state['conversa_activa'] = params['ca']


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
        for col in ['faixa_etaria', 'sexo', 'municipio', 'provincia', 'mes', 'estacao', 'status_genetico']:
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
    gravidade = determinar_gravidade(dados_paciente['hemoglobina'], dados_paciente['plaquetas'])
    resultados, erro = fazer_predicao(modelo, encoders, features, dados_paciente)
    progress_bar.empty()
    status_text.empty()
    return gravidade, resultados, erro


def svg_seringa():
    return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2l4 4"/><path d="M17 7l3-3"/><path d="M19 9l-8.7 8.7a2.1 2.1 0 0 1-3 0L3.3 13.7a2.1 2.1 0 0 1 0-3L12 2"/><path d="M5 19l3 3"/><path d="M2 22l3-3"/><line x1="9" y1="8" x2="16" y2="15"/></svg>'


def svg_seta():
    return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'


def svg_enviar():
    return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>'


def css_global():
    return """<style>
    @import url('https://fonts.googleapis.com/css2?family=Dosis:wght@200;300;400;500;600;700;800&display=swap');
    :root {
        --pri: #15291C; --sec: #D4E7DC; --accent: #C9553A;
        --bg: #FAFAF8; --surface: #FFFFFF; --surface-alt: #F3F2EE;
        --text: #1A1A18; --text-secondary: #5A5A52; --text-muted: #8A8A82;
        --border: #DDDCD7; --border-strong: #1A1A18;
        --success: #2D5A3D; --success-bg: #EDF2EE; --success-border: #C4D4C8;
        --danger: #8B1A1A; --radius: 0px;
    }
    * { font-family: 'Dosis', sans-serif !important; }
    .stApp { background: var(--bg) !important; }
    [data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu, footer, .stDeployButton { display: none !important; }
    .stTextInput > label, .stSelectbox > label, .stNumberInput > label, .stCheckbox > label {
        color: var(--text) !important; font-size: 0.75rem !important; font-weight: 700 !important;
        letter-spacing: 0.14em !important; text-transform: uppercase !important; margin-bottom: 0.5rem !important;
    }
    .stTextInput > div > div > input {
        background: var(--surface) !important; border: 2.5px solid var(--border) !important;
        border-radius: var(--radius) !important; color: var(--text) !important;
        padding: 1rem 1.1rem !important; font-size: 1rem !important; font-weight: 500 !important;
    }
    .stTextInput > div > div > input:focus { border-color: var(--border-strong) !important; box-shadow: none !important; }
    .stTextInput > div > div > input::placeholder { color: #B5B3AD !important; font-weight: 400 !important; }
    div[data-baseweb="select"] > div {
        background: var(--surface) !important; border: 2.5px solid var(--border) !important;
        border-radius: var(--radius) !important; min-height: 48px !important;
    }
    div[data-baseweb="select"] > div:focus-within { border-color: var(--border-strong) !important; box-shadow: none !important; }
    div[data-baseweb="select"] * { color: var(--text) !important; }
    div[data-baseweb="select"] span { font-weight: 500 !important; font-size: 1rem !important; }
    div[data-baseweb="select"] div[class*="placeholder"] { color: #B5B3AD !important; }
    div[data-baseweb="select"] svg { fill: var(--text-muted) !important; }
    div[data-baseweb="popover"] { border-radius: var(--radius) !important; box-shadow: 0 12px 48px rgba(26,26,24,0.12) !important; }
    div[data-baseweb="popover"] ul { background: var(--surface) !important; border: 2px solid var(--border) !important; padding: 6px !important; }
    div[data-baseweb="popover"] li { color: var(--text) !important; font-weight: 500 !important; padding: 10px 14px !important; }
    div[data-baseweb="popover"] li:hover { background: var(--surface-alt) !important; }
    div[data-baseweb="popover"] li[aria-selected="true"] { background: var(--sec) !important; font-weight: 700 !important; }
    *:focus { outline: none !important; }
    .stButton > button {
        background: transparent !important; color: var(--text) !important;
        border: 3px solid var(--border-strong) !important; border-radius: var(--radius) !important;
        font-weight: 700 !important; font-size: 0.85rem !important; padding: 1rem 2.4rem !important;
        width: 100% !important; letter-spacing: 0.13em !important; text-transform: uppercase !important;
        transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    }
    .stButton > button:hover { background: var(--pri) !important; color: var(--bg) !important; border-color: var(--pri) !important; }
    .stButton > button:active { background: #0D1E13 !important; border-color: #0D1E13 !important; color: var(--bg) !important; }
    .stFormSubmitButton > button {
        background: transparent !important; color: var(--text) !important;
        border: 3px solid var(--border-strong) !important; border-radius: var(--radius) !important;
        font-weight: 700 !important; font-size: 0.85rem !important; padding: 1rem 2.4rem !important;
        letter-spacing: 0.13em !important; text-transform: uppercase !important;
    }
    .stFormSubmitButton > button:hover { background: var(--pri) !important; color: var(--bg) !important; border-color: var(--pri) !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 0; background: transparent; border-bottom: 2px solid var(--border); padding: 0; }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; color: var(--text-muted) !important; border: none !important;
        border-bottom: 3px solid transparent !important; font-weight: 600 !important; font-size: 0.8rem !important;
        padding: 0.9rem 1.6rem !important; letter-spacing: 0.1em !important; text-transform: uppercase !important;
        margin-bottom: -2px !important;
    }
    .stTabs [data-baseweb="tab"]:hover { color: var(--text) !important; }
    .stTabs [aria-selected="true"] { color: var(--text) !important; font-weight: 800 !important; border-bottom: 3px solid var(--text) !important; }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }
    [data-testid="stMetric"] { background: var(--surface); border: 2px solid var(--border); padding: 1.4rem; }
    [data-testid="stMetric"] label { color: var(--text-muted) !important; font-weight: 700 !important; font-size: 0.7rem !important; text-transform: uppercase !important; letter-spacing: 0.1em; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 800 !important; }
    .stProgress > div > div { background: var(--pri) !important; height: 3px !important; }
    .stProgress > div { background: var(--border) !important; height: 3px !important; }
    .stNumberInput input { background: var(--surface) !important; border: 2.5px solid var(--border) !important; color: var(--text) !important; font-weight: 500 !important; }
    .stNumberInput input:focus { border-color: var(--border-strong) !important; box-shadow: none !important; }
    .stNumberInput button { background: var(--surface-alt) !important; border: 2px solid var(--border) !important; color: var(--text-muted) !important; }
    .stNumberInput button:hover { background: var(--border) !important; color: var(--text) !important; }
    [data-testid="stExpander"] { border: 2px solid var(--border) !important; background: var(--surface) !important; }
    [data-testid="stExpander"] summary { font-weight: 600 !important; color: var(--text) !important; }
    div[data-testid="stMarkdownContainer"] p { line-height: 1.75 !important; }
    .stTextArea textarea {
        background: var(--surface) !important; border: 2.5px solid var(--border) !important;
        border-radius: var(--radius) !important; color: var(--text) !important;
        font-size: 0.95rem !important; font-weight: 500 !important; font-family: 'Dosis', sans-serif !important;
    }
    .stTextArea textarea:focus { border-color: var(--border-strong) !important; box-shadow: none !important; }
    .stTextArea > label {
        color: var(--text) !important; font-size: 0.75rem !important; font-weight: 700 !important;
        letter-spacing: 0.14em !important; text-transform: uppercase !important;
    }
    @keyframes pulsar {
        0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
        40% { opacity: 1; transform: scale(1); }
    }
    </style>"""


def css_tela_inicio():
    return """<style>
    .main .block-container { max-width: 480px; margin: 0 auto; padding-top: 0 !important; padding-bottom: 3rem !important; }
    </style>"""


def css_painel_cliente():
    return """<style>
    .main .block-container { max-width: 780px; margin: 0 auto; padding: 1.5rem 2rem; }
    </style>"""


def css_painel_empresa():
    return """<style>
    .main .block-container { max-width: 1200px; margin: 0 auto; padding: 2rem 3rem; }
    [data-testid="stSidebar"] { display: block !important; background-color: var(--pri) !important; border-right: none; }
    header[data-testid="stHeader"] { display: block !important; background: transparent !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    button[data-testid="baseButton-header"] { color: #1A1A18 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #E8E6E1 !important; font-size: 0.85rem !important; font-weight: 700 !important;
        letter-spacing: 0.14em !important; text-transform: uppercase !important;
        border-bottom: 1px solid #2A4435 !important; padding-bottom: 0.6rem !important; margin-top: 1.5rem !important;
    }
    [data-testid="stSidebar"] label { color: #8A9B8E !important; font-size: 0.8rem !important; font-weight: 600 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #8A9B8E !important; }
    [data-testid="stSidebar"] strong { color: #B5C4B8 !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div, [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1E3A28 !important; border: 2px solid #2A4435 !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] *, [data-testid="stSidebar"] div[data-baseweb="select"] span { color: #E8E6E1 !important; }
    [data-testid="stSidebar"] div[data-baseweb="select"] svg { fill: #5A6B5E !important; }
    [data-testid="stSidebar"] .stNumberInput input { background-color: #1E3A28 !important; border: 2px solid #2A4435 !important; color: #E8E6E1 !important; }
    [data-testid="stSidebar"] .stNumberInput button { background-color: #2A4435 !important; border-color: #2A4435 !important; color: #B5C4B8 !important; }
    [data-testid="stSidebar"] .stCheckbox label span { color: #B5C4B8 !important; }
    [data-testid="stSidebar"] .stButton > button { background: transparent !important; border: 2.5px solid #2A4435 !important; color: #8A9B8E !important; }
    [data-testid="stSidebar"] .stButton > button:hover { background: #1E3A28 !important; border-color: #5A6B5E !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] hr { border-color: #2A4435 !important; }
    </style>"""


def componente_logo(tamanho="grande"):
    svg_icon = '<svg width="{w}" height="{h}" viewBox="0 0 44 44" fill="none"><circle cx="22" cy="22" r="16" stroke="#D4E7DC" stroke-width="2.5" fill="none"/><circle cx="22" cy="22" r="8" fill="#C9553A"/><line x1="22" y1="2" x2="22" y2="10" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/><line x1="22" y1="34" x2="22" y2="42" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/><line x1="2" y1="22" x2="10" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/><line x1="34" y1="22" x2="42" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/></svg>'
    if tamanho == "grande":
        icon = svg_icon.format(w="40", h="40")
        return (
            '<div style="text-align:center;margin-bottom:2rem;">'
            '<div style="width:80px;height:80px;background:#15291C;display:inline-flex;align-items:center;justify-content:center;margin-bottom:1.8rem;">'
            + icon +
            '</div>'
            '<div style="font-size:3rem;font-weight:900;color:#1A1A18;letter-spacing:-0.05em;line-height:0.95;">Hema<br>Sakula</div>'
            '<div style="font-size:0.68rem;color:#8A8A82;letter-spacing:0.18em;text-transform:uppercase;margin-top:1rem;font-weight:600;">Angola a Cuidar dos Seus</div>'
            '</div>'
        )
    icon = svg_icon.format(w="20", h="20")
    return (
        '<div style="display:flex;align-items:center;gap:0.7rem;">'
        '<div style="width:38px;height:38px;background:#15291C;display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
        + icon +
        '</div>'
        '<div><div style="font-size:1.1rem;font-weight:800;color:#1A1A18;letter-spacing:-0.03em;">HemaSakula</div></div>'
        '</div>'
    )


def componente_linha():
    return '<div style="height:1px;background:#DDDCD7;margin:2rem 0;"></div>'


def componente_linha_fina():
    return '<div style="margin:1rem 0 1.5rem 0;"><div style="height:3px;background:#1A1A18;width:48px;"></div></div>'


def componente_footer():
    return (
        '<div style="text-align:center;padding:3rem 0;margin-top:4rem;border-top:2px solid #DDDCD7;">'
        '<div style="color:#8A8A82;font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;font-weight:700;margin-bottom:0.5rem;">HemaSakula</div>'
        '<div style="color:#B5B3AD;font-size:0.82rem;font-weight:400;">A tua saude importa. Estamos aqui por ti.</div>'
        '</div>'
    )


def componente_digitando(nome):
    return (
        '<div style="display:flex;align-items:center;gap:0.6rem;padding:0.8rem 0;">'
        '<div style="display:flex;gap:4px;">'
        '<div style="width:6px;height:6px;background:#8A8A82;border-radius:50%;animation:pulsar 1.4s infinite ease-in-out;animation-delay:0s;"></div>'
        '<div style="width:6px;height:6px;background:#8A8A82;border-radius:50%;animation:pulsar 1.4s infinite ease-in-out;animation-delay:0.2s;"></div>'
        '<div style="width:6px;height:6px;background:#8A8A82;border-radius:50%;animation:pulsar 1.4s infinite ease-in-out;animation-delay:0.4s;"></div>'
        '</div>'
        '<span style="color:#8A8A82;font-size:0.78rem;font-weight:600;font-style:italic;">'
        + nome + ' esta a escrever</span></div>'
    )


def componente_botao_decorado(texto, icone="seta"):
    if icone == "seringa":
        svg = svg_seringa()
    elif icone == "enviar":
        svg = svg_enviar()
    else:
        svg = svg_seta()
    return (
        '<div style="display:flex;align-items:center;justify-content:center;gap:0.7rem;">'
        '<span>' + texto + '</span>'
        '<span style="display:inline-flex;align-items:center;">' + svg + '</span>'
        '</div>'
    )


def renderizar_mensagens_html(telefone, lado):
    conversa = obter_conversa(telefone)
    clientes = carregar_clientes()
    nome_cliente = clientes.get(telefone, {}).get('nome', 'Cliente')
    iniciais = ''.join([p[0].upper() for p in nome_cliente.split()[:2]]) if nome_cliente else '??'
    html_parts = []

    if not conversa:
        return ""

    data_anterior = None
    for msg in conversa:
        msg_data = msg.get('data', '')
        if msg_data != data_anterior:
            data_anterior = msg_data
            html_parts.append(
                '<div style="text-align:center;margin:1.2rem 0;">'
                '<span style="background:#F3F2EE;color:#B5B3AD;font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:0.3rem 1rem;border:1px solid #DDDCD7;">'
                + msg_data + '</span></div>'
            )

        if lado == 'cliente':
            if msg['remetente'] == 'cliente':
                html_parts.append(
                    '<div style="display:flex;justify-content:flex-end;margin-bottom:0.6rem;">'
                    '<div style="background:#15291C;color:#E8E6E1;padding:0.9rem 1.2rem;max-width:75%;">'
                    '<div style="font-size:0.9rem;line-height:1.7;font-weight:500;">' + msg['texto'] + '</div>'
                    '<div style="text-align:right;color:#5A6B5E;font-size:0.65rem;margin-top:0.4rem;font-weight:600;">' + msg['hora'] + '</div>'
                    '</div></div>'
                )
            else:
                html_parts.append(
                    '<div style="display:flex;justify-content:flex-start;margin-bottom:0.6rem;gap:0.5rem;">'
                    '<div style="width:28px;height:28px;background:#15291C;display:flex;align-items:center;justify-content:center;color:#D4E7DC;font-weight:800;font-size:0.5rem;flex-shrink:0;margin-top:0.2rem;">RL</div>'
                    '<div style="background:#FFFFFF;color:#1A1A18;padding:0.9rem 1.2rem;max-width:75%;border:2px solid #DDDCD7;">'
                    '<div style="color:#8A8A82;font-size:0.65rem;font-weight:700;margin-bottom:0.3rem;">' + msg.get('nome', 'Recepcao') + '</div>'
                    '<div style="font-size:0.9rem;line-height:1.7;font-weight:500;">' + msg['texto'] + '</div>'
                    '<div style="color:#B5B3AD;font-size:0.65rem;margin-top:0.4rem;font-weight:600;">' + msg['hora'] + '</div>'
                    '</div></div>'
                )
        else:
            if msg['remetente'] == 'cliente':
                html_parts.append(
                    '<div style="display:flex;justify-content:flex-start;margin-bottom:0.6rem;gap:0.5rem;">'
                    '<div style="width:28px;height:28px;background:#C9553A;display:flex;align-items:center;justify-content:center;color:white;font-weight:800;font-size:0.5rem;flex-shrink:0;margin-top:0.2rem;">'
                    + iniciais + '</div>'
                    '<div style="background:#FFFFFF;color:#1A1A18;padding:0.9rem 1.2rem;max-width:75%;border:2px solid #DDDCD7;">'
                    '<div style="color:#C9553A;font-size:0.65rem;font-weight:700;margin-bottom:0.3rem;">' + msg.get('nome', nome_cliente) + '</div>'
                    '<div style="font-size:0.9rem;line-height:1.7;font-weight:500;">' + msg['texto'] + '</div>'
                    '<div style="color:#B5B3AD;font-size:0.65rem;margin-top:0.4rem;font-weight:600;">' + msg['hora'] + '</div>'
                    '</div></div>'
                )
            else:
                html_parts.append(
                    '<div style="display:flex;justify-content:flex-end;margin-bottom:0.6rem;">'
                    '<div style="background:#15291C;color:#E8E6E1;padding:0.9rem 1.2rem;max-width:75%;">'
                    '<div style="color:#5A6B5E;font-size:0.65rem;font-weight:700;margin-bottom:0.3rem;">' + msg.get('nome', 'Recepcao') + '</div>'
                    '<div style="font-size:0.9rem;line-height:1.7;font-weight:500;">' + msg['texto'] + '</div>'
                    '<div style="text-align:right;color:#5A6B5E;font-size:0.65rem;margin-top:0.4rem;font-weight:600;">' + msg['hora'] + '</div>'
                    '</div></div>'
                )

    if lado == 'cliente':
        if verificar_digitando(telefone, 'empresa'):
            estado = obter_estado_conversa(telefone)
            nome_quem = estado.get('atendido_por', 'Recepcao')
            html_parts.append(componente_digitando(nome_quem))
    else:
        if verificar_digitando(telefone, 'cliente'):
            html_parts.append(componente_digitando(nome_cliente))

    return '\n'.join(html_parts)


@st.fragment(run_every=5)
def fragmento_chat_cliente(telefone):
    estado = obter_estado_conversa(telefone)
    conversa = obter_conversa(telefone)

    if estado['status'] == 'atendido' and estado.get('atendido_por'):
        st.markdown(
            '<div style="background:#EDF2EE;border:2px solid #C4D4C8;border-left:4px solid #2D5A3D;padding:1rem 1.4rem;margin-bottom:1rem;">'
            '<div style="color:#2D5A3D;font-size:0.85rem;font-weight:600;line-height:1.7;">'
            'Estas a ser atendido por <strong>' + estado['atendido_por'] + '</strong> desde as ' + estado.get('hora_atendimento', '') + '.'
            '</div></div>',
            unsafe_allow_html=True
        )
    elif estado['status'] == 'aguardando':
        st.markdown(
            '<div style="background:#FDF8F0;border:2px solid #DDD0B8;border-left:4px solid #8A6B3E;padding:1rem 1.4rem;margin-bottom:1rem;">'
            '<div style="color:#8A6B3E;font-size:0.85rem;font-weight:600;line-height:1.7;">'
            'A tua mensagem foi enviada. A recepcao vai atender-te em breve.'
            '</div></div>',
            unsafe_allow_html=True
        )

    if conversa:
        st.markdown(
            '<div style="color:#8A8A82;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.14em;font-weight:700;margin-bottom:0.8rem;">Conversa</div>',
            unsafe_allow_html=True
        )
        html = renderizar_mensagens_html(telefone, 'cliente')
        if html:
            st.markdown(html, unsafe_allow_html=True)


@st.fragment(run_every=4)
def fragmento_chat_empresa(telefone):
    conversa = obter_conversa(telefone)
    if conversa:
        html = renderizar_mensagens_html(telefone, 'empresa')
        if html:
            st.markdown(html, unsafe_allow_html=True)


@st.fragment(run_every=6)
def fragmento_lista_conversas(usuario):
    conversas = obter_conversas_pendentes()

    total = len(conversas)
    aguardando = sum(1 for c in conversas if c['status'] == 'aguardando')
    atendidas = sum(1 for c in conversas if c['status'] == 'atendido')

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Total de contactos", str(total))
    with col_m2:
        st.metric("A aguardar", str(aguardando))
    with col_m3:
        st.metric("Atendidos", str(atendidas))

    st.markdown(componente_linha(), unsafe_allow_html=True)

    if not conversas:
        st.markdown(
            '<div style="text-align:center;padding:3rem 0;">'
            '<div style="color:#B5B3AD;font-size:1.2rem;font-weight:600;margin-bottom:0.5rem;">Nenhuma mensagem de momento</div>'
            '<div style="color:#DDDCD7;font-size:0.85rem;">Quando um cliente enviar mensagem, aparece aqui.</div></div>',
            unsafe_allow_html=True
        )
        return

    st.markdown(
        '<div style="color:#8A8A82;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.14em;font-weight:700;margin-bottom:1rem;">Mensagens recebidas</div>',
        unsafe_allow_html=True
    )

    for c in conversas:
        if c['status'] == 'aguardando':
            borda_cor = '#C9553A'
            status_badge = (
                '<span style="background:#FDF2E9;color:#C9553A;border:2px solid #F0C9B5;'
                'display:inline-block;padding:0.3rem 0.8rem;font-size:0.6rem;font-weight:700;'
                'letter-spacing:0.1em;text-transform:uppercase;">NOVA</span>'
            )
        elif c['status'] == 'atendido':
            borda_cor = '#2D5A3D'
            status_badge = (
                '<span style="background:#EDF2EE;color:#2D5A3D;border:2px solid #C4D4C8;'
                'display:inline-block;padding:0.3rem 0.8rem;font-size:0.6rem;font-weight:700;'
                'letter-spacing:0.1em;text-transform:uppercase;">ATENDIDO</span>'
            )
        else:
            borda_cor = '#DDDCD7'
            status_badge = ''

        notif_html = ""
        if c['nao_lidas'] > 0:
            notif_html = (
                '<div style="background:#C9553A;color:#FFFFFF;width:24px;height:24px;'
                'border-radius:50%;display:inline-flex;align-items:center;justify-content:center;'
                'font-size:0.65rem;font-weight:800;flex-shrink:0;">'
                + str(c['nao_lidas']) + '</div>'
            )

        iniciais = ''.join([p[0].upper() for p in c['nome'].split()[:2]]) if c['nome'] else '??'
        ultima_preview = c['ultima_msg'][:60] + ('...' if len(c['ultima_msg']) > 60 else '')

        st.markdown(
            '<div style="background:#FFFFFF;border:2px solid #DDDCD7;border-left:4px solid ' + borda_cor + ';padding:1.3rem 1.4rem;margin-bottom:0.6rem;">'
            '<div style="display:flex;align-items:center;gap:1rem;">'
            '<div style="width:46px;height:46px;background:#15291C;display:flex;align-items:center;justify-content:center;color:#D4E7DC;font-weight:800;font-size:0.72rem;flex-shrink:0;letter-spacing:0.05em;">'
            + iniciais + '</div>'
            '<div style="flex:1;min-width:0;">'
            '<div style="display:flex;justify-content:space-between;align-items:center;">'
            '<div style="font-weight:700;color:#1A1A18;font-size:0.95rem;letter-spacing:-0.01em;">' + c['nome'] + '</div>'
            '<div style="display:flex;align-items:center;gap:0.5rem;">' + notif_html + status_badge + '</div></div>'
            '<div style="color:#8A8A82;font-size:0.75rem;margin-top:0.15rem;">' + c['municipio'] + ' — ' + c['telefone'] + '</div>'
            '<div style="color:#B5B3AD;font-size:0.8rem;margin-top:0.4rem;font-style:italic;">"' + ultima_preview + '"</div>'
            '<div style="color:#B5B3AD;font-size:0.65rem;margin-top:0.2rem;">' + c['ultima_data'] + ' as ' + c['ultima_hora'] + '</div>'
            '</div></div></div>',
            unsafe_allow_html=True
        )

        col_a1, col_a2 = st.columns(2)
        with col_a1:
            if c['status'] == 'aguardando':
                if st.button("ATENDER " + c['nome'].split()[0].upper(), key="btn_atender_" + c['telefone'], use_container_width=True):
                    definir_estado_conversa(c['telefone'], 'atendido', usuario.capitalize())
                    st.session_state['conversa_activa'] = c['telefone']
                    guardar_sessao_url()
                    st.rerun()
            else:
                if st.button("ABRIR CONVERSA", key="btn_abrir_" + c['telefone'], use_container_width=True):
                    st.session_state['conversa_activa'] = c['telefone']
                    guardar_sessao_url()
                    st.rerun()
        with col_a2:
            if c['status'] == 'atendido':
                atendente = obter_estado_conversa(c['telefone']).get('atendido_por', '')
                st.markdown(
                    '<div style="padding:0.8rem 0;text-align:center;color:#8A8A82;font-size:0.75rem;font-weight:600;">'
                    'Atendido por ' + atendente + '</div>',
                    unsafe_allow_html=True
                )


def tela_boas_vindas():
    st.markdown(css_global(), unsafe_allow_html=True)
    st.markdown(css_tela_inicio(), unsafe_allow_html=True)

    saudacao = obter_saudacao()
    st.markdown("<div style='height:6vh;'></div>", unsafe_allow_html=True)
    st.markdown(componente_logo("grande"), unsafe_allow_html=True)
    st.markdown(componente_linha(), unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;margin-bottom:2.5rem;">'
        '<div style="font-size:1.8rem;font-weight:800;color:#1A1A18;letter-spacing:-0.03em;margin-bottom:0.8rem;">'
        + saudacao + '.</div>'
        '<div style="font-size:0.95rem;color:#8A8A82;line-height:1.8;max-width:360px;margin:0 auto;">'
        'Fala directamente com a recepcao do Consultorio Medico Lucilio. Envia a tua mensagem e aguarda que alguem te atenda.</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(componente_linha_fina(), unsafe_allow_html=True)

    nome = st.text_input("NOME", placeholder="Como queres que te chamemos?", key="nome_cliente")
    municipio = st.selectbox("MUNICIPIO", MUNICIPIOS_LISTA, index=None, placeholder="Onde vives?", key="municipio_cliente")
    telefone = st.text_input("TELEFONE", placeholder="9xx xxx xxx", key="telefone_cliente")
    email = st.text_input("EMAIL (OPCIONAL)", placeholder="exemplo@email.com", key="email_cliente")

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;margin-bottom:0.3rem;">'
        + componente_botao_decorado("COMECAR", "seringa") +
        '</div>',
        unsafe_allow_html=True
    )

    if st.button("COMEÇAR →", key="btn_comecar", use_container_width=True):
        erros = []
        if not nome or not nome.strip():
            erros.append("Precisamos do teu nome.")
        if not municipio:
            erros.append("Escolhe o municipio onde vives.")
        if not telefone:
            erros.append("O numero de telefone e obrigatorio.")
        elif not validar_telefone(telefone):
            erros.append("O numero deve ter 9 digitos e comecar por 9.")
        if email and email.strip() and not validar_email(email.strip()):
            erros.append("O email nao parece valido.")
        if erros:
            for erro in erros:
                st.error(erro)
        else:
            sucesso, dados = registar_cliente(nome.strip(), telefone.strip(), municipio, email.strip() if email else '')
            if sucesso:
                st.session_state['ecra'] = 'cliente'
                st.session_state['cliente'] = dados
                guardar_sessao_url()
                st.rerun()

    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)
    st.markdown(componente_linha(), unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;margin-bottom:1.2rem;">'
        '<div style="color:#8A8A82;font-size:0.68rem;letter-spacing:0.14em;text-transform:uppercase;font-weight:700;">Acesso profissional</div></div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("ENTRAR COMO EMPRESA →", key="btn_empresa", use_container_width=True):
            st.session_state['ecra'] = 'login_empresa'
            guardar_sessao_url()
            st.rerun()

    st.markdown(componente_footer(), unsafe_allow_html=True)


def tela_login_empresa():
    st.markdown(css_global(), unsafe_allow_html=True)
    st.markdown(css_tela_inicio(), unsafe_allow_html=True)

    st.markdown("<div style='height:8vh;'></div>", unsafe_allow_html=True)

    svg_small = '<svg width="28" height="28" viewBox="0 0 44 44" fill="none"><circle cx="22" cy="22" r="16" stroke="#D4E7DC" stroke-width="2.5" fill="none"/><circle cx="22" cy="22" r="8" fill="#C9553A"/><line x1="22" y1="2" x2="22" y2="10" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/><line x1="22" y1="34" x2="22" y2="42" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/><line x1="2" y1="22" x2="10" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/><line x1="34" y1="22" x2="42" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/></svg>'

    st.markdown(
        '<div style="text-align:center;margin-bottom:2.5rem;">'
        '<div style="width:56px;height:56px;background:#15291C;display:inline-flex;align-items:center;justify-content:center;margin-bottom:1.5rem;">'
        + svg_small +
        '</div>'
        '<div style="font-size:1.6rem;font-weight:800;color:#1A1A18;letter-spacing:-0.03em;">Acesso Profissional</div>'
        '<div style="font-size:0.85rem;color:#8A8A82;margin-top:0.5rem;">Para clinicas e hospitais parceiros</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(componente_linha_fina(), unsafe_allow_html=True)

    usuario = st.text_input("UTILIZADOR", placeholder="O teu utilizador", key="emp_usuario")
    senha = st.text_input("PALAVRA-PASSE", type="password", placeholder="A tua palavra-passe", key="emp_senha")

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
                guardar_sessao_url()
                st.rerun()
            else:
                st.error("Credenciais incorrectas.")

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← VOLTAR", key="btn_voltar_login", use_container_width=True):
            st.session_state['ecra'] = 'inicio'
            guardar_sessao_url()
            st.rerun()

    st.markdown(
        '<div style="text-align:center;margin-top:3rem;color:#B5B3AD;font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;">'
        'Acesso restrito a profissionais autorizados</div>',
        unsafe_allow_html=True
    )


def tela_painel_cliente():
    st.markdown(css_global(), unsafe_allow_html=True)
    st.markdown(css_painel_cliente(), unsafe_allow_html=True)

    cliente = st.session_state.get('cliente', {})
    nome = cliente.get('nome', 'Amigo')
    telefone = cliente.get('telefone', '')
    primeiro_nome = nome.split()[0] if nome else 'Amigo'
    saudacao = obter_saudacao()

    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(componente_logo("pequeno"), unsafe_allow_html=True)
    with col_h2:
        st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)
        if st.button("SAIR", key="btn_sair_cliente"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.query_params.clear()
            st.rerun()

    st.markdown(componente_linha(), unsafe_allow_html=True)

    estado = obter_estado_conversa(telefone)

    if estado['status'] == 'atendido':
        status_html = (
            '<span style="background:#EDF2EE;color:#2D5A3D;border:2px solid #C4D4C8;'
            'display:inline-block;padding:0.35rem 0.9rem;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.1em;text-transform:uppercase;">O RESPONSAVEL ESTA PRONTO</span>'
        )
    elif estado['status'] == 'aguardando':
        status_html = (
            '<span style="background:#FDF8F0;color:#8A6B3E;border:2px solid #DDD0B8;'
            'display:inline-block;padding:0.35rem 0.9rem;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.1em;text-transform:uppercase;">AGUARDANDO ATENDIMENTO</span>'
        )
    else:
        status_html = (
            '<span style="background:#F3F2EE;color:#5A5A52;border:2px solid #DDDCD7;'
            'display:inline-block;padding:0.35rem 0.9rem;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.1em;text-transform:uppercase;">RECEPCAO LUCILIO</span>'
        )

    st.markdown(
        '<div style="margin-bottom:0.5rem;">'
        '<div style="font-size:2.2rem;font-weight:900;color:#1A1A18;letter-spacing:-0.04em;line-height:1.1;">'
        + saudacao + ',<br>' + primeiro_nome + '.</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(componente_linha_fina(), unsafe_allow_html=True)

    st.markdown(
        '<div style="background:#FFFFFF;border:2px solid #DDDCD7;border-left:4px solid #15291C;padding:1.3rem 1.4rem;margin-bottom:1rem;">'
        '<div style="display:flex;align-items:center;gap:1rem;">'
        '<div style="width:52px;height:52px;background:#15291C;display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
        '<span style="color:#D4E7DC;font-weight:800;font-size:0.8rem;letter-spacing:0.05em;">RL</span></div>'
        '<div style="flex:1;">'
        '<div style="font-weight:800;color:#1A1A18;font-size:1.1rem;letter-spacing:-0.02em;">Recepcao Lucilio</div>'
        '<div style="color:#8A8A82;font-size:0.82rem;margin-top:0.2rem;">Consultorio Medico Lucilio — Luanda</div></div>'
        '<div>' + status_html + '</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    if estado['status'] == 'sem_contacto':
        st.markdown(
            '<div style="color:#5A5A52;font-size:0.9rem;line-height:1.8;margin-bottom:1.5rem;">'
            'Envia uma mensagem para a recepcao do Consultorio Lucilio. '
            'Alguem da equipa vai atender-te assim que possivel.</div>',
            unsafe_allow_html=True
        )

    fragmento_chat_cliente(telefone)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    with st.form(key="form_msg_cliente", clear_on_submit=True):
        texto_msg = st.text_input(
            "ESCREVE A TUA MENSAGEM",
            placeholder="Escreve aqui...",
            key="input_msg_cliente",
        )

        col_s1, col_s2 = st.columns([3, 1])
        with col_s2:
            enviado = st.form_submit_button("ENVIAR →", use_container_width=True)

        if enviado and texto_msg and texto_msg.strip():
            enviar_mensagem_cliente(telefone, nome, texto_msg.strip())
            st.rerun()

    st.markdown(componente_linha(), unsafe_allow_html=True)

    st.markdown(
        '<div style="background:#FFFFFF;border:2px solid #DDDCD7;padding:1.3rem 1.4rem;margin-bottom:0.6rem;">'
        '<div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:700;margin-bottom:0.5rem;">Morada e contacto</div>'
        '<div style="color:#1A1A18;font-size:0.92rem;line-height:1.7;">Consultorio Medico Lucilio<br>Luanda, Angola<br>'
        '<span style="color:#8A8A82;">Tel: +244 923 000 000</span><br>'
        '<span style="color:#8A8A82;">Seg a Sex 07h30-18h — Sab 07h30-14h</span></div></div>',
        unsafe_allow_html=True
    )

    st.markdown(componente_footer(), unsafe_allow_html=True)
    guardar_sessao_url()


def tela_painel_empresa():
    st.markdown(css_global(), unsafe_allow_html=True)
    st.markdown(css_painel_empresa(), unsafe_allow_html=True)

    usuario = st.session_state.get('empresa_usuario', 'Empresa')

    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown(componente_logo("pequeno"), unsafe_allow_html=True)
    with col_header2:
        st.markdown(
            '<div style="text-align:right;padding-top:0.5rem;">'
            '<span style="color:#8A8A82;font-size:0.75rem;font-weight:600;letter-spacing:0.05em;">'
            + usuario.capitalize() + ' — ' + datetime.now().strftime("%d/%m/%Y") + '</span></div>',
            unsafe_allow_html=True
        )

    st.markdown(componente_linha(), unsafe_allow_html=True)

    svg_sidebar = '<svg width="24" height="24" viewBox="0 0 44 44" fill="none"><circle cx="22" cy="22" r="16" stroke="#D4E7DC" stroke-width="2.5" fill="none"/><circle cx="22" cy="22" r="8" fill="#C9553A"/><line x1="22" y1="2" x2="22" y2="10" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/><line x1="22" y1="34" x2="22" y2="42" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/><line x1="2" y1="22" x2="10" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/><line x1="34" y1="22" x2="42" y2="22" stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"/></svg>'

    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:1.2rem 0 1.8rem 0;">'
            '<div style="width:48px;height:48px;background:#1E3A28;display:inline-flex;align-items:center;justify-content:center;margin-bottom:0.8rem;">'
            + svg_sidebar + '</div>'
            '<div style="color:#E8E6E1;font-weight:700;font-size:0.9rem;">' + usuario.capitalize() + '</div>'
            '<div style="color:#5A6B5E;font-size:0.62rem;margin-top:0.2rem;letter-spacing:0.12em;text-transform:uppercase;font-weight:600;">Recepcao Lucilio</div></div>',
            unsafe_allow_html=True
        )

        st.markdown("---")

        if st.button("SAIR", key="btn_sair_empresa", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.query_params.clear()
            st.rerun()

    tab_mensagens, tab_hemograma = st.tabs(["MENSAGENS DE CLIENTES", "ANALISE DE HEMOGRAMA"])

    with tab_mensagens:
        conversa_activa = st.session_state.get('conversa_activa', None)
        if conversa_activa:
            renderizar_conversa_empresa(conversa_activa, usuario)
        else:
            fragmento_lista_conversas(usuario)

    with tab_hemograma:
        renderizar_tab_hemograma()

    guardar_sessao_url()


def renderizar_conversa_empresa(telefone, usuario):
    if st.button("← VOLTAR A LISTA", key="btn_voltar_lista"):
        del st.session_state['conversa_activa']
        guardar_sessao_url()
        st.rerun()

    clientes = carregar_clientes()
    info_cliente = clientes.get(telefone, {})
    nome_cliente = info_cliente.get('nome', 'Desconhecido')
    municipio_cliente = info_cliente.get('municipio', '')
    estado = obter_estado_conversa(telefone)

    iniciais = ''.join([p[0].upper() for p in nome_cliente.split()[:2]]) if nome_cliente else '??'

    if estado['status'] == 'atendido':
        status_badge = (
            '<span style="background:#EDF2EE;color:#2D5A3D;border:2px solid #C4D4C8;'
            'display:inline-block;padding:0.35rem 0.9rem;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.1em;text-transform:uppercase;">A ATENDER</span>'
        )
    else:
        status_badge = (
            '<span style="background:#FDF2E9;color:#C9553A;border:2px solid #F0C9B5;'
            'display:inline-block;padding:0.35rem 0.9rem;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.1em;text-transform:uppercase;">AGUARDANDO</span>'
        )

    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;padding:1rem 0;margin-bottom:0.5rem;">'
        '<div style="width:50px;height:50px;background:#15291C;display:flex;align-items:center;justify-content:center;color:#D4E7DC;font-weight:800;font-size:0.75rem;flex-shrink:0;letter-spacing:0.05em;">'
        + iniciais + '</div>'
        '<div style="flex:1;">'
        '<div style="font-weight:800;color:#1A1A18;font-size:1.1rem;letter-spacing:-0.02em;">' + nome_cliente + '</div>'
        '<div style="color:#8A8A82;font-size:0.78rem;margin-top:0.15rem;">' + municipio_cliente + ' — ' + telefone + '</div></div>'
        '<div>' + status_badge + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    if estado['status'] == 'aguardando':
        if st.button("ATENDER ESTE CLIENTE →", key="btn_atender_dentro", use_container_width=True):
            definir_estado_conversa(telefone, 'atendido', usuario.capitalize())
            guardar_sessao_url()
            st.rerun()

    st.markdown(componente_linha(), unsafe_allow_html=True)

    fragmento_chat_empresa(telefone)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    if estado['status'] == 'atendido':
        with st.form(key="form_resposta_empresa", clear_on_submit=True):
            texto_resp = st.text_area(
                "RESPONDER A " + nome_cliente.split()[0].upper(),
                placeholder="Escreve a tua resposta...",
                key="input_resp_empresa",
                height=100
            )

            col_r1, col_r2 = st.columns([3, 1])
            with col_r2:
                enviado = st.form_submit_button("ENVIAR →", use_container_width=True)

            if enviado and texto_resp and texto_resp.strip():
                enviar_mensagem_empresa(telefone, usuario.capitalize(), texto_resp.strip())
                marcar_digitando(telefone, 'empresa', False)
                st.rerun()

        if texto_resp and texto_resp.strip():
            marcar_digitando(telefone, 'empresa', True)
        else:
            marcar_digitando(telefone, 'empresa', False)
    else:
        st.markdown(
            '<div style="background:#FDF8F0;border:2px solid #DDD0B8;padding:1rem 1.4rem;">'
            '<div style="color:#8A6B3E;font-size:0.85rem;font-weight:600;">Clica em "ATENDER ESTE CLIENTE" para poderes responder.</div></div>',
            unsafe_allow_html=True
        )


def renderizar_tab_hemograma():
    st.markdown(
        '<div style="background:#FFFFFF;border:2px solid #DDDCD7;border-left:4px solid #8A8A82;padding:1.2rem 1.4rem;margin-bottom:1.5rem;">'
        '<div style="color:#5A5A52;font-size:0.88rem;line-height:1.7;">'
        '<strong style="color:#1A1A18;">Atencao:</strong> Este sistema serve de apoio a decisao clinica. '
        'Nao substitui a avaliacao presencial nem o julgamento do profissional de saude.</div></div>',
        unsafe_allow_html=True
    )

    modelo, encoders, features = carregar_modelo()
    if modelo is None:
        st.error("Modelo nao encontrado. Executa primeiro: python modelo_ml.py")
        return

    st.markdown(
        '<div style="background:#EDF2EE;border:2px solid #C4D4C8;border-left:4px solid #2D5A3D;padding:1rem 1.4rem;margin-bottom:1.5rem;">'
        '<span style="color:#2D5A3D;font-weight:700;font-size:0.82rem;letter-spacing:0.05em;">SISTEMA OPERACIONAL — MODELO CARREGADO</span></div>',
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.header("Identificacao")
        faixa_etaria = st.selectbox("Faixa etaria", FAIXAS_ETARIAS, index=5)
        sexo = st.selectbox("Sexo biologico", SEXOS)
        gestante = False
        if sexo == 'Feminino' and ('Adulto' in faixa_etaria or 'Adolescente' in faixa_etaria):
            gestante = st.checkbox("Gravida")
        peso = st.number_input("Peso (kg)", 1.0, 200.0, 65.0, 0.5)

        st.header("Localizacao")
        municipio = st.selectbox("Municipio", list(MUNICIPIOS_INFO.keys()))
        info_mun = MUNICIPIOS_INFO[municipio]
        provincia = info_mun['provincia']
        st.markdown("**Provincia:** " + provincia)
        st.markdown("**Risco:** " + info_mun['risco'])

        st.header("Colheita")
        mes = st.selectbox("Mes", MESES, index=datetime.now().month - 1)
        estacao = ESTACOES_POR_MES[mes]
        st.markdown("**Estacao:** " + estacao)

        st.header("Antecedentes")
        status_genetico = st.selectbox("Hemoglobina (genetica)", STATUS_GENETICO)
        mordedura = st.checkbox("Mordedura animal recente")

    st.markdown(
        '<div style="margin-bottom:0.3rem;">'
        '<div style="font-size:1.6rem;font-weight:900;color:#1A1A18;letter-spacing:-0.04em;">Hemograma</div></div>',
        unsafe_allow_html=True
    )
    st.markdown(componente_linha_fina(), unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div style="color:#C9553A;font-weight:800;font-size:0.7rem;letter-spacing:0.14em;text-transform:uppercase;padding-bottom:0.6rem;margin-bottom:1.2rem;border-bottom:3px solid #C9553A;">Serie Vermelha</div>',
            unsafe_allow_html=True
        )
        hemoglobina = st.number_input("Hemoglobina (g/dL)", 3.0, 22.0, 12.5, 0.1)
        hematocrito = st.number_input("Hematocrito (%)", 10.0, 70.0, 38.0, 0.5)
        hemacias = st.number_input("Eritrocitos (x10^6/uL)", 2.0, 7.0, 4.5, 0.1)
        vcm = st.number_input("VCM (fL)", 50.0, 120.0, 88.0, 1.0)
        hcm = st.number_input("HCM (pg)", 15.0, 40.0, 29.0, 0.5)
        chcm = st.number_input("CHCM (g/dL)", 28.0, 40.0, 33.5, 0.5)
        rdw = st.number_input("RDW (%)", 10.0, 25.0, 13.5, 0.1)

    with col2:
        st.markdown(
            '<div style="color:#1A1A18;font-weight:800;font-size:0.7rem;letter-spacing:0.14em;text-transform:uppercase;padding-bottom:0.6rem;margin-bottom:1.2rem;border-bottom:3px solid #1A1A18;">Serie Branca</div>',
            unsafe_allow_html=True
        )
        leucocitos = st.number_input("Leucocitos (/mm3)", 500, 50000, 7500, 100)
        neutrofilos = st.number_input("Neutrofilos (%)", 10.0, 90.0, 58.0, 1.0)
        linfocitos = st.number_input("Linfocitos (%)", 5.0, 70.0, 32.0, 1.0)
        monocitos = st.number_input("Monocitos (%)", 0.0, 20.0, 6.0, 0.5)
        eosinofilos = st.number_input("Eosinofilos (%)", 0.0, 25.0, 3.0, 0.5)
        basofilos = st.number_input("Basofilos (%)", 0.0, 3.0, 0.5, 0.1)
        valido, soma = validar_leucograma(neutrofilos, linfocitos, monocitos, eosinofilos, basofilos)
        if not valido:
            st.warning("O diferencial soma " + str(round(soma, 1)) + "% — o esperado e proximo de 100%.")

    with col3:
        st.markdown(
            '<div style="color:#15291C;font-weight:800;font-size:0.7rem;letter-spacing:0.14em;text-transform:uppercase;padding-bottom:0.6rem;margin-bottom:1.2rem;border-bottom:3px solid #15291C;">Plaquetas e Outros</div>',
            unsafe_allow_html=True
        )
        plaquetas = st.number_input("Plaquetas (/mm3)", 5000, 1000000, 250000, 5000)
        vpm = st.number_input("VPM (fL)", 5.0, 15.0, 9.5, 0.5)
        reticulocitos = st.number_input("Reticulocitos (%)", 0.2, 15.0, 1.2, 0.1)

    st.markdown(componente_linha(), unsafe_allow_html=True)

    with st.form(key="form_analise"):
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit = st.form_submit_button("ANALISAR HEMOGRAMA →", use_container_width=True)

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

        gravidade, resultados, erro = processar_analise(modelo, encoders, features, dados)

        if erro:
            st.error("Erro no processamento: " + erro)
            return
        if not resultados:
            st.error("Nao consegui gerar resultados. Confere os dados.")
            return

        diag_principal = resultados[0][0]

        st.markdown(
            '<div style="margin-top:2.5rem;">'
            '<div style="font-size:1.6rem;font-weight:900;color:#1A1A18;letter-spacing:-0.04em;">Resultados</div></div>',
            unsafe_allow_html=True
        )
        st.markdown(componente_linha_fina(), unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            cores_grav = {
                "LEVE": ("background:#EDF2EE;color:#2D5A3D;border:2px solid #C4D4C8;", "LEVE"),
                "MODERADO": ("background:#FDF2E9;color:#C9553A;border:2px solid #F0C9B5;", "MODERADO"),
                "GRAVE": ("background:#FCEAEA;color:#8B1A1A;border:2px solid #E8B5B5;", "GRAVE"),
                "CRITICO": ("background:#1A1A18;color:#FAFAF8;border:2px solid #1A1A18;", "CRITICO"),
            }
            estilo_g, texto_g = cores_grav.get(gravidade, ("background:#F3F2EE;color:#1A1A18;border:2px solid #DDDCD7;", gravidade))
            st.markdown(
                '<div style="background:#FFFFFF;border:2px solid #DDDCD7;padding:1.3rem 1.4rem;margin-bottom:0.6rem;">'
                '<div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:700;">Gravidade</div>'
                '<div style="margin-top:0.8rem;"><span style="' + estilo_g + 'display:inline-block;padding:0.35rem 0.9rem;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">' + texto_g + '</span></div></div>',
                unsafe_allow_html=True
            )

        with col_r2:
            st.markdown(
                '<div style="background:#FFFFFF;border:2px solid #DDDCD7;padding:1.3rem 1.4rem;margin-bottom:0.6rem;">'
                '<div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:700;">Referenciar para</div>'
                '<div style="margin-top:0.8rem;font-weight:700;color:#1A1A18;font-size:0.95rem;">' + info_mun["hospital"] + '</div></div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div style="color:#8A8A82;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.14em;font-weight:700;margin-bottom:0.8rem;">Hipoteses diagnosticas</div>',
            unsafe_allow_html=True
        )

        for i, (diag, prob) in enumerate(resultados[:3]):
            num = "0" + str(i + 1)
            if i == 0:
                st.markdown(
                    '<div style="background:#FFFFFF;border:2px solid #DDDCD7;border-left:4px solid #1A1A18;padding:1.3rem 1.4rem;margin-bottom:0.6rem;">'
                    '<div style="display:flex;justify-content:space-between;align-items:center;">'
                    '<span style="font-size:1.1rem;font-weight:800;color:#1A1A18;letter-spacing:-0.02em;">' + num + ' — ' + diag + '</span>'
                    '<span style="background:#1A1A18;color:#FAFAF8;padding:0.45rem 1.1rem;font-weight:800;font-size:0.82rem;letter-spacing:0.02em;">' + str(round(prob, 1)) + '%</span>'
                    '</div></div>',
                    unsafe_allow_html=True
                )
                st.progress(prob / 100)
            else:
                st.markdown(
                    '<div style="background:#FFFFFF;border:2px solid #DDDCD7;padding:1.3rem 1.4rem;margin-bottom:0.6rem;">'
                    '<div style="display:flex;justify-content:space-between;align-items:center;">'
                    '<span style="color:#5A5A52;font-weight:600;font-size:0.9rem;">' + num + ' — ' + diag + '</span>'
                    '<span style="color:#8A8A82;font-weight:700;font-size:0.85rem;">' + str(round(prob, 1)) + '%</span>'
                    '</div></div>',
                    unsafe_allow_html=True
                )

        if diag_principal in CONDUTAS:
            cond = CONDUTAS[diag_principal]
            st.markdown(
                '<div style="color:#8A8A82;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.14em;font-weight:700;margin-bottom:0.8rem;">Conduta clinica</div>',
                unsafe_allow_html=True
            )
            if gravidade in ["GRAVE", "CRITICO"]:
                st.error("**Caso grave:** " + cond['grave'])
            else:
                st.info("**Conduta:** " + cond['leve'])

            st.markdown(
                '<div style="background:#FFFFFF;border:2px solid #DDDCD7;padding:1.3rem 1.4rem;margin-bottom:0.6rem;">'
                '<div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:700;margin-bottom:0.5rem;">Exame para confirmar</div>'
                '<div style="color:#1A1A18;font-weight:600;font-size:0.92rem;">' + cond["exame"] + '</div></div>',
                unsafe_allow_html=True
            )

            if cond['alertas']:
                with st.expander("Sinais de alarme"):
                    for a in cond['alertas']:
                        st.markdown("- " + a)

        st.markdown(
            '<div style="color:#8A8A82;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.14em;font-weight:700;margin-bottom:0.8rem;">Interpretacao do hemograma</div>',
            unsafe_allow_html=True
        )

        col_l1, col_l2 = st.columns(2)
        with col_l1:
            _, hb_l = classificar_valor(hemoglobina, 11.5, 16.5)
            st.metric("Hemoglobina", str(hemoglobina) + " g/dL", hb_l)
            _, plt_l = classificar_valor(plaquetas, 140000, 400000)
            st.metric("Plaquetas", formatar_numero(plaquetas) + "/mm3", plt_l)
            _, leu_l = classificar_valor(leucocitos, 4000, 10000)
            st.metric("Leucocitos", formatar_numero(leucocitos) + "/mm3", leu_l)
        with col_l2:
            _, vcm_l = classificar_valor(vcm, 80, 98)
            st.metric("VCM", str(vcm) + " fL", vcm_l)
            _, eos_l = classificar_valor(eosinofilos, 1, 5)
            st.metric("Eosinofilos", str(eosinofilos) + "%", eos_l)
            _, ret_l = classificar_valor(reticulocitos, 0.5, 2.5)
            st.metric("Reticulocitos", str(reticulocitos) + "%", ret_l)

        if status_genetico in ['Traço falciforme (AS)', 'Drepanocitose (SS)']:
            st.warning("**Hemoglobinopatia: " + status_genetico + ".** Seguimento no IHL ou centro de drepanocitose. Acido folico 5 mg/dia, beber muita agua, evitar frio.")

        if mordedura:
            st.error("**Mordedura animal — risco rabico!** Lavar a ferida com agua e sabao durante 15 minutos. Iniciar profilaxia anti-rabica sem esperar resultados.")

    st.markdown(componente_footer(), unsafe_allow_html=True)


def main():
    restaurar_sessao_url()
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
