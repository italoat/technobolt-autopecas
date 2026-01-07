import streamlit as st
import google.generativeai as genai
import os
import time
import docx
from io import BytesIO
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# --- 1. CONFIGURAÇÃO DE SEGURANÇA E PROTOCOLO (REAL ACESSÓRIOS) ---
st.set_page_config(
    page_title="TechnoBolt IA - Real Acessórios Hub",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. GESTÃO DE ESTADO (INICIALIZAÇÃO BLINDADA) ---
chaves_sessao = {
    'logged_in': False,
    'user_atual': None,
    'perfil_cliente': {
        "nome_empresa": "Real Acessórios",
        "setor": "Varejo de Autopeças e Acessórios",
        "missao": "Prover soluções em autopeças com precisão técnica e agilidade logística.",
        "valores": "Confiança, Conhecimento Técnico, Prontidão, Ética.",
        "tom_voz": "Técnico, Consultivo e Eficiente"
    },
    'uso_sessao': {},
    'mostrar_resultado': False,
    'resultado_ia': "",
    'titulo_resultado': "",
    'login_time': time.time()
}

for chave, valor in chaves_sessao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

# --- 3. SISTEMA DE AUDITORIA E LOGOUT ---
def enviar_notificacao_email(assunto, corpo):
    sg_key = os.environ.get("SENDGRID_API_KEY") 
    message = Mail(
        from_email='technoboltconsultoria@gmail.com',
        to_emails='technoboltconsultoria@gmail.com',
        subject=assunto,
        plain_text_content=corpo)
    try:
        sg = SendGridAPIClient(sg_key)
        sg.send(message)
        return True
    except:
        return False

def protocol_logout():
    if st.session_state.get('logged_in'):
        tempo = round((time.time() - st.session_state.get('login_time', time.time())) / 60, 2)
        relatorio = f"LOGOUT REAL ACESSÓRIOS\nOperador: {st.session_state.user_atual}\nTempo: {tempo} min\nAções: {st.session_state.uso_sessao}"
        enviar_notificacao_email(f"Sessão Encerrada - {st.session_state.user_atual}", relatorio)
    st.session_state.logged_in = False
    st.session_state.user_atual = None
    st.session_state.uso_sessao = {}
    st.rerun()

def registrar_evento(funcao):
    if 'uso_sessao' not in st.session_state: st.session_state.uso_sessao = {}
    st.session_state.uso_sessao[funcao] = st.session_state.uso_sessao.get(funcao, 0) + 1

# --- 4. MOTOR DE INTELIGÊNCIA COM FAILOVER PENTACAMADA ---
MODEL_FAILOVER_LIST = [
    "models/gemini-1.5-pro", 
    "models/gemini-1.5-flash", 
    "models/gemini-1.5-flash-8b", 
    "models/gemini-2.0-flash-exp", 
    "models/gemini-pro"
]

def call_technobolt_ai(prompt, attachments=None, system_context="default"):
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key: genai.configure(api_key=api_key)
    
    p = st.session_state.perfil_cliente
    dna_context = f"DNA EMPRESA: {p['nome_empresa']} | SETOR: {p['setor']} | TOM: {p['tom_voz']}\n\n"

    contexts = {
        "estoque": "Aja como Gestor de Inventário Automotivo Sênior. Foque em Curva ABC, Giro de Estoque e identificação de peças obsoletas.",
        "compras": "Aja como Comprador Estratégico de Autopeças. Analise orçamentos de distribuidores, foque em margem bruta e condições de frete.",
        "tecnico": "Aja como Consultor Técnico Especialista em Catálogos Automotivos (TecDoc/Original). Resolva compatibilidades e aplicações de peças.",
        "vendas": "Aja como Especialista em Vendas de Balcão e Atendimento WhatsApp para oficinas. Crie abordagens rápidas, técnicas e persuasivas.",
        "default": "Você é o Motor TechnoBolt focado na Real Acessórios. Respostas técnicas e estruturadas."
    }

    final_sys_instr = dna_context + contexts.get(system_context, contexts["default"])

    for model_name in MODEL_FAILOVER_LIST:
        try:
            model = genai.GenerativeModel(model_name, system_instruction=final_sys_instr)
            payload = [prompt] + attachments if attachments else prompt
            response = model.generate_content(payload)
            return response.text, model_name
        except:
            continue
    return "⚠️ Motores de IA Offline. Contate o suporte.", "OFFLINE"

# --- 5. DESIGN SYSTEM (ESTÉTICA ELITE HUB) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #f8fafc !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { display: none !important; }
    header, footer { visibility: hidden !important; }
    .main-card {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 24px;
        padding: 45px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04); margin-bottom: 30px;
    }
    .hero-title {
        font-size: 42px; font-weight: 800; text-align: center;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: -2px; margin-bottom: 10px;
    }
    .stButton > button {
        width: 100%; border-radius: 14px; height: 3.8em; font-weight: 700;
        background: #1e40af !important; color: white !important; border: none !important;
        text-transform: uppercase; letter-spacing: 1.5px; transition: 0.4s;
    }
    .stButton > button:hover { background: #1e3a8a !important; transform: translateY(-2px); }
    .status-badge {
        padding: 6px 18px; border-radius: 50px; background: #eff6ff; 
        color: #1e40af; font-size: 12px; font-weight: 700; border: 1px solid #dbeafe;
    }
</style>
""", unsafe_allow_html=True)

# --- 6. TELA DE LOGIN (USUÁRIOS ORIGINAIS) ---
if not st.session_state.logged_in:
    st.markdown("<div style='height: 12vh;'></div>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.4, 1])
    with col_login:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown("<h1 class='hero-title'>REAL ACESSÓRIOS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748b; margin-bottom:40px;'>SISTEMA DE GESTÃO COGNITIVA</p>", unsafe_allow_html=True)
        
        user_id = st.text_input("Operador", placeholder="Usuário")
        user_key = st.text_input("Chave", type="password", placeholder="Senha")

        if st.button("CONECTAR"):
            banco_users = {
                "admin": "admin",
                "anderson.bezerra": "teste@2025", 
                "fabricio.felix": "teste@2025", 
                "jackson.antonio": "teste@2025", 
                "luiza.trovao": "teste@2025"
            }
            if user_id in banco_users and banco_users[user_id] == user_key:
                st.session_state.logged_in = True
                st.session_state.user_atual = user_id
                st.session_state.login_time = time.time()
                enviar_notificacao_email("Login Real Acessórios", f"Operador {user_id} acessou o sistema.")
                st.rerun()
    st.stop()

# --- 7. CABEÇALHO E NAVEGAÇÃO ---
st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
h1, h2 = st.columns([4, 1.2])
with h1: 
    st.markdown(f"**OPERADOR:** <span class='status-badge'>{st.session_state.user_atual.upper()}</span>", unsafe_allow_html=True)
with h2: 
    if st.button("🚪 Sair do Hub"): protocol_logout()

menu = [
    "🏠 Centro de Comando",
    "📦 Auditor de Estoque",
    "💰 Inteligência de Compras",
    "🛠️ Consultoria Técnica",
    "💬 Vendas & WhatsApp",
    "📊 Relatório Master"
]
escolha = st.selectbox("Seletor de Módulo", menu, label_visibility="collapsed")
st.markdown("<hr style='margin: 10px 0 35px 0; border: 0.5px solid #e2e8f0;'>", unsafe_allow_html=True)

# --- 8. MÓDULOS OPERACIONAIS ---

# --- DASHBOARD CENTRAL (RESTAURADO) ---
if "🏠 Centro" in escolha:
    st.markdown('<div class="main-card"><h1>Command Center</h1><p>MONITORIA DE SOBERANIA DIGITAL & INTELIGÊNCIA AUTOMOTIVA</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0; border-radius: 24px; overflow: hidden; background: #ffffff; padding: 20px; border: 1px solid #e2e8f0;">
        <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcXlsaTYwaDZkeGc2MjMxcXk4MWJjMGtwcHEwNTZ6dHFkaXV0NzNxbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/eljCVpMrhepUSgZaVP/giphy.gif" 
             width="450" style="border-radius: 15px;">
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Failover Status", "Active (5/5)", "Redundância On")
    c2.metric("Sessão", st.session_state.user_atual.split('.')[0].upper(), "Protegida")
    c3.metric("DNA Ativo", "Real Acessórios", "Autopeças")

elif "📦 Auditor" in escolha:
    st.markdown('<div class="main-card"><h2>📦 Auditor de Estoque</h2><p>Identificação de peças paradas e prioridades de giro.</p></div>', unsafe_allow_html=True)
    up = st.file_uploader("Upload de Inventário (PDF/DOCX/TXT)", type=['pdf', 'docx', 'txt'])
    if up and st.button("ANALISAR ESTOQUE"):
        registrar_evento("Auditoria Estoque")
        with st.spinner("IA Analisando giro de peças..."):
            res, mod = call_technobolt_ai("Analise este estoque para a Real Acessórios.", system_context="estoque")
            st.session_state.titulo_resultado, st.session_state.resultado_ia, st.session_state.mostrar_resultado = "Diagnóstico de Inventário", res, True
            st.rerun()

elif "💰 Inteligência de Compras" in escolha:
    st.markdown('<div class="main-card"><h2>💰 Inteligência de Compras</h2><p>Comparação de orçamentos entre distribuidores.</p></div>', unsafe_allow_html=True)
    dados = st.text_area("Insira os itens e preços dos fornecedores:")
    if st.button("CALCULAR MELHOR COMPRA"):
        registrar_evento("Analise Compras")
        with st.spinner("Calculando margens..."):
            res, _ = call_technobolt_ai(dados, system_context="compras")
            st.session_state.titulo_resultado, st.session_state.resultado_ia, st.session_state.mostrar_resultado = "Análise Comparativa", res, True
            st.rerun()

elif "🛠️ Consultoria Técnica" in escolha:
    st.markdown('<div class="main-card"><h2>🛠️ Consultoria Técnica</h2><p>Dúvidas de aplicação, conversão e compatibilidade.</p></div>', unsafe_allow_html=True)
    duvida = st.text_input("Peça ou veículo alvo:")
    if st.button("CONSULTAR TÉCNICO IA"):
        registrar_evento("Consulta Técnica")
        res, _ = call_technobolt_ai(duvida, system_context="tecnico")
        st.session_state.titulo_resultado, st.session_state.resultado_ia, st.session_state.mostrar_resultado = "Ficha Técnica IA", res, True
        st.rerun()

elif "💬 Vendas" in escolha:
    st.markdown('<div class="main-card"><h2>💬 Vendas & WhatsApp</h2><p>Scripts rápidos para orçamentos e fechamentos.</p></div>', unsafe_allow_html=True)
    detalhes = st.text_area("O que deseja comunicar ao cliente?")
    if st.button("GERAR SCRIPT PROFISSIONAL"):
        registrar_evento("Script Vendas")
        res, _ = call_technobolt_ai(detalhes, system_context="vendas")
        st.session_state.titulo_resultado, st.session_state.resultado_ia, st.session_state.mostrar_resultado = "Script de Abordagem", res, True
        st.rerun()

elif "📊 Relatório Master" in escolha:
    st.markdown('<div class="main-card"><h2>📊 Relatório Master</h2><p>Consolidado semanal para diretoria.</p></div>', unsafe_allow_html=True)
    fatos = st.text_area("Eventos críticos e métricas da semana:")
    if st.button("CONSOLIDAR RELATÓRIO"):
        registrar_evento("Relatório Master")
        res, _ = call_technobolt_ai(fatos)
        st.session_state.titulo_resultado, st.session_state.resultado_ia, st.session_state.mostrar_resultado = "Dossiê Semanal Real", res, True
        st.rerun()

# --- 9. COMPONENTE DE RESULTADO UX CENTRALIZADO ---
if st.session_state.get('mostrar_resultado'):
    st.markdown("---")
    _, col_central, _ = st.columns([1, 8, 1])
    with col_central:
        st.markdown(f"""
            <div class="main-card" style="border-top: 5px solid #1e40af;">
                <h2 style="color: #1e40af; margin-bottom: 20px;">{st.session_state.titulo_resultado}</h2>
                <div style="background: #fdfdfd; padding: 25px; border-radius: 12px; border: 1px solid #f1f5f9; white-space: pre-wrap; color: #334155; line-height: 1.6;">
                    {st.session_state.resultado_ia}
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("✖️ LIMPAR E FECHAR"):
            st.session_state.mostrar_resultado = False
            st.rerun()

st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
st.caption(f"TechnoBolt Solutions © 2026 | Real Acessórios Hub v1.0 | Operador: {st.session_state.user_atual.upper()}")
