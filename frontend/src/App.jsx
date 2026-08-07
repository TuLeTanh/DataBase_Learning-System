import { useState, useEffect, useRef } from 'react'

const API_BASE_URL = "http://localhost:8000";

function App() {
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Chào bạn, mình là Trợ lý học Cơ sở dữ liệu. Mình có thể giúp gì cho bạn hôm nay?' }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState("checking..."); // checking, ok, error
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Health check on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/health`)
      .then(res => {
        if (res.ok) setServerStatus("ok");
        else setServerStatus("error");
      })
      .catch(() => setServerStatus("error"));
  }, []);

  const handleSend = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    if (serverStatus !== "ok") {
      alert("Không thể kết nối với server backend. Vui lòng đảm bảo server backend đang chạy ở http://localhost:8000");
      return;
    }

    const userMessage = { role: 'user', text: trimmedInput };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmedInput })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Có lỗi từ máy chủ");
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'bot', text: data.answer }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', text: `[Lỗi]: ${error.message}. Vui lòng thử lại sau.` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-600 text-white py-4 px-6 shadow-md flex justify-between items-center z-10">
        <div>
          <h1 className="text-xl font-bold">Trợ lý học Cơ sở dữ liệu</h1>
          <p className="text-sm opacity-80">RAG Chatbot - Học CSDL thông minh</p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span>Backend Status:</span>
          {serverStatus === 'checking...' && <span className="text-yellow-300">Đang kiểm tra...</span>}
          {serverStatus === 'ok' && <span className="text-green-300 font-bold">Kết nối tốt</span>}
          {serverStatus === 'error' && <span className="text-red-300 font-bold">Mất kết nối</span>}
        </div>
      </header>

      {/* Chat History */}
      <main className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] rounded-2xl px-5 py-3 shadow-sm whitespace-pre-wrap ${
              msg.role === 'user' 
                ? 'bg-blue-500 text-white rounded-br-none' 
                : 'bg-white text-gray-800 border border-gray-100 rounded-bl-none'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[75%] rounded-2xl px-5 py-3 shadow-sm bg-white border border-gray-100 text-gray-500 rounded-bl-none flex gap-2 items-center">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Input Area */}
      <footer className="bg-white border-t border-gray-200 p-4">
        <div className="max-w-4xl mx-auto flex gap-3">
          <textarea
            className="flex-1 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none max-h-32"
            rows={1}
            placeholder="Nhập câu hỏi của bạn (Nhấn Enter để gửi)..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || !input.trim() || serverStatus !== 'ok'}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-xl px-6 py-3 transition-colors flex items-center justify-center min-w-[100px]"
          >
            {isLoading ? 'Đang gửi...' : 'Gửi'}
          </button>
        </div>
      </footer>
    </div>
  )
}

export default App
