"""
ANGOGEN-DX-PRO: Sistema de Inteligência Epidemiológica Contextual - Angola (2026)

Desenvolvido para a realidade epidemiologica, geografica e farmacologica de
Angola. Este modulo contem toda a inteligencia clinica necessaria para apoiar
decisoes medicas baseadas no hemograma e contexto do paciente.

Objetivo s: Autenticidade, Precisao e Seguranca Farmaceutica

Versao: 1.0.0

Regiao: Luanda e Icolo e Bengo
"""

# lista completa das vinte e uma provincias de angola depois da nova divisao
PROVINCIAS = [
    'Bengo', 'Benguela', 'Bié', 'Cabinda', 'Cuanza Norte', 'Cuanza Sul',
    'Cunene', 'Huambo', 'Huíla', 'Malanje', 'Namibe', 'Uíge', 'Zaire',
    'Lunda Norte', 'Lunda Sul', 'Moxico', 'Moxico Leste', 'Cuando',
    'Cubango', 'Luanda', 'Icolo e Bengo'
]

# provincias novas
PROVINCIAS_NOVAS = {
    'Moxico Leste': {'origem': 'Moxico', 'capital': 'Cazombo'},
    'Cuando': {'origem': 'Cuando Cubango', 'capital': 'Mavinga'},
    'Cubango': {'origem': 'Cuando Cubango', 'capital': 'Menongue'},
    'Icolo e Bengo': {'origem': 'Luanda', 'capital': 'Catete'}
}


# dados por municipio
MUNICIPIOS = {
    # municipios da provincia de luanda
    'Ingombota': {
        'provincia': 'Luanda',
        'pobreza': 'Baixa',
        'saneamento': 'Aceitável',
        'acesso_saude': 'Alto',
        'risco_malaria': 0.30,
        'risco_colera': 0.15,
        'risco_dengue': 0.25,
        'hospital_referencia': 'Hospital Josina Machel (ex Maria Pia)'
    },
    'Talatona': {
        'provincia': 'Luanda',
        'pobreza': 'Baixa',
        'saneamento': 'Aceitável',
        'acesso_saude': 'Alto',
        'risco_malaria': 0.20,
        'risco_colera': 0.10,
        'risco_dengue': 0.20,
        'hospital_referencia': 'Clínica Sagrada Esperança'
    },
    'Belas': {
        'provincia': 'Luanda',
        'pobreza': 'Média',
        'saneamento': 'Razoável',
        'acesso_saude': 'Médio',
        'risco_malaria': 0.40,
        'risco_colera': 0.25,
        'risco_dengue': 0.30,
        'hospital_referencia': 'Hospital Américo Boavida'
    },
    'Viana': {
        'provincia': 'Luanda',
        'pobreza': 'Média',
        'saneamento': 'Mau',
        'acesso_saude': 'Médio',
        'risco_malaria': 0.50,
        'risco_colera': 0.40,
        'risco_dengue': 0.35,
        'hospital_referencia': 'Hospital Geral de Viana - Bispo Emílio de Carvalho'
    },
    'Cacuaco': {
        'provincia': 'Luanda',
        'pobreza': 'Alta',
        'saneamento': 'Muito Mau',
        'acesso_saude': 'Baixo',
        'risco_malaria': 0.70,
        'risco_colera': 0.60,
        'risco_dengue': 0.45,
        'hospital_referencia': 'Hospital Geral de Cacuaco - Heróis de Kifangondo'
    },
    'Cazenga': {
        'provincia': 'Luanda',
        'pobreza': 'Alta',
        'saneamento': 'Crítico',
        'acesso_saude': 'Médio',
        'risco_malaria': 0.75,
        'risco_colera': 0.65,
        'risco_dengue': 0.50,
        'hospital_referencia': 'Hospital Municipal do Cazenga (Somague)'
    },
    'Kilamba Kiaxi': {
        'provincia': 'Luanda',
        'pobreza': 'Média',
        'saneamento': 'Baixo',
        'acesso_saude': 'Médio',
        'risco_malaria': 0.55,
        'risco_colera': 0.35,
        'risco_dengue': 0.40,
        'hospital_referencia': 'Hospital Geral de Luanda'
    },
    'Rangel': {
        'provincia': 'Luanda',
        'pobreza': 'Alta',
        'saneamento': 'Baixo',
        'acesso_saude': 'Médio',
        'risco_malaria': 0.50,
        'risco_colera': 0.55,
        'risco_dengue': 0.35,
        'hospital_referencia': 'Hospital Américo Boavida'
    },
    'Maianga': {
        'provincia': 'Luanda',
        'pobreza': 'Média',
        'saneamento': 'Médio',
        'acesso_saude': 'Alto',
        'risco_malaria': 0.35,
        'risco_colera': 0.20,
        'risco_dengue': 0.25,
        'hospital_referencia': 'Hospital Josina Machel'
    },
    'Samba': {
        'provincia': 'Luanda',
        'pobreza': 'Média',
        'saneamento': 'Baixo',
        'acesso_saude': 'Médio',
        'risco_malaria': 0.45,
        'risco_colera': 0.30,
        'risco_dengue': 0.35,
        'hospital_referencia': 'Hospital Américo Boavida'
    },
    # municipios da provincia de icolo e bengo
    'Catete': {
        'provincia': 'Icolo e Bengo',
        'pobreza': 'Alta',
        'saneamento': 'Mau',
        'acesso_saude': 'Baixo',
        'risco_malaria': 0.60,
        'risco_colera': 0.45,
        'risco_dengue': 0.30,
        'hospital_referencia': 'Hospital Municipal de Catete'
    },
    'Icolo e Bengo': {
        'provincia': 'Icolo e Bengo',
        'pobreza': 'Alta',
        'saneamento': 'Mau',
        'acesso_saude': 'Baixo',
        'risco_malaria': 0.65,
        'risco_colera': 0.50,
        'risco_dengue': 0.30,
        'hospital_referencia': 'Consultório Médico Ubuntu'
    }
}

#HEMOGRAMA

# valores de referencia para adultos (adultos angolanos) 
HEMOGRAMA_ADULTO = {
    'Homem': {
        'hemacias': {'min': 4.5, 'max': 5.9, 'unidade': 'x10⁶/mm³'},
        'hemoglobina': {'min': 12.5, 'max': 16.5, 'unidade': 'g/dL'},
        'hematocrito': {'min': 38.0, 'max': 50.0, 'unidade': '%'},
        'vcm': {'min': 80, 'max': 98, 'unidade': 'fL'},
        'hcm': {'min': 27, 'max': 33, 'unidade': 'pg'},
        'chcm': {'min': 32, 'max': 36, 'unidade': '%'},
        'rdw': {'min': 11.5, 'max': 14.5, 'unidade': '%'},
        'leucocitos': {'min': 4000, 'max': 10000, 'unidade': '/mm³'},
        'neutrofilos': {'min': 45, 'max': 70, 'unidade': '%'},
        'linfocitos': {'min': 20, 'max': 45, 'unidade': '%'},
        'monocitos': {'min': 2, 'max': 10, 'unidade': '%'},
        'eosinofilos': {'min': 1, 'max': 5, 'unidade': '%'},
        'basofilos': {'min': 0, 'max': 1, 'unidade': '%'},
        'plaquetas': {'min': 140000, 'max': 400000, 'unidade': '/mm³'},
        'vpm': {'min': 7.0, 'max': 11.0, 'unidade': 'fL'},
        'reticulocitos': {'min': 0.5, 'max': 2.5, 'unidade': '%'}
    },
    'Mulher': {
        'hemacias': {'min': 4.0, 'max': 5.2, 'unidade': 'x10⁶/mm³'},
        'hemoglobina': {'min': 11.5, 'max': 15.5, 'unidade': 'g/dL'},
        'hematocrito': {'min': 35.0, 'max': 45.0, 'unidade': '%'},
        'vcm': {'min': 80, 'max': 98, 'unidade': 'fL'},
        'hcm': {'min': 27, 'max': 33, 'unidade': 'pg'},
        'chcm': {'min': 32, 'max': 36, 'unidade': '%'},
        'rdw': {'min': 11.5, 'max': 14.5, 'unidade': '%'},
        'leucocitos': {'min': 4000, 'max': 10000, 'unidade': '/mm³'},
        'neutrofilos': {'min': 45, 'max': 70, 'unidade': '%'},
        'linfocitos': {'min': 20, 'max': 45, 'unidade': '%'},
        'monocitos': {'min': 2, 'max': 10, 'unidade': '%'},
        'eosinofilos': {'min': 1, 'max': 5, 'unidade': '%'},
        'basofilos': {'min': 0, 'max': 1, 'unidade': '%'},
        'plaquetas': {'min': 140000, 'max': 400000, 'unidade': '/mm³'},
        'vpm': {'min': 7.0, 'max': 11.0, 'unidade': 'fL'},
        'reticulocitos': {'min': 0.5, 'max': 2.5, 'unidade': '%'}
    },
    'Gestante': {
        'hemacias': {'min': 3.8, 'max': 5.0, 'unidade': 'x10⁶/mm³'},
        'hemoglobina': {'min': 10.5, 'max': 13.0, 'unidade': 'g/dL'},
        'hematocrito': {'min': 33.0, 'max': 44.0, 'unidade': '%'},
        'vcm': {'min': 80, 'max': 100, 'unidade': 'fL'},
        'hcm': {'min': 27, 'max': 33, 'unidade': 'pg'},
        'chcm': {'min': 32, 'max': 36, 'unidade': '%'},
        'rdw': {'min': 11.5, 'max': 14.5, 'unidade': '%'},
        'leucocitos': {'min': 6000, 'max': 16000, 'unidade': '/mm³'},
        'neutrofilos': {'min': 50, 'max': 75, 'unidade': '%'},
        'linfocitos': {'min': 15, 'max': 40, 'unidade': '%'},
        'monocitos': {'min': 2, 'max': 10, 'unidade': '%'},
        'eosinofilos': {'min': 1, 'max': 5, 'unidade': '%'},
        'basofilos': {'min': 0, 'max': 1, 'unidade': '%'},
        'plaquetas': {'min': 140000, 'max': 400000, 'unidade': '/mm³'},
        'vpm': {'min': 7.0, 'max': 11.0, 'unidade': 'fL'},
        'reticulocitos': {'min': 0.5, 'max': 2.5, 'unidade': '%'}
    }
}

# valores de referencia pediatricos por faixa etaria
HEMOGRAMA_PEDIATRICO = {
    'Recém-nascido (0-28 dias)': {
        'hemoglobina': {'min': 14.5, 'max': 22.5, 'unidade': 'g/dL'},
        'hematocrito': {'min': 45.0, 'max': 67.0, 'unidade': '%'},
        'leucocitos': {'min': 9000, 'max': 30000, 'unidade': '/mm³'},
        'plaquetas': {'min': 150000, 'max': 450000, 'unidade': '/mm³'},
        'reticulocitos': {'min': 3.0, 'max': 7.0, 'unidade': '%'},
        'observacao': 'Hemoglobina alta é fisiológica; leucocitose comum nos primeiros dias.'
    },
    'Lactente (1-12 meses)': {
        'hemoglobina': {'min': 10.0, 'max': 13.0, 'unidade': 'g/dL'},
        'hematocrito': {'min': 30.0, 'max': 40.0, 'unidade': '%'},
        'leucocitos': {'min': 6000, 'max': 17500, 'unidade': '/mm³'},
        'plaquetas': {'min': 150000, 'max': 450000, 'unidade': '/mm³'},
        'reticulocitos': {'min': 0.5, 'max': 2.5, 'unidade': '%'},
        'observacao': 'Queda fisiológica da Hb aos 3-6 meses (nadir fisiológico).'
    },
    'Criança (1-5 anos)': {
        'hemoglobina': {'min': 10.5, 'max': 13.5, 'unidade': 'g/dL'},
        'hematocrito': {'min': 33.0, 'max': 42.0, 'unidade': '%'},
        'leucocitos': {'min': 5000, 'max': 15500, 'unidade': '/mm³'},
        'plaquetas': {'min': 150000, 'max': 450000, 'unidade': '/mm³'},
        'reticulocitos': {'min': 0.5, 'max': 2.5, 'unidade': '%'},
        'observacao': 'Faixa de MAIOR RISCO para Malária Grave e Anemia Severa.'
    },
    'Criança (5-12 anos)': {
        'hemoglobina': {'min': 11.5, 'max': 14.5, 'unidade': 'g/dL'},
        'hematocrito': {'min': 35.0, 'max': 45.0, 'unidade': '%'},
        'leucocitos': {'min': 4500, 'max': 13500, 'unidade': '/mm³'},
        'plaquetas': {'min': 150000, 'max': 450000, 'unidade': '/mm³'},
        'reticulocitos': {'min': 0.5, 'max': 2.5, 'unidade': '%'},
        'observacao': 'Perfil aproxima-se do adulto. Atenção à drepanocitose.'
    }
}

# valores criticos acao imediata
VALORES_CRITICOS = {
    'hemoglobina_critica': {'valor': 7.0, 'acao': 'Avaliar necessidade de transfusão'},
    'hemoglobina_muito_critica': {'valor': 5.0, 'acao': 'Transfusão URGENTE'},
    'plaquetas_criticas': {'valor': 50000, 'acao': 'Risco de hemorragia espontânea'},
    'plaquetas_muito_criticas': {'valor': 20000, 'acao': 'Risco de hemorragia cerebral'},
    'leucocitos_neutropenia': {'valor': 1500, 'acao': 'Risco elevado de infecção grave'},
    'leucocitos_leucocitose_severa': {'valor': 50000, 'acao': 'Investigar leucemia'}
}

#DOENCAS

DOENCAS = {
    # doencas infecciosas
    'Malária': {
        'agente': 'Plasmodium falciparum (principal parasita pelo mosquito Anopheles)',
        'assinatura': {
            'hemoglobina': 'Baixa (Anemia)',
            'plaquetas': 'Muito baixas (< 100.000/mm³)',
            'leucocitos': 'Normais ou baixos (Leucopenia)',
            'hematocrito': 'Baixo'
        },
        'marcador_chave': 'Anemia + Trombocitopenia em contexto febril',
        'exame_confirmatorio': 'Gota Espessa (Padrão Ouro) ou Teste de Diagnóstico Rápido',
        'conduta_leve': 'Coartem (Arteméter/Lumefantrina) - tomar sempre após uma refeição com gordura (almoço/jantar) ou com pão com manteiga ou jinguba se for matabichar simples',
        'conduta_grave': 'Artesunato EV (até tolerar oral) + Internamento',
        'sinais_alarme': [
    'Convulsões',
    'Alteração do estado de consciência (coma ou sonolência excessiva)',
    'Vómitos repetidos (não retém nada no estômago)',
    'Urina cor de coca-cola (hemoglobinúria)',
    'Dificuldade em respirar (respiração profunda/cansada)',
    'Icterícia (olhos amarelos)',
    'Prostração extrema (não consegue sentar ou ficar de pé)'
],
        'referencia': 'Hospital Pediátrico David Bernardino (crianças) / Hospital Josina Machel (adultos)'
    },
    'Dengue': {
        'agente': 'Vírus Dengue (DENV 1-4)',
        'assinatura': {
            'hemoglobina': 'Estável ou AUMENTADA (hemoconcentração)',
            'hematocrito': 'AUMENTADO (sinal de extravasamento plasmático)',
            'plaquetas': 'Queda rápida e precoce (< 100.000)',
            'leucocitos': 'Leucopenia pronunciada'
        },
        'marcador_chave': 'Hemoconcentração + Plaquetopenia severa',
        'exame_confirmatorio': 'NS1 (fase aguda) ou IgM/IgG',
        'conduta_leve': 'Hidratação oral rigorosa (60-80 mL/kg/dia)',
        'conduta_grave': 'Hidratação IV + Monitorização do Ht a cada 2h',
        'sinais_alarme': [
            'Dor abdominal intensa e contínua',
            'Vómitos persistentes (3+ episódios)',
            'Sangramento de mucosas (gengivas/nariz)',
            'Letargia ou irritabilidade',
            'Aumento do fígado > 2cm'
        ],
        'referencia': 'Hospital Américo Boavida'
    },
    'Febre Tifóide': {
        'agente': 'Salmonella typhi',
        'assinatura': {
            'leucocitos': 'Leucopenia (paradoxal para infecção bacteriana)',
            'eosinofilos': 'Zero ou muito baixos (Aneosinofilia)',
            'plaquetas': 'Normais ou baixas'
        },
        'marcador_chave': 'Leucopenia + Eosinófilos = 0 + Febre prolongada',
        'exame_confirmatorio': 'Hemocultura (1ª semana) ou Coprocultura (2ª semana)',
        'conduta_leve': 'Ciprofloxacina 500mg 12/12h x 7-14 dias',
        'conduta_grave': 'Ceftriaxona IV 2g/dia + Internamento',
        'sinais_alarme': [
            'Dor abdominal tipo tábua (rigidez) - sinal de perfuração',
            'Confusão mental',
            'Hemorragia digestiva'
        ],
        'referencia': 'Hospital Américo Boavida'
    },
    'Cólera': {
        'agente': 'Vibrio cholerae',
        'assinatura': {
            'hematocrito': 'Muito alto (desidratação severa)',
            'hemoglobina': 'Falsamente alta (hemoconcentração)',
            'leucocitos': 'Leucocitose leve'
        },
        'marcador_chave': 'Hemoconcentração + Diarreia aquosa tipo água de arroz',
        'exame_confirmatorio': 'Cultura de fezes',
        'conduta_leve': 'Plano A/B de hidratação (SRO)',
        'conduta_grave': 'Plano C (Ringer Lactato IV) + Azitromicina',
        'sinais_alarme': [
            'Olhos encovados',
            'Sinal da prega positivo (> 2 segundos)',
            'Ausência de lágrimas',
            'Letargia ou inconsciência'
        ],
        'referencia': 'Centro de Tratamento de Doenças Diarreicas'
    },
    'Tuberculose': {
        'agente': 'Mycobacterium tuberculosis',
        'assinatura': {
            'monocitos': 'Monocitose (> 10%)',
            'hemoglobina': 'Anemia de doença crónica (normocítica)',
            'leucocitos': 'Normais ou elevados',
            'vhs': 'Elevada (se disponível)'
        },
        'marcador_chave': 'Monocitose + Anemia + Tosse > 2 semanas',
        'exame_confirmatorio': 'Baciloscopia (BAAR) ou GeneXpert',
        'conduta': 'Protocolo DOTS (Rifampicina + Isoniazida + Pirazinamida + Etambutol)',
        'sinais_alarme': [
            'Hemoptise (sangue na tosse)',
            'Perda de peso > 10%',
            'Sudorese noturna profusa'
        ],
        'referencia': 'Hospital Sanatório de Luanda'
    },
    'HIV/SIDA': {
        'agente': 'Vírus da Imunodeficiência Humana',
        'assinatura': {
            'linfocitos': 'Linfopenia progressiva (CD4 baixo)',
            'hemoglobina': 'Anemia (multifatorial)',
            'plaquetas': 'Podem estar baixas',
            'leucocitos': 'Leucopenia'
        },
        'marcador_chave': 'Pancitopenia leve + Infecções oportunistas',
        'exame_confirmatorio': 'Teste Rápido HIV (com aconselhamento)',
        'conduta': 'TARV (Dolutegravir + Tenofovir + Lamivudina)',
        'profilaxia': 'Cotrimoxazol se CD4 < 200',
        'referencia': 'Hospital Sanatório de Luanda'
    },
    'Hepatites Virais': {
        'agente': 'Vírus Hepatite A, B, C, E',
        'assinatura': {
            'leucocitos': 'Leucopenia leve',
            'transaminases': 'Elevadas (TGO/TGP > 10x)',
            'bilirrubinas': 'Elevadas (icterícia)'
        },
        'marcador_chave': 'Leucopenia + Icterícia + Transaminases altas',
        'exame_confirmatorio': 'Serologia (HBsAg, Anti-HCV, IgM anti-HAV)',
        'conduta': 'Suporte + Repouso + Evitar hepatotóxicos',
        'referencia': 'Hospital Américo Boavida'
    },
        'Raiva (Mordedura Animal)': {
        'agente': 'Vírus da Raiva (transmitido por cães, macacos, gatos)',
        'assinatura': {
            'hemograma': 'NORMAL (a doença não altera o sangue)',
            'historia_clinica': 'História recente de mordedura ou lambedura em ferida'
        },
        'marcador_chave': 'História de mordedura + Sem alteração no hemograma',
        'exame_confirmatorio': 'Não esperar exames! O diagnóstico é a história do acidente.',
        'conduta_leve': 'Lavar com água e sabão por 15 min + Vacina Antirrábica (Dia 0, 3, 7, 14)',
        'conduta_grave': 'Soro Antirrábico + Vacina (se mordedura na cabeça, pescoço ou mãos)',
        'sinais_alarme': [
            'Hidrofobia (medo de água)',
            'Aerofobia (medo de ventilação)',
            'Agitação psicomotora'
        ],
        'aviso_critico': 'Se aparecerem sintomas, a mortalidade é de quase 100%. Vacinar IMEDIATAMENTE após a mordida.',
        'referencia': 'Direção Municipal de Saúde (Área de Vacinação) / Hospital Josina Machel'
    },
    # doencas parasitarias
    'Esquistossomose': {
        'agente': 'Schistosoma haematobium / mansoni',
        'assinatura': {
            'eosinofilos': 'Eosinofilia marcada (> 15%)',
            'hemoglobina': 'Anemia leve a moderada'
        },
        'marcador_chave': 'Eosinofilia + Hematúria (S. haematobium)',
        'exame_confirmatorio': 'Pesquisa de ovos na urina ou fezes',
        'conduta': 'Praziquantel 40mg/kg dose única',
        'referencia': 'Centro de Saúde'
    },
    'Ascaridíase': {
        'agente': 'Ascaris lumbricoides',
        'assinatura': {
            'eosinofilos': 'Eosinofilia (5-15%)',
            'hemoglobina': 'Anemia microcítica leve'
        },
        'marcador_chave': 'Eosinofilia + Dor abdominal + Desnutrição',
        'exame_confirmatorio': 'Exame parasitológico de fezes',
        'conduta': 'Albendazol 400mg dose única',
        'referencia': 'Centro de Saúde'
    },
    'Ancilostomíase': {
        'agente': 'Ancylostoma duodenale / Necator americanus',
        'assinatura': {
            'eosinofilos': 'Eosinofilia',
            'hemoglobina': 'Anemia microcítica hipocrômica (por perda de sangue)',
            'vcm': 'Baixo',
            'hcm': 'Baixo'
        },
        'marcador_chave': 'Eosinofilia + Anemia ferropriva + Geofagia',
        'exame_confirmatorio': 'Exame parasitológico de fezes',
        'conduta': 'Albendazol 400mg x 3 dias + Sulfato Ferroso',
        'referencia': 'Centro de Saúde'
    },
    # doencas hematologicas
    'Drepanocitose (SS)': {
        'agente': 'Hemoglobina S homozigótica',
        'assinatura': {
            'hemoglobina': 'Muito baixa (6-9 g/dL)',
            'vcm': 'Normal ou ligeiramente baixo',
            'reticulocitos': 'Elevados (> 3%) - hemólise ativa',
            'esfregaco': 'Células em foice (drepanócitos)',
            'bilirrubina_indireta': 'Elevada'
        },
        'marcador_chave': 'Anemia crónica + Reticulocitose + Crises vaso-oclusivas',
        'exame_confirmatorio': 'Eletroforese de Hemoglobina (HbS majoritária)',
        'conduta_base': 'Ácido Fólico 5mg/dia + Hidratação + Evitar frio',
        'conduta_crise': 'Analgesia + Hidratação IV + O2 se necessário',
        'sinais_alarme': [
            'Febre (risco de infecção grave)',
            'Dor torácica (síndrome torácica aguda)',
            'Priapismo',
            'AVC (fraqueza súbita)'
        ],
        'referencia': 'Instituto de Hematologia de Luanda (IHL)'
    },
    'Traço Falciforme (AS)': {
        'assinatura': {
            'hemograma': 'Geralmente NORMAL',
            'vcm': 'Normal ou leve microcitose'
        },
        'marcador_chave': 'Hemograma normal em paciente com história familiar',
        'exame_confirmatorio': 'Eletroforese de Hemoglobina (HbA + HbS)',
        'conduta': 'Aconselhamento genético para reprodução',
        'observacao': 'Portador assintomático - não é doença, mas transmite o gene'
    },
    'Talassemia': {
        'assinatura': {
            'hemoglobina': 'Pouco baixa (desproporcional ao VCM)',
            'vcm': 'MUITO baixo (< 70 fL)',
            'hcm': 'Baixo',
            'rdw': 'Normal (diferente da ferropriva)',
            'hemacias': 'Normais ou ELEVADAS'
        },
        'marcador_chave': 'Microcitose severa com anemia leve',
        'exame_confirmatorio': 'Eletroforese de Hemoglobina (HbA2 elevada)',
        'conduta': 'Referir Hematologia - não dar ferro sem confirmação',
        'referencia': 'Instituto de Hematologia de Luanda (IHL)'
    },
    'Anemia Ferropriva': {
        'assinatura': {
            'hemoglobina': 'Baixa',
            'vcm': 'Baixo (< 80 fL) - Microcitose',
            'hcm': 'Baixo - Hipocromia',
            'rdw': 'ELEVADO (> 15%) - Anisocitose',
            'ferritina': 'Baixa (se disponível)'
        },
        'marcador_chave': 'Anemia microcítica hipocrômica + RDW alto',
        'conduta': 'Sulfato Ferroso 3-6 meses (tomar em jejum com sumo de limão)',
        'orientacao_nutricional': 'Aumentar consumo de fígado, quizaca, feijão',
        'aviso': 'Evitar chá ou café junto às refeições (cortam absorção)'
    },
    'Anemia Megaloblástica': {
        'assinatura': {
            'hemoglobina': 'Baixa',
            'vcm': 'MUITO alto (> 110 fL) - Macrocitose',
            'neutrofilos_hipersegmentados': 'Presentes no esfregaço'
        },
        'marcador_chave': 'Anemia macrocítica + VCM > 110',
        'exame_confirmatorio': 'Dosagem de B12 e Ácido Fólico',
        'conduta': 'Vitamina B12 IM + Ácido Fólico',
        'causas_angola': 'Alcoolismo, dieta pobre em proteínas, gastrite crónica'
    },
    'Leucemia (Suspeita)': {
        'assinatura': {
            'leucocitos': 'Muito altos (> 50.000) OU muito baixos com anemia',
            'hemoglobina': 'Baixa',
            'plaquetas': 'Baixas',
            'blastos': 'Presentes no esfregaço'
        },
        'marcador_chave': 'Pancitopenia + Leucocitose extrema + Blastos',
        'exame_confirmatorio': 'Mielograma',
        'conduta': 'Referência URGENTE',
        'referencia': 'Instituto Angolano de Controlo do Cancro (IACC/IOA)'
    },
    # outras condicoes
    'Desnutrição (Kwashiorkor/Marasmo)': {
        'assinatura': {
            'hemoglobina': 'Baixa',
            'proteinas_totais': 'Baixas',
            'albumina': 'Baixa',
            'linfocitos': 'Baixos (imunodepressão)'
        },
        'marcador_chave': 'Anemia + Edema + Hipoalbuminemia',
        'conduta': 'Protocolo F-75 (fase inicial) / F-100 (recuperação)',
        'referencia': 'Centro de Recuperação Nutricional'
    },
    'Desidratação': {
        'assinatura': {
            'hematocrito': 'FALSAMENTE alto (hemoconcentração)',
            'hemoglobina': 'FALSAMENTE alta',
            'ureia': 'Elevada (se disponível)'
        },
        'marcador_chave': 'Hemoconcentração + Sinais clínicos de desidratação',
        'conduta': 'Plano A (leve), B (moderada) ou C (grave) de hidratação',
        'sinais_clinicos': [
            'Olhos encovados',
            'Sinal da prega > 2 segundos',
            'Fontanela deprimida (lactentes)',
            'Ausência de lágrimas'
        ]
    }
}

#FARMACOLOGIA E SEGURANCA

MEDICAMENTOS = {
    # antimalaricos
    'Coartem': {
        'principio_ativo': 'Arteméter + Lumefantrina',
        'indicacao': 'Malária não complicada por P. falciparum',
        'dose_adulto': '4 comprimidos de 12/12h por 3 dias (total 24 comp)',
        'dose_pediatrica': 'Conforme peso - ver tabela específica',
        'aviso_importante': 'OBRIGATÓRIO tomar com leite ou comida gordurosa para absorção',
        'contraindicacao': 'Primeiro trimestre de gravidez'
    },
    'Artesunato IV': {
        'principio_ativo': 'Artesunato',
        'indicacao': 'Malária GRAVE',
        'dose': '2.4 mg/kg IV às 0h, 12h, 24h, depois 1x/dia',
        'aviso_importante': 'Monitorar Hemoglobina no dia 7 e 14 (risco de anemia pós-artesunato)',
        'local': 'Apenas uso hospitalar'
    },
    'Quinino': {
        'principio_ativo': 'Sulfato ou Dicloridrato de Quinino',
        'indicacao': 'Alternativa se falha de artemisininas',
        'aviso_importante': 'Risco de HIPOGLICEMIA e OTOTOXICIDADE (surdez)',
        'monitorizacao': 'Glicemia capilar a cada 4-6h'
    },
    # antibioticos
    'Amoxicilina/Clavulanato': {
        'indicacao': 'Infecções respiratórias, otites, sinusites',
        'dose_adulto': '500/125mg de 8/8h ou 875/125mg de 12/12h',
        'dose_pediatrica': '25-45 mg/kg/dia dividido em 2-3 doses'
    },
    'Ceftriaxona': {
        'indicacao': 'Sépsis, meningite, tifóide grave',
        'dose_adulto': '1-2g IV 1x/dia',
        'dose_pediatrica': '50-100 mg/kg/dia (máx 4g)',
        'local': 'Uso hospitalar'
    },
    'Ciprofloxacina': {
        'indicacao': 'Febre tifóide, infecções urinárias',
        'dose_adulto': '500mg de 12/12h',
        'aviso_importante': 'EVITAR em crianças e grávidas (afeta cartilagem)'
    },
    'Cotrimoxazol': {
        'indicacao': 'Profilaxia em HIV+, infecções urinárias',
        'dose_adulto': '800/160mg 1x/dia (profilaxia)',
        'aviso_importante': 'Iniciar se CD4 < 200 ou SIDA definidora'
    },
    'Azitromicina': {
        'indicacao': 'Cólera, clamídia, respiratórias atípicas',
        'dose_adulto': '1g dose única (cólera) ou 500mg/dia x 3 dias',
        'dose_pediatrica': '10-20 mg/kg/dia'
    },
    # antiparasitarios
    'Albendazol': {
        'indicacao': 'Parasitoses intestinais (Áscaris, Ancilostoma)',
        'dose_adulto': '400mg dose única ou 400mg/dia x 3 dias',
        'dose_pediatrica': '> 2 anos: mesma dose do adulto',
        'aviso_importante': 'Evitar no primeiro trimestre de gravidez'
    },
    'Praziquantel': {
        'indicacao': 'Esquistossomose',
        'dose': '40 mg/kg dose única',
        'aviso_importante': 'Pode causar tontura - tomar à noite'
    },
    # suplementos
    'Sulfato Ferroso': {
        'indicacao': 'Anemia ferropriva',
        'dose_adulto': '60mg de ferro elementar 2-3x/dia',
        'dose_pediatrica': '3-6 mg/kg/dia de ferro elementar',
        'duracao': '3-6 meses (até normalizar ferritina)',
        'aviso_importante': 'Tomar em JEJUM com sumo de LIMÃO (vitamina C)',
        'evitar': 'Chá, café, leite junto à dose (cortam absorção)'
    },
    'Ácido Fólico': {
        'indicacao': 'Drepanocitose, gravidez, anemia megaloblástica',
        'dose': '5mg/dia',
        'observacao': 'ESSENCIAL na drepanocitose (hemólise crónica)'
    },
    'Vitamina B12': {
        'indicacao': 'Anemia megaloblástica',
        'dose': '1000mcg IM 1x/semana x 4 semanas, depois 1x/mês',
        'causas_deficiencia': 'Alcoolismo, vegetarianismo estrito, gastrite atrófica'
    }
}

# alertas farmacogeneticos especificos para populacao angolana
ALERTAS_FARMACOGENETICOS = {
    'Inibidores da ECA': {
        'exemplos': 'Enalapril, Lisinopril, Captopril',
        'alerta': 'Populações de origem africana podem responder MENOS a estes fármacos isolados',
        'risco': 'Maior risco de ANGIOEDEMA (inchaço de face/língua)',
        'alternativa': 'Considerar associar com Hidroclorotiazida ou usar Amlodipina'
    },
    'Varfarina': {
        'alerta': 'Variação genética comum em Angola (VKORC1, CYP2C9)',
        'risco': 'Dose padrão internacional pode causar HEMORRAGIA',
        'conduta': 'Iniciar com doses baixas e monitorar INR frequentemente'
    },
    'Efavirenz': {
        'alerta': 'Metabolismo lento comum em Angola (CYP2B6 *6/*6)',
        'risco': 'Dose padrão pode causar TONTURA severa, pesadelos, toxicidade',
        'conduta': 'Preferir Dolutegravir nos novos regimes de TARV'
    },
    'Codeína': {
        'alerta': 'Metabolizadores ultrarrápidos (CYP2D6) podem ter toxicidade',
        'risco': 'Depressão respiratória, especialmente em crianças',
        'conduta': 'Evitar em crianças; preferir Paracetamol ou Ibuprofeno'
    }
}

# interacoes medicamentosas perigosas
INTERACOES_PERIGOSAS = {
    'Varfarina + Quizaca/Couve': {
        'mecanismo': 'Folhas verdes são ricas em Vitamina K',
        'efeito': 'CORTA o efeito anticoagulante',
        'conduta': 'Manter dieta estável, não variar bruscamente'
    },
    'Sulfato Ferroso + Chá/Café': {
        'mecanismo': 'Taninos quelam o ferro',
        'efeito': 'Reduz absorção em até 60%',
        'conduta': 'Ferro 2h antes ou depois de chá/café'
    },
    'Quinino + Hipoglicemiantes': {
        'mecanismo': 'Quinino estimula secreção de insulina',
        'efeito': 'Hipoglicemia severa',
        'conduta': 'Monitorar glicemia a cada 4-6h'
    },
    'Ciprofloxacina + Antiácidos': {
        'mecanismo': 'Alumínio e magnésio quelam a ciprofloxacina',
        'efeito': 'Reduz absorção drasticamente',
        'conduta': 'Tomar cipro 2h antes ou 6h depois de antiácidos'
    }
}

#SAZONALIDADE E EPIDEMIOLOGIA

# calendario epidemiologico de luanda
SAZONALIDADE_LUANDA = {
    'Janeiro': {
        'estacao': 'Chuvosa',
        'temperatura': '25-32°C',
        'riscos_principais': ['Cólera', 'Malária', 'Doenças diarreicas'],
        'alerta': 'Início dos surtos de cólera'
    },
    'Fevereiro': {
        'estacao': 'Chuvosa (Pico)',
        'temperatura': '26-33°C',
        'riscos_principais': ['Cólera', 'Malária', 'Dengue'],
        'alerta': 'Chuvas torrenciais - pico de cólera'
    },
    'Março': {
        'estacao': 'Chuvosa (Pico)',
        'temperatura': '26-33°C',
        'riscos_principais': ['Malária', 'Cólera', 'Dengue'],
        'alerta': 'PICO de Malária (águas paradas)'
    },
    'Abril': {
        'estacao': 'Chuvosa (Pico)',
        'temperatura': '25-32°C',
        'riscos_principais': ['Malária', 'Dengue', 'Febre Tifóide'],
        'alerta': 'Proliferação do Aedes aegypti'
    },
    'Maio': {
        'estacao': 'Chuvosa (Final)',
        'temperatura': '24-30°C',
        'riscos_principais': ['Malária', 'Dengue'],
        'alerta': 'Malária ainda elevada'
    },
    'Junho': {
        'estacao': 'Cacimbo',
        'temperatura': '18-26°C',
        'riscos_principais': ['Doenças respiratórias', 'Crises de drepanocitose'],
        'alerta': 'Frio e poeira - proteger drepanocíticos'
    },
    'Julho': {
        'estacao': 'Cacimbo',
        'temperatura': '17-25°C',
        'riscos_principais': ['Doenças respiratórias', 'Asma'],
        'alerta': 'Mês mais frio - poeira intensa'
    },
    'Agosto': {
        'estacao': 'Cacimbo',
        'temperatura': '18-26°C',
        'riscos_principais': ['Doenças respiratórias'],
        'alerta': 'Final do período seco'
    },
    'Setembro': {
        'estacao': 'Transição',
        'temperatura': '20-28°C',
        'riscos_principais': ['Doenças respiratórias'],
        'alerta': 'Início da transição para chuvas'
    },
    'Outubro': {
        'estacao': 'Chuvosa (Início)',
        'temperatura': '22-30°C',
        'riscos_principais': ['Febre Tifóide', 'Malária'],
        'alerta': 'Início do período húmido'
    },
    'Novembro': {
        'estacao': 'Chuvosa',
        'temperatura': '24-31°C',
        'riscos_principais': ['Malária', 'Febre Tifóide'],
        'alerta': 'Chuvas regulares'
    },
    'Dezembro': {
        'estacao': 'Chuvosa',
        'temperatura': '25-32°C',
        'riscos_principais': ['Malária', 'Doenças diarreicas'],
        'alerta': 'Preparar para surtos de Janeiro'
    }
}

# picos de doencas resumo
PICOS_DOENCAS = {
    'Malária': {'meses': ['Março', 'Abril', 'Maio'], 'justificativa': 'Pós-chuvas intensas, águas paradas'},
    'Cólera': {'meses': ['Janeiro', 'Fevereiro', 'Março'], 'justificativa': 'Chuvas torrenciais e inundações'},
    'Dengue': {'meses': ['Abril', 'Maio', 'Junho'], 'justificativa': 'Proliferação do Aedes pós-chuvas'},
    'Respiratórias': {'meses': ['Junho', 'Julho', 'Agosto'], 'justificativa': 'Cacimbo - frio e poeira'},
    'Febre Tifóide': {'meses': ['Outubro', 'Novembro', 'Dezembro', 'Janeiro', 'Fevereiro', 'Março', 'Abril'], 'justificativa': 'Período húmido'}
}

#REFERENCIAS E CUSTOS

CENTROS_REFERENCIA = {
    'Leucemia e Cancro': {
        'nome': 'Instituto Angolano de Controlo do Cancro (IACC/IOA)',
        'tipo': 'Referência nacional para oncologia'
    },
    'Drepanocitose': {
        'nome': 'Instituto de Hematologia de Luanda (IHL)',
        'tipo': 'Referência para doenças do sangue'
    },
    'Malária Grave Pediátrica': {
        'nome': 'Hospital Pediátrico David Bernardino',
        'tipo': 'Referência pediátrica'
    },
    'Malária Grave Adultos': {
        'nome': 'Hospital Josina Machel',
        'tipo': 'Hospital central'
    },
    'Trauma e Cirurgia': {
        'nome': 'Hospital Américo Boavida',
        'tipo': 'Urgências e cirurgia'
    },
    'HIV/SIDA e Tuberculose': {
        'nome': 'Hospital Sanatório de Luanda',
        'tipo': 'Doenças infecciosas'
    },
    'Doenças Diarreicas': {
        'nome': 'Centro de Tratamento de Doenças Diarreicas (CTDD)',
        'tipo': 'Cólera e desidratação grave'
    }
}

# custos aproximados em luanda 2026
CUSTOS_HEMOGRAMA = {
    'Público': {
        'valor': '500 - 1.000 Kz',
        'observacao': 'Gratuito na teoria, taxa simbólica na prática. Frequente rutura de reagentes.'
    },
    'Privado Médio': {
        'valor': '5.000 - 8.500 Kz',
        'observacao': 'Laboratórios de bairro, resultado em 24-48h'
    },
    'Privado Elite': {
        'valor': '12.000 - 25.000 Kz',
        'observacao': 'Clínicas de referência, resultado em 2-6h'
    }
}

#GRAVIDADE

SCORES_GRAVIDADE = {
    'Leve': {
        'criterios': {
            'hemoglobina': '> 10 g/dL',
            'plaquetas': '> 100.000/mm³',
            'estado_consciencia': 'Consciente e orientado',
            'sinais_vitais': 'Estáveis'
        },
        'acao': 'Tratamento ambulatorial',
        'seguimento': 'Reavaliação em 48-72h'
    },
    'Moderado': {
        'criterios': {
            'hemoglobina': '7-10 g/dL',
            'plaquetas': '50.000-100.000/mm³',
            'febre': '> 39°C',
            'vomitos': 'Presentes mas controlados'
        },
        'acao': 'Observação no Centro de Saúde (6-24h)',
        'seguimento': 'Reavaliação a cada 6h'
    },
    'Grave': {
        'criterios': {
            'hemoglobina': '< 7 g/dL',
            'plaquetas': '< 50.000/mm³',
            'vomitos': 'Persistentes',
            'desidratacao': 'Moderada a grave'
        },
        'acao': 'Internamento hospitalar OBRIGATÓRIO',
        'seguimento': 'Monitorização contínua'
    },
    'Crítico': {
        'criterios': {
            'hemoglobina': '< 5 g/dL',
            'plaquetas': '< 20.000/mm³',
            'consciencia': 'Alterada (letargia, coma)',
            'choque': 'Presente (PA baixa, pulso fraco)',
            'convulsoes': 'Presentes'
        },
        'acao': 'Referência URGENTE para Hospital Central',
        'seguimento': 'UCI se disponível'
    }
}

#EXAMES COMPLEMENTARES

EXAMES_COMPLEMENTARES = {
    'Malária': {
        'padrao_ouro': 'Gota Espessa (microscopia)',
        'alternativa': 'TDR (Teste de Diagnóstico Rápido)',
        'quando_pedir': 'Toda febre em zona endémica',
        'observacao': 'TDR pode dar falso negativo em parasitemia baixa'
    },
    'Febre Tifóide': {
        'primeira_semana': 'Hemocultura',
        'segunda_semana': 'Coprocultura',
        'teste_rapido': 'Widal (baixa especificidade - usar com cautela)',
        'observacao': 'Widal positivo isolado NÃO confirma diagnóstico'
    },
    'Anemia': {
        'ferritina': 'Avaliar reservas de ferro',
        'eletroforese_hb': 'Se suspeita de drepanocitose ou talassemia',
        'reticulocitos': 'Avaliar produção medular',
        'esfregaco': 'Ver morfologia (drepanócitos, esquizócitos)'
    },
    'HIV': {
        'teste_rapido': 'Determine ou similar',
        'observacao': 'SEMPRE com aconselhamento pré e pós-teste',
        'confirmacao': 'Segundo teste rápido de marca diferente'
    },
        'Raiva (Suspeita)': {
        'padrao_ouro': 'Imunofluorescência (post-mortem do animal)',
        'conduta_imediata': 'Não aguardar laboratório. Iniciar profilaxia pós-exposição.',
        'observacao': 'O hemograma normal não descarta a doença.'
    },
    'Dengue': {
        'fase_aguda': 'NS1 (até 5º dia)',
        'fase_tardia': 'IgM/IgG (após 5º dia)',
        'hemograma_seriado': 'A cada 12-24h para monitorar hemoconcentração'
    }
}

# alternativas quando hemograma nao disponivel 
AVALIACAO_CLINICA_SEM_LABORATORIO = {
    'Anemia': {
        'sinais': [
            'Palidez palmar (comparar com a do examinador)',
            'Palidez conjuntival (pálpebra inferior)',
            'Palidez do leito ungueal'
        ],
        'classificacao': {
            'Palidez intensa': 'Anemia grave provável (Hb < 7)',
            'Palidez leve': 'Anemia leve a moderada (Hb 7-10)',
            'Sem palidez': 'Provavelmente sem anemia'
        }
    },
    'Desidratação': {
        'sinais': [
            'Olhos encovados',
            'Sinal da prega cutânea (> 2 segundos = grave)',
            'Fontanela deprimida (lactentes)',
            'Mucosas secas',
            'Ausência de lágrimas'
        ]
    },
    'Desnutrição': {
        'sinais': [
            'Emagrecimento visível',
            'Edema bilateral de membros inferiores',
            'Cabelo ralo e descolorido',
            'Dermatoses (pele descamativa)'
        ]
    }
}

# NUTRICAO E DIETA ANGOLANA

DIETA_ANGOLANA = {
    'Fontes_Ferro_Animal': [
        'Fígado (boi ou galinha) - MELHOR fonte',
        'Miúdos (moela, coração, rim)',
        'Peixe seco (cacusso, makayabu, etc)',
        'Carne de caça (Verificação Obrigatória)',
        'Sangue (chouriço de sangue)'
    ],
    'Fontes_Ferro_Vegetal': [
        'Quizaca (folhas de mandioqueira)',
        'Jimboa (folha verde escura)',
        'Espinafre agrícola',
        'Feijão (todos os tipos)',
        'Lentilha',
        'Grão-de-bico'
    ],
    'Potenciadores_Absorcao': [
        'Limão (vitamina C)',
        'Laranja',
        'Tomate',
        'Pimento'
    ],
    'Inibidores_Absorcao': [
        'Chá (taninos)',
        'Café (taninos)',
        'Leite junto ao ferro',
        'Antiácidos'
    ],
    'Recomendacao_Pratica': 'Comer fígado ou quizaca 2-3x por semana. Espremer limão na comida. Evitar chá/café nas refeições principais.'
}


# PREVALENCIAS E DADOS EPIDEMIOLOGICOS


PREVALENCIAS_ANGOLA = {
    'Traço Falciforme (HbAS)': {
        'percentagem': '18-20%',
        'observacao': 'Portadores saudáveis - aconselhamento genético é importante'
    },
    'Doença Falciforme (HbSS)': {
        'percentagem': '~2%',
        'observacao': 'Doença crónica grave - acompanhamento no IHL'
    },
    'Anemia (crianças < 5 anos)': {
        'percentagem': '~65%',
        'observacao': 'Multifatorial: malária, nutrição, parasitoses'
    },
    'Anemia (mulheres grávidas)': {
        'percentagem': '~50%',
        'observacao': 'Suplementação de ferro obrigatória no pré-natal'
    },
    'Malária (casos/ano)': {
        'numero': '> 10 milhões',
        'observacao': 'Principal causa de mortalidade'
    },
    'HIV (adultos 15-49)': {
        'percentagem': '~1.8%',
        'observacao': 'Testar e iniciar TARV'
    },
    'Parasitoses Intestinais (rural)': {
        'percentagem': '~50%',
        'observacao': 'Desparasitação semestral recomendada'
    }
}


#CALCULOS PEDIATRICOS


# tabela de doses por peso para medicamentos comuns
DOSES_PEDIATRICAS = {
    'Artesunato IV': {
        'dose': '2.4 mg/kg',
        'frequencia': '0h, 12h, 24h, depois 1x/dia',
        'via': 'IV',
        'diluicao': 'Diluir em bicarbonato de sódio 5%'
    },
    'Paracetamol': {
        'dose': '10-15 mg/kg',
        'frequencia': 'De 6/6h ou 8/8h',
        'via': 'Oral ou Retal',
        'maximo': 'Não exceder 60 mg/kg/dia (e NUNCA exceder 4g totais/dia em adolescentes/adultos)'
    },
    'Ibuprofeno': {
        'dose': '5-10 mg/kg',
        'frequencia': 'De 8/8h',
        'via': 'Oral',
        'aviso': 'Evitar se desidratação ou dengue'
    },
    'Amoxicilina': {
        'dose': '25-50 mg/kg/dia',
        'frequencia': 'Dividido em 3 doses (8/8h)',
        'via': 'Oral'
    },
    'Ceftriaxona': {
        'dose': '50-100 mg/kg/dia',
        'frequencia': '1x/dia',
        'via': 'IV ou IM',
        'maximo': '4g/dia'
    },
    'Sulfato Ferroso': {
        'dose_tratamento': '3-6 mg/kg/dia de ferro elementar',
        'dose_profilaxia': '1-2 mg/kg/dia',
        'frequencia': 'Em jejum, com vitamina C',
        'duracao': '3-6 meses'
    }
}


def calcular_dose(peso_kg, medicamento):
    """
    calcula a dose de um medicamento com base no peso do paciente
    retorna a dose calculada e instrucoes
    """
    if medicamento not in DOSES_PEDIATRICAS:
        return None, f"Medicamento '{medicamento}' não encontrado na base de dados"
    
    info = DOSES_PEDIATRICAS[medicamento]
    dose_str = info['dose']
    
    #tirar o valorda dose
    import re
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:-\s*(\d+(?:\.\d+)?))?\s*mg/kg', dose_str)
    
    if match:
        dose_min = float(match.group(1))
        dose_max = float(match.group(2)) if match.group(2) else dose_min
        
        dose_calculada_min = dose_min * peso_kg
        dose_calculada_max = dose_max * peso_kg
        
        resultado = {
            'medicamento': medicamento,
            'peso': peso_kg,
            'dose_min': round(dose_calculada_min, 1),
            'dose_max': round(dose_calculada_max, 1),
            'frequencia': info['frequencia'],
            'via': info['via']
        }
        
        if 'maximo' in info:
            resultado['aviso_maximo'] = info['maximo']
        if 'aviso' in info:
            resultado['aviso'] = info['aviso']
            
        return resultado, None
    
    return None, "Não foi possível calcular a dose"



#FUNCOES DE ANALISE

def classificar_hemograma(valores, perfil='Homem'):
    """
    classifica cada parametro do hemograma como baixo, normal ou alto
    com base nos valores de referencia para o perfil do paciente
    """
    if perfil in HEMOGRAMA_ADULTO:
        referencias = HEMOGRAMA_ADULTO[perfil]
    elif perfil in HEMOGRAMA_PEDIATRICO:
        referencias = HEMOGRAMA_PEDIATRICO[perfil]
    else:
        return None, f"Perfil '{perfil}' não encontrado"
    
    resultado = {}
    
    for parametro, valor in valores.items():
        if parametro in referencias:
            ref = referencias[parametro]
            if valor < ref['min']:
                resultado[parametro] = {
                    'valor': valor,
                    'status': 'BAIXO',
                    'referencia': f"{ref['min']}-{ref['max']} {ref['unidade']}"
                }
            elif valor > ref['max']:
                resultado[parametro] = {
                    'valor': valor,
                    'status': 'ALTO',
                    'referencia': f"{ref['min']}-{ref['max']} {ref['unidade']}"
                }
            else:
                resultado[parametro] = {
                    'valor': valor,
                    'status': 'Normal',
                    'referencia': f"{ref['min']}-{ref['max']} {ref['unidade']}"
                }
    
    return resultado, None


def sugerir_diagnostico(hemograma_classificado, contexto=None):
    """
    sugere possiveis diagnosticos com base no padrao do hemograma
    e no contexto epidemiologico (municipio, mes)
    """
    sugestoes = []
    
    hb_status = hemograma_classificado.get('hemoglobina', {}).get('status', 'Normal')
    plt_status = hemograma_classificado.get('plaquetas', {}).get('status', 'Normal')
    leuco_status = hemograma_classificado.get('leucocitos', {}).get('status', 'Normal')
    eosino_valor = hemograma_classificado.get('eosinofilos', {}).get('valor', 0)
    ht_status = hemograma_classificado.get('hematocrito', {}).get('status', 'Normal')
    
    # padrao de malaria: anemia + plaquetopenia
    if hb_status == 'BAIXO' and plt_status == 'BAIXO':
        sugestoes.append({
            'diagnostico': 'Malária',
            'probabilidade': 'Alta',
            'conduta': 'Pedir Gota Espessa ou TDR',
            'urgencia': 'Avaliar sinais de gravidade'
        })
    
    # padrao de dengue: hematocrito alto + plaquetopenia
    if ht_status == 'ALTO' and plt_status == 'BAIXO':
        sugestoes.append({
            'diagnostico': 'Dengue',
            'probabilidade': 'Alta',
            'conduta': 'Hidratação rigorosa + Hemograma seriado',
            'urgencia': 'Monitorar sinais de alarme'
        })
    
    # eosinofilia: parasitoses
    if eosino_valor > 5:
        sugestoes.append({
            'diagnostico': 'Parasitose Intestinal',
            'probabilidade': 'Moderada',
            'conduta': 'Exame parasitológico de fezes',
            'urgencia': 'Rotina'
        })
    
    # anemia isolada
    if hb_status == 'BAIXO' and plt_status == 'Normal' and leuco_status == 'Normal':
        vcm_status = hemograma_classificado.get('vcm', {}).get('status', 'Normal')
        if vcm_status == 'BAIXO':
            sugestoes.append({
                'diagnostico': 'Anemia Ferropriva ou Talassemia',
                'probabilidade': 'Alta',
                'conduta': 'Dosar ferritina; considerar eletroforese de Hb',
                'urgencia': 'Rotina'
            })
    
    # ajustar probabilidades para contexto
    if contexto:
        municipio = contexto.get('municipio')
        mes = contexto.get('mes')
        
        if municipio and municipio in MUNICIPIOS:
            risco_malaria = MUNICIPIOS[municipio]['risco_malaria']
            for s in sugestoes:
                if s['diagnostico'] == 'Malária' and risco_malaria > 0.5:
                    s['observacao'] = f"Município de alto risco ({municipio})"
        
        if mes and mes in SAZONALIDADE_LUANDA:
            riscos_mes = SAZONALIDADE_LUANDA[mes]['riscos_principais']
            for s in sugestoes:
                if s['diagnostico'] in riscos_mes:
                    s['observacao_sazonal'] = f"Doença comum em {mes}"
    
    return sugestoes


def avaliar_gravidade(hemoglobina, plaquetas, consciencia='normal', sinais_choque=False):
    """
    avalia o score de gravidade do paciente
    retorna o nivel e a acao recomendada
    """
    if hemoglobina < 5 or plaquetas < 20000 or consciencia != 'normal' or sinais_choque:
        return SCORES_GRAVIDADE['Crítico']
    elif hemoglobina < 7 or plaquetas < 50000:
        return SCORES_GRAVIDADE['Grave']
    elif hemoglobina < 10 or plaquetas < 100000:
        return SCORES_GRAVIDADE['Moderado']
    else:
        return SCORES_GRAVIDADE['Leve']


def gerar_alerta_farmacogenetico(medicamento):
    """
    verifica se ha alertas farmacogeneticos para um medicamento
    especificos para a populacao angolana
    """
    alertas = []
    
    for categoria, info in ALERTAS_FARMACOGENETICOS.items():
        if 'exemplos' in info:
            if medicamento.lower() in info['exemplos'].lower():
                alertas.append({
                    'categoria': categoria,
                    'alerta': info['alerta'],
                    'risco': info['risco'],
                    'alternativa': info.get('alternativa') or info.get('conduta')
                })
        elif medicamento.lower() in categoria.lower():
            alertas.append({
                'categoria': categoria,
                'alerta': info['alerta'],
                'risco': info['risco'],
                'conduta': info.get('conduta', 'Monitorar')
            })
    
    return alertas



#MENSAGENS E AVISOS DO SISTEMA


AVISOS_SISTEMA = {
    'disclaimer': """
    ═══════════════════════════════════════════════════════════════════════════
    AVISO IMPORTANTE: Este sistema é uma ferramenta de APOIO À DECISÃO CLÍNICA.
    NÃO substitui o julgamento médico nem a avaliação presencial do paciente.
    Todas as decisões diagnósticas e terapêuticas são de responsabilidade do
    profissional de saúde assistente.
    ═══════════════════════════════════════════════════════════════════════════
    """,
    'escassez': """
    [NOTA] Se o hemograma não estiver disponível, utilize a avaliação clínica:
    - Palidez palmar/conjuntival para estimar anemia
    - Sinais de desidratação (prega cutânea, olhos encovados)
    - Contagem respiratória e frequência cardíaca
    """,
    'versao': 'angogen-dx-pro v1.0.0 | Luanda, Angola'
}



# TESTE DO MODULO


if __name__ == "__main__":
    print("=" * 70)
    print("ANGOGEN-DX-PRO: Sistema de Inteligência a Decisao Clinica")
    print("Versao: 1.0.0 | Angola 2026")
    print("=" * 70)
    print()
    print(f"Provincias carregadas: {len(PROVINCIAS)}")
    print(f"Municipios mapeados: {len(MUNICIPIOS)}")
    print(f"Doencas catalogadas: {len(DOENCAS)}")
    print(f"Medicamentos registados: {len(MEDICAMENTOS)}")
    print()
    print("Modulo carregado com sucesso Mestre!")
    print("=" * 70)
