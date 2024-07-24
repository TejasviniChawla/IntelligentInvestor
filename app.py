from flask import Flask, request, jsonify, render_template_string
import llm_for_qa 
import markdown


app = Flask(__name__)

# HTML template for serving the interface
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Finance Chatbot</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-color: #f0fff0;
            --container-bg: #fff;
            --header-bg: #2e8b57;
            --text-color: #333;
            --bot-msg-bg: #e0f2e0;
            --user-msg-bg: #3cb371;
            --input-border: #a8d5a8;
        }
        .dark-mode {
            --bg-color: #1a1a1a;
            --container-bg: #2c2c2c;
            --header-bg: #1e5e3a;
            --text-color: #f0f0f0;
            --bot-msg-bg: #3a3a3a;
            --user-msg-bg: #2e7d32;
            --input-border: #4a4a4a;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: var(--bg-color);
            transition: background-color 0.3s;
        }
        .chat-container {
            width: 90%;
            max-width: 400px;
            height: 80vh;
            max-height: 600px;
            border-radius: 20px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            background-color: var(--container-bg);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        .chat-header {
            background-color: var(--header-bg);
            color: white;
            padding: 20px;
            text-align: center;
            font-weight: bold;
            font-size: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .mode-toggle {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
        }
        .chat-messages {
            flex-grow: 1;
            padding: 20px;
            overflow-y: auto;
            background-color: var(--container-bg);
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 75%;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }
        .bot-message {
            background-color: var(--bot-msg-bg);
            align-self: flex-start;
            border-bottom-left-radius: 5px;
            color: var(--text-color);
        }
        .user-message {
            background-color: var(--user-msg-bg);
            color: white;
            align-self: flex-end;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }
        .chat-input {
            display: flex;
            padding: 15px;
            background-color: var(--container-bg);
            border-top: 1px solid var(--input-border);
        }
        #user-input {
            flex-grow: 1;
            padding: 12px;
            border: 1px solid var(--input-border);
            border-radius: 25px;
            font-size: 16px;
            background-color: var(--container-bg);
            color: var(--text-color);
        }
        #send-button {
            padding: 12px 20px;
            background-color: var(--header-bg);
            color: white;
            border: none;
            border-radius: 25px;
            margin-left: 10px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        #send-button:hover {
            opacity: 0.9;
        }
        .finance-icon {
            font-size: 24px;
            margin-right: 10px;
        }
        @media (max-width: 480px) {
            .chat-container {
                width: 100%;
                height: 100vh;
                max-height: none;
                border-radius: 0;
            }
            .chat-header {
                font-size: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <i class="fas fa-chart-line finance-icon"></i>
            Good Evening, Investor!
            <button class="mode-toggle" onclick="toggleDarkMode()">
                <i class="fas fa-moon"></i>
            </button>
        </div>
        <div class="chat-messages" id="chat-messages"></div>
        <div class="chat-input">
            <input type="text" id="user-input" placeholder="Ask about finances...">
            <button id="send-button"><i class="fas fa-paper-plane"></i></button>
        </div>
    </div>

    <script>

        const chatMessages = document.getElementById('chat-messages');
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');

        function addMessage(message, isUser) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message');
            messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
            messageElement.innerHTML = message;  // Changed to innerHTML
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            const modeIcon = document.querySelector('.mode-toggle i');
            modeIcon.classList.toggle('fa-moon');
            modeIcon.classList.toggle('fa-sun');
        }

        function handleUserInput() {
            const message = userInput.value.trim();
            if (message) {
                addMessage(message, true);
                userInput.value = '';
                fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ question: message })
                })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.answer, false);
                })
                .catch(error => {
                    console.error('Error:', error);
                    addMessage("Error: Could not process the request.", false);
                });
            }
        }

        sendButton.addEventListener('click', handleUserInput);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleUserInput();
            }
        });

        // Initial bot message
        addMessage("Welcome to the Finance Chatbot. How can I help you with your financial queries today?", false);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        answer = llm_for_qa.query_bot(question)
        # Convert Markdown to HTML
        answer_html = markdown.markdown(answer)
        return jsonify({'answer': answer_html})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
