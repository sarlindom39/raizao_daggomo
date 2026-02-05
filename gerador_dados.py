"""
ANGOGEN-DX-PRO: Gerador de Dados Sinteticos
Cria pacientes virtuais baseados na epidemiologia real de Luanda/Angola
"""

import random
import pandas as pd
import numpy as np
import os

# semente para reproducibilidade
random.seed(42)
np.random.seed(42)


MUNICIPIOS = {
    'Ingombota': {'provincia': 'Luanda', 'risco_malaria': 0.30, 'risco_colera': 0.15, 'risco_dengue': 0.25},
    'Talatona': {'provincia': 'Luanda', 'risco_malaria': 0.20, 'risco_colera': 0.10, 'risco_dengue': 0.20},
    'Belas': {'provincia': 'Luanda', 'risco_malaria': 0.40, 'risco_colera': 0.25, 'risco_dengue': 0.30},
    'Viana': {'provincia': 'Luanda', 'risco_malaria': 0.50, 'risco_colera': 0.40, 'risco_dengue': 0.35},
    'Cacuaco': {'provincia': 'Luanda', 'risco_malaria': 0.70, 'risco_colera': 0.60, 'risco_dengue': 0.45},
    'Cazenga': {'provincia': 'Luanda', 'risco_malaria': 0.75, 'risco_colera': 0.65, 'risco_dengue': 0.50},
    'Kilamba Kiaxi': {'provincia': 'Luanda', 'risco_malaria': 0.55, 'risco_colera': 0.35, 'risco_dengue': 0.40},
    'Rangel': {'provincia': 'Luanda', 'risco_malaria': 0.50, 'risco_colera': 0.55, 'risco_dengue': 0.35},
    'Maianga': {'provincia': 'Luanda', 'risco_malaria': 0.35, 'risco_colera': 0.20, 'risco_dengue': 0.25},
    'Samba': {'provincia': 'Luanda', 'risco_malaria': 0.45, 'risco_colera': 0.30, 'risco_dengue': 0.35},
    'Catete': {'provincia': 'Icolo e Bengo', 'risco_malaria': 0.60, 'risco_colera': 0.45, 'risco_dengue': 0.30},
    'Icolo e Bengo': {'provincia': 'Icolo e Bengo', 'risco_malaria': 0.65, 'risco_colera': 0.50, 'risco_dengue': 0.30}
}

SAZONALIDADE = {
    'Janeiro': {'estacao': 'Chuvosa', 'riscos': ['Cólera', 'Malária']},
    'Fevereiro': {'estacao': 'Chuvosa (Pico)', 'riscos': ['Cólera', 'Malária', 'Dengue']},
    'Março': {'estacao': 'Chuvosa (Pico)', 'riscos': ['Malária', 'Cólera', 'Dengue']},
    'Abril': {'estacao': 'Chuvosa (Pico)', 'riscos': ['Malária', 'Dengue', 'Febre Tifóide']},
    'Maio': {'estacao': 'Chuvosa (Final)', 'riscos': ['Malária', 'Dengue']},
    'Junho': {'estacao': 'Cacimbo', 'riscos': ['Doenças respiratórias']},
    'Julho': {'estacao': 'Cacimbo', 'riscos': ['Doenças respiratórias']},
    'Agosto': {'estacao': 'Cacimbo', 'riscos': ['Doenças respiratórias']},
    'Setembro': {'estacao': 'Transição', 'riscos': ['Doenças respiratórias']},
    'Outubro': {'estacao': 'Chuvosa (Início)', 'riscos': ['Febre Tifóide', 'Malária']},
    'Novembro': {'estacao': 'Chuvosa', 'riscos': ['Malária', 'Febre Tifóide']},
    'Dezembro': {'estacao': 'Chuvosa', 'riscos': ['Malária', 'Doenças diarreicas']}
}

PICOS_DOENCAS = {
    'Malária': ['Março', 'Abril', 'Maio'],
    'Cólera': ['Janeiro', 'Fevereiro', 'Março'],
    'Dengue': ['Abril', 'Maio', 'Junho'],
    'Febre Tifóide': ['Outubro', 'Novembro', 'Dezembro', 'Janeiro', 'Fevereiro', 'Março', 'Abril']
}

# valores de referencia para hemograma
HEMOGRAMA_REFS = {
    'Homem': {
        'hemoglobina': (12.5, 16.5), 'hematocrito': (38.0, 50.0), 'hemacias': (4.5, 5.9),
        'vcm': (80, 98), 'hcm': (27, 33), 'chcm': (32, 36), 'rdw': (11.5, 14.5),
        'leucocitos': (4000, 10000), 'neutrofilos': (45, 70), 'linfocitos': (20, 45),
        'monocitos': (2, 10), 'eosinofilos': (1, 5), 'basofilos': (0, 1),
        'plaquetas': (140000, 400000), 'vpm': (7.0, 11.0), 'reticulocitos': (0.5, 2.5)
    },
    'Mulher': {
        'hemoglobina': (11.5, 15.5), 'hematocrito': (35.0, 45.0), 'hemacias': (4.0, 5.2),
        'vcm': (80, 98), 'hcm': (27, 33), 'chcm': (32, 36), 'rdw': (11.5, 14.5),
        'leucocitos': (4000, 10000), 'neutrofilos': (45, 70), 'linfocitos': (20, 45),
        'monocitos': (2, 10), 'eosinofilos': (1, 5), 'basofilos': (0, 1),
        'plaquetas': (140000, 400000), 'vpm': (7.0, 11.0), 'reticulocitos': (0.5, 2.5)
    },
    'Gestante': {
        'hemoglobina': (10.5, 13.0), 'hematocrito': (33.0, 44.0), 'hemacias': (3.8, 5.0),
        'vcm': (80, 100), 'hcm': (27, 33), 'chcm': (32, 36), 'rdw': (11.5, 14.5),
        'leucocitos': (6000, 16000), 'neutrofilos': (50, 75), 'linfocitos': (15, 40),
        'monocitos': (2, 10), 'eosinofilos': (1, 5), 'basofilos': (0, 1),
        'plaquetas': (140000, 400000), 'vpm': (7.0, 11.0), 'reticulocitos': (0.5, 2.5)
    },
    'Criança (1-5 anos)': {
        'hemoglobina': (10.5, 13.5), 'hematocrito': (33.0, 42.0), 'hemacias': (4.0, 5.2),
        'vcm': (75, 90), 'hcm': (24, 30), 'chcm': (32, 36), 'rdw': (11.5, 14.5),
        'leucocitos': (5000, 15500), 'neutrofilos': (30, 60), 'linfocitos': (35, 55),
        'monocitos': (2, 10), 'eosinofilos': (1, 5), 'basofilos': (0, 1),
        'plaquetas': (150000, 450000), 'vpm': (7.0, 11.0), 'reticulocitos': (0.5, 2.5)
    },
    'Criança (5-12 anos)': {
        'hemoglobina': (11.5, 14.5), 'hematocrito': (35.0, 45.0), 'hemacias': (4.2, 5.4),
        'vcm': (77, 95), 'hcm': (25, 32), 'chcm': (32, 36), 'rdw': (11.5, 14.5),
        'leucocitos': (4500, 13500), 'neutrofilos': (40, 65), 'linfocitos': (25, 45),
        'monocitos': (2, 10), 'eosinofilos': (1, 5), 'basofilos': (0, 1),
        'plaquetas': (150000, 450000), 'vpm': (7.0, 11.0), 'reticulocitos': (0.5, 2.5)
    },
    'Lactente (1-12 meses)': {
        'hemoglobina': (10.0, 13.0), 'hematocrito': (30.0, 40.0), 'hemacias': (3.8, 5.0),
        'vcm': (70, 86), 'hcm': (23, 31), 'chcm': (32, 36), 'rdw': (11.5, 14.5),
        'leucocitos': (6000, 17500), 'neutrofilos': (20, 45), 'linfocitos': (45, 70),
        'monocitos': (2, 10), 'eosinofilos': (1, 5), 'basofilos': (0, 1),
        'plaquetas': (150000, 450000), 'vpm': (7.0, 11.0), 'reticulocitos': (0.5, 2.5)
    },
    'Recém-nascido (0-28 dias)': {
        'hemoglobina': (14.5, 22.5), 'hematocrito': (45.0, 67.0), 'hemacias': (4.5, 6.5),
        'vcm': (95, 115), 'hcm': (30, 37), 'chcm': (32, 36), 'rdw': (11.5, 16.0),
        'leucocitos': (9000, 30000), 'neutrofilos': (40, 70), 'linfocitos': (20, 45),
        'monocitos': (2, 10), 'eosinofilos': (1, 5), 'basofilos': (0, 1),
        'plaquetas': (150000, 450000), 'vpm': (7.0, 11.0), 'reticulocitos': (3.0, 7.0)
    }
}


# ==============================================================================
# FUNCOES DO GERADOR
# ==============================================================================

def gerar_perfil_paciente():
    """
    gera um perfil demografico aleatorio para um paciente
    com distribuicao realista para angola (populacao jovem)
    """
    # distribuicao etaria baseada na piramide populacional angolana
    faixas = [
        ('Recém-nascido (0-28 dias)', 0.02),
        ('Lactente (1-12 meses)', 0.05),
        ('Criança (1-5 anos)', 0.15),
        ('Criança (5-12 anos)', 0.18),
        ('Adolescente (12-18 anos)', 0.12),
        ('Adulto (18-45 anos)', 0.35),
        ('Adulto (45-65 anos)', 0.10),
        ('Idoso (>65 anos)', 0.03)
    ]
    
    faixa = random.choices(
        [f[0] for f in faixas],
        weights=[f[1] for f in faixas]
    )[0]
    
    sexo = random.choice(['Masculino', 'Feminino'])
    
    # se mulher adulta, chance de estar gravida
    gestante = False
    if sexo == 'Feminino' and 'Adulto' in faixa and '18-45' in faixa:
        gestante = random.random() < 0.08
    
    # municipio com peso baseado na populacao
    municipios_peso = {
        'Viana': 0.18, 'Cacuaco': 0.16, 'Cazenga': 0.14, 'Belas': 0.12,
        'Kilamba Kiaxi': 0.10, 'Rangel': 0.08, 'Maianga': 0.06,
        'Ingombota': 0.05, 'Samba': 0.05, 'Talatona': 0.03,
        'Catete': 0.02, 'Icolo e Bengo': 0.01
    }
    
    municipio = random.choices(
        list(municipios_peso.keys()),
        weights=list(municipios_peso.values())
    )[0]
    
    mes = random.choice(list(SAZONALIDADE.keys()))
    
    # determinar perfil para referencias do hemograma
    if 'Recém-nascido' in faixa:
        perfil_hemograma = 'Recém-nascido (0-28 dias)'
    elif 'Lactente' in faixa:
        perfil_hemograma = 'Lactente (1-12 meses)'
    elif 'Criança (1-5' in faixa:
        perfil_hemograma = 'Criança (1-5 anos)'
    elif 'Criança (5-12' in faixa:
        perfil_hemograma = 'Criança (5-12 anos)'
    elif gestante:
        perfil_hemograma = 'Gestante'
    elif sexo == 'Masculino':
        perfil_hemograma = 'Homem'
    else:
        perfil_hemograma = 'Mulher'
    
    # peso aproximado
    if 'Recém-nascido' in faixa:
        peso = round(random.uniform(2.5, 4.5), 1)
    elif 'Lactente' in faixa:
        peso = round(random.uniform(4, 10), 1)
    elif 'Criança (1-5' in faixa:
        peso = round(random.uniform(10, 20), 1)
    elif 'Criança (5-12' in faixa:
        peso = round(random.uniform(20, 40), 1)
    elif 'Adolescente' in faixa:
        peso = round(random.uniform(40, 65), 1)
    else:
        peso = round(random.uniform(50, 85), 1)
    
    # traco falciforme (AS) - 20% da populacao angolana e portadora
    # isto e independente de estar doente ou nao
    traco_falciforme = random.random() < 0.20
    
    # historia de mordedura animal (para raiva) - raro mas acontece
    mordedura_recente = random.random() < 0.005  # 0.5% tem historia recente
    
    return {
        'faixa_etaria': faixa,
        'sexo': sexo,
        'gestante': gestante,
        'municipio': municipio,
        'mes': mes,
        'perfil_hemograma': perfil_hemograma,
        'peso_kg': peso,
        'traco_falciforme_AS': traco_falciforme,
        'mordedura_recente': mordedura_recente
    }


def calcular_risco_doenca(paciente, doenca):
    """
    calcula a probabilidade de um paciente ter uma doenca especifica
    baseado no municipio, mes e perfil demografico
    """
    municipio = paciente['municipio']
    mes = paciente['mes']
    faixa = paciente['faixa_etaria']
    
    risco_base = 0.05
    
    if municipio in MUNICIPIOS:
        dados_mun = MUNICIPIOS[municipio]
        if doenca == 'Malária':
            risco_base = dados_mun['risco_malaria']
        elif doenca == 'Cólera':
            risco_base = dados_mun['risco_colera']
        elif doenca == 'Dengue':
            risco_base = dados_mun['risco_dengue']
    
    # ajuste por sazonalidade
    if doenca in PICOS_DOENCAS:
        if mes in PICOS_DOENCAS[doenca]:
            risco_base *= 1.8
    
    # ajuste por faixa etaria
    if doenca == 'Malária':
        if 'Criança (1-5' in faixa:
            risco_base *= 2.0
        elif paciente['gestante']:
            risco_base *= 1.5
    
    return min(0.95, max(0.01, risco_base))


def gerar_hemograma_normal(perfil):
    """
    gera valores de hemograma dentro da faixa normal
    """
    if perfil in HEMOGRAMA_REFS:
        refs = HEMOGRAMA_REFS[perfil]
    else:
        refs = HEMOGRAMA_REFS['Homem']
    
    hemograma = {}
    
    for param, (min_val, max_val) in refs.items():
        media = (min_val + max_val) / 2
        desvio = (max_val - min_val) / 6
        valor = np.random.normal(media, desvio)
        valor = max(min_val, min(max_val, valor))
        
        if param in ['plaquetas', 'leucocitos']:
            hemograma[param] = int(round(valor, -2))
        elif param == 'hemacias':
            hemograma[param] = round(valor, 2)
        else:
            hemograma[param] = round(valor, 1)
    
    return hemograma


def aplicar_alteracao_doenca(hemograma, doenca, gravidade='moderado'):
    """
    modifica os valores do hemograma de acordo com a assinatura
    hematologica de uma doenca especifica
    """
    if doenca == 'Malária':
        if gravidade == 'grave':
            hemograma['hemoglobina'] -= random.uniform(4, 6)
            hemograma['plaquetas'] = int(hemograma['plaquetas'] * random.uniform(0.15, 0.3))
        else:
            hemograma['hemoglobina'] -= random.uniform(2, 4)
            hemograma['plaquetas'] = int(hemograma['plaquetas'] * random.uniform(0.3, 0.5))
        hemograma['hematocrito'] -= random.uniform(5, 10)
        hemograma['leucocitos'] = int(hemograma['leucocitos'] * random.uniform(0.6, 0.9))
    
    elif doenca == 'Dengue':
        hemograma['hematocrito'] += random.uniform(3, 8)
        hemograma['hemoglobina'] += random.uniform(0.5, 1.5)
        if gravidade == 'grave':
            hemograma['plaquetas'] = int(hemograma['plaquetas'] * random.uniform(0.1, 0.2))
        else:
            hemograma['plaquetas'] = int(hemograma['plaquetas'] * random.uniform(0.2, 0.4))
        hemograma['leucocitos'] = int(hemograma['leucocitos'] * random.uniform(0.4, 0.7))
    
    elif doenca == 'Febre Tifóide':
        hemograma['leucocitos'] = int(hemograma['leucocitos'] * random.uniform(0.5, 0.7))
        hemograma['eosinofilos'] = 0  # aneosinofilia classica
        hemograma['neutrofilos'] -= random.uniform(5, 15)
    
    elif doenca == 'Cólera':
        hemograma['hematocrito'] += random.uniform(8, 15)
        hemograma['hemoglobina'] += random.uniform(2, 4)
        hemograma['leucocitos'] = int(hemograma['leucocitos'] * random.uniform(1.1, 1.4))
    
    elif doenca == 'Parasitose Intestinal':
        hemograma['eosinofilos'] = random.uniform(8, 20)
        hemograma['hemoglobina'] -= random.uniform(0.5, 2)
    
    elif doenca == 'Drepanocitose (SS)':
        hemograma['hemoglobina'] = random.uniform(6, 9)
        hemograma['hematocrito'] = random.uniform(20, 30)
        hemograma['reticulocitos'] = random.uniform(3, 8)
        hemograma['vcm'] = random.uniform(75, 95)
    
    elif doenca == 'Anemia Ferropriva':
        hemograma['hemoglobina'] -= random.uniform(2, 5)
        hemograma['vcm'] = random.uniform(60, 78)
        hemograma['hcm'] = random.uniform(20, 26)
        hemograma['rdw'] = random.uniform(15, 20)
    
    elif doenca == 'Tuberculose':
        hemograma['monocitos'] = random.uniform(10, 18)
        hemograma['hemoglobina'] -= random.uniform(1, 3)
        hemograma['vcm'] = random.uniform(80, 95)
    
    elif doenca == 'HIV/SIDA':
        hemograma['linfocitos'] = random.uniform(10, 18)
        hemograma['hemoglobina'] -= random.uniform(1, 3)
        hemograma['plaquetas'] = int(hemograma['plaquetas'] * random.uniform(0.6, 0.85))
        hemograma['leucocitos'] = int(hemograma['leucocitos'] * random.uniform(0.6, 0.8))
    
    elif doenca in ['Saudável', 'Traço Falciforme (AS)', 'Raiva (Mordedura Animal)']:
        # hemograma normal nestas condicoes
        pass
    
    # garantir valores minimos fisiologicos
    hemograma['hemoglobina'] = max(3.0, hemograma['hemoglobina'])
    hemograma['hematocrito'] = max(10, min(70, hemograma['hematocrito']))
    hemograma['plaquetas'] = max(5000, hemograma['plaquetas'])
    hemograma['leucocitos'] = max(500, hemograma['leucocitos'])
    hemograma['eosinofilos'] = max(0, min(25, hemograma['eosinofilos']))
    hemograma['neutrofilos'] = max(20, min(90, hemograma['neutrofilos']))
    hemograma['linfocitos'] = max(5, min(70, hemograma['linfocitos']))
    hemograma['monocitos'] = max(0, min(20, hemograma['monocitos']))
    hemograma['reticulocitos'] = max(0.2, min(15, hemograma['reticulocitos']))
    
    return hemograma


def determinar_gravidade(hemograma):
    """
    determina o nivel de gravidade com base nos valores do hemograma
    """
    hb = hemograma['hemoglobina']
    plt = hemograma['plaquetas']
    
    if hb < 5 or plt < 20000:
        return 'Crítico'
    elif hb < 7 or plt < 50000:
        return 'Grave'
    elif hb < 10 or plt < 100000:
        return 'Moderado'
    else:
        return 'Leve'


def gerar_dataset(n_amostras=5000, seed=42):
    """
    gera um dataset completo de pacientes sinteticos
    """
    random.seed(seed)
    np.random.seed(seed)
    
    dados = []
    
    # distribuicao de diagnosticos clinicos (baseada na realidade angolana)
    doencas_possiveis = [
        ('Saudável', 0.25),
        ('Malária', 0.25),
        ('Anemia Ferropriva', 0.15),
        ('Parasitose Intestinal', 0.10),
        ('Dengue', 0.05),
        ('Drepanocitose (SS)', 0.02),  # so os homozigoticos SS
        ('Febre Tifóide', 0.04),
        ('Tuberculose', 0.03),
        ('Cólera', 0.03),
        ('HIV/SIDA', 0.02),
        ('Raiva (Mordedura Animal)', 0.005)  # raro mas critico
    ]
    
    for i in range(n_amostras):
        paciente = gerar_perfil_paciente()
        
        # primeiro verificar se tem mordedura recente (raiva)
        if paciente['mordedura_recente']:
            doenca_escolhida = 'Raiva (Mordedura Animal)'
        else:
            # escolher doenca com base nos riscos contextuais
            doenca_escolhida = 'Saudável'
            
            for doenca, prob_base in doencas_possiveis:
                if doenca in ['Saudável', 'Raiva (Mordedura Animal)']:
                    continue
                
                # se ja tem drepanocitose SS, nao pode ter traco AS
                if doenca == 'Drepanocitose (SS)':
                    # 2% da populacao tem a doenca (nao confundir com traco)
                    if random.random() < 0.02:
                        doenca_escolhida = doenca
                        paciente['traco_falciforme_AS'] = False  # e SS, nao AS
                        break
                    continue
                
                risco = calcular_risco_doenca(paciente, doenca)
                risco_final = risco * prob_base * 3
                
                if random.random() < risco_final:
                    doenca_escolhida = doenca
                    break
        
        # gerar hemograma
        hemograma = gerar_hemograma_normal(paciente['perfil_hemograma'])
        
        # determinar gravidade clinica
        gravidade_clinica = 'leve'
        if doenca_escolhida not in ['Saudável', 'Traço Falciforme (AS)', 'Raiva (Mordedura Animal)']:
            r = random.random()
            if r < 0.1:
                gravidade_clinica = 'grave'
            elif r < 0.4:
                gravidade_clinica = 'moderado'
        
        # aplicar alteracoes da doenca
        hemograma = aplicar_alteracao_doenca(hemograma, doenca_escolhida, gravidade_clinica)
        
        # determinar gravidade laboratorial
        gravidade_lab = determinar_gravidade(hemograma)
        
        # determinar status genetico final
        # se e Drepanocitose SS, nao tem traco AS
        # se e saudavel com traco AS, registar como portador
        status_genetico = 'Normal'
        if doenca_escolhida == 'Drepanocitose (SS)':
            status_genetico = 'HbSS (Doença)'
        elif paciente['traco_falciforme_AS']:
            status_genetico = 'HbAS (Traço)'
        
        # montar registro
        registro = {
            'id_paciente': f'AO-2026-{i+1:05d}',
            'faixa_etaria': paciente['faixa_etaria'],
            'sexo': paciente['sexo'],
            'gestante': paciente['gestante'],
            'peso_kg': paciente['peso_kg'],
            'municipio': paciente['municipio'],
            'provincia': MUNICIPIOS[paciente['municipio']]['provincia'],
            'mes': paciente['mes'],
            'estacao': SAZONALIDADE[paciente['mes']]['estacao'],
            
            # genetica
            'status_genetico': status_genetico,
            
            # historia relevante
            'mordedura_recente': paciente['mordedura_recente'],
            
            # hemograma
            'hemoglobina': hemograma.get('hemoglobina', 0),
            'hematocrito': hemograma.get('hematocrito', 0),
            'hemacias': hemograma.get('hemacias', 0),
            'vcm': hemograma.get('vcm', 0),
            'hcm': hemograma.get('hcm', 0),
            'chcm': hemograma.get('chcm', 0),
            'rdw': hemograma.get('rdw', 0),
            'leucocitos': hemograma.get('leucocitos', 0),
            'neutrofilos': hemograma.get('neutrofilos', 0),
            'linfocitos': hemograma.get('linfocitos', 0),
            'monocitos': hemograma.get('monocitos', 0),
            'eosinofilos': hemograma.get('eosinofilos', 0),
            'basofilos': hemograma.get('basofilos', 0),
            'plaquetas': hemograma.get('plaquetas', 0),
            'vpm': hemograma.get('vpm', 0),
            'reticulocitos': hemograma.get('reticulocitos', 0),
            
            # diagnostico
            'diagnostico': doenca_escolhida,
            'gravidade': gravidade_lab
        }
        
        dados.append(registro)
        
        if (i + 1) % 1000 == 0:
            print(f"Gerados {i + 1}/{n_amostras} pacientes...")
    
    df = pd.DataFrame(dados)
    
    return df


def analisar_dataset(df):
    """
    mostra estatisticas do dataset gerado
    """
    print("\n" + "=" * 60)
    print("ESTATISTICAS DO DATASET GERADO")
    print("=" * 60)
    
    print(f"\nTotal de pacientes: {len(df)}")
    
    print("\n--- Distribuicao por Diagnostico ---")
    print(df['diagnostico'].value_counts())
    
    print("\n--- Status Genetico (Drepanocitose) ---")
    print(df['status_genetico'].value_counts())
    
    print("\n--- Distribuicao por Municipio ---")
    print(df['municipio'].value_counts().head(8))
    
    print("\n--- Distribuicao por Gravidade ---")
    print(df['gravidade'].value_counts())
    
    print("\n--- Taxa de Malaria por Municipio ---")
    malaria_mun = df[df['diagnostico'] == 'Malária'].groupby('municipio').size()
    total_mun = df.groupby('municipio').size()
    taxa = (malaria_mun / total_mun * 100).round(1)
    print(taxa.sort_values(ascending=False).head(6))
    
    print("\n--- Portadores do Traco Falciforme (AS) ---")
    n_traco = len(df[df['status_genetico'] == 'HbAS (Traço)'])
    print(f"Total: {n_traco} ({n_traco/len(df)*100:.1f}% da populacao)")
    
    print("\n--- Casos de Mordedura Animal (Raiva) ---")
    n_raiva = len(df[df['diagnostico'] == 'Raiva (Mordedura Animal)'])
    print(f"Total: {n_raiva} casos")


def main():
    """
    funcao principal
    """
    print("=" * 60)
    print("ANGOGEN-DX-PRO: Gerador de Dados Sinteticos")
    print("Baseado na Epidemiologia de Luanda/Angola 2026")
    print("=" * 60)
    
    n_amostras = 5000
    print(f"\nGerando {n_amostras} pacientes virtuais...")
    
    df = gerar_dataset(n_amostras=n_amostras)
    
    analisar_dataset(df)
    
    # criar pasta data se nao existir
    os.makedirs('data', exist_ok=True)
    
    arquivo_csv = 'data/dataset_angogen.csv'
    df.to_csv(arquivo_csv, index=False)
    
    print(f"\nDataset salvo em: {arquivo_csv}")
    print("=" * 60)
    
    return df


if __name__ == "__main__":
    df = main()
