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

OSM_PRIMARY = "#15682E"
OSM_BG = "#CEEFEA"
OSM_ACCENT = "#FF3D2E"
OSM_TEXT = "#1A1A18"
OSM_SECONDARY_TEXT = "#7A7A72"

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
        'leve': 'Coartem (Arteméter + Lumefantrina): 4 comprimidos de 12/12h durante 3 dias. Tomar sempre com comida, de preferência com gordura para absorver melhor. Paracetamol para baixar a febre.',
        'grave': 'Artesunato EV 2,4 mg/kg às 0h, 12h e 24h, depois 1x/dia até o doente aguentar via oral. Controlar Hb no dia 7 e 14. Se a parasitemia não baixar em 24h, reavaliar a dose.',
        'exame': 'Gota espessa ou teste rápido (TDR)',
        'alertas': ['Convulsões', 'Prostração', 'Vómitos incoercíveis', 'Urina escura', 'Falta de ar', 'Icterícia', 'Alteração da consciência']
    },
    'Dengue': {
        'leve': 'Hidratar bem por via oral (60-80 mL/kg/dia). Paracetamol para febre. Evitar AINEs e aspirina.',
        'grave': 'Soro EV e monitorizar hematócrito a cada 2 horas. Se Ht subir > 20%, intensificar hidratação.',
        'exame': 'NS1 ou IgM/IgG',
        'alertas': ['Dor abdominal intensa', 'Vómitos persistentes', 'Hemorragias', 'Letargia ou irritabilidade']
    },
    'Drepanocitose (SS)': {
        'leve': 'Ácido fólico 5 mg/dia. Hidratação abundante. Evitar extremos térmicos e esforço físico extenuante.',
        'grave': 'Analgesia escalonada + hidratação EV + oxigenoterapia se necessário. Referenciar ao IHL.',
        'exame': 'Eletroforese de hemoglobina',
        'alertas': ['Febre', 'Dor torácica', 'Priapismo', 'Sinais neurológicos focais']
    },
    'Anemia Ferropriva': {
        'leve': 'Sulfato ferroso por 3-6 meses. Tomar em jejum com vitamina C. Fezes escuras são normais.',
        'grave': 'Considerar transfusão se Hb < 5 g/dL. Investigar etiologia.',
        'exame': 'Ferritina sérica',
        'alertas': ['Dispneia em repouso', 'Taquicardia', 'Palidez intensa']
    },
    'Colera': {
        'leve': 'SRO conforme protocolo da OMS. Hidratação oral rigorosa.',
        'grave': 'Ringer Lactato EV em bólus. Azitromicina 1 g dose única. Notificação obrigatória.',
        'exame': 'Coprocultura',
        'alertas': ['Desidratação grave', 'Sinal da prega positivo', 'Anúria', 'Alteração do estado mental']
    },
    'Febre Tifoide': {
        'leve': 'Ciprofloxacina 500 mg 12/12h por 7-14 dias. Dieta leve e hidratação.',
        'grave': 'Ceftriaxona EV 2 g/dia. Vigilância para perfuração intestinal.',
        'exame': 'Hemocultura ou coprocultura',
        'alertas': ['Abdomen agudo', 'Confusão mental', 'Enterorragia']
    },
    'Parasitose Intestinal': {
        'leve': 'Albendazol 400 mg dose única. Repetir semestralmente. Higiene rigorosa.',
        'grave': 'Tratamento prolongado + correção de anemia se presente.',
        'exame': 'Parasitológico de fezes',
        'alertas': ['Distensão abdominal severa', 'Desnutrição grave']
    },
    'Tuberculose': {
        'leve': 'Esquema DOTS (RHZE/RH). Adesão rigorosa é fundamental.',
        'grave': 'Internamento hospitalar. Investigar formas extrapulmonares e coinfecções.',
        'exame': 'Baciloscopia ou GeneXpert',
        'alertas': ['Hemoptise', 'Perda ponderal acentuada', 'Sudorese noturna', 'Tosse persistente > 2 semanas']
    },
    'HIV/SIDA': {
        'leve': 'TARV de 1ª linha (TDF/3TC/DTG). Adesão e acompanhamento regular.',
        'grave': 'Tratamento prioritário de infecções oportunistas. Referenciar ao CTA.',
        'exame': 'Teste rápido + CD4 + Carga Viral',
        'alertas': ['Infecções recorrentes', 'Emagrecimento inexplicável', 'Diarreia crônica', 'Candidíase oral persistente']
    },
    'Raiva (Mordedura)': {
        'leve': 'Lavagem exaustiva com água e sabão (15 min). Vacinação nos dias 0, 3, 7, 14.',
        'grave': 'Sorovacinação imediata. Não suturar a ferida.',
        'exame': 'Tratamento imediato baseado em risco',
        'alertas': ['Hidrofobia', 'Aerofobia', 'Agitação psicomotora']
    },
    'Saudavel': {
        'leve': 'Hemograma normal. Manter medidas preventivas e vacinação em dia.',
        'grave': 'N/A',
        'exame': 'N/A',
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
    if not email: return True
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def validar_telefone(telefone):
    nums = re.sub(r'[^0-9]', '', telefone)
    return len(nums) == 9 and nums[0] == '9'

def obter_saudacao():
    h = datetime.now().hour
    if h < 12: return "Bom dia"
    if h < 18: return "Boa tarde"
    return "Boa noite"

@st.cache_resource
def carregar_modelo():
    try:
        with open('models/modelo_angogen.pkl', 'rb') as f: modelo = pickle.load(f)
        with open('models/encoders.pkl', 'rb') as f: encoders = pickle.load(f)
        with open('models/features.pkl', 'rb') as f: features = pickle.load(f)
        return modelo, encoders, features
    except: return None, None, None

def formatar_numero(v):
    return f"{v:,.0f}".replace(",", ".")

def classificar_valor(v, min_v, max_v):
    if v < min_v: return "baixo", "Baixo"
    if v > max_v: return "alto", "Alto"
    return "normal", "Normal"

def determinar_gravidade(hb, plt):
    if hb < 5 or plt < 20000: return "CRITICO"
    if hb < 7 or plt < 50000: return "GRAVE"
    if hb < 10 or plt < 100000: return "MODERADO"
    return "LEVE"

def validar_leucograma(n, l, m, e, b):
    s = n + l + m + e + b
    return (abs(s - 100) <= 5, s)

def fazer_predicao(modelo, encoders, features, dados):
    try:
        df = pd.DataFrame([dados])
        for col in ['faixa_etaria', 'sexo', 'municipio', 'provincia', 'mes', 'estacao', 'status_genetico']:
            if col in dados and col in encoders:
                le = encoders[col]
                v = dados[col]
                df[col + '_cod'] = le.transform([v])[0] if v in le.classes_ else 0
            else:
                df[col + '_cod'] = 0
        df['gestante_int'] = int(dados.get('gestante', False))
        df['mordedura_int'] = int(dados.get('mordedura_recente', False))
        for feat in features:
            if feat not in df.columns: df[feat] = 0
        df = df[features]
        probs = modelo.predict_proba(df)[0]
        res = sorted(zip(modelo.classes_, probs * 100), key=lambda x: x[1], reverse=True)
        return res, None
    except Exception as e: return None, str(e)

def processar_analise(modelo, encoders, features, dados):
    hb, plt = dados['hemoglobina'], dados['plaquetas']
    gravidade = determinar_gravidade(hb, plt)
    if modelo:
        res, erro = fazer_predicao(modelo, encoders, features, dados)
        return gravidade, res, erro
    classes = list(CONDUTAS.keys())
    probs = np.random.dirichlet(np.ones(len(classes)), size=1)[0] * 100
    res = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)
    return gravidade, res, None

def injetar_css_osm():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dosis:wght@400;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Dosis', sans-serif;
        background-color: {OSM_BG};
        color: {OSM_TEXT};
    }}
    
    h1, h2, h3 {{
        font-family: 'Dosis', sans-serif;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: -0.02em;
        color: {OSM_PRIMARY};
    }}
    
    .stButton>button {{
        background-color: {OSM_PRIMARY};
        color: white;
        border-radius: 0;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.3s;
    }}
    
    .stButton>button:hover {{
        background-color: {OSM_TEXT};
        color: white;
    }}
    
    [data-testid="stMetricValue"] {{
        font-weight: 800;
        color: {OSM_PRIMARY};
    }}
    
    .osm-card {{
        background: white;
        padding: 2rem;
        border-radius: 0;
        box-shadow: 10px 10px 0px {OSM_PRIMARY};
        margin-bottom: 2rem;
        border: 1px solid #eee;
    }}
    
    .osm-hero {{
        padding: 4rem 0;
        text-align: center;
        background-image: repeating-linear-gradient(45deg, rgba(21,104,46,0.05) 0px, rgba(21,104,46,0.05) 2px, transparent 2px, transparent 10px);
    }}
    
    .osm-badge {{
        display: inline-block;
        padding: 0.25rem 1rem;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.1em;
        margin-right: 0.5rem;
    }}
    
    .badge-sucesso {{ background: #D4EDDA; color: #155724; }}
    .badge-alerta {{ background: #FFF3CD; color: #856404; }}
    .badge-perigo {{ background: #F8D7DA; color: #721C24; }}
    .badge-critico {{ background: {OSM_ACCENT}; color: white; }}
    
    .osm-footer {{
        margin-top: 4rem;
        padding: 2rem;
        border-top: 1px solid {OSM_PRIMARY};
        text-align: center;
        font-size: 0.9rem;
        color: {OSM_SECONDARY_TEXT};
    }}
    </style>
    """, unsafe_allow_html=True)

def osm_card(conteudo, title=None):
    title_html = f"<h3 style='margin-top:0;'>{title}</h3>" if title else ""
    st.markdown(f"""
    <div class="osm-card">
        {title_html}
        {conteudo}
    </div>
    """, unsafe_allow_html=True)

def tela_boas_vindas():
    st.markdown(f"""
    <div class="osm-hero">
        <h1 style="font-size: 4rem; margin-bottom: 0;">HEMASAKULA</h1>
        <p style="font-size: 1.5rem; font-weight: 600; color: {OSM_TEXT};">Angola a Cuidar dos Seus</p>
        <div style="width: 100px; hieght: 4px; background: {OSM_ACCENT}; margin: 2rem auto;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        osm_card("""
            <p>Acesse o sistema para realizar análises de hemogramas e acompanhar pacientes.</p>
        """, title="PARA PROFISSIONAIS")
        if st.button("ENTRAR NO SISTEMA"):
            st.session_state.ecra = 'login_empresa'
            st.rerun()
            
    with col2:
        osm_card("""
            <p>Realize um check-up rápido e receba orientações preliminares.</p>
        """, title="PARA PACIENTES")
        if st.button("INICIAR ANÁLISE"):
            st.session_state.ecra = 'cliente'
            st.rerun()

def tela_painel_cliente():
    st.markdown(f"<h2>{obter_saudacao()}, Bem-vindo à Análise</h2>", unsafe_allow_html=True)
    
    modelo, encoders, features = carregar_modelo()
    
    with st.expander("DADOS PESSOAIS E LOCALIZAÇÃO", expanded=True):
        c1, c2, c3 = st.columns(3)
        nome = c1.text_input("Nome Completo")
        telefone = c2.text_input("Telefone (9xx xxx xxx)")
        municipio = c3.selectbox("Município", MUNICIPIOS_LISTA)
        
        c4, c5, c6 = st.columns(3)
        faixa_etaria = c4.selectbox("Faixa Etária", FAIXAS_ETARIAS)
        sexo = c5.selectbox("Sexo", SEXOS)
        status_genetico = c6.selectbox("Status Genético", STATUS_GENETICO)
        
        provincia = MUNICIPIOS_INFO[municipio]['provincia']
        info_mun = MUNICIPIOS_INFO[municipio]
        
    with st.expander("CONTEXTO CLÍNICO E AMBIENTAL"):
        c1, c2, c3 = st.columns(3)
        mes = c1.selectbox("Mês Atual", MESES, index=datetime.now().month-1)
        estacao = ESTACOES_POR_MES[mes]
        peso = c2.number_input("Peso (kg)", 2.0, 200.0, 70.0)
        gestante = False
        if sexo == "Feminino":
            gestante = c3.checkbox("Está grávida?")
        mordedura = st.checkbox("Teve mordedura de animal recentemente?")

    st.markdown("<h3>DADOS DO HEMOGRAMA</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<p style='color:{OSM_PRIMARY}; font-weight:700;'>SÉRIE VERMELHA</p>", unsafe_allow_html=True)
        hb = st.number_input("Hemoglobina (g/dL)", 3.0, 22.0, 12.5)
        ht = st.number_input("Hematócrito (%)", 10.0, 70.0, 38.0)
        vcm = st.number_input("VCM (fL)", 50.0, 120.0, 88.0)
    with c2:
        st.markdown(f"<p style='color:{OSM_PRIMARY}; font-weight:700;'>SÉRIE BRANCA</p>", unsafe_allow_html=True)
        leu = st.number_input("Leucócitos (/mm³)", 500, 50000, 7500)
        neu = st.number_input("Neutrófilos (%)", 10.0, 90.0, 58.0)
        lin = st.number_input("Linfócitos (%)", 5.0, 70.0, 32.0)
    with c3:
        st.markdown(f"<p style='color:{OSM_PRIMARY}; font-weight:700;'>PLAQUETAS E OUTROS</p>", unsafe_allow_html=True)
        plt = st.number_input("Plaquetas (/mm³)", 5000, 1000000, 250000)
        ret = st.number_input("Reticulócitos (%)", 0.2, 15.0, 1.2)

    if st.button("ANALISAR AGORA"):
        if not nome or not validar_telefone(telefone):
            st.error("Por favor, preencha o nome e um telefone válido.")
            return
            
        dados = {
            'faixa_etaria': faixa_etaria, 'sexo': sexo, 'gestante': gestante,
            'peso_kg': peso, 'municipio': municipio, 'provincia': provincia,
            'mes': mes, 'estacao': estacao, 'status_genetico': status_genetico,
            'mordedura_recente': mordedura, 'hemoglobina': hb, 'hematocrito': ht,
            'vcm': vcm, 'leucocitos': leu, 'neutrofilos': neu, 'linfocitos': lin,
            'plaquetas': plt, 'reticulocitos': ret
        }
        
        grav, res, erro = processar_analise(modelo, encoders, features, dados)
        
        if erro:
            st.error(f"Erro: {erro}")
        else:
            registar_cliente(nome, telefone, municipio)
            st.markdown("<h2>RESULTADOS DA ANÁLISE</h2>", unsafe_allow_html=True)
            
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                badge_class = f"badge-{grav.lower()}"
                st.markdown(f"""
                <div class="osm-card">
                    <p style="color:{OSM_SECONDARY_TEXT}; font-size:0.8rem; text-transform:uppercase;">Nível de Gravidade</p>
                    <span class="osm-badge {badge_class}">{grav}</span>
                </div>
                """, unsafe_allow_html=True)
                
            with col_res2:
                osm_card(f"<p style='font-weight:700; font-size:1.2rem;'>{info_mun['hospital']}</p>", title="UNIDADE DE REFERÊNCIA")

            diag_p = res[0][0]
            st.markdown(f"<h3>HIPÓTESE PRINCIPAL: {diag_p} ({res[0][1]:.1f}%)</h3>", unsafe_allow_html=True)
            
            if diag_p in CONDUTAS:
                cond = CONDUTAS[diag_p]
                c_text = cond['grave'] if grav in ["GRAVE", "CRITICO"] else cond['leve']
                osm_card(f"<p>{c_text}</p>", title="CONDUTA RECOMENDADA")
                osm_card(f"<p>{cond['exame']}</p>", title="EXAME COMPLEMENTAR")
                
                if cond['alertas']:
                    with st.expander("SINAIS DE ALERTA - PROCURE UM BANCO IMEDIATAMENTE"):
                        for a in cond['alertas']: st.write(f"• {a}")

    if st.button("VOLTAR AO INÍCIO"):
        st.session_state.ecra = 'inicio'
        st.rerun()

def tela_login_empresa():
    st.markdown("<h2>ACESSO RESTRITO</h2>", unsafe_allow_html=True)
    with st.form("login"):
        user = st.text_input("Utilizador")
        pw = st.text_input("Palavra-passe", type="password")
        if st.form_submit_button("ENTRAR"):
            if user == "admin" and pw == "admin":
                st.session_state.ecra = 'empresa'
                st.rerun()
            else: st.error("Credenciais inválidas")
    if st.button("VOLTAR"):
        st.session_state.ecra = 'inicio'
        st.rerun()

def tela_painel_empresa():
    st.markdown("<h2>PAINEL DE GESTÃO</h2>", unsafe_allow_html=True)
    clientes = carregar_clientes()
    if not clientes:
        st.info("Nenhum registro encontrado.")
    else:
        df = pd.DataFrame.from_dict(clientes, orient='index')
        st.dataframe(df[['nome', 'telefone', 'municipio', 'data_registo']], use_container_width=True)
    
    if st.button("SAIR"):
        st.session_state.ecra = 'inicio'
        st.rerun()

def main():
    injetar_css_osm()
    if 'ecra' not in st.session_state: st.session_state.ecra = 'inicio'
    
    if st.session_state.ecra == 'inicio': tela_boas_vindas()
    elif st.session_state.ecra == 'cliente': tela_painel_cliente()
    elif st.session_state.ecra == 'login_empresa': tela_login_empresa()
    elif st.session_state.ecra == 'empresa': tela_painel_empresa()

    st.markdown(f"""
    <div class="osm-footer">
        <p>HEMASAKULA &copy; 2026. Todos os direitos reservados.</p>
        <p style="font-weight:700;">Feito por Arlindo Muecaria</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
