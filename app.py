<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tracker de Recuperação</title>
    <style>
        :root {
            --bg-color: #000000;
            --text-color: #e0e0e0;
            --accent-green: #00ff88;
            --accent-red: #ff4d4d;
            --card-bg: #1a1a1a;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }

        /* --- Tipografia Grande para Visão --- */
        h1 { font-size: 1.5rem; opacity: 0.8; }
        
        .timer-display {
            font-size: 6rem;
            font-weight: bold;
            font-variant-numeric: tabular-nums;
            margin: 20px 0;
            color: var(--accent-green);
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        }

        /* --- Botões Grandes e Acessíveis --- */
        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            width: 100%;
            max-width: 400px;
        }

        button {
            padding: 20px;
            font-size: 1.2rem;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: transform 0.1s;
            font-weight: bold;
        }

        .btn-start { background-color: var(--accent-green); color: #000; }
        .btn-stop { background-color: var(--accent-red); color: #fff; }
        .btn-mode { background-color: #333; color: #fff; grid-column: span 2; }
        
        button:active { transform: scale(0.98); }

        /* --- Formulário de Registro --- */
        .log-section {
            background-color: var(--card-bg);
            padding: 20px;
            border-radius: 15px;
            width: 100%;
            max-width: 400px;
            margin-top: 30px;
            display: none; /* Escondido até parar o timer */
        }

        input, select, textarea {
            width: 100%;
            padding: 15px;
            margin-bottom: 15px;
            background: #333;
            border: 1px solid #444;
            color: white;
            font-size: 1rem;
            border-radius: 8px;
            box-sizing: border-box;
        }

        label { display: block; margin-bottom: 5px; color: #aaa; }

        /* --- Histórico --- */
        .history-section {
            width: 100%;
            max-width: 400px;
            margin-top: 40px;
        }
        .history-item {
            border-bottom: 1px solid #333;
            padding: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .energy-tag {
            background: #333;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>

    <h1>Monitor de Energia</h1>

    <div id="timer" class="timer-display">20:00</div>
    <div id="status-text" style="color: #888; margin-bottom: 10px;">MODO FOCO</div>

    <div class="controls">
        <button id="btn-toggle" class="btn-start" onclick="toggleTimer()">INICIAR</button>
        <button class="btn-mode" onclick="switchMode()">Alternar para Descanso (20min)</button>
    </div>

    <div id="log-section" class="log-section">
        <h3>📝 Registrar Sessão</h3>
        
        <label>Matéria / Atividade</label>
        <input type="text" id="subject" placeholder="Ex: Planejamento Aulas">

        <label>Nível de Energia (1 = Baixo, 5 = Alto)</label>
        <select id="energy">
            <option value="5">5 - Alta (Pico)</option>
            <option value="4">4 - Boa</option>
            <option value="3">3 - Média</option>
            <option value="2">2 - Baixa</option>
            <option value="1">1 - Exausto</option>
        </select>

        <label>Notas (Opcional)</label>
        <textarea id="notes" rows="3"></textarea>

        <button class="btn-start" onclick="saveLog()" style="width:100%">Salvar Registro</button>
    </div>

    <div class="history-section">
        <h3>Histórico Recente <button onclick="downloadCSV()" style="font-size:0.8rem; padding:5px 10px; margin-left:10px; background:#333;">Baixar CSV</button></h3>
        <div id="history-list"></div>
    </div>

    <audio id="alarm-sound" src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg"></audio>

    <script>
        let timeLeft = 20 * 60;
        let isRunning = false;
        let timerId = null;
        let mode = "FOCO"; // ou DESCANSO

        // Elementos
        const display = document.getElementById('timer');
        const btnToggle = document.getElementById('btn-toggle');
        const statusText = document.getElementById('status-text');
        const logSection = document.getElementById('log-section');
        const historyList = document.getElementById('history-list');
        const alarm = document.getElementById('alarm-sound');

        // Carregar dados ao iniciar
        let studyData = JSON.parse(localStorage.getItem('studyTrackerData')) || [];
        renderHistory();

        function updateDisplay() {
            const m = Math.floor(timeLeft / 60);
            const s = timeLeft % 60;
            display.textContent = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        }

        function toggleTimer() {
            if (isRunning) {
                // Parar
                clearInterval(timerId);
                isRunning = false;
                btnToggle.textContent = "RETOMAR";
                btnToggle.className = "btn-start";
                
                // Se for modo foco, mostra o log
                if (mode === "FOCO") {
                    logSection.style.display = "block";
                    window.scrollTo(0, document.body.scrollHeight);
                }
            } else {
                // Iniciar
                logSection.style.display = "none";
                isRunning = true;
                btnToggle.textContent = "PAUSAR";
                btnToggle.className = "btn-stop";
                
                timerId = setInterval(() => {
                    if (timeLeft > 0) {
                        timeLeft--;
                        updateDisplay();
                    } else {
                        finishTimer();
                    }
                }, 1000);
            }
        }

        function finishTimer() {
            clearInterval(timerId);
            isRunning = false;
            btnToggle.textContent = "INICIAR";
            btnToggle.className = "btn-start";
            alarm.play();
            alert("⏰ Tempo Esgotado!");
            if (mode === "FOCO") {
                logSection.style.display = "block";
            }
        }

        function switchMode() {
            clearInterval(timerId);
            isRunning = false;
            btnToggle.textContent = "INICIAR";
            
            if (mode === "FOCO") {
                mode = "DESCANSO";
                timeLeft = 20 * 60; // 20 min descanso
                document.documentElement.style.setProperty('--accent-green', '#00d2ff'); // Azul para descanso
                statusText.textContent = "MODO DESCANSO (Olhe longe das telas)";
            } else {
                mode = "FOCO";
                timeLeft = 20 * 60; // 20 min foco
                document.documentElement.style.setProperty('--accent-green', '#00ff88'); // Verde para foco
                statusText.textContent = "MODO FOCO";
            }
            updateDisplay();
            logSection.style.display = "none";
        }

        function saveLog() {
            const subject = document.getElementById('subject').value;
            const energy = document.getElementById('energy').value;
            const notes = document.getElementById('notes').value;

            const entry = {
                date: new Date().toLocaleString(),
                subject,
                energy,
                notes,
                duration: "20 min" // Simplificado para blocos fixos
            };

            studyData.unshift(entry); // Adiciona no começo
            localStorage.setItem('studyTrackerData', JSON.stringify(studyData));
            
            // Limpa form
            document.getElementById('subject').value = "";
            document.getElementById('notes').value = "";
            logSection.style.display = "none";
            
            renderHistory();
        }

        function renderHistory() {
            historyList.innerHTML = "";
            studyData.slice(0, 5).forEach(item => { // Mostra só os últimos 5
                const div = document.createElement('div');
                div.className = "history-item";
                div.innerHTML = `
                    <div>
                        <div style="font-weight:bold">${item.subject || "Estudo Geral"}</div>
                        <div style="font-size:0.8rem; color:#888">${item.date}</div>
                    </div>
                    <div class="energy-tag">⚡ ${item.energy}/5</div>
                `;
                historyList.appendChild(div);
            });
        }

        function downloadCSV() {
            let csvContent = "data:text/csv;charset=utf-8,Data,Materia,Energia,Notas\n";
            studyData.forEach(row => {
                csvContent += `${row.date},${row.subject},${row.energy},"${row.notes}"\n`;
            });
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "historico_estudos.csv");
            document.body.appendChild(link);
            link.click();
        }
    </script>
</body>
</html>
