import { useState, useEffect, useRef } from 'react'

const API_BASE_URL = "http://localhost:8000";

function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  
  // Sidebar state
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(() => {
    const saved = localStorage.getItem('isSidebarExpanded');
    return saved !== null ? JSON.parse(saved) : true;
  });

  useEffect(() => {
    localStorage.setItem('isSidebarExpanded', JSON.stringify(isSidebarExpanded));
  }, [isSidebarExpanded]);
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isAttachmentMenuOpen, setIsAttachmentMenuOpen] = useState(false);
  const fileInputRef = useRef(null);
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

  // Initial load
  useEffect(() => {
    checkServerAndLoadSessions();
  }, []);

  const checkServerAndLoadSessions = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/health`);
      if (res.ok) {
        setServerStatus("ok");
        await fetchSessions();
      } else {
        setServerStatus("error");
      }
    } catch (error) {
      setServerStatus("error");
    }
  };

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/sessions`);
      const data = await res.json();
      setSessions(data);
      if (data.length > 0) {
        selectSession(data[0].id);
      } else {
        createNewSession();
      }
    } catch (error) {
      console.error("Error fetching sessions:", error);
    }
  };

  const createNewSession = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/sessions`, { method: "POST" });
      const data = await res.json();
      const newSessionId = data.session_id;
      
      const newSession = { id: newSessionId, title: "New Chat", created_at: new Date().toISOString() };
      setSessions(prev => [newSession, ...prev]);
      
      setActiveSessionId(newSessionId);
      setMessages([{ role: 'bot', text: 'Chào bạn, mình là Trợ lý học Cơ sở dữ liệu. Mình có thể giúp gì cho bạn hôm nay?' }]);
    } catch (error) {
      console.error("Error creating session:", error);
    }
  };

  const selectSession = async (sessionId) => {
    setActiveSessionId(sessionId);
    setMessages([]); // Clear while loading
    
    try {
      const res = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`);
      const data = await res.json();
      
      // If session is empty, show default greeting
      if (data.messages && data.messages.length > 0) {
        setMessages(data.messages);
      } else {
        setMessages([{ role: 'bot', text: 'Chào bạn, mình là Trợ lý học Cơ sở dữ liệu. Mình có thể giúp gì cho bạn hôm nay?' }]);
      }
    } catch (error) {
      console.error("Error fetching session messages:", error);
    }
  };

  const deleteSession = async (sessionId, e) => {
    e.stopPropagation();
    if (!window.confirm("Bạn có chắc chắn muốn xóa cuộc hội thoại này?")) {
      return;
    }
    
    try {
      await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, { method: "DELETE" });
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      
      // If we deleted the active session, pick another one
      if (activeSessionId === sessionId) {
        const remaining = sessions.filter(s => s.id !== sessionId);
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          createNewSession();
        }
      }
    } catch (error) {
      console.error("Error deleting session:", error);
    }
  };

  const processNewFiles = (files) => {
    setIsAttachmentMenuOpen(false);
    
    if (selectedFiles.length + files.length > 3) {
      alert("Chỉ được đính kèm tối đa 3 file.");
      return;
    }
    
    const validFiles = [];
    for (let file of files) {
      if (file.size > 10 * 1024 * 1024) {
        alert(`File ${file.name} vượt quá giới hạn 10MB.`);
        continue;
      }
      validFiles.push(file);
    }
    
    setSelectedFiles(prev => [...prev, ...validFiles].slice(0, 3));
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    processNewFiles(files);
    if (fileInputRef.current) {
      fileInputRef.current.value = ""; // reset
    }
  };

  const handlePaste = (e) => {
    const items = e.clipboardData.items;
    const files = [];
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image/") === 0) {
        const file = items[i].getAsFile();
        if (file) files.push(file);
      }
    }
    
    if (files.length > 0) {
      e.preventDefault();
      processNewFiles(files);
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const triggerFileInput = (accept) => {
    if (fileInputRef.current) {
      fileInputRef.current.accept = accept;
      fileInputRef.current.click();
    }
  };

  const handleSend = async () => {
    const trimmedInput = input.trim();
    if ((!trimmedInput && selectedFiles.length === 0) || isLoading || !activeSessionId) return;

    if (serverStatus !== "ok") {
      alert("Không thể kết nối với server backend.");
      return;
    }

    // Prepare temp previews for optimistic UI
    const tempAttachments = selectedFiles.map(f => ({
      filename: f.name,
      is_image: f.type.startsWith("image/"),
      tempUrl: f.type.startsWith("image/") ? URL.createObjectURL(f) : null
    }));

    const userMessage = { role: 'user', text: trimmedInput, attachments: tempAttachments };
    setMessages(prev => [...prev, userMessage]);
    
    const formData = new FormData();
    formData.append("session_id", activeSessionId);
    formData.append("question", trimmedInput);
    selectedFiles.forEach(file => {
      formData.append("files", file);
    });

    setInput("");
    setSelectedFiles([]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/ask`, {
        method: "POST",
        body: formData // No Content-Type header so browser sets it with boundary
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Có lỗi từ máy chủ");
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'bot', text: data.answer }]);
      
      if (data.new_title) {
        setSessions(prev => prev.map(s => s.id === activeSessionId ? { ...s, title: data.new_title } : s));
      }
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

  const handleInput = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      
      {/* Sidebar */}
      <div className={`${isSidebarExpanded ? 'w-64' : 'w-16'} bg-gray-900 text-white flex flex-col shadow-xl z-20 transition-all duration-300 shrink-0`}>
        <div className={`p-4 border-b border-gray-800 flex items-center ${isSidebarExpanded ? 'justify-between' : 'justify-center'}`}>
          {isSidebarExpanded && <h2 className="font-semibold text-lg whitespace-nowrap overflow-hidden">CSDL Chat</h2>}
          <button 
            onClick={() => setIsSidebarExpanded(!isSidebarExpanded)}
            className="text-gray-400 hover:text-white transition-colors p-1 rounded-md hover:bg-gray-800"
            title={isSidebarExpanded ? "Thu gọn sidebar" : "Mở rộng sidebar"}
          >
            {isSidebarExpanded ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
            )}
          </button>
        </div>
        
        <div className="p-4 flex justify-center">
          <button 
            onClick={createNewSession}
            className={`flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium shadow-sm ${isSidebarExpanded ? 'w-full py-2.5 px-4' : 'w-10 h-10 p-2'}`}
            title="Tạo cuộc hội thoại mới"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            {isSidebarExpanded && <span className="whitespace-nowrap overflow-hidden">New chat</span>}
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1 scrollbar-thin">
          {isSidebarExpanded ? (
            sessions.map(session => (
              <div 
                key={session.id}
                onClick={() => selectSession(session.id)}
                className={`group flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                  activeSessionId === session.id 
                    ? 'bg-gray-800 text-white' 
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                  <span className="truncate text-sm font-medium">{session.title}</span>
                </div>
                <button 
                  onClick={(e) => deleteSession(session.id, e)}
                  className="opacity-0 group-hover:opacity-100 hover:text-red-400 transition-all shrink-0 p-1"
                  title="Xoá cuộc hội thoại"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
              </div>
            ))
          ) : (
            <div className="flex flex-col items-center gap-4 mt-2">
              <button 
                onClick={() => setIsSidebarExpanded(true)}
                className="text-gray-400 hover:text-white transition-colors p-2 rounded-md hover:bg-gray-800"
                title="Danh sách hội thoại"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
              </button>
            </div>
          )}
          {isSidebarExpanded && sessions.length === 0 && (
            <div className="text-gray-500 text-sm text-center py-4">Chưa có cuộc hội thoại nào</div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-screen min-w-0">
        
        {/* Header */}
        <header className="bg-white border-b border-gray-200 py-3 px-6 shadow-sm flex justify-between items-center z-10 shrink-0">
          <div>
            <h1 className="text-xl font-bold text-gray-800">Trợ lý học Cơ sở dữ liệu</h1>
          </div>
          <div className="flex items-center gap-2 text-sm">
            {serverStatus === 'checking...' && <span className="text-yellow-500">Đang kiểm tra...</span>}
            {serverStatus === 'ok' && <span className="text-green-500 font-bold flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500"></span> Trực tuyến</span>}
            {serverStatus === 'error' && <span className="text-red-500 font-bold flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500"></span> Mất kết nối</span>}
          </div>
        </header>

        {/* Chat History */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 flex flex-col gap-5 bg-gray-50/50">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-5 py-3.5 shadow-sm whitespace-pre-wrap text-[15px] leading-relaxed ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-br-sm' 
                  : 'bg-white text-gray-800 border border-gray-100 rounded-bl-sm'
              }`}>
                {msg.attachments && msg.attachments.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-2">
                    {msg.attachments.map((att, i) => (
                      <div key={i} className="relative rounded-lg overflow-hidden bg-black/10 border border-black/10 flex items-center justify-center">
                        {att.is_image ? (
                          <img src={att.thumbnail || att.tempUrl} alt={att.filename} className="w-16 h-16 object-cover" title={att.filename} />
                        ) : (
                          <div className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium max-w-[150px]" title={att.filename}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                            <span className="truncate">{att.filename}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                {msg.text}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[75%] rounded-2xl px-5 py-4 shadow-sm bg-white border border-gray-100 text-gray-500 rounded-bl-sm flex gap-2 items-center">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </main>

        {/* Input Area */}
        <footer className="bg-transparent border-t border-gray-200 p-4 shrink-0 pb-6">
          <div 
            className="max-w-4xl mx-auto flex flex-col relative bg-white border border-gray-300 rounded-2xl shadow-sm focus-within:ring-1 focus-within:ring-blue-500 focus-within:border-blue-500 transition-all cursor-text"
            onClick={() => document.getElementById('chat-input').focus()}
            onPaste={handlePaste}
          >
            
            {/* File Preview Area (Inside the pill, top) */}
            {selectedFiles.length > 0 && (
              <div className="flex gap-2 flex-wrap px-3 pt-3">
                {selectedFiles.map((file, idx) => (
                  <div key={idx} className="relative bg-gray-100 rounded-lg p-1.5 flex items-center gap-2 border border-gray-200 pr-8 group">
                    {file.type.startsWith('image/') ? (
                      <img src={URL.createObjectURL(file)} alt="preview" className="w-10 h-10 object-cover rounded" />
                    ) : (
                      <div className="w-10 h-10 flex items-center justify-center bg-white rounded border border-gray-200">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-500"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path></svg>
                      </div>
                    )}
                    <span className="text-xs font-medium text-gray-700 max-w-[120px] truncate">{file.name}</span>
                    <button 
                      onClick={() => removeFile(idx)}
                      className="absolute right-1.5 top-1/2 -translate-y-1/2 bg-gray-400 hover:bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity shadow-sm"
                      title="Xóa"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            {/* Textarea */}
            <textarea
              id="chat-input"
              className="w-full bg-transparent border-none focus:ring-0 resize-none px-4 py-3 max-h-32 shadow-none text-[15px] outline-none"
              rows={1}
              placeholder="Nhập câu hỏi của bạn (Shift+Enter để xuống dòng)..."
              value={input}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              onPaste={handlePaste}
            />

            {/* Bottom Controls Area */}
            <div className="flex justify-between items-end px-2 pb-2">
              {/* Attachment Button & Menu */}
              <div className="relative">
                <button 
                  onClick={() => setIsAttachmentMenuOpen(!isAttachmentMenuOpen)}
                  className="w-[36px] h-[36px] flex items-center justify-center text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors shrink-0"
                  title="Đính kèm file"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                </button>
                
                {isAttachmentMenuOpen && (
                  <div className="absolute bottom-[44px] left-0 bg-white border border-gray-200 rounded-lg shadow-lg w-48 py-1 z-50">
                    <button 
                      onClick={() => triggerFileInput("image/jpeg,image/png,image/webp")}
                      className="w-full text-left px-4 py-2.5 hover:bg-gray-50 text-sm font-medium flex items-center gap-2"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                      Thêm ảnh
                    </button>
                    <button 
                      onClick={() => triggerFileInput(".pdf,.docx,.txt")}
                      className="w-full text-left px-4 py-2.5 hover:bg-gray-50 text-sm font-medium flex items-center gap-2"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                      Thêm tài liệu
                    </button>
                  </div>
                )}
                <input type="file" ref={fileInputRef} onChange={handleFileSelect} multiple className="hidden" />
              </div>

              {/* Send Button */}
              <button 
                onClick={handleSend}
                disabled={isLoading || (!input.trim() && selectedFiles.length === 0) || serverStatus !== 'ok'}
                className="w-[36px] h-[36px] flex items-center justify-center bg-black hover:bg-gray-800 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-lg transition-colors"
                title="Gửi tin nhắn"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>
              </button>
            </div>
          </div>
          <div className="text-center mt-2 text-xs text-gray-400">
             Trợ lý có thể mắc sai lầm. Hãy kiểm tra lại thông tin quan trọng.
          </div>
        </footer>
      </div>
    </div>
  )
}

export default App
