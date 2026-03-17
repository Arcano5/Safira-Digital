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

# === FUNÇÃO DE FALLBACK PARA MATCH (APENAS NUMÉRICO) ===
def calcular_match_fallback(vaga, curriculo):
    """Fallback apenas numérico quando o Gemini não retorna o match"""
    vaga_lower = vaga.lower()
    curriculo_lower = curriculo.lower()
    
    # Palavras-chave comuns em vagas com pesos
    keywords_peso = {
        'conciliação': 3, 'conferência': 2, 'controle': 2,
        'fluxo de caixa': 3, 'caixa': 2, 'financeiro': 2,
        'excel': 2, 'planilhas': 2, 'planilha': 2,
        'estoque': 2, 'atendimento': 2, 'cliente': 1,
        'analítica': 2, 'análise': 1, 'prazos': 2, 'prazo': 1,
        'organizado': 1, 'organizada': 1, 'resiliente': 1,
        'processos': 1, 'sistema': 1, 'gestão': 1, 'operações': 1
    }
    
    total_pontos = 0
    pontos_obtidos = 0
    
    for keyword, peso in keywords_peso.items():
        total_pontos += peso
        if keyword in curriculo_lower:
            pontos_obtidos += peso
    
    # Também verifica termos da vaga que aparecem no currículo
    palavras_vaga = set(re.findall(r'\b[a-z]{4,}\b', vaga_lower))
    palavras_curriculo = set(re.findall(r'\b[a-z]{4,}\b', curriculo_lower))
    
    if palavras_vaga:
        # Adiciona pontos por palavras em comum (mas com peso menor)
        palavras_comuns = palavras_vaga.intersection(palavras_curriculo)
        pontos_obtidos += len(palavras_comuns) * 0.5
        total_pontos += len(palavras_vaga) * 0.5
    
    if total_pontos > 0:
        percentual = int((pontos_obtidos / total_pontos) * 100)
        return max(0, min(100, percentual))
    return 30  # fallback seguro

# === ANÁLISE DE FORMATAÇÃO ATS (REFINADA) ===
def analisar_formatacao_ats(texto_curriculo):
    problemas = []
    acertos = []
    
    # Lista de títulos de seção comuns para ignorar na detecção de CAPSLOCK
    secoes_comuns = [
        'OBJETIVO', 'PROFISSIONAL', 'RESUMO', 'FORMAÇÃO', 'EXPERIÊNCIA', 
        'HABILIDADES', 'IDIOMAS', 'COMPETÊNCIAS', 'CURSOS', 'CERTIFICAÇÕES',
        'PROJETOS', 'PUBLICAÇÕES', 'PRÊMIOS', 'VOLUNTÁRIO', 'CONTATO',
        'EDUCAÇÃO', 'FORMAÇÃO ACADÊMICA', 'HISTÓRICO PROFISSIONAL',
        'QUALIFICAÇÕES', 'PERFIL', 'SOBRE', 'DADOS PESSOAIS'
    ]
    
    # 1. DETECTAR CAPSLOCK (ignorar títulos de seção)
    linhas = texto_curriculo.split('\n')
    caps_problematicos = []
    
    for linha in linhas:
        palavras = linha.split()
        for palavra in palavras:
            # Ignorar palavras curtas, números ou títulos conhecidos
            if len(palavra) <= 3:
                continue
            if palavra in secoes_comuns:
                continue
            if palavra.isupper() and len(palavra) > 3:
                caps_problematicos.append(palavra)
    
    if caps_problematicos:
        # Limitar a 3 exemplos
        exemplos = caps_problematicos[:3]
        problemas.append(f"❌ Evite usar CAPSLOCK em palavras do corpo do texto: {', '.join(exemplos)}")
    
    # 2. DETECTAR COLUNAS/TABELAS
    colunas_detectadas = 0
    for linha in linhas[:20]:
        if '\t' in linha or '  ' in linha:
            partes = re.split(r'\s{2,}|\t', linha)
            if len(partes) >= 2 and all(len(p.strip()) > 0 for p in partes):
                colunas_detectadas += 1
                if colunas_detectadas >= 2:
                    problemas.append("❌ Formatação em colunas/tabela - ATS pode não ler corretamente")
                    break
    
    # 3. DETECTAR ESTRUTURA FORA DE ORDEM (mais flexível)
    secoes_esperadas = ['resumo|objetivo', 'experiência', 'formação', 'habilidades']
    posicoes = {}
    for i, linha in enumerate(linhas[:30]):
        linha_lower = linha.lower()
        for secao in secoes_esperadas:
            if re.search(secao, linha_lower) and secao not in posicoes:
                posicoes[secao] = i
    
    # Apenas alertar se a diferença for muito grande (ex: formação muito antes da experiência)
    if posicoes.get('experiência', 999) < posicoes.get('formação', 0):
        problemas.append("⚠️ Formação acadêmica aparece antes da experiência profissional - não é um erro, mas o inverso é mais comum")
    
    # 4. DETECTAR DATAS COMPLETAS
    datas_completas = re.findall(r'\d{2}/\d{2}/\d{4}', texto_curriculo)
    if datas_completas:
        problemas.append("❌ Use apenas anos (ex: 2023) em vez de datas completas")
    else:
        acertos.append("✅ Datas em formato ano (recomendado)")
    
    # 5. DETECTAR OBJETIVO GENÉRICO
    if re.search(r'objetivo.*aprender.*crescer.*oportunidade', texto_curriculo, re.IGNORECASE):
        problemas.append("⚠️ Objetivo genérico detectado - personalize para a vaga")
    
    # 6. DETECTAR CARACTERES ESPECIAIS
    caracteres_problematicos = ['•', '►', '→', '▪', '‣', '♦', '★', '☆', '✓']
    for char in caracteres_problematicos:
        if char in texto_curriculo:
            problemas.append(f"⚠️ Uso de caractere especial '{char}' - use hífen (-) simples")
            break
    
    # Calcular score (mais rigoroso)
    score = 100
    score -= len(problemas) * 12
    score = max(0, min(100, score))
    
    # Se não houver problemas, dar 100% com elogio
    if not problemas and score == 100:
        acertos.append("✅ Excelente! Formatação compatível com ATS")
    
    return {
        "score_formatacao": score,
        "problemas": problemas[:7],
        "acertos": acertos[:3],
        "dica_rapida": "Use formatação simples, sem colunas/tabelas, com seções bem definidas."
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
Lista separada por vírgula com as hard skills do candidato que são relevantes para a vaga

<<<SOFT_SKILLS>>>
Lista separada por vírgula com as soft skills do candidato que são relevantes para a vaga

<<<FALTANTES>>>
Lista separada por vírgula com as habilidades (técnicas ou comportamentais) que a vaga pede mas o currículo NÃO possui. Se todas estiverem presentes, escreva "Nenhuma".

<<<EXCEDENTES>>>
Lista separada por vírgula com informações do currículo que NÃO são relevantes para a vaga e poderiam ser removidas para tornar o currículo mais focado. Se nada for excedente, escreva "Nenhuma".

<<<MATCH>>>
Apenas um número inteiro de 0 a 100

<<<CARGO>>>
Cargo mais compatível

NÃO escreva nada fora desses blocos.

VAGA:
{vaga[:4000]}

CURRÍCULO:
{curriculo[:4000]}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

    headers = {'Content-Type': 'application/json'}

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024,
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

                # Extração robusta do número
                numeros = re.findall(r'\d+', match_bloco)
                if numeros:
                    match_num = int(numeros[0])
                    match_num = max(0, min(100, match_num))
                else:
                    # Usando a função de fallback apenas para o número
                    match_num = calcular_match_fallback(vaga, curriculo)

                status.update(label="✅ Análise concluída!", state="complete")

                return {
                    "hard_skills": hard or "Não identificado",
                    "soft_skills": soft or "Não identificado",
                    "habilidades_faltantes": faltantes or "Não identificado",
                    "excedentes": excedentes or "Nenhuma",
                    "percentual_match": match_num,
                    "cargo_alvo": cargo or "Profissional da área"
                }

        except Exception as e:
            st.warning(f"⚠️ Erro: {str(e)[:100]}")
            if tentativa == max_retries - 1:
                return {
                    "hard_skills": "Erro na comunicação",
                    "soft_skills": "Erro na comunicação",
                    "habilidades_faltantes": "Não foi possível identificar",
                    "excedentes": "Não foi possível identificar",
                    "percentual_match": calcular_match_fallback(vaga, curriculo),
                    "cargo_alvo": "Erro"
                }

    return {
        "hard_skills": "Erro",
        "soft_skills": "Erro",
        "habilidades_faltantes": "Erro",
        "excedentes": "Erro",
        "percentual_match": calcular_match_fallback(vaga, curriculo),
        "cargo_alvo": "Erro"
    }