# ia_services.py
import streamlit as st
import re
import time
import requests
from PyPDF2 import PdfReader
from docx import Document
from datetime import datetime, timedelta

# === RATE LIMITER ===
class RateLimiter:
    def __init__(self, max_calls_per_minute=5):
        self.max_calls = max_calls_per_minute
        self.calls = []
    
    def can_call(self):
        agora = datetime.now()
        self.calls = [c for c in self.calls if c > agora - timedelta(minutes=1)]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(agora)
            return True, 0
        else:
            mais_antiga = min(self.calls)
            tempo_espera = 60 - (agora - mais_antiga).seconds
            return False, max(1, tempo_espera)
    
    def get_status(self):
        agora = datetime.now()
        self.calls = [c for c in self.calls if c > agora - timedelta(minutes=1)]
        return len(self.calls), self.max_calls

# === EXTRAÇÃO DE TEXTO ===
def extrair_texto_pdf(arquivo):
    try:
        reader = PdfReader(arquivo)
        texto = []
        for pagina in reader.pages:
            conteudo = pagina.extract_text()
            if conteudo:
                texto.append(conteudo)
        return "\n".join(texto)
    except Exception as e:
        st.error(f"Erro ao ler PDF: {str(e)}")
        return ""

def extrair_texto_docx(arquivo):
    try:
        doc = Document(arquivo)
        return "\n".join([paragrafo.text for paragrafo in doc.paragraphs])
    except Exception as e:
        st.error(f"Erro ao ler DOCX: {str(e)}")
        return ""

def extrair_texto_arquivo(arquivo):
    if arquivo is None:
        return ""
    
    if arquivo.size > 5 * 1024 * 1024:
        st.error("❌ Arquivo muito grande. Máximo 5MB.")
        return ""
    
    extensao = arquivo.name.split('.')[-1].lower()
    
    if extensao == 'pdf':
        return extrair_texto_pdf(arquivo)
    elif extensao in ['docx', 'doc']:
        return extrair_texto_docx(arquivo)
    else:
        st.error("❌ Formato não suportado. Use PDF ou DOCX.")
        return ""

# === ANÁLISE DE FORMATAÇÃO ATS ===
def analisar_formatacao_ats(texto_curriculo):
    problemas = []
    acertos = []
    
    secoes_necessarias = [
        (r'experiência|experiencia|histórico|historico', "Experiência Profissional"),
        (r'formação|formaçao|educação|educacao|acadêmico|academico', "Formação Acadêmica"),
        (r'habilidades|competências|competencias|skills', "Habilidades")
    ]
    
    for padrao, nome_secao in secoes_necessarias:
        if re.search(padrao, texto_curriculo, re.IGNORECASE):
            acertos.append(f"✅ Seção '{nome_secao}' encontrada")
        else:
            problemas.append(f"❌ Seção '{nome_secao}' não identificada")
    
    caracteres_problematicos = ['•', '►', '→', '▪', '‣', '♦']
    for char in caracteres_problematicos:
        if char in texto_curriculo:
            problemas.append(f"⚠️ Uso de caractere especial '{char}' - use hífen (-) simples")
            break
    
    linhas = texto_curriculo.split('\n')
    colunas_detectadas = 0
    for linha in linhas[:20]:
        if linha.count('\t') >= 2 or linha.count('    ') >= 2:
            colunas_detectadas += 1
    
    if colunas_detectadas >= 3:
        problemas.append("❌ Possível formatação em colunas - ATS pode não ler corretamente")
    
    datas_estranhas = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', texto_curriculo)
    if datas_estranhas:
        problemas.append("⚠️ Use apenas anos (ex: 2023) em vez de datas completas")
    else:
        acertos.append("✅ Datas em formato ano (recomendado)")
    
    score = max(0, 100 - (len(problemas) * 15))
    score = min(100, score)
    
    return {
        "score_formatacao": score,
        "problemas": problemas[:5],
        "acertos": acertos[:3],
        "dica_rapida": "Use formatação simples, sem colunas, com seções bem definidas."
    }

# === ANÁLISE COMPARATIVA COM IA ===
def analisar_com_ia(vaga, curriculo, gemini_api_key, rate_limiter, max_retries=2):
    pode_chamar, tempo_espera = rate_limiter.can_call()
    if not pode_chamar:
        st.warning(f"⏳ Limite de chamadas. Aguarde {tempo_espera}s...")
        time.sleep(tempo_espera)

    prompt = f"""
Você é um especialista em análise de currículos para ATS.

Compare VAGA e CURRÍCULO.

Responda OBRIGATORIAMENTE usando exatamente este formato:

<<<HARD_SKILLS>>>
Lista separada por vírgula

<<<SOFT_SKILLS>>>
Lista separada por vírgula

<<<FALTANTES>>>
Lista separada por vírgula ou "Nenhuma"

<<<EXCEDENTES>>>
Lista separada por vírgula ou "Nenhuma"

<<<MATCH>>>
Apenas um número inteiro de 0 a 100

<<<CARGO>>>
Cargo mais compatível

<<<PLANO>>>
Dia 1: ...
Dia 2: ...
Dia 3: ...
Dia 4: ...
Dia 5: ...
Dia 6: ...
Dia 7: ...

NÃO escreva nada fora desses blocos.

VAGA:
{vaga[:4000]}

CURRÍCULO:
{curriculo[:4000]}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"

    headers = {'Content-Type': 'application/json'}

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 2048,
        }
    }

    def extrair_bloco(texto, marcador):
        padrao = rf"{marcador}\s*(.*?)\s*(?=<<<|$)"
        match = re.search(padrao, texto, re.DOTALL)
        return match.group(1).strip() if match else ""

    for tentativa in range(max_retries):
        try:
            with st.status(f"📡 Analisando... (tentativa {tentativa+1}/{max_retries})", expanded=False) as status:

                response = requests.post(url, headers=headers, json=payload, timeout=60)

                if response.status_code != 200:
                    status.update(label=f"❌ Erro {response.status_code}", state="error")
                    continue

                resultado = response.json()
                texto_resposta = resultado['candidates'][0]['content']['parts'][0]['text']

                hard = extrair_bloco(texto_resposta, r'<<<HARD_SKILLS>>>')
                soft = extrair_bloco(texto_resposta, r'<<<SOFT_SKILLS>>>')
                faltantes = extrair_bloco(texto_resposta, r'<<<FALTANTES>>>')
                excedentes = extrair_bloco(texto_resposta, r'<<<EXCEDENTES>>>')
                match_bloco = extrair_bloco(texto_resposta, r'<<<MATCH>>>')
                cargo = extrair_bloco(texto_resposta, r'<<<CARGO>>>')
                plano = extrair_bloco(texto_resposta, r'<<<PLANO>>>')

                # Extração robusta do número
                numeros = re.findall(r'\d+', match_bloco)
                if numeros:
                    match_num = int(numeros[0])
                    match_num = max(0, min(100, match_num))
                else:
                    # fallback inteligente baseado em interseção simples
                    match_num = calcular_match_basico(vaga, curriculo)

                status.update(label="✅ Análise concluída!", state="complete")

                return {
                    "hard_skills": hard or "Não identificado",
                    "soft_skills": soft or "Não identificado",
                    "habilidades_faltantes": faltantes or "Não identificado",
                    "percentual_match": match_num,
                    "cargo_alvo": cargo or "Profissional da área",
                    "plano_7_dias": plano or "Plano não gerado"
                }

        except Exception as e:
            st.warning(f"⚠️ Erro: {str(e)[:100]}")
            if tentativa == max_retries - 1:
                return {
                    "hard_skills": "Erro",
                    "soft_skills": "Erro",
                    "habilidades_faltantes": "Erro na comunicação",
                    "percentual_match": calcular_match_basico(vaga, curriculo),
                    "cargo_alvo": "Erro",
                    "plano_7_dias": "Tente novamente"
                }

    return {
        "hard_skills": "Erro",
        "soft_skills": "Erro",
        "habilidades_faltantes": "Erro",
        "percentual_match": calcular_match_basico(vaga, curriculo),
        "cargo_alvo": "Erro",
        "plano_7_dias": "Tente novamente"
    }

def calcular_match_basico(vaga, curriculo):
    vaga_set = set(re.findall(r'\w+', vaga.lower()))
    curriculo_set = set(re.findall(r'\w+', curriculo.lower()))

    if not vaga_set:
        return 0

    intersecao = vaga_set.intersection(curriculo_set)
    percentual = int((len(intersecao) / len(vaga_set)) * 100)

    return max(0, min(100, percentual))