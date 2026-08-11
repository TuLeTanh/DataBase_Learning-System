import { useState, useEffect, useRef } from 'react'
import vi from './locales/vi.json'
import en from './locales/en.json'
import SqlSandbox from './SqlSandbox';

const locales = { vi, en };

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [isSandboxMode, setIsSandboxMode] = useState(false);

  // Settings state
  const [uiLang, setUiLang] = useState(() => localStorage.getItem('uiLang') || 'vi');
  const [accentColor, setAccentColor] = useState(() => localStorage.getItem('accentColor') || 'blue');
  const [fontSize, setFontSize] = useState(() => localStorage.getItem('fontSize') || 'medium');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem('uiLang', uiLang);
    localStorage.setItem('accentColor', accentColor);
    localStorage.setItem('fontSize', fontSize);
    document.documentElement.setAttribute('data-accent', accentColor);
    document.documentElement.setAttribute('data-fontsize', fontSize);
  }, [uiLang, accentColor, fontSize]);

  const t = (key, params = {}) => {
    let str = locales[uiLang][key] || locales['vi'][key] || key;
    Object.keys(params).forEach(p => {
      str = str.replace(`{${p}}`, params[p]);
    });
    return str;
  };

  
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
  }, [messages, isLoading, isSandboxMode]);

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
    if (!window.confirm(t("alert.deleteConfirm"))) {
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
      alert(t("alert.maxFiles"));
      return;
    }
    
    const validFiles = [];
    for (let file of files) {
      if (file.size > 10 * 1024 * 1024) {
        alert(t("alert.maxSize", { name: file.name }));
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
      alert(t("alert.noConnection"));
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
        throw new Error(errorData.detail || t("alert.serverError"));
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'bot', text: data.answer }]);
      
      if (data.new_title) {
        setSessions(prev => prev.map(s => s.id === activeSessionId ? { ...s, title: data.new_title } : s));
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', text: t("error.prefix", { error: error.message }) }]);
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
    <div className="flex h-dvh bg-mesh overflow-hidden font-sans text-slate-100">
      
      {/* Sidebar */}
      <div className={`${isSidebarExpanded ? 'w-[280px]' : 'w-20'} bg-white/5 backdrop-blur-3xl border-r border-white/10 flex flex-col z-20 transition-[width] transition-colors duration-300 ease-out shrink-0 relative shadow-[4px_0_24px_rgba(0,0,0,0.5)]`}>
        <div className={`p-5 border-b border-white/10 flex items-center ${isSidebarExpanded ? 'justify-between' : 'justify-center'}`}>
          {isSidebarExpanded && <h2 className="font-semibold text-lg whitespace-nowrap overflow-hidden text-white/90 tracking-wide">{t("app.title")}</h2>}
          <button 
            onClick={() => setIsSidebarExpanded(!isSidebarExpanded)}
            className="text-white/60 hover:text-white hover:bg-white/10 transition p-1.5 rounded-xl hover:scale-105 active:scale-95 focus-ring"
            title={isSidebarExpanded ? t("sidebar.collapse") : t("sidebar.expand")}
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
            className={`flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 text-white rounded-2xl transition font-medium shadow-sm border border-white/5 hover:scale-[1.02] active:scale-[0.98] focus-ring group ${isSidebarExpanded ? 'w-full py-3 px-4' : 'w-12 h-12 p-3 rounded-2xl'}`}
            title={t("sidebar.newChat")}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0 text-accent-400 group-hover:text-accent-300 transition-colors"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            {isSidebarExpanded && <span className="whitespace-nowrap overflow-hidden">{t("sidebar.newChatLabel")}</span>}
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1 scrollbar-thin">
          {isSidebarExpanded ? (
            sessions.map((session, idx) => (
              <div 
                key={session.id}
                onClick={() => selectSession(session.id)}
                className={`group animate-fade-up flex items-center justify-between px-3 py-3 rounded-xl cursor-pointer transition duration-300 focus-ring ${
                  activeSessionId === session.id 
                    ? 'bg-accent-600/20 text-accent-100 border border-accent-500/30' 
                    : 'text-white/60 border border-transparent hover:bg-white/5 hover:text-white hover:border-white/10 hover:scale-[0.99]'
                }`}
                style={{ animationDelay: `${idx * 40}ms` }}
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`shrink-0 ${activeSessionId === session.id ? 'text-accent-400' : ''}`}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                  <span className="truncate text-sm font-medium">{session.title}</span>
                </div>
                <button 
                  onClick={(e) => deleteSession(session.id, e)}
                  className="opacity-0 group-hover:opacity-100 text-white/40 hover:text-red-400 transition shrink-0 p-1 rounded-md hover:bg-white/10"
                  title={t("sidebar.deleteChat")}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
              </div>
            ))
          ) : (
            <div className="flex flex-col items-center gap-4 mt-2 animate-fade-up">
              <button 
                onClick={() => setIsSidebarExpanded(true)}
                className="text-white/60 hover:text-white transition p-3 rounded-xl hover:bg-white/10 hover:scale-[1.05] active:scale-[0.95]"
                title={t("sidebar.chatList")}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
              </button>
            </div>
          )}
          {isSidebarExpanded && sessions.length === 0 && (
            <div className="text-white/40 text-sm text-center py-6 animate-fade-up">{t("sidebar.empty")}</div>
          )}
        </div>

        <div className="mt-auto px-4 py-3 border-t border-white/10 flex flex-col gap-2 shrink-0">
          <button 
            onClick={() => setIsSettingsOpen(true)}
            className={`flex items-center gap-3 p-2.5 rounded-xl hover:bg-white/10 transition focus-ring group ${!isSidebarExpanded ? 'justify-center' : ''}`}
            title={!isSidebarExpanded ? t("settings.title") : ""}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white/60 group-hover:text-white transition-colors shrink-0">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
            {isSidebarExpanded && <span className="font-medium text-white/80 group-hover:text-white transition-colors">{t("settings.title")}</span>}
          </button>
          
          {/* Avatar Dummy */}
          <div className={`flex items-center gap-3 p-2.5 rounded-xl hover:bg-white/5 transition cursor-pointer ${!isSidebarExpanded ? 'justify-center' : ''}`}>
             <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-accent-500 to-purple-500 flex items-center justify-center shrink-0 border border-white/20">
               <span className="text-sm font-bold text-white shadow-sm">U</span>
             </div>
             {isSidebarExpanded && <span className="font-medium text-white/90 truncate">User</span>}
          </div>
        </div>
      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col h-dvh min-w-0 relative">
        
        {/* Header */}
        <header className="absolute top-0 inset-x-0 bg-[#020617]/60 backdrop-blur-xl border-b border-white/5 py-4 px-6 md:px-8 flex justify-between items-center z-10 shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-medium tracking-wide text-white/90">{t("app.headerTitle")}</h1>
            <div className="flex items-center bg-white/5 rounded-lg p-1 border border-white/10">
              <button
                onClick={() => setIsSandboxMode(false)}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${!isSandboxMode ? 'bg-accent-600 text-white shadow-sm' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
              >
                Chat
              </button>
              <button
                onClick={() => setIsSandboxMode(true)}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${isSandboxMode ? 'bg-accent-600 text-white shadow-sm' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
              >
                SQL Sandbox
              </button>
            </div>
          </div>
          <div className="flex items-center gap-3 text-sm font-medium">
            {serverStatus === 'checking...' && <span className="text-yellow-400/80 flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-yellow-400/80 animate-pulse"></div>{t("server.checking")}</span>}
            {serverStatus === 'ok' && <span className="text-emerald-400/90 flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-400/90"></div>{t("server.online")}</span>}
            {serverStatus === 'error' && <span className="text-red-400/90 flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-red-400/90"></div>{t("server.offline")}</span>}
          </div>
        </header>

        {isSandboxMode ? (
          <div className="flex-1 pt-20">
            <SqlSandbox activeSessionId={activeSessionId} t={t} />
          </div>
        ) : (
          <>
            {/* Chat History */}
            <main className="flex-1 overflow-y-auto px-4 md:px-12 lg:px-24 pt-24 pb-4 flex flex-col gap-8 scrollbar-thin scroll-smooth relative z-0">
              {messages.length === 0 && !isLoading && (
                <div className="m-auto flex flex-col items-center justify-center animate-fade-up text-center max-w-md">
                  <div className="w-20 h-20 mb-6 bg-gradient-to-tr from-accent-600/30 to-purple-500/30 rounded-3xl flex items-center justify-center border border-white/10 shadow-[0_0_40px_rgba(37,99,235,0.2)]">
                     <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-accent-400"><path d="M12 2a10 10 0 0 1 10 10c0 5.5-4.5 10-10 10S2 17.5 2 12 6.5 2 12 2Z"></path><path d="m9 12 2 2 4-4"></path></svg>
                  </div>
                  <h3 className="text-2xl font-medium text-white mb-2">{t("chat.emptyTitle")}</h3>
                  <p className="text-white/50 text-sm leading-relaxed">{t("chat.emptyDesc")}</p>
                </div>
              )}

              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-up group`}>
                  <div className={`p-[1px] rounded-[28px] max-w-[85%] md:max-w-[75%] shadow-lg ${
                    msg.role === 'user' 
                      ? 'bg-gradient-to-b from-accent-500/50 to-accent-600/20 rounded-br-sm' 
                      : 'bg-gradient-to-b from-white/10 to-transparent rounded-bl-sm'
                  }`}>
                    <div className={`whitespace-pre-wrap text-[15px] leading-relaxed px-5 py-4 ${
                      msg.role === 'user' 
                        ? 'bg-accent-600/80 text-white border border-accent-500/30 rounded-[27px] rounded-br-[3px]' 
                        : 'bg-white/5 text-slate-200 border border-white/5 rounded-[27px] rounded-bl-[3px]'
                    }`}>
                      {msg.attachments && msg.attachments.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-3">
                          {msg.attachments.map((att, i) => (
                            <div key={i} className="p-[1px] bg-gradient-to-b from-white/20 to-white/5 rounded-xl">
                              <div className="relative rounded-[11px] overflow-hidden bg-black/40 border border-white/5 flex items-center justify-center">
                                {att.is_image ? (
                                  <img src={att.thumbnail || att.tempUrl} alt={att.filename} className="w-16 h-16 object-cover" title={att.filename} />
                                ) : (
                                  <div className="flex items-center gap-2 px-3 py-2 text-xs font-medium max-w-[150px] text-white/80" title={att.filename}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0 text-white/50"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                                    <span className="truncate">{att.filename}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      {msg.text}
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start animate-fade-up">
                  <div className="p-[1px] rounded-[28px] rounded-bl-sm bg-gradient-to-b from-white/10 to-transparent w-full max-w-[85%] md:max-w-[75%]">
                    <div className="bg-white/5 backdrop-blur-md border border-white/5 rounded-[27px] rounded-bl-[3px] p-5 flex flex-col gap-3">
                      <div className="h-3 bg-white/10 rounded-full w-3/4 animate-skeleton"></div>
                      <div className="h-3 bg-white/10 rounded-full w-full animate-skeleton" style={{animationDelay: '200ms'}}></div>
                      <div className="h-3 bg-white/10 rounded-full w-5/6 animate-skeleton" style={{animationDelay: '400ms'}}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} className="h-1" />
            </main>

            {/* Input Area */}
            <footer className="bg-transparent p-4 md:p-6 shrink-0 relative z-10 w-full flex flex-col items-center">

          <div className="w-full max-w-4xl p-[1px] bg-gradient-to-b from-white/15 to-white/5 rounded-[32px] shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
            <div 
              className="w-full bg-[#0B101E]/80 backdrop-blur-2xl border border-white/10 rounded-[31px] transition focus-within:bg-[#0B101E]/95 focus-within:border-white/20 focus-within:ring-4 focus-within:ring-accent-500/10 cursor-text flex flex-col"
              onClick={() => document.getElementById('chat-input').focus()}
              onPaste={handlePaste}
            >
              
              {/* File Preview Area (Inside the pill, top) */}
              {selectedFiles.length > 0 && (
                <div className="flex gap-2 flex-wrap px-4 pt-4">
                  {selectedFiles.map((file, idx) => (
                    <div key={idx} className="p-[1px] bg-gradient-to-b from-white/20 to-white/5 rounded-2xl group animate-fade-up shrink-0">
                      <div className="relative bg-[#1A2235]/90 backdrop-blur-md rounded-[15px] p-1.5 flex items-center gap-3 pr-9 border border-white/5 h-[52px]">
                        {file.type.startsWith('image/') ? (
                          <img src={URL.createObjectURL(file)} alt="preview" className="w-10 h-10 object-cover rounded-xl" />
                        ) : (
                          <div className="w-10 h-10 flex items-center justify-center bg-white/5 rounded-xl border border-white/5">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white/60"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path></svg>
                          </div>
                        )}
                        <span className="text-xs font-medium text-white/90 max-w-[120px] truncate tabular-nums">{file.name}</span>
                        <button 
                          onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                          className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/10 hover:bg-red-500/80 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition focus-ring shadow-sm hover:scale-110 active:scale-95"
                          title={t("file.delete")}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Textarea */}
              <textarea
                id="chat-input"
                className="w-full bg-transparent border-none focus:ring-0 resize-none px-5 py-4 max-h-40 shadow-none text-[15px] text-white placeholder:text-white/40 outline-none leading-relaxed"
                rows={1}
                placeholder={t("input.placeholder")}
                value={input}
                onChange={handleInput}
                onKeyDown={handleKeyDown}
                onPaste={handlePaste}
              />

              {/* Bottom Controls Area */}
              <div className="flex justify-between items-end px-3 pb-3">
                {/* Attachment Button & Menu */}
                <div className="relative">
                  <button 
                    onClick={(e) => { e.stopPropagation(); setIsAttachmentMenuOpen(!isAttachmentMenuOpen); }}
                    className="w-10 h-10 flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 rounded-full transition shrink-0 hover:scale-[1.05] active:scale-[0.95] focus-ring"
                    title={t("input.attach")}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                  </button>
                  
                  {isAttachmentMenuOpen && (
                    <div className="absolute bottom-[52px] left-0 bg-[#1A2235]/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl w-48 py-1.5 z-50 animate-fade-up">
                      <button 
                        onClick={() => triggerFileInput("image/jpeg,image/png,image/webp")}
                        className="w-full text-left px-4 py-2.5 hover:bg-white/10 text-sm font-medium flex items-center gap-3 text-white/90 transition-colors focus-ring"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white/50"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                        Thêm ảnh
                      </button>
                      <button 
                        onClick={() => triggerFileInput(".pdf,.docx,.txt")}
                        className="w-full text-left px-4 py-2.5 hover:bg-white/10 text-sm font-medium flex items-center gap-3 text-white/90 transition-colors focus-ring"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white/50"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        Thêm tài liệu
                      </button>
                    </div>
                  )}
                  <input type="file" ref={fileInputRef} onChange={handleFileSelect} multiple className="hidden" />
                </div>

                {/* Send Button */}
                <button 
                  onClick={(e) => { e.stopPropagation(); handleSend(); }}
                  disabled={isLoading || (!input.trim() && selectedFiles.length === 0) || serverStatus !== 'ok'}
                  className="h-10 pl-4 pr-1 bg-white/10 hover:bg-white/20 disabled:bg-white/5 disabled:opacity-50 text-white rounded-full flex items-center gap-2 transition hover:scale-105 active:scale-95 focus-ring group"
                  title={t("input.sendTooltip")}
                >
                  <span className="text-sm font-medium tracking-wide">{t("input.send")}</span>
                  <div className="w-8 h-8 bg-accent-600 rounded-full flex items-center justify-center group-hover:bg-accent-500 group-disabled:bg-white/20 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="transform group-hover:translate-x-[2px] group-hover:-translate-y-[2px] transition-transform"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                  </div>
                </button>
              </div>
            </div>
          </div>
          <div className="text-center mt-3 text-xs text-white/40 tracking-wide">
             Trợ lý có thể mắc sai lầm. Hãy kiểm tra lại thông tin quan trọng.
          </div>
        </footer>
          </>
        )}
      </div>

      {isSettingsOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-fade-up">
          <div className="p-[1px] bg-gradient-to-b from-white/20 to-white/5 rounded-3xl shadow-2xl w-full max-w-md mx-4">
            <div className="bg-[#0B101E]/95 backdrop-blur-2xl border border-white/10 rounded-[31px] p-6 flex flex-col gap-6">
              
              <div className="flex justify-between items-center border-b border-white/10 pb-4">
                <h2 className="text-xl font-semibold text-white">{t("settings.title")}</h2>
                <button 
                  onClick={() => setIsSettingsOpen(false)}
                  className="text-white/50 hover:text-white hover:bg-white/10 p-2 rounded-xl transition active:scale-95 focus-ring"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
              </div>

              {/* Theme / Accent Color */}
              <div className="flex flex-col gap-3">
                <label className="text-sm font-medium text-white/70">{t("settings.theme")}</label>
                <div className="flex gap-3">
                  {['blue', 'purple', 'emerald'].map(c => (
                    <button
                      key={c}
                      onClick={() => setAccentColor(c)}
                      className={`w-10 h-10 rounded-full transition flex items-center justify-center focus-ring ${c === 'blue' ? 'bg-blue-500' : c === 'purple' ? 'bg-purple-500' : 'bg-emerald-500'} ${accentColor === c ? 'ring-2 ring-white ring-offset-2 ring-offset-[#0B101E] scale-110' : 'opacity-70 hover:opacity-100 hover:scale-105'}`}
                    >
                      {accentColor === c && <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>}
                    </button>
                  ))}
                </div>
              </div>

              {/* Language */}
              <div className="flex flex-col gap-3">
                <label className="text-sm font-medium text-white/70">{t("settings.language")}</label>
                <select 
                  value={uiLang}
                  onChange={(e) => setUiLang(e.target.value)}
                  className="bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 text-white/90 outline-none focus:border-accent-500 focus:ring-1 focus:ring-accent-500/50 appearance-none cursor-pointer"
                >
                  <option value="vi">Tiếng Việt</option>
                  <option value="en">English</option>
                </select>
              </div>

              {/* Font Size */}
              <div className="flex flex-col gap-3">
                <label className="text-sm font-medium text-white/70">{t("settings.fontSize")}</label>
                <div className="flex bg-black/40 border border-white/10 rounded-xl p-1">
                  {['small', 'medium', 'large'].map(s => (
                    <button
                      key={s}
                      onClick={() => setFontSize(s)}
                      className={`flex-1 py-2 text-sm font-medium rounded-lg transition focus-ring ${fontSize === s ? 'bg-white/10 text-white shadow-sm' : 'text-white/50 hover:text-white/80'}`}
                    >
                      {s === 'small' ? t("settings.fontSizeSmall") : s === 'medium' ? t("settings.fontSizeMedium") : t("settings.fontSizeLarge")}
                    </button>
                  ))}
                </div>
              </div>

              {/* Danger Zone */}
              <div className="flex flex-col gap-3 pt-4 border-t border-white/10">
                <label className="text-sm font-medium text-red-400">{t("settings.dangerZone")}</label>
                <button
                  onClick={async () => {
                    if (window.confirm(t("settings.deleteAllConfirm"))) {
                      for (let s of sessions) {
                        await fetch(`${API_BASE_URL}/api/sessions/${s.id}`, { method: "DELETE" });
                      }
                      setSessions([]);
                      setActiveSessionId(null);
                      setMessages([]);
                      setIsSettingsOpen(false);
                      const res = await fetch(`${API_BASE_URL}/api/sessions`, { method: "POST" });
                      const data = await res.json();
                      setSessions([{ id: data.session_id, title: "New Chat", created_at: new Date().toISOString() }]);
                      setActiveSessionId(data.session_id);
                      setMessages([{ role: 'bot', text: 'Chào bạn, mình là Trợ lý học Cơ sở dữ liệu. Mình có thể giúp gì cho bạn hôm nay?' }]);
                    }
                  }}
                  className="w-full py-2.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 hover:border-red-500/30 rounded-xl transition font-medium focus-ring"
                >
                  {t("settings.deleteAll")}
                </button>
              </div>
              
              <div className="text-center text-xs text-white/30 pt-2 font-medium">
                {t("app.version")}
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}

export default App
