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

# ─── Equipa do Consultório Médico Lucílio ───
EQUIPA_LUCILIO = {
    'dra_maria': {
        'nome': 'Dra. Maria Lucílio',
        'cargo': 'Directora Clínica · Medicina Geral',
        'iniciais': 'ML',
        'cor': '#1B6B3A',
        'disponivel': True,
        'bio': 'Mais de 15 anos a cuidar de famílias em Luanda. '
               'Especialista em medicina preventiva e saúde comunitária.',
        'horario': 'Seg–Sex · 08h–17h',
    },
    'dr_pedro': {
        'nome': 'Dr. Pedro Nsimba',
        'cargo': 'Médico · Clínica Geral e Pediatria',
        'iniciais': 'PN',
        'cor': '#15291C',
        'disponivel': True,
        'bio': 'Dedicado à saúde infantil. '
               'Acompanha crianças desde o nascimento até à adolescência.',
        'horario': 'Seg–Sex · 09h–18h',
    },
    'enf_teresa': {
        'nome': 'Enf.ª Teresa Mbuende',
        'cargo': 'Enfermeira-Chefe · Vacinação e Triagem',
        'iniciais': 'TM',
        'cor': '#C9553A',
        'disponivel': True,
        'bio': 'Responsável pela triagem e pelo programa de vacinação. '
               'Sempre disponível para tirar dúvidas sobre vacinas.',
        'horario': 'Seg–Sáb · 07h–14h',
    },
    'dr_joao': {
        'nome': 'Dr. João Kamutali',
        'cargo': 'Médico · Medicina Interna',
        'iniciais': 'JK',
        'cor': '#5A3E8B',
        'disponivel': False,
        'bio': 'Especialista em doenças crónicas e acompanhamento '
               'de pacientes com drepanocitose e hipertensão.',
        'horario': 'Ter–Sex · 10h–16h',
    },
    'sec_ana': {
        'nome': 'Ana Cristina',
        'cargo': 'Secretária · Marcação de Consultas',
        'iniciais': 'AC',
        'cor': '#8A6B3E',
        'disponivel': True,
        'bio': 'Trata de tudo o que é marcação, reagendamento '
               'e informações gerais. Fala contigo com todo o carinho.',
        'horario': 'Seg–Sex · 07h30–17h30',
    },
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


# ─── Funções de persistência ───

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


# ─── Funções de mensagens (chat persistente) ───

def carregar_mensagens():
    if os.path.exists(FICHEIRO_MENSAGENS):
        with open(FICHEIRO_MENSAGENS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def guardar_mensagens(dados):
    with open(FICHEIRO_MENSAGENS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def obter_conversa(telefone_cliente, id_membro):
    """Retorna a lista de mensagens entre um cliente e um membro."""
    mensagens = carregar_mensagens()
    chave = f"{telefone_cliente}___{id_membro}"
    return mensagens.get(chave, [])

def enviar_mensagem(telefone_cliente, id_membro, remetente, texto):
    """
    Guarda uma nova mensagem.
    remetente: 'cliente' ou 'membro'
    """
    mensagens = carregar_mensagens()
    chave = f"{telefone_cliente}___{id_membro}"
    if chave not in mensagens:
        mensagens[chave] = []
    mensagens[chave].append({
        'remetente': remetente,
        'texto': texto,
        'hora': datetime.now().strftime('%H:%M'),
        'data': datetime.now().strftime('%d/%m/%Y'),
        'timestamp': datetime.now().isoformat(),
    })
    guardar_mensagens(mensagens)

def contar_mensagens_nao_lidas(telefone_cliente, id_membro, perspectiva='cliente'):
    """Conta mensagens do outro lado que ainda não foram 'vistas'."""
    conversa = obter_conversa(telefone_cliente, id_membro)
    outro = 'membro' if perspectiva == 'cliente' else 'cliente'
    cont = 0
    for msg in reversed(conversa):
        if msg['remetente'] == outro:
            cont += 1
        else:
            break
    return cont


# ─── Validações ───

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


# ─── Modelo ML ───

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


# ══════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════

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
        font-size: 0.75rem !important;
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
        font-size: 1rem !important;
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

    div[data-baseweb="select"] { color: var(--text) !important; }

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

    div[data-baseweb="select"] * { color: var(--text) !important; }
    div[data-baseweb="select"] span {
        color: var(--text) !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
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
    }

    div[data-baseweb="popover"] li[aria-selected="true"] {
        color: var(--text) !important;
        background: var(--sec) !important;
        font-weight: 700 !important;
    }

    *:focus { outline: none !important; }
    input:focus, select:focus, textarea:focus { outline: none !important; }

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
    }

    .stButton > button:active {
        background: #0D1E13 !important;
        border-color: #0D1E13 !important;
        color: var(--bg) !important;
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

    .stTabs [data-baseweb="tab"]:hover { color: var(--text) !important; }

    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: var(--text) !important;
        font-weight: 800 !important;
        border-bottom: 3px solid var(--text) !important;
        box-shadow: none !important;
    }

    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

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

    div[data-testid="stDecoration"] { display: none !important; }

    button[data-testid="baseButton-header"] {
        color: #1A1A18 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #E8E6E1 !important;
        font-family: 'Dosis', sans-serif !important;
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

    [data-testid="stSidebar"] strong { color: #B5C4B8 !important; }

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

    [data-testid="stSidebar"] hr { border-color: #2A4435 !important; }

    button[kind="header"] {
        background: transparent !important;
        border: none !important;
        color: #E8E6E1 !important;
    }
    </style>"""


# ══════════════════════════════════════════════════════
#  Componentes visuais reutilizáveis
# ══════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════
#  TELAS
# ══════════════════════════════════════════════════════

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
            Fala directamente com a equipa do
            Consultório Médico Lucílio.
            Marca consultas, tira dúvidas, cuida de ti.
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


# ══════════════════════════════════════════════════════
#  PAINEL DO CLIENTE — CHAT COM EQUIPA LUCÍLIO
# ══════════════════════════════════════════════════════

def tela_painel_cliente():
    st.markdown(css_global(), unsafe_allow_html=True)
    st.markdown(css_painel_cliente(), unsafe_allow_html=True)

    cliente = st.session_state.get('cliente', {})
    nome = cliente.get('nome', 'Amigo')
    telefone = cliente.get('telefone', '')
    municipio = cliente.get('municipio', 'Luanda')
    primeiro_nome = nome.split()[0] if nome else 'Amigo'
    saudacao = obter_saudacao()

    # ─── Cabeçalho ───
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(componente_logo("pequeno"), unsafe_allow_html=True)
    with col_h2:
        st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)
        if st.button("SAIR", key="btn_sair_cliente"):
            for k in ['ecra', 'cliente', 'chat_membro_activo']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    st.markdown(componente_linha(), unsafe_allow_html=True)

    # ─── Se está dentro de uma conversa ───
    membro_activo = st.session_state.get('chat_membro_activo', None)

    if membro_activo and membro_activo in EQUIPA_LUCILIO:
        _renderizar_conversa(telefone, membro_activo, primeiro_nome)
        return

    # ─── Ecrã principal: saudação + lista da equipa ───
    st.markdown(f'''
    <div style="margin-bottom:0.5rem;">
        <div style="font-size:2.2rem;font-weight:900;color:#1A1A18;
            letter-spacing:-0.04em;line-height:1.1;">
            {saudacao},<br>{primeiro_nome}.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(componente_linha_fina(), unsafe_allow_html=True)

    # ─── Card do Consultório ───
    st.markdown(componente_card(f'''
    <div style="display:flex;align-items:center;gap:1rem;">
        <div style="width:52px;height:52px;background:#15291C;
            border-radius:0;display:flex;align-items:center;
            justify-content:center;flex-shrink:0;">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none"
                stroke="#D4E7DC" stroke-width="2" stroke-linecap="round"
                stroke-linejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
        </div>
        <div style="flex:1;">
            <div style="font-weight:800;color:#1A1A18;font-size:1.1rem;
                letter-spacing:-0.02em;">
                Consultório Médico Lucílio
            </div>
            <div style="color:#8A8A82;font-size:0.82rem;margin-top:0.2rem;">
                Luanda · Seg–Sáb · 07h30–18h
            </div>
        </div>
        <div>{componente_badge("Aberto", "sucesso")}</div>
    </div>
    ''', borda_esquerda="#15291C"), unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    st.markdown(f'''
    <div style="color:#5A5A52;font-size:0.9rem;line-height:1.8;
        margin-bottom:1.5rem;">
        Escolhe com quem queres falar. Podes marcar consulta,
        tirar dúvidas sobre exames, pedir informações ou simplesmente
        conversar sobre a tua saúde. Estamos aqui por ti.
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(componente_label("Equipa disponível"), unsafe_allow_html=True)

    # ─── Lista de membros ───
    for id_membro, membro in EQUIPA_LUCILIO.items():
        n_nao_lidas = contar_mensagens_nao_lidas(telefone, id_membro, 'cliente')

        badge_status = componente_badge(
            "Disponível", "sucesso"
        ) if membro['disponivel'] else componente_badge(
            "Indisponível", "normal"
        )

        notif_html = ""
        if n_nao_lidas > 0:
            notif_html = f'''
            <div style="background:#C9553A;color:#FFFFFF;width:22px;height:22px;
                border-radius:50%;display:flex;align-items:center;
                justify-content:center;font-size:0.65rem;font-weight:800;
                flex-shrink:0;">
                {n_nao_lidas}
            </div>'''

        conteudo = f'''
        <div style="display:flex;align-items:center;gap:1rem;">
            <div style="width:46px;height:46px;background:{membro['cor']};
                border-radius:0;display:flex;align-items:center;
                justify-content:center;color:white;font-weight:800;
                font-size:0.72rem;flex-shrink:0;letter-spacing:0.05em;">
                {membro['iniciais']}
            </div>
            <div style="flex:1;min-width:0;">
                <div style="font-weight:700;color:#1A1A18;font-size:0.92rem;
                    letter-spacing:-0.01em;">
                    {membro['nome']}
                </div>
                <div style="color:#8A8A82;font-size:0.75rem;margin-top:0.15rem;">
                    {membro['cargo']}
                </div>
                <div style="color:#B5B3AD;font-size:0.7rem;margin-top:0.1rem;">
                    {membro['horario']}
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:0.5rem;">
                {notif_html}
                {badge_status}
            </div>
        </div>'''
        st.markdown(componente_card(conteudo), unsafe_allow_html=True)

        if membro['disponivel']:
            if st.button(
                f"CONVERSAR COM {membro['nome'].upper().split('.')[-1].strip().split(' ')[0]}",
                key=f"btn_chat_{id_membro}",
                use_container_width=True
            ):
                st.session_state['chat_membro_activo'] = id_membro
                st.rerun()
        else:
            st.markdown(f'''
            <div style="text-align:center;color:#B5B3AD;font-size:0.75rem;
                padding:0.5rem 0 0.8rem 0;font-weight:600;
                letter-spacing:0.08em;">
                Indisponível de momento — tenta mais tarde
            </div>
            ''', unsafe_allow_html=True)

    st.markdown(componente_linha(), unsafe_allow_html=True)

    # ─── Informação rápida ───
    st.markdown(componente_label("Informação rápida"), unsafe_allow_html=True)

    st.markdown(componente_card(f'''
    <div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.12em;font-weight:700;margin-bottom:0.5rem;">
        Morada
    </div>
    <div style="color:#1A1A18;font-size:0.92rem;line-height:1.7;">
        Consultório Médico Lucílio<br>
        Luanda, Angola<br>
        <span style="color:#8A8A82;">Tel: +244 923 000 000</span>
    </div>
    '''), unsafe_allow_html=True)

    st.markdown(componente_card(f'''
    <div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;
        letter-spacing:0.12em;font-weight:700;margin-bottom:0.5rem;">
        Serviços
    </div>
    <div style="color:#5A5A52;font-size:0.88rem;line-height:1.8;">
        Consultas de clínica geral · Pediatria · Vacinação ·
        Medicina interna · Exames laboratoriais · Check-ups ·
        Acompanhamento de doenças crónicas
    </div>
    '''), unsafe_allow_html=True)

    st.markdown(componente_footer(), unsafe_allow_html=True)


def _renderizar_conversa(telefone, id_membro, primeiro_nome):
    """Renderiza o ecrã de conversa com um membro específico."""
    membro = EQUIPA_LUCILIO[id_membro]
    conversa = obter_conversa(telefone, id_membro)

    # ─── Cabeçalho da conversa ───
    if st.button("← VOLTAR", key="btn_voltar_chat"):
        del st.session_state['chat_membro_activo']
        st.rerun()

    st.markdown(f'''
    <div style="display:flex;align-items:center;gap:1rem;
        padding:1rem 0;margin-bottom:0.5rem;">
        <div style="width:50px;height:50px;background:{membro['cor']};
            border-radius:0;display:flex;align-items:center;
            justify-content:center;color:white;font-weight:800;
            font-size:0.75rem;flex-shrink:0;letter-spacing:0.05em;">
            {membro['iniciais']}
        </div>
        <div style="flex:1;">
            <div style="font-weight:800;color:#1A1A18;font-size:1.1rem;
                letter-spacing:-0.02em;">
                {membro['nome']}
            </div>
            <div style="color:#8A8A82;font-size:0.78rem;margin-top:0.15rem;">
                {membro['cargo']}
            </div>
        </div>
        <div>{componente_badge("Online", "sucesso") if membro['disponivel'] else componente_badge("Offline", "normal")}</div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(componente_linha(), unsafe_allow_html=True)

    # ─── Bio do membro ───
    if not conversa:
        st.markdown(f'''
        <div style="background:#F3F2EE;border:2px solid #DDDCD7;
            border-radius:0;padding:1.3rem;margin-bottom:1.5rem;">
            <div style="color:#8A8A82;font-size:0.65rem;text-transform:uppercase;
                letter-spacing:0.12em;font-weight:700;margin-bottom:0.5rem;">
                Sobre
            </div>
            <div style="color:#5A5A52;font-size:0.88rem;line-height:1.8;">
                {membro['bio']}
            </div>
            <div style="color:#B5B3AD;font-size:0.78rem;margin-top:0.8rem;">
                Escreve a tua primeira mensagem. Estamos aqui para te ajudar.
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # ─── Mensagens ───
    if conversa:
        data_anterior = None
        for msg in conversa:
            # Separador de data
            if msg.get('data') != data_anterior:
                data_anterior = msg.get('data', '')
                st.markdown(f'''
                <div style="text-align:center;margin:1.2rem 0;">
                    <span style="background:#F3F2EE;color:#B5B3AD;
                        font-size:0.65rem;font-weight:700;
                        letter-spacing:0.1em;text-transform:uppercase;
                        padding:0.3rem 1rem;border:1px solid #DDDCD7;">
                        {data_anterior}
                    </span>
                </div>
                ''', unsafe_allow_html=True)

            if msg['remetente'] == 'cliente':
                # Mensagem do cliente (direita)
                st.markdown(f'''
                <div style="display:flex;justify-content:flex-end;
                    margin-bottom:0.6rem;">
                    <div style="background:#15291C;color:#E8E6E1;
                        padding:0.9rem 1.2rem;max-width:75%;
                        border-radius:0;">
                        <div style="font-size:0.9rem;line-height:1.7;
                            font-weight:500;">
                            {msg['texto']}
                        </div>
                        <div style="text-align:right;color:#5A6B5E;
                            font-size:0.65rem;margin-top:0.4rem;
                            font-weight:600;">
                            {msg['hora']}
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                # Mensagem do membro (esquerda)
                st.markdown(f'''
                <div style="display:flex;justify-content:flex-start;
                    margin-bottom:0.6rem;gap:0.5rem;">
                    <div style="width:28px;height:28px;
                        background:{membro['cor']};border-radius:0;
                        display:flex;align-items:center;
                        justify-content:center;color:white;
                        font-weight:800;font-size:0.55rem;
                        flex-shrink:0;margin-top:0.2rem;">
                        {membro['iniciais']}
                    </div>
                    <div style="background:#FFFFFF;color:#1A1A18;
                        padding:0.9rem 1.2rem;max-width:75%;
                        border:2px solid #DDDCD7;border-radius:0;">
                        <div style="font-size:0.9rem;line-height:1.7;
                            font-weight:500;">
                            {msg['texto']}
                        </div>
                        <div style="color:#B5B3AD;font-size:0.65rem;
                            margin-top:0.4rem;font-weight:600;">
                            {msg['hora']}
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    # ─── Campo de envio ───
    with st.form(key=f"form_msg_{id_membro}", clear_on_submit=True):
        st.markdown(componente_label("Escreve a tua mensagem"), unsafe_allow_html=True)

        texto_msg = st.text_input(
            "MENSAGEM",
            placeholder=f"Escreve para {membro['nome'].split('.')[-1].strip().split(' ')[0]}...",
            key=f"input_msg_{id_membro}",
            label_visibility="collapsed"
        )

        col_s1, col_s2 = st.columns([3, 1])
        with col_s2:
            enviado = st.form_submit_button("ENVIAR →", use_container_width=True)

        if enviado and texto_msg and texto_msg.strip():
            enviar_mensagem(telefone, id_membro, 'cliente', texto_msg.strip())

            # ─── Resposta automática humanizada ───
            _gerar_resposta_automatica(telefone, id_membro, texto_msg.strip(), primeiro_nome)

            st.rerun()

    # ─── Sugestões rápidas ───
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(componente_label("Sugestões rápidas"), unsafe_allow_html=True)

    sugestoes = _obter_sugestoes(id_membro)
    cols = st.columns(len(sugestoes))
    for i, (sug_texto, sug_btn) in enumerate(sugestoes):
        with cols[i]:
            if st.button(sug_btn, key=f"sug_{id_membro}_{i}", use_container_width=True):
                enviar_mensagem(telefone, id_membro, 'cliente', sug_texto)
                _gerar_resposta_automatica(telefone, id_membro, sug_texto, primeiro_nome)
                st.rerun()


def _obter_sugestoes(id_membro):
    """Retorna sugestões de mensagens rápidas por tipo de membro."""
    sugestoes_por_membro = {
        'dra_maria': [
            ("Quero marcar uma consulta geral.", "MARCAR CONSULTA"),
            ("Tenho tido febres. O que devo fazer?", "TENHO FEBRE"),
            ("Preciso de um check-up completo.", "CHECK-UP"),
        ],
        'dr_pedro': [
            ("Quero marcar consulta para o meu filho.", "CONSULTA CRIANÇA"),
            ("O meu bebé tem febre. É grave?", "BEBÉ COM FEBRE"),
            ("Quando devo vacinar o meu filho?", "VACINAS"),
        ],
        'enf_teresa': [
            ("Quais vacinas o meu filho precisa?", "CALENDÁRIO VACINAL"),
            ("Preciso de uma triagem rápida.", "TRIAGEM"),
            ("Posso ir sem marcação?", "SEM MARCAÇÃO"),
        ],
        'dr_joao': [
            ("Tenho drepanocitose e preciso de acompanhamento.", "DREPANOCITOSE"),
            ("A minha tensão está alta. O que faço?", "HIPERTENSÃO"),
            ("Preciso de seguimento para doença crónica.", "DOENÇA CRÓNICA"),
        ],
        'sec_ana': [
            ("Quero marcar uma consulta.", "MARCAR"),
            ("Preciso remarcar a minha consulta.", "REMARCAR"),
            ("Qual é o horário de funcionamento?", "HORÁRIO"),
        ],
    }
    return sugestoes_por_membro.get(id_membro, [
        ("Olá, preciso de ajuda.", "AJUDA"),
        ("Quero marcar consulta.", "MARCAR"),
    ])


def _gerar_resposta_automatica(telefone, id_membro, texto_cliente, nome_cliente):
    """
    Gera uma resposta automática humanizada com base no contexto.
    Simula a resposta do membro da equipa.
    """
    membro = EQUIPA_LUCILIO[id_membro]
    texto_lower = texto_cliente.lower()

    # ─── Respostas por contexto ───
    if any(p in texto_lower for p in ['marcar', 'consulta', 'agendar', 'marcação']):
        respostas = {
            'dra_maria': (
                f"Olá {nome_cliente}! Claro que sim. "
                f"Temos horários disponíveis esta semana. "
                f"Preferes de manhã ou à tarde? "
                f"Assim que me disseres, reservo logo para ti."
            ),
            'dr_pedro': (
                f"Olá {nome_cliente}! Vamos tratar disso. "
                f"A criança tem quantos anos? Assim consigo "
                f"preparar melhor a consulta. Diz-me também "
                f"se é a primeira vez que vem cá."
            ),
            'enf_teresa': (
                f"Olá {nome_cliente}! Para marcação de consulta, "
                f"o melhor é falares com a Ana Cristina, a nossa "
                f"secretária. Ela trata de tudo! Mas se precisares "
                f"de triagem ou vacinação, estou cá para ti."
            ),
            'dr_joao': (
                f"Olá {nome_cliente}! Vou pedir à Ana Cristina "
                f"para te encaixar na minha agenda. Enquanto isso, "
                f"podes dizer-me que medicação estás a tomar "
                f"actualmente?"
            ),
            'sec_ana': (
                f"Olá {nome_cliente}! Com todo o gosto. "
                f"Com qual médico gostarias de marcar? "
                f"Temos a Dra. Maria (clínica geral), "
                f"o Dr. Pedro (pediatria) e o Dr. João "
                f"(medicina interna). Diz-me qual preferes "
                f"e o melhor horário para ti."
            ),
        }
        resposta = respostas.get(id_membro, f"Olá {nome_cliente}! Vamos tratar disso.")

    elif any(p in texto_lower for p in ['febre', 'febres', 'temperatura']):
        respostas = {
            'dra_maria': (
                f"{nome_cliente}, febre é sempre para levar a sério, "
                f"especialmente aqui em Luanda. Há quantos dias tens febre? "
                f"E tens outros sintomas — dores no corpo, dor de cabeça, "
                f"vómitos? Enquanto isso, bebe muita água e toma paracetamol "
                f"se a febre subir acima de 38°C."
            ),
            'dr_pedro': (
                f"Vamos com calma, {nome_cliente}. A criança tem febre "
                f"há quanto tempo? Está a comer e a beber normalmente? "
                f"Se a febre passar de 38.5°C, dá paracetamol na dose "
                f"certa para o peso. E se puder, vem cá amanhã logo "
                f"de manhã para fazermos um teste rápido de malária."
            ),
            'enf_teresa': (
                f"{nome_cliente}, febre pode ser muita coisa. "
                f"O melhor é vires cá para uma triagem rápida — "
                f"fazemos teste de malária em 15 minutos. "
                f"Podes vir logo de manhã sem marcação."
            ),
        }
        resposta = respostas.get(id_membro, (
            f"{nome_cliente}, se tens febre, o mais seguro é vires ao "
            f"consultório para fazermos uma avaliação. Não deixes passar."
        ))

    elif any(p in texto_lower for p in ['check-up', 'checkup', 'exames', 'exame']):
        resposta = (
            f"Boa ideia, {nome_cliente}! Prevenir é sempre melhor. "
            f"O nosso check-up inclui hemograma completo, "
            f"teste de malária, glicemia e tensão arterial. "
            f"Queres que te marque um horário esta semana?"
        )

    elif any(p in texto_lower for p in ['vacina', 'vacinas', 'vacinação', 'calendário']):
        respostas = {
            'enf_teresa': (
                f"{nome_cliente}, aqui no consultório fazemos todas as "
                f"vacinas do calendário nacional. Se me disseres a idade "
                f"da criança, digo-te exactamente quais faltam. "
                f"Traz o boletim de vacinas se tiveres."
            ),
            'dr_pedro': (
                f"As vacinas são fundamentais, {nome_cliente}! "
                f"A Enf.ª Teresa é a melhor pessoa para te orientar "
                f"sobre isso — ela conhece o calendário vacinal de cor. "
                f"Mas se tiveres dúvidas médicas, estou cá."
            ),
        }
        resposta = respostas.get(id_membro, (
            f"{nome_cliente}, para questões de vacinação, "
            f"a nossa Enf.ª Teresa é a pessoa ideal. "
            f"Ela vai ajudar-te com tudo."
        ))

    elif any(p in texto_lower for p in ['drepanocitose', 'drep', 'falciforme', 'ss']):
        respostas = {
            'dr_joao': (
                f"{nome_cliente}, fazes bem em procurar acompanhamento. "
                f"A drepanocitose precisa de seguimento regular. "
                f"Estás a tomar ácido fólico? E como tens passado — "
                f"tiveste alguma crise recente? Conta-me tudo "
                f"para eu poder ajudar-te melhor."
            ),
            'dra_maria': (
                f"{nome_cliente}, para drepanocitose o Dr. João é "
                f"quem melhor te pode acompanhar. Vou pedir à Ana "
                f"para te marcar com ele. Entretanto, lembra-te de "
                f"beber muita água e evitar o frio."
            ),
        }
        resposta = respostas.get(id_membro, (
            f"{nome_cliente}, o Dr. João Kamutali é o nosso especialista "
            f"em drepanocitose. Vou encaminhar-te para ele."
        ))

    elif any(p in texto_lower for p in ['horário', 'horario', 'aberto', 'funciona']):
        resposta = (
            f"Claro, {nome_cliente}! O consultório funciona de "
            f"segunda a sexta das 07h30 às 18h, e ao sábado "
            f"das 07h30 às 14h. Domingo estamos fechados. "
            f"Precisas de mais alguma coisa?"
        )

    elif any(p in texto_lower for p in ['remarcar', 'reagendar', 'mudar', 'alterar']):
        resposta = (
            f"Sem problema, {nome_cliente}! Diz-me a data que "
            f"tinhas marcada e o novo horário que preferes. "
            f"Vou verificar a disponibilidade e confirmo-te já."
        )

    elif any(p in texto_lower for p in ['obrigado', 'obrigada', 'agradeço', 'valeu']):
        resposta = (
            f"De nada, {nome_cliente}! É para isso que estamos cá. "
            f"Qualquer coisa, não hesites em escrever. "
            f"Cuida-te bem! 🙏"
        )

    elif any(p in texto_lower for p in ['olá', 'ola', 'oi', 'bom dia', 'boa tarde', 'boa noite']):
        saudacao = obter_saudacao()
        resposta = (
            f"{saudacao}, {nome_cliente}! Que bom falar contigo. "
            f"Em que te posso ajudar hoje?"
        )

    elif any(p in texto_lower for p in ['triagem', 'sem marcação', 'urgente', 'urgência']):
        resposta = (
            f"{nome_cliente}, podes vir directamente ao consultório "
            f"para triagem — não precisas de marcação para isso. "
            f"A Enf.ª Teresa faz a avaliação inicial e, se for "
            f"necessário, és atendido logo pelo médico. "
            f"O melhor é vires logo de manhã."
        )

    elif any(p in texto_lower for p in ['tensão', 'tensao', 'pressão', 'pressao', 'hipertensão']):
        resposta = (
            f"{nome_cliente}, a tensão alta não dá para brincar. "
            f"Sabes os valores que tens medido? Se estiver acima "
            f"de 14/9, convém vires cá para fazermos uma avaliação "
            f"completa. Enquanto isso, reduz o sal na comida "
            f"e tenta caminhar um pouco todos os dias."
        )

    elif any(p in texto_lower for p in ['dor', 'dores', 'doi', 'doer']):
        resposta = (
            f"{nome_cliente}, diz-me onde é a dor e há quanto tempo "
            f"sentes. É uma dor constante ou vai e vem? "
            f"Isso ajuda-me a perceber melhor o que se passa. "
            f"Se a dor for muito forte, vem ao consultório "
            f"— não fiques a sofrer em casa."
        )

    else:
        # Resposta genérica mas calorosa
        respostas_genericas = [
            (
                f"{nome_cliente}, obrigado por partilhares isso comigo. "
                f"Podes dar-me mais detalhes para eu te ajudar melhor? "
                f"Estou aqui com toda a atenção."
            ),
            (
                f"Entendi, {nome_cliente}. Deixa-me perceber melhor — "
                f"podes explicar-me um pouco mais? Quero ter a certeza "
                f"de que te dou a melhor orientação possível."
            ),
            (
                f"{nome_cliente}, estou a ouvir-te. Conta-me mais "
                f"para eu poder ajudar-te da melhor forma. "
                f"Aqui no Consultório Lucílio estamos sempre do teu lado."
            ),
        ]
        import random
        resposta = random.choice(respostas_genericas)

    # Simular um pequeno atraso antes da resposta
    enviar_mensagem(telefone, id_membro, 'membro', resposta)


# ══════════════════════════════════════════════════════
#  PAINEL DA EMPRESA
# ══════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════

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
