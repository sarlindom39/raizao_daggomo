import streamlit as st
import pandas as pd
import numpy as np
import pickle
import time
from datetime import datetime

st.set_page_config(
    page_title="RAÍZAO EXPERIMENT",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        except:
            st.session_state["erro_login"] = True

    if st.session_state.get("autenticado", False):
        return True

    st.markdown("""
    <style>
    .login-box {
        max-width: 380px;
        margin: 80px auto;
        padding: 2.5rem;
        background: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
    }
    .login-title {
        text-align: center;
        color: #0F172A;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .login-subtitle {
        text-align: center;
        color: #64748B;
        font-size: 0.875rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<p class="login-title">RAÍZAO EXPERIMENT</p>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Acesso restrito</p>', unsafe_allow_html=True)
        st.text_input("Utilizador", key="input_usuario", placeholder="Digite o utilizador")
        st.text_input("Senha", type="password", key="input_senha", placeholder="Digite a senha")
        if st.button("Entrar", type="primary", use_container_width=True):
            processar_login()
            if st.session_state.get("autenticado"):
                st.rerun()
        if st.session_state.get("erro_login", False):
            st.error("Credenciais inválidas")
            st.session_state["erro_login"] = False
        st.markdown('</div>', unsafe_allow_html=True)

    return False

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

.stApp { background-color: #F8FAFC; color: #0F172A; }
.main .block-container { padding: 2.5rem 4rem; max-width: 1300px; }

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

.stFormSubmitButton > button {
    background-color: #312E81 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.75rem 2.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}

.stFormSubmitButton > button:hover {
    background-color: #3730A3 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
}

[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

[data-testid="stMetric"] label {
    color: #64748B !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #0F172A !important;
    font-weight: 700 !important;
}

.stProgress > div > div { background-color: #312E81 !important; border-radius: 4px; }
.stProgress > div { background-color: #E2E8F0 !important; border-radius: 4px; }

.card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.badge {
    display: inline-block;
    padding: 0.35rem 0.85rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.025em;
}

.badge-leve { background-color: #F0FDF4; color: #166534; border: 1px solid #DCFCE7; }
.badge-moderado { background-color: #FFFBEB; color: #92400E; border: 1px solid #FEF3C7; }
.badge-grave { background-color: #FEF2F2; color: #991B1B; border: 1px solid #FEE2E2; }
.badge-critico { background-color: #7F1D1D; color: #FFFFFF; }

.status-operacional {
    background-color: #F0FDF4;
    border: 1px solid #DCFCE7;
    border-left: 4px solid #166534;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin: 1.5rem 0;
}

.status-operacional p { margin: 0; color: #166534; font-weight: 600; }

.aviso-institucional {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #475569;
    border-radius: 8px;
    padding: 1.25rem;
    margin: 1.5rem 0;
}

.aviso-institucional p { margin: 0; color: #334155; font-size: 0.9rem; line-height: 1.6; }

.serie-vermelha-header {
    color: #B91C1C !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border-bottom: 2px solid #B91C1C;
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem !important;
}

.serie-branca-header {
    color: #475569 !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border-bottom: 2px solid #475569;
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem !important;
}

.serie-plaquetas-header {
    color: #4338CA !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border-bottom: 2px solid #4338CA;
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem !important;
}

hr { border: none; height: 1px; background-color: #E2E8F0; margin: 2rem 0; }

.text-muted { color: #64748B; font-size: 0.875rem; }
.text-small { font-size: 0.8125rem; }

.footer {
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
    border-top: 1px solid #E2E8F0;
    color: #94A3B8;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

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
    'Janeiro': 'Chuvas',
    'Fevereiro': 'Chuvas (pico)',
    'Março': 'Chuvas (pico)',
    'Abril': 'Chuvas (pico)',
    'Maio': 'Chuvas (a acabar)',
    'Junho': 'Cacimbo',
    'Julho': 'Cacimbo',
    'Agosto': 'Cacimbo',
    'Setembro': 'Transição',
    'Outubro': 'Chuvas (início)',
    'Novembro': 'Chuvas',
    'Dezembro': 'Chuvas'
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
            'Artesunato EV 2,4 mg/kg às 0h, 12h e 24h, depois 1x/dia '
            'até tolerar via oral. Controlar Hb no dia 7 e 14. '
            'Se a parasitémia não baixar em 24h, reavaliar dose.'
        ),
        'exame': 'Gota espessa ou teste rápido (TDR)',
        'alertas': [
            'Convulsões',
            'Não consegue acordar / confuso',
            'Vómitos que não param',
            'Urina escura (cor de coca-cola)',
            'Falta de ar',
            'Olhos amarelos',
            'Prostração — não come, não bebe, não anda'
        ]
    },
    'Dengue': {
        'leve': (
            'Hidratar bem por via oral (60–80 mL/kg/dia). Paracetamol '
            'para a febre. Nada de ibuprofeno nem aspirina — aumenta '
            'o risco de sangramento.'
        ),
        'grave': (
            'Soro EV com controlo do hematócrito de 2/2h. Se o Ht subir '
            'mais de 20%, aumentar o ritmo da hidratação.'
        ),
        'exame': 'NS1 (nos primeiros dias) ou IgM/IgG (a partir do 5.º dia)',
        'alertas': [
            'Dor de barriga forte e que não passa',
            'Vómitos sem parar',
            'Sangramento das gengivas ou nariz',
            'Muito sonolento, sem energia'
        ]
    },
    'Drepanocitose (SS)': {
        'leve': (
            'Ácido fólico 5 mg/dia, todos os dias. Beber muita água. '
            'Evitar frio e esforço físico exagerado. '
            'Consulta de rotina no IHL ou no centro de drepanocitose.'
        ),
        'grave': (
            'Crise vaso-oclusiva: analgesia forte (tramadol ou morfina '
            'conforme a dor) + soro EV + oxigénio se SpO2 < 95%. '
            'Referenciar ao IHL com urgência.'
        ),
        'exame': 'Electroforese de hemoglobina',
        'alertas': [
            'Febre (num drepanocítico é sempre urgência)',
            'Dor no peito — pode ser síndrome torácica aguda',
            'Priapismo (erecção dolorosa que não passa)',
            'Sinais de AVC — boca torta, braço fraco, fala arrastada'
        ]
    },
    'Anemia Ferropriva': {
        'leve': (
            'Sulfato ferroso durante 3 a 6 meses. Tomar em jejum com '
            'sumo de limão (a vitamina C ajuda a absorver). Avisar que '
            'as fezes vão ficar escuras — é normal.'
        ),
        'grave': (
            'Se Hb abaixo de 5 g/dL, avaliar transfusão. '
            'Investigar a causa — parasitose? Hemorragia oculta?'
        ),
        'exame': 'Ferritina sérica (é o mais fiável para ver reservas de ferro)',
        'alertas': [
            'Falta de ar em repouso',
            'Coração muito acelerado',
            'Palidez intensa — verificar palmas das mãos e conjuntivas'
        ]
    },
    'Cólera': {
        'leve': (
            'Sais de reidratação oral (SRO) conforme protocolo OMS. '
            'Preparar 1 saqueta em 1 litro de água tratada. '
            'Dar aos poucos, com frequência.'
        ),
        'grave': (
            'Ringer Lactato EV em bólus até melhorar a hemodinâmica. '
            'Azitromicina 1 g dose única. Notificar a DPS imediatamente.'
        ),
        'exame': 'Cultura de fezes (coprocultura)',
        'alertas': [
            'Olhos encovados, boca seca',
            'Pele que demora a voltar ao lugar quando puxada (sinal da prega)',
            'Criança sem lágrimas ao chorar',
            'Sonolência ou agitação extrema'
        ]
    },
    'Febre Tifóide': {
        'leve': (
            'Ciprofloxacina 500 mg de 12/12h durante 7 a 14 dias. '
            'Se for criança, preferir azitromicina. '
            'Manter boa hidratação e alimentação leve.'
        ),
        'grave': (
            'Ceftriaxona EV 2 g/dia + internamento. '
            'Vigiar sinais de perfuração intestinal — '
            'barriga dura, dor intensa, febre que dispara.'
        ),
        'exame': 'Hemocultura (mais fiável) ou coprocultura',
        'alertas': [
            'Barriga dura como tábua — pode ser perfuração',
            'Confusão mental',
            'Sangue nas fezes'
        ]
    },
    'Parasitose Intestinal': {
        'leve': (
            'Albendazol 400 mg dose única (para crianças acima de 2 anos '
            'e adultos). Repetir desparasitação de 6/6 meses. '
            'Reforçar lavagem das mãos e tratamento da água.'
        ),
        'grave': (
            'Albendazol 400 mg durante 3 dias + sulfato ferroso '
            'se houver anemia associada. Investigar carga parasitária.'
        ),
        'exame': 'Parasitológico de fezes (3 amostras em dias diferentes é o ideal)',
        'alertas': [
            'Barriga muito inchada e dura — pode haver obstrução',
            'Desnutrição grave, especialmente em crianças'
        ]
    },
    'Tuberculose': {
        'leve': (
            'Esquema DOTS — fase intensiva com RHZE durante 2 meses, '
            'depois RH durante 4 meses. O doente não pode abandonar '
            'o tratamento. Toma observada directamente.'
        ),
        'grave': (
            'Internamento. Investigar formas extrapulmonares '
            '(meníngea, ganglionar, óssea). Se HIV+, coordenar '
            'com o programa TARV — atenção às interacções.'
        ),
        'exame': 'Baciloscopia (BK) ou GeneXpert (mais rápido e detecta resistência)',
        'alertas': [
            'Tossir sangue (hemoptise)',
            'Perda de peso acima de 10% do peso habitual',
            'Suores nocturnos que encharcam a roupa',
            'Tosse há mais de 2 semanas sem melhoria'
        ]
    },
    'HIV/SIDA': {
        'leve': (
            'TARV de 1.ª linha: Dolutegravir + Tenofovir + Lamivudina '
            '(comprimido único diário). Adesão é tudo — tomar todos os '
            'dias à mesma hora. Controlo de CD4 e carga viral aos 6 meses.'
        ),
        'grave': (
            'Se houver infecção oportunista activa, tratar primeiro. '
            'Iniciar TARV 2 semanas depois (excepto na meningite '
            'criptocócica — aí esperar 4–6 semanas). '
            'Referenciar ao CTA mais próximo.'
        ),
        'exame': 'Teste rápido HIV + CD4 + carga viral',
        'alertas': [
            'Infecções oportunistas de repetição',
            'Perda de peso sem explicação',
            'Diarreia que dura mais de 1 mês',
            'Candidíase oral persistente'
        ]
    },
    'Raiva (Mordedura)': {
        'leve': (
            'Lavar a ferida imediatamente com água e sabão durante '
            '15 minutos — isto salva vidas. Vacina antirrábica nos '
            'dias 0, 3, 7 e 14. Não suturar a ferida.'
        ),
        'grave': (
            'Soro antirrábico + vacina. Não esperar por resultados. '
            'Se o animal morreu ou desapareceu, tratar como caso '
            'de alto risco. Cada hora conta.'
        ),
        'exame': 'Não esperar confirmação laboratorial — tratar de imediato',
        'alertas': [
            'Medo de água (hidrofobia)',
            'Medo de vento (aerofobia)',
            'Agitação intensa e desorientação',
            'Se estes sinais já apareceram, o prognóstico é muito mau'
        ]
    },
    'Saudável': {
        'leve': (
            'Hemograma dentro dos valores normais. Orientar prevenção: '
            'rede mosquiteira, água tratada, desparasitação regular, '
            'vacinação em dia.'
        ),
        'grave': 'Não se aplica.',
        'exame': 'Sem necessidade de exames adicionais',
        'alertas': []
    }
}


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

    for texto, progresso in [
        ("A validar dados do paciente...", 20),
        ("A analisar parâmetros do hemograma...", 50),
        ("A cruzar com dados epidemiológicos...", 80),
        ("A finalizar...", 100)
    ]:
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


def main():
    if not verificar_acesso():
        st.stop()

    col_header1, col_header2 = st.columns([3, 1])

    with col_header1:
        st.title("RAÍZAO EXPERIMENT")
        st.markdown(
            '<p style="color: #64748B; font-size: 1rem; margin-top: -0.5rem;">'
            'Apoio à decisão clínica para Luanda e Icolo e Bengo</p>',
            unsafe_allow_html=True
        )

    with col_header2:
        st.markdown(f'''
        <div style="text-align: right; padding-top: 1rem; color: #94A3B8;
             font-size: 0.875rem;">
            {datetime.now().strftime("%d/%m/%Y")}
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="aviso-institucional">
        <p><strong>Atenção:</strong> Este sistema serve de apoio — não substitui
        a avaliação clínica presencial nem o julgamento do médico.
        Os resultados devem ser sempre interpretados no contexto do doente.</p>
    </div>
    ''', unsafe_allow_html=True)

    modelo, encoders, features = carregar_modelo()

    if modelo is None:
        st.error("Modelo não encontrado. Corra primeiro: python modelo_ml.py")
        return

    st.markdown('''
    <div class="status-operacional">
        <p>Sistema pronto — modelo carregado com sucesso</p>
    </div>
    ''', unsafe_allow_html=True)

    with st.sidebar:
        st.header("Dados do Paciente")

        st.subheader("Identificação")
        faixa_etaria = st.selectbox("Faixa etária", FAIXAS_ETARIAS, index=5)
        sexo = st.selectbox("Sexo biológico", SEXOS)

        gestante = False
        if sexo == 'Feminino' and ('Adulto' in faixa_etaria or 'Adolescente' in faixa_etaria):
            gestante = st.checkbox("Grávida")

        peso = st.number_input("Peso (kg)", 1.0, 200.0, 65.0, 0.5)

        st.subheader("Localização")
        municipio = st.selectbox("Município", list(MUNICIPIOS_INFO.keys()))
        info_mun = MUNICIPIOS_INFO[municipio]
        provincia = info_mun['provincia']

        st.markdown(f"**Província:** {provincia}")
        st.markdown(f"**Risco epidemiológico:** {info_mun['risco']}")

        st.subheader("Quando foi colhido")
        mes = st.selectbox("Mês da coleta", MESES, index=datetime.now().month - 1)
        estacao = ESTACOES_POR_MES[mes]
        st.markdown(f"**Estação:** {estacao}")

        st.subheader("Antecedentes")
        status_genetico = st.selectbox("Hemoglobina (genética)", STATUS_GENETICO)
        mordedura = st.checkbox("Mordedura de animal recente")

    st.header("Hemograma")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<p class="serie-vermelha-header">Série Vermelha</p>',
            unsafe_allow_html=True
        )
        hemoglobina = st.number_input("Hemoglobina (g/dL)", 3.0, 22.0, 12.5, 0.1)
        hematocrito = st.number_input("Hematócrito (%)", 10.0, 70.0, 38.0, 0.5)
        hemacias = st.number_input("Eritrócitos (×10⁶/µL)", 2.0, 7.0, 4.5, 0.1)
        vcm = st.number_input("VCM (fL)", 50.0, 120.0, 88.0, 1.0)
        hcm = st.number_input("HCM (pg)", 15.0, 40.0, 29.0, 0.5)
        chcm = st.number_input("CHCM (g/dL)", 28.0, 40.0, 33.5, 0.5)
        rdw = st.number_input("RDW (%)", 10.0, 25.0, 13.5, 0.1)

    with col2:
        st.markdown(
            '<p class="serie-branca-header">Série Branca</p>',
            unsafe_allow_html=True
        )
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
            st.warning(f"O diferencial soma {soma:.1f}% — devia estar perto de 100%.")

    with col3:
        st.markdown(
            '<p class="serie-plaquetas-header">Plaquetas e Outros</p>',
            unsafe_allow_html=True
        )
        plaquetas = st.number_input("Plaquetas (/mm³)", 5000, 1000000, 250000, 5000)
        vpm = st.number_input("VPM (fL)", 5.0, 15.0, 9.5, 0.5)
        reticulocitos = st.number_input("Reticulócitos (%)", 0.2, 15.0, 1.2, 0.1)

    st.markdown("---")

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
                st.error("Não foi possível gerar resultados. Verifique os dados.")
                return

            diag_principal = resultados[0][0]

            st.header("Resultados")

            col_r1, col_r2 = st.columns(2)

            with col_r1:
                classe = obter_classe_gravidade(gravidade)
                st.markdown(f'''
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
                ''', unsafe_allow_html=True)

            with col_r2:
                st.markdown(f'''
                <div class="card">
                    <div class="text-muted text-small"
                         style="text-transform: uppercase; letter-spacing: 0.05em;">
                        Referenciar para
                    </div>
                    <div style="margin-top: 0.75rem; font-weight: 600; color: #0F172A;">
                        {info_mun['hospital']}
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            st.subheader("Hipóteses diagnósticas")

            for i, (diag, prob) in enumerate(resultados[:3]):
                if i == 0:
                    st.markdown(f'''
                    <div class="card" style="border-left: 4px solid #312E81;">
                        <div style="display: flex; justify-content: space-between;
                             align-items: center;">
                            <span style="font-size: 1.1rem; font-weight: 600;
                                  color: #0F172A;">
                                1. {diag}
                            </span>
                            <span style="background: #312E81; color: white;
                                  padding: 0.4rem 1rem; border-radius: 6px;
                                  font-weight: 600;">
                                {prob:.1f}%
                            </span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    st.progress(prob / 100)
                else:
                    st.markdown(f'''
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
                    ''', unsafe_allow_html=True)

            st.subheader("O que fazer")

            if diag_principal in CONDUTAS:
                cond = CONDUTAS[diag_principal]
                if gravidade in ["GRAVE", "CRÍTICO"]:
                    st.error(f"**Conduta:** {cond['grave']}")
                else:
                    st.info(f"**Conduta:** {cond['leve']}")

                st.markdown(
                    f'<div class="card"><strong>Exame para confirmar:</strong> '
                    f'{cond["exame"]}</div>',
                    unsafe_allow_html=True
                )

                if cond['alertas']:
                    with st.expander("Sinais de alarme — levar ao hospital já"):
                        for a in cond['alertas']:
                            st.markdown(f"- {a}")

            st.subheader("Leitura do hemograma")

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
                    f"Acompanhar no IHL ou centro de drepanocitose. "
                    f"Ácido fólico 5 mg/dia, boa hidratação, evitar frio "
                    f"e situações que provoquem crises."
                )

            if mordedura:
                st.error(
                    "**Mordedura de animal — risco rábico.** "
                    "Lavar a ferida já com água e sabão durante 15 minutos. "
                    "Iniciar profilaxia antirrábica sem esperar resultados. "
                    "Cada hora que passa conta."
                )

    st.markdown('''
    <div class="footer">
        <strong>RAÍZAO EXPERIMENT</strong><br>
        Apoio à decisão clínica — Luanda e Icolo e Bengo
    </div>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
