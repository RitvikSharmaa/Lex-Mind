import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTime, setSearchTime] = useState(0);
  const [expandedDoc, setExpandedDoc] = useState<number | null>(null);
  
  // Summarization state
  const [summaryMode, setSummaryMode] = useState<'select' | 'custom'>('select');
  const [cases, setCases] = useState<string[]>([]);
  const [casesLoading, setCasesLoading] = useState(false);
  const [selectedCase, setSelectedCase] = useState('');
  const [caseSearchQuery, setCaseSearchQuery] = useState('');
  const [customText, setCustomText] = useState('');
  const [originalText, setOriginalText] = useState('');
  const [summary, setSummary] = useState('');
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryStats, setSummaryStats] = useState({ original: 0, summary: 0, compression: 0 });
  const [maxLength, setMaxLength] = useState(150);
  const [minLength, setMinLength] = useState(50);
  const [showOriginalDoc, setShowOriginalDoc] = useState(false);
  
  // QA/Chat state
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{role: string, content: string}>>([]);
  const [qaLoading, setQaLoading] = useState(false);
  const [retrievedDocs, setRetrievedDocs] = useState<any[]>([]);
  const [expandedDocId, setExpandedDocId] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  
  // Analytics state
  const [stats, setStats] = useState<any>(null);

  // Auto-scroll to bottom when chat updates
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, qaLoading]);

  // Load cases for summarization
  useEffect(() => {
    if (activeTab === 'summarization' && cases.length === 0) {
      console.log('Fetching cases...');
      setCasesLoading(true);
      fetch('http://localhost:5000/api/cases')
        .then(res => {
          console.log('Cases response status:', res.status);
          return res.json();
        })
        .then(data => {
          console.log('Cases loaded:', data.cases?.length || 0);
          setCases(data.cases || []);
          setCasesLoading(false);
        })
        .catch(err => {
          console.error('Error loading cases:', err);
          alert('Error loading cases. Check if backend is running.');
          setCasesLoading(false);
        });
    }
  }, [activeTab, cases.length]);

  // Load analytics stats
  useEffect(() => {
    if (activeTab === 'analytics' && !stats) {
      fetch('http://localhost:5000/api/stats')
        .then(res => res.json())
        .then(data => setStats(data))
        .catch(err => console.error(err));
    }
  }, [activeTab]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    const start = performance.now();
    
    try {
      const response = await fetch('http://localhost:5000/api/retrieve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, k: 5 }),
      });
      const data = await response.json();
      setResults(data.results || []);
      setSearchTime((performance.now() - start) / 1000);
    } catch (error) {
      console.error('Error:', error);
      alert('Error connecting to backend. Make sure Flask is running on port 5000');
    }
    setLoading(false);
  };

  const handleSummarize = async () => {
    let textToSummarize = '';
    
    setSummaryLoading(true);
    
    if (summaryMode === 'select') {
      if (!selectedCase) {
        alert('Please select a case');
        setSummaryLoading(false);
        return;
      }
      try {
        const caseResponse = await fetch(`http://localhost:5000/api/case/${selectedCase}`);
        const caseData = await caseResponse.json();
        textToSummarize = caseData.text;
        setOriginalText(textToSummarize); // Store original for viewing
      } catch (error) {
        console.error('Error fetching case:', error);
        setSummaryLoading(false);
        return;
      }
    } else {
      textToSummarize = customText;
      setOriginalText(textToSummarize);
    }

    if (!textToSummarize.trim()) {
      alert('Please enter text to summarize');
      setSummaryLoading(false);
      return;
    }

    try {
      console.log('Sending to backend:', { max_length: maxLength, min_length: minLength });
      const response = await fetch('http://localhost:5000/api/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: textToSummarize, 
          max_length: maxLength, 
          min_length: minLength 
        }),
      });
      const data = await response.json();
      console.log('Received from backend:', data);
      setSummary(data.summary);
      setSummaryStats({
        original: data.original_length,
        summary: data.summary_length,
        compression: data.compression_ratio,
      });
    } catch (error) {
      console.error('Error:', error);
      alert('Error generating summary');
    }
    setSummaryLoading(false);
  };

  const handleQA = async () => {
    if (!question.trim()) return;
    
    // Add user message to chat
    const userMessage = { role: 'user', content: question };
    setChatHistory(prev => [...prev, userMessage]);
    setQuestion('');
    setQaLoading(true);
    
    try {
      console.log('Sending chat request:', question);
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          question, 
          history: chatHistory 
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Chat response:', data);
      
      if (data.success) {
        // Add assistant message to chat
        const assistantMessage = { role: 'assistant', content: data.answer };
        setChatHistory(prev => [...prev, assistantMessage]);
        setRetrievedDocs(data.retrieved_docs || []);
      } else {
        const errorMessage = { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' };
        setChatHistory(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Chat Error:', error);
      const errorMessage = { role: 'assistant', content: 'Error: Could not connect to the server. Please try again.' };
      setChatHistory(prev => [...prev, errorMessage]);
    }
    setQaLoading(false);
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Sidebar */}
      <div className="w-64 bg-gradient-to-b from-purple-900 via-purple-800 to-blue-900 text-white p-6 flex flex-col">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">⚖️ LexMind AI</h1>
          <p className="text-sm text-purple-200 mt-1">Legal Intelligence</p>
        </div>
        <nav className="space-y-2 flex-1">
          {[
            { id: 'home', icon: '🏠', label: 'Home' },
            { id: 'retrieval', icon: '🔍', label: 'Case Retrieval' },
            { id: 'summarization', icon: '📝', label: 'Summarization' },
            { id: 'qa', icon: '❓', label: 'Q&A' },
            { id: 'analytics', icon: '📊', label: 'Analytics' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full text-left px-4 py-3 rounded-lg transition ${
                activeTab === tab.id ? 'bg-white/20 shadow-lg' : 'hover:bg-white/10'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
        <div className="mt-auto pt-6 border-t border-white/20 text-sm text-purple-200">
          <p className="font-semibold text-white mb-2">AI Models:</p>
          <p>🧠 MPNet</p>
          <p>📝 BART</p>
          <p>❓ BERT</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-8">
        {activeTab === 'home' && (
          <div className="space-y-8 animate-fade-in">
            <div className="text-center">
              <h1 className="text-6xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
                LexMind AI
              </h1>
              <p className="text-2xl text-gray-600">Deep Learning Powered Legal Intelligence</p>
            </div>

            <div className="grid grid-cols-4 gap-6">
              {[
                { label: 'Documents', value: '3,111', color: 'purple' },
                { label: 'Embedding Dims', value: '768', color: 'blue' },
                { label: 'Speed', value: '<100ms', color: 'green' },
                { label: 'AI Models', value: '3', color: 'pink' },
              ].map((stat, idx) => (
                <div key={idx} className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition">
                  <div className={`text-3xl font-bold text-${stat.color}-600`}>{stat.value}</div>
                  <div className="text-gray-600">{stat.label}</div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-6">
              {[
                { id: 'retrieval', icon: '🔍', title: 'Case Retrieval', desc: 'Find similar legal cases' },
                { id: 'summarization', icon: '📝', title: 'Summarization', desc: 'Generate summaries' },
                { id: 'qa', icon: '❓', title: 'Legal Q&A', desc: 'Ask questions' },
                { id: 'analytics', icon: '📊', title: 'Analytics', desc: 'View statistics' },
              ].map(feature => (
                <div
                  key={feature.id}
                  onClick={() => setActiveTab(feature.id)}
                  className="bg-white rounded-2xl p-8 shadow-lg cursor-pointer hover:shadow-xl hover:scale-105 transition"
                >
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="text-2xl font-bold mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'retrieval' && (
          <div className="space-y-6">
            <h1 className="text-4xl font-bold text-gray-800">🔍 Case Retrieval</h1>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., What are precedents for cheque bounce under section 138?"
                className="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-purple-500 outline-none"
                rows={4}
              />
              <button
                onClick={handleSearch}
                disabled={loading}
                className="mt-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-xl font-semibold hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Searching...
                  </span>
                ) : 'Search Cases'}
              </button>
              
              {searchTime > 0 && (
                <div className="mt-4 text-green-600 font-semibold">
                  ✅ Found {results.length} cases in {searchTime.toFixed(3)}s
                </div>
              )}
            </div>

            {results.length > 0 && (
              <div className="space-y-4">
                {results.map((result, idx) => (
                  <div key={idx} className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-bold text-gray-800">
                          #{result.rank} {result.case_id}
                        </h3>
                        <p className="text-gray-600">Type: {result.label}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-purple-600">
                          {(result.similarity_score * 100).toFixed(1)}%
                        </div>
                        <div className="text-sm text-gray-600">Similarity</div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-xl p-4">
                      <p className="text-gray-700 leading-relaxed">
                        {expandedDoc === idx ? result.text : result.text.substring(0, 300) + '...'}
                      </p>
                      <button
                        onClick={() => setExpandedDoc(expandedDoc === idx ? null : idx)}
                        className="mt-2 text-purple-600 font-semibold hover:text-purple-700"
                      >
                        {expandedDoc === idx ? '▲ Show Less' : '▼ View Full Document'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'summarization' && (
          <div className="space-y-6">
            <h1 className="text-4xl font-bold text-gray-800">📝 Summarization</h1>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="flex space-x-4 mb-6">
                <button
                  onClick={() => setSummaryMode('select')}
                  className={`px-6 py-2 rounded-lg font-semibold transition ${
                    summaryMode === 'select'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  📚 Select from Database
                </button>
                <button
                  onClick={() => setSummaryMode('custom')}
                  className={`px-6 py-2 rounded-lg font-semibold transition ${
                    summaryMode === 'custom'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  ✍️ Enter Custom Text
                </button>
              </div>

              {summaryMode === 'select' ? (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Search and select a case:
                  </label>
                  {casesLoading ? (
                    <div className="text-center py-4">
                      <svg className="animate-spin h-8 w-8 text-purple-600 mx-auto" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                      </svg>
                      <p className="text-gray-600 mt-2">Loading cases...</p>
                    </div>
                  ) : cases.length === 0 ? (
                    <div className="text-center py-4 text-red-600">
                      No cases loaded. Check backend connection.
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <input
                        type="text"
                        value={caseSearchQuery}
                        onChange={(e) => setCaseSearchQuery(e.target.value)}
                        placeholder="Type to search cases (e.g., C123, C456)..."
                        className="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 outline-none"
                      />
                      <div className="max-h-48 overflow-y-auto border-2 border-gray-200 rounded-xl">
                        {cases
                          .filter(caseId => 
                            caseSearchQuery === '' || 
                            caseId.toLowerCase().includes(caseSearchQuery.toLowerCase())
                          )
                          .slice(0, 50)
                          .map(caseId => (
                            <div
                              key={caseId}
                              onClick={() => {
                                setSelectedCase(caseId);
                                setCaseSearchQuery(caseId);
                              }}
                              className={`p-3 cursor-pointer hover:bg-purple-50 transition ${
                                selectedCase === caseId ? 'bg-purple-100 font-semibold' : ''
                              }`}
                            >
                              {caseId}
                            </div>
                          ))}
                        {cases.filter(caseId => 
                          caseSearchQuery === '' || 
                          caseId.toLowerCase().includes(caseSearchQuery.toLowerCase())
                        ).length === 0 && (
                          <div className="p-4 text-center text-gray-500">
                            No cases found matching "{caseSearchQuery}"
                          </div>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">
                        {selectedCase ? `Selected: ${selectedCase}` : 'No case selected'} 
                        {' • '}
                        Showing {Math.min(50, cases.filter(c => 
                          caseSearchQuery === '' || 
                          c.toLowerCase().includes(caseSearchQuery.toLowerCase())
                        ).length)} of {cases.filter(c => 
                          caseSearchQuery === '' || 
                          c.toLowerCase().includes(caseSearchQuery.toLowerCase())
                        ).length} matching cases
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Enter text to summarize:
                  </label>
                  <textarea
                    value={customText}
                    onChange={(e) => setCustomText(e.target.value)}
                    placeholder="Paste your legal document here..."
                    className="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-purple-500 outline-none"
                    rows={10}
                  />
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 mt-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Max Length: {maxLength}
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="300"
                    value={maxLength}
                    onChange={(e) => setMaxLength(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Min Length: {minLength}
                  </label>
                  <input
                    type="range"
                    min="20"
                    max="100"
                    value={minLength}
                    onChange={(e) => setMinLength(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>

              <button
                onClick={handleSummarize}
                disabled={summaryLoading}
                className="mt-6 w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-xl font-semibold hover:shadow-lg transition disabled:opacity-50"
              >
                {summaryLoading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Generating Summary... (30-60s)
                  </span>
                ) : '✨ Generate Summary'}
              </button>
            </div>

            {summary && (
              <div className="space-y-6">
                <div className="bg-white rounded-2xl p-6 shadow-lg">
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">📝 Generated Summary</h2>
                  
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="bg-purple-50 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-purple-600">{summaryStats.original}</div>
                      <div className="text-sm text-gray-600">Original Chars</div>
                    </div>
                    <div className="bg-blue-50 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600">{summaryStats.summary}</div>
                      <div className="text-sm text-gray-600">Summary Chars</div>
                    </div>
                    <div className="bg-green-50 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-green-600">{summaryStats.compression.toFixed(1)}%</div>
                      <div className="text-sm text-gray-600">Compression</div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6">
                    <p className="text-gray-800 leading-relaxed">{summary}</p>
                  </div>
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-lg">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold text-gray-800">📄 Original Document</h2>
                    <button
                      onClick={() => setShowOriginalDoc(!showOriginalDoc)}
                      className="text-purple-600 font-semibold hover:text-purple-700"
                    >
                      {showOriginalDoc ? '▲ Hide' : '▼ View Full Document'}
                    </button>
                  </div>
                  
                  {showOriginalDoc && (
                    <div className="bg-gray-50 rounded-xl p-6 max-h-96 overflow-y-auto">
                      <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{originalText}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'qa' && (
          <div className="flex flex-col h-[calc(100vh-4rem)]">
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-4xl font-bold text-gray-800">💬 Legal Chat (RAG)</h1>
              {chatHistory.length > 0 && (
                <button
                  onClick={() => {
                    setChatHistory([]);
                    setRetrievedDocs([]);
                  }}
                  className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
                >
                  🗑️ Clear Chat
                </button>
              )}
            </div>

            <div className="flex-1 flex flex-row gap-4 min-h-0">
              {/* Chat Panel - Left Side */}
              <div className="flex flex-col w-3/5 min-h-0">
                {/* Chat Messages Area */}
                <div className="flex-1 bg-white rounded-2xl p-6 shadow-lg overflow-y-auto space-y-4 min-h-0">
                  {chatHistory.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-gray-400">
                      <div className="text-center">
                        <div className="text-6xl mb-4">💬</div>
                        <p className="text-xl">Start a conversation about Indian law</p>
                        <p className="text-sm mt-2">Ask questions and get AI-powered answers with legal context</p>
                      </div>
                    </div>
                  ) : (
                    chatHistory.map((msg, idx) => (
                      <div
                        key={idx}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[70%] rounded-2xl p-4 ${
                            msg.role === 'user'
                              ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          <div className="flex items-start space-x-2">
                            <div className="text-2xl flex-shrink-0">
                              {msg.role === 'user' ? '👤' : '🤖'}
                            </div>
                            <div className="flex-1 prose prose-sm max-w-none">
                              {msg.role === 'user' ? (
                                <p className="leading-relaxed whitespace-pre-wrap text-white m-0">{msg.content}</p>
                              ) : (
                                <div className="markdown-content">
                                  <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    rehypePlugins={[rehypeHighlight]}
                                    components={{
                                      h1: ({node, ...props}) => <h1 className="text-2xl font-bold mt-4 mb-2 text-gray-800" {...props} />,
                                      h2: ({node, ...props}) => <h2 className="text-xl font-bold mt-3 mb-2 text-gray-800" {...props} />,
                                      h3: ({node, ...props}) => <h3 className="text-lg font-bold mt-2 mb-1 text-gray-800" {...props} />,
                                      p: ({node, ...props}) => <p className="mb-2 leading-relaxed text-gray-800" {...props} />,
                                      strong: ({node, ...props}) => <strong className="font-bold text-gray-900" {...props} />,
                                      em: ({node, ...props}) => <em className="italic text-gray-700" {...props} />,
                                      ul: ({node, ...props}) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
                                      ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
                                      li: ({node, ...props}) => <li className="text-gray-800" {...props} />,
                                      code: ({node, inline, ...props}: any) => 
                                        inline ? (
                                          <code className="bg-purple-100 text-purple-800 px-1.5 py-0.5 rounded text-sm font-mono" {...props} />
                                        ) : (
                                          <code className="block bg-gray-800 text-gray-100 p-3 rounded-lg overflow-x-auto text-sm font-mono my-2" {...props} />
                                        ),
                                      pre: ({node, ...props}) => <pre className="bg-gray-800 rounded-lg overflow-hidden my-2" {...props} />,
                                      blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-purple-500 pl-4 italic text-gray-700 my-2" {...props} />,
                                      table: ({node, ...props}) => (
                                        <div className="overflow-x-auto my-2">
                                          <table className="min-w-full border-collapse border border-gray-300" {...props} />
                                        </div>
                                      ),
                                      thead: ({node, ...props}) => <thead className="bg-purple-100" {...props} />,
                                      th: ({node, ...props}) => <th className="border border-gray-300 px-4 py-2 text-left font-bold text-gray-800" {...props} />,
                                      td: ({node, ...props}) => <td className="border border-gray-300 px-4 py-2 text-gray-800" {...props} />,
                                      a: ({node, ...props}) => <a className="text-purple-600 hover:text-purple-800 underline" {...props} />,
                                    }}
                                  >
                                    {msg.content}
                                  </ReactMarkdown>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                  
                  {qaLoading && (
                    <div className="flex justify-start">
                      <div className="max-w-[70%] rounded-2xl p-4 bg-gray-100">
                        <div className="flex items-center space-x-2">
                          <div className="text-2xl">🤖</div>
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                {/* Input Area - Fixed at bottom */}
                <div className="bg-white rounded-2xl p-4 shadow-lg mt-4 flex-shrink-0">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !qaLoading && question.trim()) {
                          handleQA();
                        }
                      }}
                      placeholder="Ask about Indian law, cheque dishonour, legal precedents..."
                      className="flex-1 p-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 outline-none"
                      disabled={qaLoading}
                    />
                    <button
                      onClick={handleQA}
                      disabled={qaLoading || !question.trim()}
                      className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {qaLoading ? (
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                        </svg>
                      ) : '📤'}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    💡 Powered by NVIDIA Nemotron Nano 9B + RAG retrieval from 3,111 legal documents
                  </p>
                </div>
              </div>

              {/* Retrieved Documents Panel - Right Side */}
              {retrievedDocs.length > 0 && (
                <div className="bg-white rounded-2xl p-4 shadow-lg overflow-y-auto w-2/5 min-h-0">
                  <h3 className="text-lg font-bold text-gray-700 mb-3 sticky top-0 bg-white pb-2">
                    📚 Retrieved Documents ({retrievedDocs.length})
                  </h3>
                  <div className="space-y-2">
                    {retrievedDocs.map((doc, idx) => (
                      <div key={idx} className="bg-gray-50 rounded-lg overflow-hidden border border-gray-200">
                        <div 
                          className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-100 transition"
                          onClick={() => setExpandedDocId(expandedDocId === doc.case_id ? null : doc.case_id)}
                        >
                          <div className="flex-1">
                            <span className="font-semibold text-purple-600 block">{doc.case_id}</span>
                            <span className="text-gray-600 text-xs">{doc.label}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="text-green-600 text-sm font-semibold">{(doc.similarity_score * 100).toFixed(1)}%</span>
                            <span className="text-gray-400">
                              {expandedDocId === doc.case_id ? '▲' : '▼'}
                            </span>
                          </div>
                        </div>
                        {expandedDocId === doc.case_id && doc.text && (
                          <div className="p-4 bg-white border-t border-gray-200 max-h-96 overflow-y-auto">
                            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                              {doc.text}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <h1 className="text-4xl font-bold text-gray-800">📊 Analytics Dashboard</h1>
            
            {stats ? (
              <>
                <div className="grid grid-cols-4 gap-6">
                  {[
                    { label: 'Total Documents', value: stats.total_documents.toLocaleString(), color: 'purple' },
                    { label: 'Embedding Dim', value: stats.embedding_dim, color: 'blue' },
                    { label: 'Avg Length', value: `${stats.avg_length.toLocaleString()} chars`, color: 'green' },
                    { label: 'Max Length', value: `${stats.max_length.toLocaleString()} chars`, color: 'pink' },
                  ].map((stat, idx) => (
                    <div key={idx} className="bg-white rounded-2xl p-6 shadow-lg">
                      <div className={`text-3xl font-bold text-${stat.color}-600`}>{stat.value}</div>
                      <div className="text-gray-600">{stat.label}</div>
                    </div>
                  ))}
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-lg">
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">Document Type Distribution</h2>
                  <div className="space-y-4">
                    {Object.entries(stats.labels).map(([label, count]: [string, any]) => {
                      const percentage = (count / stats.total_documents) * 100;
                      return (
                        <div key={label}>
                          <div className="flex justify-between mb-2">
                            <span className="font-semibold text-gray-700">{label}</span>
                            <span className="text-gray-600">{count} ({percentage.toFixed(1)}%)</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-3">
                            <div
                              className="bg-gradient-to-r from-purple-600 to-blue-600 h-3 rounded-full transition-all duration-500"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-6">
                  {[
                    { label: 'Retrieval Speed', value: '<100ms', color: 'green' },
                    { label: 'Summarization', value: '30-60s', color: 'blue' },
                    { label: 'Q&A Response', value: '<2s', color: 'purple' },
                  ].map((perf, idx) => (
                    <div key={idx} className="bg-white rounded-2xl p-6 shadow-lg text-center">
                      <div className={`text-4xl font-bold text-${perf.color}-600 mb-2`}>{perf.value}</div>
                      <div className="text-gray-600">{perf.label}</div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <svg className="animate-spin h-16 w-16 text-purple-600 mx-auto mb-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  <p className="text-gray-600">Loading analytics...</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
