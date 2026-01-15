from flask import Flask, render_template_string, request, jsonify
import time

app = Flask(__name__)

# Estrutura: { 'ID_UNICO': {'ia_ativa': True, 'mensagens': [], 'nome': 'Exibicao'} }
salas = {}

def gerar_id_unico(nome_input):
    # Se tiver nome, usa o nome. Se não, gera ID baseado no IP e timestamp
    if nome_input and nome_input.strip():
        return nome_input.strip()
    
    ip = request.remote_addr
    # Gera um ID baseado no final do IP + milissegundos atuais para ser único
    ts = str(int(time.time() * 1000))[-4:]
    ip_final = ip.split('.')[-1] if '.' in ip else '0'
    return f"Paciente_{ip_final}_{ts}"

def resposta_ia(mensagem):
    msg = mensagem.lower()
    if any(word in msg for word in ["oi", "olá", "bom dia"]):
        return "Olá! Sou a IA da ZenSpot. Como posso ajudar com sua saúde?"
    return "Entendido. Um especialista foi notificado e entrará no chat em breve."

STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { height: 100%; width: 100%; background-color: #050505; font-family: 'Rajdhani', sans-serif; color: #fff; overflow-x: hidden; }
    .app-container { width: 100%; max-width: 500px; min-height: 100vh; margin: 0 auto; background: linear-gradient(180deg, #000 0%, #0d1b2a 60%, #1b263b 100%); display: flex; flex-direction: column; padding: 20px; position: relative; }
    .logo-text { font-family: 'Orbitron', sans-serif; color: #CCFF00; font-size: 30px; text-shadow: 0 0 10px #CCFF00; text-align: center; margin-top: 30px; }
    .input-field { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid #333; border-radius: 12px; padding: 15px; color: #fff; margin-bottom: 15px; font-size: 16px; outline: none; }
    .btn-login { background: #CCFF00; color: #000; padding: 15px; border-radius: 12px; width: 100%; font-weight: bold; text-transform: uppercase; border:none; cursor:pointer; font-size: 16px; text-align:center; display:block; text-decoration:none; }
    .asymmetric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .grid-item { border: 1px solid rgba(204, 255, 0, 0.4); border-radius: 15px; padding: 15px; text-decoration: none; color: #CCFF00; font-weight: bold; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 13px; background: rgba(204,255,0,0.02); }
    .item-large { grid-column: span 2; height: 80px; font-size: 18px; }
    .item-tall { grid-row: span 2; height: 170px; flex-direction: column; }
    .chat-icon { position: fixed; right: 0; top: 60%; transform: translateY(-50%); width: 50px; height: 60px; background: #CCFF00; border-radius: 20px 0 0 20px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 24px; z-index: 99; color: #000; }
    #chat-window { position: fixed; bottom: 10px; right: 10px; left: 10px; height: 70vh; background: #0a0a0a; border: 2px solid #CCFF00; border-radius: 25px; display: none; flex-direction: column; z-index: 100; }
    .chat-header { background: #CCFF00; color: #000; padding: 15px; font-weight: bold; display: flex; justify-content: space-between; border-radius: 22px 22px 0 0; }
    .chat-messages { flex-grow: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
    .msg { padding: 10px; border-radius: 12px; max-width: 85%; background: #1a1a1a; border-left: 3px solid #CCFF00; font-size: 14px; }
    .msg-admin { border-left-color: #fff; background: #222; align-self: flex-start; }
    .chat-input-area { display: flex; padding: 15px; gap: 8px; border-top: 1px solid #333; }
    .chat-input-area input { flex-grow: 1; background: #111; border: 1px solid #CCFF00; color: #fff; padding: 12px; border-radius: 10px; outline: none; }
    .room-selector { background: #111; border: 2px solid #CCFF00; color: #CCFF00; padding: 12px; border-radius: 10px; margin-bottom: 10px; width: 100%; font-weight: bold; }
</style>
"""

@app.route('/')
def login_page():
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">{STYLE}</head>
    <body><div class="app-container">
        <h1 class="logo-text">ZenSpot</h1>
        <p style="text-align:center; letter-spacing:5px; color:#888; margin-bottom:30px;">BEM-VINDO</p>
        <input type="text" id="user_input" class="input-field" placeholder="NOME">
        <input type="password" id="pass_input" class="input-field" placeholder="SENHA">
        <button onclick="fazerLogin()" class="btn-login">ENTRAR</button>
    </div>
    <script>
        function fazerLogin() {{
            const u = document.getElementById('user_input').value;
            const p = document.getElementById('pass_input').value;
            if(u === '.\\\\administrador' && p === 'simsim2') window.location.href = '/admin';
            else window.location.href = '/menu?nome=' + encodeURIComponent(u);
        }}
    </script></body></html>
    """)

@app.route('/menu')
def menu_page():
    nome_cru = request.args.get('nome', '')
    usuario_id = gerar_id_unico(nome_cru)
    
    if usuario_id not in salas:
        salas[usuario_id] = {'ia_ativa': True, 'mensagens': []}

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">{STYLE}</head>
    <body><div class="app-container">
        <h2 style="color:#CCFF00; font-family:'Orbitron'; font-size: 16px; margin-top:10px;">CONECTADO: {usuario_id}</h2>
        <div class="asymmetric-grid">
            <div class="grid-item item-large">PSIQUIATRAS</div>
            <div class="grid-item item-tall">PSICÓLOGOS</div>
            <div class="grid-item item-normal">RECEITAS</div>
            <a href="/info/farmacias" class="grid-item item-normal" style="text-decoration:none;">FARMÁCIAS</a>
            <div class="grid-item item-large">MÉDICOS</div>
            <div class="grid-item item-large" style="background:#CCFF00; color:#000; border:none;">SUPORTE 24H</div>
        </div>
        <a href="/" style="color:#666; text-decoration:none; margin-top:auto; text-align:center; padding: 20px 0;">← SAIR</a>
        <div id="chat-window">
            <div class="chat-header"><span>Suporte ZenSpot</span><span style="cursor:pointer" onclick="toggleChat()">✕</span></div>
            <div id="chat-box" class="chat-messages"></div>
            <div class="chat-input-area"><input type="text" id="chat-in" placeholder="Digite aqui..."><button onclick="enviar()" style="background:#CCFF00; border:none; padding:10px; border-radius:10px;">↑</button></div>
        </div>
        <div class="chat-icon" onclick="toggleChat()">💬</div>
    </div>
    <script>
        function toggleChat() {{ document.getElementById('chat-window').style.display = document.getElementById('chat-window').style.display === 'flex' ? 'none' : 'flex'; }}
        async function enviar() {{
            const i = document.getElementById('chat-in'); if(!i.value) return;
            const txt = i.value; i.value = '';
            await fetch('/send_msg', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{sala_id: '{usuario_id}', user: '{usuario_id}', msg: txt, is_admin: false}}) }});
            atualizar();
        }}
        async function atualizar() {{
            const res = await fetch('/get_messages?sala_id={usuario_id}'); 
            const data = await res.json();
            document.getElementById('chat-box').innerHTML = data.msgs.map(m => `<div class="msg ${{m.is_admin ? 'msg-admin' : ''}}"><b>${{m.user}}:</b> ${{m.msg}}</div>`).join('');
            const b = document.getElementById('chat-box'); b.scrollTop = b.scrollHeight;
        }}
        setInterval(atualizar, 2000);
    </script></body></html>
    """)

@app.route('/admin')
def admin_page():
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">{STYLE}</head>
    <body><div class="app-container">
        <h2 style="color:#CCFF00; font-family:'Orbitron'; font-size: 18px; margin-bottom:10px;">PAINEL DE CONTROLE</h2>
        <select id="room-select" class="room-selector" onchange="mudarSala()">
            <option value="">AGUARDANDO CONEXÕES...</option>
        </select>
        <div id="chat-box" class="chat-messages" style="flex-grow:1; border: 1px solid #333; border-radius:15px; margin-bottom:10px; background: rgba(0,0,0,0.3);"></div>
        <div class="chat-input-area"><input type="text" id="chat-in" placeholder="/clear para limpar sala"><button onclick="enviarAdmin()" style="background:#CCFF00; border:none; padding:10px; border-radius:10px;">↑</button></div>
        <a href="/" style="color:#666; text-decoration:none; text-align:center; padding: 10px;">← LOGOUT</a>
    </div>
    <script>
        let salaAtual = "";
        async function atualizarListaSalas() {{
            const res = await fetch('/get_salas'); const data = await res.json();
            const sel = document.getElementById('room-select');
            const atual = sel.value;
            sel.innerHTML = '<option value="">SELECIONE UM CHAT ATIVO</option>' + data.map(s => `<option value="${{s}}">${{s}}</option>`).join('');
            if(data.includes(atual)) sel.value = atual;
        }}
        function mudarSala() {{ salaAtual = document.getElementById('room-select').value; document.getElementById('chat-box').innerHTML = ''; atualizar(); }}
        async function enviarAdmin() {{
            if(!salaAtual) return alert("Selecione um paciente!");
            const i = document.getElementById('chat-in'); if(!i.value) return;
            const txt = i.value; i.value = '';
            await fetch('/send_msg', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{sala_id: salaAtual, user: 'ADMIN', msg: txt, is_admin: true}}) }});
            atualizar();
        }}
        async function atualizar() {{
            if(!salaAtual) return;
            const res = await fetch('/get_messages?sala_id=' + salaAtual); const data = await res.json();
            document.getElementById('chat-box').innerHTML = data.msgs.map(m => `<div class="msg ${{m.is_admin ? 'msg-admin' : ''}}"><b>${{m.user}}:</b> ${{m.msg}}</div>`).join('');
            const b = document.getElementById('chat-box'); b.scrollTop = b.scrollHeight;
        }}
        setInterval(atualizarListaSalas, 4000);
        setInterval(atualizar, 2000);
    </script></body></html>
    """)

@app.route('/send_msg', methods=['POST'])
def send_msg():
    data = request.json
    sid = data['sala_id']
    msg_texto = data['msg']
    is_admin = data.get('is_admin', False)

    if sid not in salas: salas[sid] = {'ia_ativa': True, 'mensagens': []}

    if msg_texto.strip() == "/clear" and is_admin:
        salas[sid]['mensagens'] = []
        return jsonify(success=True)

    if is_admin:
        salas[sid]['ia_ativa'] = False

    salas[sid]['mensagens'].append({"user": data['user'], "msg": msg_texto, "is_admin": is_admin})

    if salas[sid]['ia_ativa'] and not is_admin:
        resp = resposta_ia(msg_texto)
        salas[sid]['mensagens'].append({"user": "ZenBot", "msg": resp, "is_admin": True})

    return jsonify(success=True)

@app.route('/get_messages')
def get_messages():
    sid = request.args.get('sala_id')
    return jsonify({"msgs": salas.get(sid, {}).get('mensagens', [])})

@app.route('/get_salas')
def get_salas():
    # Retorna apenas salas que possuem mensagens para não poluir a lista
    return jsonify([s for s in salas if len(salas[s]['mensagens']) > 0])

@app.route('/info/farmacias')
def farmacias():
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">{STYLE}</head>
    <body><div class="app-container">
        <h2 style="color:#CCFF00; font-family:'Orbitron';">FARMÁCIAS</h2>
        <div style="background: rgba(255,255,255,0.07); padding: 25px; border-radius: 20px; margin: 20px 0; border: 1px solid #CCFF0022;">
            <p style="font-size: 18px;">Localizando drogarias próximas com base na sua posição atual.</p>
        </div>
        <a href="https://www.google.com/maps/search/farmacias+perto+de+mim" target="_blank" class="btn-login">ABRIR MAPA</a>
        <a href="/menu" class="btn-login" style="background:none; border:1px solid #CCFF00; color:#CCFF00; margin-top:auto;">VOLTAR</a>
    </div></body></html>
    """)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
