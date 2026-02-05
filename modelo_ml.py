"""
ANGOGEN-DX-PRO: Modelo de Machine Learning
Treina e avalia o modelo de apoio a decisao clinica
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import os
import warnings
warnings.filterwarnings('ignore')


def carregar_dados():
    """
    carrega o dataset gerado
    """
    arquivo = 'data/dataset_angogen.csv'
    
    if not os.path.exists(arquivo):
        print(f"[ERRO] Ficheiro {arquivo} nao encontrado!")
        print("Executa primeiro: python gerador_dados.py")
        return None
    
    df = pd.read_csv(arquivo)
    print(f"Dataset carregado: {len(df)} registos")
    
    return df


def preparar_features(df):
    """
    prepara as features para o modelo
    converte categoricas em numericas
    """
    df_prep = df.copy()
    
    # criar encoders para variaveis categoricas
    encoders = {}
    
    colunas_categoricas = [
        'faixa_etaria', 'sexo', 'municipio', 'provincia', 
        'mes', 'estacao', 'status_genetico'
    ]
    
    for col in colunas_categoricas:
        le = LabelEncoder()
        df_prep[col + '_cod'] = le.fit_transform(df_prep[col].astype(str))
        encoders[col] = le
    
    # converter booleanos para int
    df_prep['gestante_int'] = df_prep['gestante'].astype(int)
    df_prep['mordedura_int'] = df_prep['mordedura_recente'].astype(int)
    
    # features para o modelo
    feature_cols = [
        # demograficas
        'faixa_etaria_cod', 'sexo_cod', 'gestante_int', 'peso_kg',
        # geograficas
        'municipio_cod', 'provincia_cod',
        # temporais
        'mes_cod', 'estacao_cod',
        # geneticas
        'status_genetico_cod',
        # historia
        'mordedura_int',
        # hemograma
        'hemoglobina', 'hematocrito', 'hemacias', 'vcm', 'hcm', 'chcm', 'rdw',
        'leucocitos', 'neutrofilos', 'linfocitos', 'monocitos', 'eosinofilos',
        'basofilos', 'plaquetas', 'vpm', 'reticulocitos'
    ]
    
    X = df_prep[feature_cols]
    
    # target: diagnostico
    le_target = LabelEncoder()
    y = le_target.fit_transform(df_prep['diagnostico'])
    encoders['diagnostico'] = le_target
    
    return X, y, encoders, feature_cols


def treinar_modelo(X, y, modelo_tipo='random_forest'):
    """
    treina o modelo de classificacao
    """
    # dividir em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nDados de treino: {len(X_train)}")
    print(f"Dados de teste: {len(X_test)}")
    
    # escolher modelo
    if modelo_tipo == 'random_forest':
        modelo = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
    elif modelo_tipo == 'gradient_boosting':
        modelo = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=8,
            learning_rate=0.1,
            random_state=42
        )
    
    print(f"\nTreinando modelo: {modelo_tipo}")
    modelo.fit(X_train, y_train)
    
    # avaliar
    y_pred = modelo.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nAccuracy no teste: {accuracy*100:.2f}%")
    
    # cross validation
    cv_scores = cross_val_score(modelo, X, y, cv=5)
    print(f"Cross-validation (5-fold): {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*2*100:.2f}%)")
    
    return modelo, X_test, y_test, y_pred


def analisar_resultados(modelo, X_test, y_test, y_pred, encoders, feature_cols):
    """
    analisa os resultados do modelo
    """
    le_diag = encoders['diagnostico']
    
    print("\n" + "=" * 60)
    print("RELATORIO DE CLASSIFICACAO")
    print("=" * 60)
    
    # relatorio detalhado
    print("\n--- Por Diagnostico ---")
    print(classification_report(
        y_test, y_pred, 
        target_names=le_diag.classes_,
        zero_division=0
    ))
    
    # features mais importantes
    print("\n--- Features Mais Importantes ---")
    importancias = pd.DataFrame({
        'feature': feature_cols,
        'importancia': modelo.feature_importances_
    }).sort_values('importancia', ascending=False)
    
    print(importancias.head(15).to_string(index=False))
    
    return importancias


def salvar_modelo(modelo, encoders, feature_cols):
    """
    salva o modelo treinado e os encoders
    """
    os.makedirs('models', exist_ok=True)
    
    # salvar modelo
    with open('models/modelo_angogen.pkl', 'wb') as f:
        pickle.dump(modelo, f)
    
    # salvar encoders
    with open('models/encoders.pkl', 'wb') as f:
        pickle.dump(encoders, f)
    
    # salvar lista de features
    with open('models/features.pkl', 'wb') as f:
        pickle.dump(feature_cols, f)
    
    print("\nModelo salvo em: models/modelo_angogen.pkl")
    print("Encoders salvos em: models/encoders.pkl")
    print("Features salvas em: models/features.pkl")


def carregar_modelo():
    """
    carrega o modelo treinado
    """
    with open('models/modelo_angogen.pkl', 'rb') as f:
        modelo = pickle.load(f)
    
    with open('models/encoders.pkl', 'rb') as f:
        encoders = pickle.load(f)
    
    with open('models/features.pkl', 'rb') as f:
        feature_cols = pickle.load(f)
    
    return modelo, encoders, feature_cols


def prever_diagnostico(modelo, encoders, feature_cols, dados_paciente):
    """
    faz uma predicao para um paciente especifico
    retorna os 3 diagnosticos mais provaveis com probabilidades
    """
    # preparar dados
    df_temp = pd.DataFrame([dados_paciente])
    
    # codificar categoricas
    for col in ['faixa_etaria', 'sexo', 'municipio', 'provincia', 'mes', 'estacao', 'status_genetico']:
        if col in dados_paciente:
            le = encoders[col]
            valor = dados_paciente[col]
            if valor in le.classes_:
                df_temp[col + '_cod'] = le.transform([valor])[0]
            else:
                df_temp[col + '_cod'] = 0
    
    # booleanos
    df_temp['gestante_int'] = int(dados_paciente.get('gestante', False))
    df_temp['mordedura_int'] = int(dados_paciente.get('mordedura_recente', False))
    
    # selecionar features
    X_pred = df_temp[feature_cols]
    
    # prever probabilidades
    probas = modelo.predict_proba(X_pred)[0]
    
    # mapear para diagnosticos
    le_diag = encoders['diagnostico']
    resultados = []
    
    for idx, prob in enumerate(probas):
        diagnostico = le_diag.inverse_transform([idx])[0]
        resultados.append((diagnostico, prob * 100))
    
    # ordenar por probabilidade
    resultados.sort(key=lambda x: x[1], reverse=True)
    
    return resultados[:5]


def main():
    """
    funcao principal
    """
    print("=" * 60)
    print("ANGOGEN-DX-PRO: Treinamento do Modelo")
    print("=" * 60)
    
    # carregar dados
    df = carregar_dados()
    if df is None:
        return
    
    # preparar features
    print("\nPreparando features...")
    X, y, encoders, feature_cols = preparar_features(df)
    print(f"Features: {len(feature_cols)}")
    print(f"Classes (diagnosticos): {len(encoders['diagnostico'].classes_)}")
    
    # treinar modelo
    modelo, X_test, y_test, y_pred = treinar_modelo(X, y, 'random_forest')
    
    # analisar
    importancias = analisar_resultados(modelo, X_test, y_test, y_pred, encoders, feature_cols)
    
    # salvar
    salvar_modelo(modelo, encoders, feature_cols)
    
    # teste rapido
    print("\n" + "=" * 60)
    print("TESTE RAPIDO: Paciente Exemplo")
    print("=" * 60)
    
    paciente_teste = {
        'faixa_etaria': 'Criança (1-5 anos)',
        'sexo': 'Masculino',
        'gestante': False,
        'peso_kg': 15,
        'municipio': 'Cacuaco',
        'provincia': 'Luanda',
        'mes': 'Março',
        'estacao': 'Chuvosa (Pico)',
        'status_genetico': 'Normal',
        'mordedura_recente': False,
        'hemoglobina': 8.5,
        'hematocrito': 28,
        'hemacias': 4.0,
        'vcm': 82,
        'hcm': 28,
        'chcm': 34,
        'rdw': 13,
        'leucocitos': 5500,
        'neutrofilos': 55,
        'linfocitos': 35,
        'monocitos': 5,
        'eosinofilos': 3,
        'basofilos': 0.5,
        'plaquetas': 65000,
        'vpm': 9,
        'reticulocitos': 1.5
    }
    
    print("\nDados do paciente:")
    print(f"  - Crianca de 5 anos em Cacuaco")
    print(f"  - Mes: Marco (pico de malaria)")
    print(f"  - Hemoglobina: 8.5 g/dL (BAIXA)")
    print(f"  - Plaquetas: 65.000 (BAIXAS)")
    
    resultados = prever_diagnostico(modelo, encoders, feature_cols, paciente_teste)
    
    print("\nDiagnosticos mais provaveis:")
    for i, (diag, prob) in enumerate(resultados, 1):
        print(f"  {i}. {diag}: {prob:.1f}%")
    
    print("\n" + "=" * 60)
    print("Modelo treinado com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    main()
