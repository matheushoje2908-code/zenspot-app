from flask import Flask, render_template_string, request, jsonify

# INICIALIZAÇÃO CORRETA (Corrige o NameError)
app = Flask(__name__)

# Banco de dados temporário e controle da IA
mensagens_chat = []
ia_ativa = True 

def resposta_ia(mensagem):
    if not ia_ativa:
        return None  # IA não responde se o Admin assumiu
    
    msg = mensagem.lower()
    if any(word in msg for word in ["oi", "olá", "bom dia"]):
        return "Olá! Sou a IA da ZenSpot. Como posso ajudar com sua saúde hoje?"
    return "Recebi sua mensagem. Um atendente humano foi notificado."

STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { height: 100%; width: 100%; background-color: #050505; font-family: 'Rajdhani', sans-serif; color: #fff; overflow-x: hidden; }
    
    .app-container {
        width: 100%; max-width: 500px; min-height: 100vh; margin: 0 auto;
        background: linear-gradient(180deg, #000 0%, #0d1b2a 60%, #1b263b 100%);
        display: flex; flex-direction: column; padding: 20px; position: relative;
    }

    .logo-text { font-family: 'Orbitron', sans-serif; color: #CCFF00; font-size: 30px; text-shadow: 0 0 10px #CCFF00; text-align: center; margin-top: 30px; }
    .input-field { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid #333; border-radius: 12px; padding: 15px; color: #fff; margin-bottom: 15px; font-size: 16px; outline: none; }
    .btn-login { background: #CCFF00; color: #000; padding: 15px; border-radius: 12px; width: 100%; font-weight: bold; text-transform: uppercase; border:none; cursor:pointer; font-size: 16px; text-align:center; display:block; text-decoration:none; }

    .asymmetric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .grid-item { border: 1px solid rgba(204, 255, 0, 0.4); border-radius: 15px; padding: 15px; text-decoration: none; color: #CCFF00; font-weight: bold; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 13px; }
    .item-large { grid-column: span 2; height: 80px; font-size: 18px; }
    .item-tall { grid-row: span 2; height: 170px; flex-direction: column; }
    .item-normal { height: 80px; }

    .chat-icon { 
        position: fixed; right: 0; top: 60%; transform: translateY(-50%);
        width: 50px; height: 60px; background: #CCFF00; border-radius: 20px 0 0 20px; 
        display: flex; align-items: center; justify-content: center; cursor: pointer; 
        font-size: 24px; z-index: 99; color: #000; box-shadow: -2px 0 10px #CCFF0066;
    }

    #chat-window { 
        position: fixed; bottom: 10px; right: 10px; left: 10px; height: 70vh; 
        background: #0a0a0a; border: 2px solid #CCFF00; border-radius: 25px; 
        display: none; flex-direction: column; z-index: 100;
    }

    .chat-header { background: #CCFF00; color: #000; padding: 15px; font-weight: bold; display: flex; justify-content: space-between; border-radius: 22px 22px 0 0; }
    .chat-messages { flex-grow: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
    .msg { padding: 10px; border-radius: 12px; max-width: 85%; background: #1a1a1a; border-left: 3px solid #CCFF00; font-size: 14px; }
    .msg-admin { border-left-color: #fff; background: #222; align-self: flex-start; }
    .chat-input-area { display: flex; padding: 15px; gap: 8px; border-top: 1px solid #333; }
    .chat-input-area input { flex-grow: 1; background: #111; border: 1px solid #CCFF00; color: #fff; padding: 12px; border-radius: 10px; outline: none; }
</style>
"""

@app.route('/')
def login_page():
    return render_template_string(f"""
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">{STYLE}</head>
    <body>
        <div class="app-container">
            <h1 class="logo-text">ZenSpot</h1>
            <p style="text-align:center; letter-spacing:5px; color:#888; margin-bottom:30px;">BEM-VINDO</p>
            <input type="text" id="user_input" class="input-field" placeholder="USUÁRIO">
            <input type="password" id="pass_input" class="input-field" placeholder="SENHA">
            <button onclick="fazerLogin()" class="btn-login">ENTRAR</button>
        </div>
        <script>
            function fazerLogin() {{
                const u = document.getElementById('user_input').value;
                const p = document.getElementById('pass_input').value;
                if(u === '.\\\\administrador' && p === 'simsim2') window.location.href = '/admin';
                else window.location.href = '/menu?nome=' + u;
            }}
        </script>
    </body></html>
    """)

@app.route('/menu')
def menu_page():
    nome = request.args.get('nome', 'Cliente')
    return render_template_string(f"""
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0">{STYLE}</head>
    <body>
        <div class="app-container">
            <h2 style="color:#CCFF00; font-family:'Orbitron'; font-size: 18px; margin-top:10px;">SERVIÇOS</h2>
            <div class="asymmetric-grid">
                <a href="/info/psiquiatras" class="grid-item item-large">PSIQUIATRAS</a>
                <a href="/info/psicologos" class="grid-item item-tall">PSICÓLOGOS</a>
                <a href="/info/receitas" class="grid-item item-normal">RECEITAS</a>
                <a href="/info/farmacias" class="grid-item item-normal">FARMÁCIAS</a>
                <a href="/info/medicos" class="grid-item item-large">MÉDICOS</a>
                <a href="/info/suporte" class="grid-item item-large" style="background:#CCFF00; color:#000; border:none;">SUPORTE 24H</a>
            </div>
            <a href="/" style="color:#666; text-decoration:none; margin-top:auto; text-align:center; padding: 20px 0;">← SAIR</a>
            <div id="chat-window">
                <div class="chat-header"><span>Suporte ZenSpot</span><span style="cursor:pointer" onclick="toggleChat()">✕</span></div>
                <div id="chat-box" class="chat-messages"></div>
                <div class="chat-input-area"><input type="text" id="chat-in"><button onclick="enviar()" style="background:#CCFF00; border:none; padding:10px; border-radius:10px;">↑</button></div>
            </div>
            <div class="chat-icon" onclick="toggleChat()">💬</div>
        </div>
        <script>
            function toggleChat() {{ document.getElementById('chat-window').style.display = document.getElementById('chat-window').style.display === 'flex' ? 'none' : 'flex'; }}
            async function enviar() {{
                const i = document.getElementById('chat-in'); if(!i.value) return;
                await fetch('/send_msg', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{user: '{nome}', msg: i.value, is_admin: false}}) }});
                i.value = ''; atualizar();
            }}
            async function atualizar() {{
                const res = await fetch('/get_messages'); const msgs = await res.json();
                document.getElementById('chat-box').innerHTML = msgs.map(m => `<div class="msg ${{m.is_admin ? 'msg-admin' : ''}}"><b>${{m.user}}:</b> ${{m.msg}}</div>`).join('');
                const b = document.getElementById('chat-box'); b.scrollTop = b.scrollHeight;
            }}
            setInterval(atualizar, 2000);
        </script>
    </body></html>
    """)

@app.route('/admin')
def admin_page():
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">{STYLE}</head>
    <body>
        <div class="app-container">
            <h2 style="color:#CCFF00; font-family:'Orbitron'; font-size: 18px;">PAINEL ADMIN</h2>
            <div id="chat-box" class="chat-messages" style="flex-grow:1; border: 1px solid #333; margin: 10px 0; border-radius:15px;"></div>
            <div class="chat-input-area"><input type="text" id="chat-in"><button onclick="enviarAdmin()" style="background:#CCFF00; border:none; padding:10px; border-radius:10px;">↑</button></div>
            <a href="/" style="color:#666; text-decoration:none; text-align:center; padding-bottom:10px;">← LOGOUT</a>
        </div>
        <script>
            async function enviarAdmin() {{
                const i = document.getElementById('chat-in'); if(!i.value) return;
                await fetch('/send_msg', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{user: 'Admin', msg: i.value, is_admin: true}}) }});
                i.value = ''; atualizar();
            }}
            async function atualizar() {{
                const res = await fetch('/get_messages'); const msgs = await res.json();
                document.getElementById('chat-box').innerHTML = msgs.map(m => `<div class="msg ${{m.is_admin ? 'msg-admin' : ''}}"><b>${{m.user}}:</b> ${{m.msg}}</div>`).join('');
                const b = document.getElementById('chat-box'); b.scrollTop = b.scrollHeight;
            }}
            setInterval(atualizar, 2000);
        </script>
    </body></html>
    """)

@app.route('/send_msg', methods=['POST'])
def send_msg():
    global ia_ativa
    data = request.json
    is_admin = data.get('is_admin', False)
    
    # Se o admin mandou mensagem, desativa a IA para sempre nesta sessão
    if is_admin:
        ia_ativa = False
    
    mensagens_chat.append({"user": data['user'], "msg": data['msg'], "is_admin": is_admin})
    
    # Resposta da IA apenas se ela estiver ativa e se não foi o admin quem escreveu
    if ia_ativa and not is_admin:
        resp = resposta_ia(data['msg'])
        if resp:
            mensagens_chat.append({"user": "ZenBot", "msg": resp, "is_admin": True})
            
    return jsonify(success=True)

@app.route('/get_messages')
def get_messages(): return jsonify(mensagens_chat)

@app.route('/info/<tipo>')
def info_page(tipo):
    conteudo = {
        "psiquiatras": ["PSIQUIATRAS", "Associação Brasileira de Psiquiatria (ABP).", "https://www.abp.org.br/"],
        "psicologos": ["PSICÓLOGOS", "Conselho Federal de Psicologia (CFP).", "https://site.cfp.org.br/"],
        "receitas": ["RECEITAS", "Validação de Receitas Digitais (ITI).", "https://assinaturadigital.iti.br/"],
        "farmacias": ["FARMÁCIAS", "Localizador de proximidade Google Maps.", "https://www.google.com/maps/search/farmacias+perto+de+mim"],
        "medicos": ["MÉDICOS", "Conselho Federal de Medicina (CFM).", "https://portal.cfm.org.br/"],
        "suporte": ["SUPORTE 24H", "Centro de Valorização da Vida (CVV).", "https://www.cvv.org.br/"]
    }
    item = conteudo.get(tipo, ["ERRO", "Página não encontrada", "#"])
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">{STYLE}</head>
    <body><div class="app-container">
        <h2 style="color:#CCFF00; font-family:'Orbitron';">{item[0]}</h2>
        <div style="background: rgba(255,255,255,0.07); padding: 25px; border-radius: 20px; margin: 20px 0; border: 1px solid #CCFF0022;">
            <p style="font-size: 18px;">{item[1]}</p>
        </div>
        <a href="{item[2]}" target="_blank" class="btn-login">ACESSAR OFICIAL</a>
        <a href="/menu" class="btn-login" style="background:none; border:1px solid #CCFF00; color:#CCFF00; margin-top:auto;">VOLTAR</a>
    </div></body></html>
    """)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)