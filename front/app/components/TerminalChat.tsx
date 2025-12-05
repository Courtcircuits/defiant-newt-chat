'use client';

import { useState, useEffect, useRef } from 'react';

interface Message {
  text: string;
  sender: 'system' | 'local' | 'remote';
  timestamp: Date;
}

export default function TerminalChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [serverUrl, setServerUrl] = useState('');
  const [showUrlInput, setShowUrlInput] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (connected) {
      inputRef.current?.focus();
    }
  }, [connected]);

  const addMessage = (text: string, sender: 'system' | 'local' | 'remote') => {
    setMessages(prev => [...prev, { text, sender, timestamp: new Date() }]);
  };

  const connectToServer = () => {
    if (!serverUrl) {
      addMessage('ERROR: Please enter a WebSocket URL', 'system');
      return;
    }

    try {
      const websocket = new WebSocket(serverUrl);

      websocket.onopen = () => {
        setConnected(true);
        setShowUrlInput(false);
        addMessage('MONITOR READY.', 'system');
        addMessage('CONNECTION ESTABLISHED', 'system');
        addMessage('> ', 'system');
      };

      websocket.onmessage = (event) => {
        addMessage(event.data, 'remote');
      };

      websocket.onerror = () => {
        addMessage('ERROR: CONNECTION FAILED', 'system');
      };

      websocket.onclose = () => {
        setConnected(false);
        addMessage('CONNECTION CLOSED', 'system');
        addMessage('> ', 'system');
      };

      setWs(websocket);
    } catch (error) {
      addMessage('ERROR: Invalid WebSocket URL', 'system');
    }
  };

  const sendMessage = () => {
    if (!input.trim()) return;

    if (ws && connected) {
      ws.send(input);
      addMessage(`> ${input}`, 'local');
      setInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (showUrlInput) {
        connectToServer();
      } else {
        sendMessage();
      }
    }
  };

  useEffect(() => {
    addMessage('SPATIAL COMPUTER BY DISTRACTED/DEFIANT TOUGH NEWTS', 'system');
    addMessage('DEBUG ROM V0.3   28 JUN 2018', 'system');
    addMessage('512KB AVAILABLE RAM', 'system');
    addMessage('', 'system');
    addMessage('ENGINE: NEXTv16.0.6', 'system');
    addMessage('128040960 BYTES', 'system');
    addMessage('OFFSETS: F33 K279 D311', 'system');
    addMessage('', 'system');

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  return (
    <div className="crt-container">
      <div className="crt-screen">
        <div className="crt-overlay" />
        <div className="crt-content" style={{
          width: '100vw',
          height: '100vh',
          backgroundColor: '#000',
          color: '#00ff00',
          fontFamily: "'Courier New', Courier, monospace",
          fontSize: '16px',
          lineHeight: '1.4',
          padding: '20px',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{
            flex: 1,
            overflowY: 'auto',
            marginBottom: '10px',
            paddingRight: '10px'
          }}>
            {messages.map((msg, idx) => (
              <div key={idx} style={{
                color: msg.sender === 'system' ? '#00ff00' :
                       msg.sender === 'local' ? '#00ff00' : '#00aa00',
                marginBottom: '2px',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}>
                {msg.text}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            {showUrlInput ? (
              <>
                <span style={{ color: '#00ff00' }}>CONNECT TO:</span>
                <input
                  type="text"
                  value={serverUrl}
                  onChange={(e) => setServerUrl(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="ws://localhost:8001/ws"
                  autoFocus
                  style={{
                    flex: 1,
                    backgroundColor: '#000',
                    color: '#00ff00',
                    border: 'none',
                    outline: 'none',
                    fontFamily: "'Courier New', Courier, monospace",
                    fontSize: '16px',
                    caretColor: '#00ff00'
                  }}
                />
              </>
            ) : connected ? (
              <>
                <span style={{ color: '#00ff00' }}>{'>'}</span>
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  style={{
                    flex: 1,
                    backgroundColor: '#000',
                    color: '#00ff00',
                    border: 'none',
                    outline: 'none',
                    fontFamily: "'Courier New', Courier, monospace",
                    fontSize: '16px',
                    caretColor: '#00ff00'
                  }}
                />
                <div style={{
                  width: '10px',
                  height: '18px',
                  backgroundColor: '#00ff00',
                  animation: 'blink 1s infinite'
                }} />
              </>
            ) : (
              <span style={{ color: '#00ff00' }}>DISCONNECTED - Press Enter to reconnect</span>
            )}
          </div>

          <style jsx>{`
            @keyframes blink {
              0%, 49% { opacity: 1; }
              50%, 100% { opacity: 0; }
            }

            input::placeholder {
              color: #006600;
            }

            ::-webkit-scrollbar {
              width: 8px;
            }

            ::-webkit-scrollbar-track {
              background: #000;
            }

            ::-webkit-scrollbar-thumb {
              background: #00ff00;
            }
          `}</style>
        </div>
      </div>
    </div>
  );
}
