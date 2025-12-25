import { useState, useEffect, useRef } from 'react';
import { AlertCircle, Activity, Map, Brain, Users, CheckCircle, Mic, Camera, LogOut, Bell, Send, MapPin } from 'lucide-react';
import { auth, signInWithGooglePopup, signOutUser } from './firebase';
import { onAuthStateChanged } from 'firebase/auth';

const API_BASE = 'http://localhost:8000';

// Allowed emails for Health Official role
const OFFICIAL_WHITELIST = new Set([
  'soham.pethkar1710@gmail.com',
  'dcharshvardhanpondkule@gmail.com',
]);

const api = {
  async get(endpoint) {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  },
  async post(endpoint, data) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  },
  async postForm(endpoint, formData) {
    const res = await fetch(`${API_BASE}${endpoint}`, { method: 'POST', body: formData });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  }
};

const SanketApp = () => {
  const [currentUser, setCurrentUser] = useState(null);
  const [showLogin, setShowLogin] = useState(true);

  // Final client-side guard: if someone reaches an Official state without authorization,
  // force sign-out and redirect to login page.
  useEffect(() => {
    const enforceOfficialGuard = async () => {
      if (currentUser?.role === 'official') {
        const email = (currentUser.email || '').toLowerCase();
        if (!OFFICIAL_WHITELIST.has(email)) {
          try { await signOutUser(); } catch (_) {}
          localStorage.removeItem('sanket_user');
          setCurrentUser(null);
          setShowLogin(true);
          try { window.location.replace('/'); } catch (_) {}
          setTimeout(() => { try { window.location.reload(); } catch (_) {} }, 50);
        }
      }
    };
    enforceOfficialGuard();
  }, [currentUser]);

  useEffect(() => {
    const savedUser = localStorage.getItem('sanket_user');
    if (savedUser) { setCurrentUser(JSON.parse(savedUser)); setShowLogin(false); }

    // Sync with Firebase Auth state
    const unsub = onAuthStateChanged(auth, async (fbUser) => {
      if (fbUser) {
        // Only auto-login if an app session exists; otherwise keep login page
        const storedRaw = localStorage.getItem('sanket_user');
        if (!storedRaw) {
          setShowLogin(true);
          return;
        }
        const stored = JSON.parse(storedRaw || '{}');
        const requestedOfficial = stored.role === 'official';
        const email = (fbUser.email || '').toLowerCase();
        if (requestedOfficial && !OFFICIAL_WHITELIST.has(email)) {
          try { await signOutUser(); } catch (_) {}
          localStorage.removeItem('sanket_user');
          // Set a one-shot warning flag for the login page to read
          try { localStorage.setItem('unauthorized_official', '1'); } catch (_) {}
          setCurrentUser(null);
          setShowLogin(true);
          // Also show an immediate alert for current view
          alert('This email is not authorized as Health Official. Please sign in with an approved account.');
          // Hard-redirect to login page (root) to ensure full reset
          try { window.location.replace('/'); } catch (_) {}
          // Fallback in case replace is blocked by environment
          setTimeout(() => { try { window.location.reload(); } catch (_) {} }, 50);
          return;
        }
        const desiredRole = requestedOfficial ? 'official' : 'asha';
        const mapped = {
          id: fbUser.uid,
          name: fbUser.displayName || fbUser.email || 'User',
          email: fbUser.email || '',
          role: desiredRole,
        };
        setCurrentUser(mapped);
        localStorage.setItem('sanket_user', JSON.stringify(mapped));
        setShowLogin(false);
      }
    });
    return () => unsub();
  }, []);

  const handleLogin = (user) => { setCurrentUser(user); localStorage.setItem('sanket_user', JSON.stringify(user)); setShowLogin(false); };
  const handleLogout = async () => { try { await signOutUser(); } catch (_) {} setCurrentUser(null); localStorage.removeItem('sanket_user'); setShowLogin(true); };

  if (showLogin) return <LoginPage onLogin={handleLogin} />;
  if (currentUser?.role === 'official') {
    // Final guard to prevent unauthorized official access
    if (!OFFICIAL_WHITELIST.has((currentUser.email || '').toLowerCase())) {
      return <ASHAInterface user={{ ...currentUser, role: 'asha' }} onLogout={handleLogout} />;
    }
    return <OfficialDashboard user={currentUser} onLogout={handleLogout} />;
  }
  if (currentUser?.role === 'asha') return <ASHAInterface user={currentUser} onLogout={handleLogout} />;
  return <LoginPage onLogin={handleLogin} />;
};

const LoginPage = ({ onLogin }) => {
  const [isSignup, setIsSignup] = useState(false);
  const [role, setRole] = useState('asha');
  const [formData, setFormData] = useState({ name: '', email: '', password: '', village: '', phone: '' });
  const [warnUnauthorizedOfficial, setWarnUnauthorizedOfficial] = useState(false);

  useEffect(() => {
    try {
      if (localStorage.getItem('unauthorized_official') === '1') {
        setWarnUnauthorizedOfficial(true);
        localStorage.removeItem('unauthorized_official');
      }
    } catch (_) {}
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const emailLower = (formData.email || '').toLowerCase();
    if (role === 'official' && !OFFICIAL_WHITELIST.has(emailLower)) {
      try { localStorage.setItem('unauthorized_official', '1'); } catch (_) {}
      setWarnUnauthorizedOfficial(true);
      alert('This email is not authorized as Health Official. Please sign in with an approved account.');
      return; // stay on login page
    }
    onLogin({ id: Math.random().toString(36).substring(2, 11), name: formData.name, email: formData.email, role, village: formData.village, phone: formData.phone });
  };

  const demoLogin = (demoRole) => {
    const demoUsers = {
      asha: { id: 'asha_001', name: 'Priya Sharma', email: 'priya@asha.gov.in', role: 'asha', village: 'Dharavi', phone: '+91 98765 43210' },
      asha_kalyan: { id: 'asha_002', name: 'Sunita Patil', email: 'sunita@asha.gov.in', role: 'asha', village: 'Kalyan', phone: '+91 98765 43211' },
      asha_thane: { id: 'asha_003', name: 'Meera Desai', email: 'meera@asha.gov.in', role: 'asha', village: 'Thane', phone: '+91 98765 43212' },
      asha_navi: { id: 'asha_004', name: 'Rekha Singh', email: 'rekha@asha.gov.in', role: 'asha', village: 'Navi Mumbai', phone: '+91 98765 43213' },
      official: { id: 'official_001', name: 'Dr. Rajesh Kumar', email: 'rajesh@health.gov.in', role: 'official', district: 'Mumbai', designation: 'District Health Officer' }
    };
    onLogin(demoUsers[demoRole]);
  };

  const loginWithGoogle = async () => {
    try {
      const cred = await signInWithGooglePopup();
      const fbUser = cred.user;
      const emailLower = (fbUser.email || '').toLowerCase();
      if (role === 'official' && !OFFICIAL_WHITELIST.has(emailLower)) {
        try { await signOutUser(); } catch (_) {}
        try { localStorage.setItem('unauthorized_official', '1'); } catch (_) {}
        alert('This email is not authorized as Health Official. Please sign in with an approved account.');
        try { window.location.replace('/'); } catch (_) {}
        setTimeout(() => { try { window.location.reload(); } catch (_) {} }, 50);
        return; // redirect to login page
      }
      onLogin({
        id: fbUser.uid,
        name: fbUser.displayName || 'User',
        email: fbUser.email || '',
        role,
        village: formData.village,
        phone: formData.phone,
      });
    } catch (e) {
      alert('Google Sign-In failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-full mx-auto flex items-center justify-center mb-4">
            <Activity className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Sanket</h1>
          <p className="text-gray-600 mt-2">Quantum-Enhanced Epidemiology Network</p>
        </div>
        {warnUnauthorizedOfficial && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">
            This email is not authorized as Health Official. Please sign in with an approved account or continue as ASHA.
          </div>
        )}
        <div className="flex gap-2 mb-6">
          <button onClick={() => setRole('asha')} className={`flex-1 py-3 rounded-lg font-medium transition-all ${role === 'asha' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600'}`}>ASHA Worker</button>
          <button onClick={() => setRole('official')} className={`flex-1 py-3 rounded-lg font-medium transition-all ${role === 'official' ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-600'}`}>Health Official</button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {isSignup && <input type="text" placeholder="Full Name" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} className="w-full px-4 py-3 border border-gray-300 rounded-lg" required />}
          <input type="email" placeholder="Email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} className="w-full px-4 py-3 border border-gray-300 rounded-lg" required />
          <input type="password" placeholder="Password" value={formData.password} onChange={(e) => setFormData({...formData, password: e.target.value})} className="w-full px-4 py-3 border border-gray-300 rounded-lg" required />
          {isSignup && role === 'asha' && (<>
            <input type="text" placeholder="Village Name" value={formData.village} onChange={(e) => setFormData({...formData, village: e.target.value})} className="w-full px-4 py-3 border border-gray-300 rounded-lg" required />
            <input type="tel" placeholder="Phone Number" value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} className="w-full px-4 py-3 border border-gray-300 rounded-lg" required />
          </>)}
          <button type="submit" className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium">{isSignup ? 'Sign Up' : 'Login'}</button>
        </form>
        <div className="mt-4">
          <button onClick={loginWithGoogle} className="w-full py-3 bg-white border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50">
            Continue with Google
          </button>
        </div>
        <div className="mt-4 text-center"><button onClick={() => setIsSignup(!isSignup)} className="text-indigo-600 hover:underline">{isSignup ? 'Already have an account? Login' : "Don't have an account? Sign Up"}</button></div>
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-600 text-center mb-3">Quick Demo Access</p>
          <div className="space-y-2">
            <div className="flex gap-2">
              <button onClick={() => demoLogin('asha')} className="flex-1 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium">Dharavi ASHA</button>
              <button onClick={() => demoLogin('asha_kalyan')} className="flex-1 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium">Kalyan ASHA</button>
            </div>
            <div className="flex gap-2">
              <button onClick={() => demoLogin('asha_thane')} className="flex-1 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium">Thane ASHA</button>
              <button onClick={() => demoLogin('asha_navi')} className="flex-1 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium">Navi Mumbai ASHA</button>
            </div>
            <button onClick={() => demoLogin('official')} className="w-full py-2 bg-purple-100 text-purple-700 rounded-lg text-sm font-medium">Health Official</button>
          </div>
        </div>
      </div>
    </div>
  );
};

const ASHAInterface = ({ user, onLogout }) => {
  const [view, setView] = useState('report');
  const [recording, setRecording] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [reportData, setReportData] = useState({ symptoms: [], voice: null, image: null, notes: '' });
  const [submitting, setSubmitting] = useState(false);
  const [recentReports, setRecentReports] = useState([]);
  const [apiStatus, setApiStatus] = useState({ connected: false, message: 'Checking...' });
  const fileInputRef = useRef(null);
  const symptomOptions = ['Fever', 'Headache', 'Body Pain', 'Vomiting', 'Diarrhea', 'Rash', 'Cough', 'Breathing Difficulty', 'Fatigue', 'Nausea'];

  useEffect(() => {
    api.get('/health').then(() => setApiStatus({ connected: true, message: 'Connected to Backend' })).catch(() => setApiStatus({ connected: false, message: 'Backend offline' }));
  }, []);

  const toggleSymptom = (s) => setReportData(d => ({ ...d, symptoms: d.symptoms.includes(s) ? d.symptoms.filter(x => x !== s) : [...d.symptoms, s] }));
  const handleImageUpload = (e) => { const f = e.target.files[0]; if (f) { const r = new FileReader(); r.onloadend = () => { setImagePreview(r.result); setReportData(d => ({...d, image: f})); }; r.readAsDataURL(f); }};
  const startRecording = () => { setRecording(true); setTimeout(() => { setRecording(false); setReportData(d => ({...d, voice: new Blob(['audio'], { type: 'audio/wav' })})); }, 3000); };

  const submitReport = async () => {
    if (reportData.symptoms.length === 0) { alert('Please select at least one symptom'); return; }
    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('village_id', user.village || 'Dharavi');
      reportData.symptoms.forEach(s => formData.append('symptoms', s));
      if (reportData.voice) formData.append('voice', reportData.voice, 'voice.wav');
      if (reportData.image) formData.append('image', reportData.image);
      const result = await api.postForm('/api/v1/edge/submit-report?village_id=' + (user.village || 'Dharavi') + '&symptoms=' + reportData.symptoms.join('&symptoms='), formData);
      const newReport = { id: Date.now(), symptoms: reportData.symptoms, hasVoice: !!reportData.voice, hasImage: !!reportData.image, notes: reportData.notes, timestamp: new Date().toLocaleString(), status: 'Processed', apiResponse: result };
      setRecentReports(r => [newReport, ...r]);
      setReportData({ symptoms: [], voice: null, image: null, notes: '' }); setImagePreview(null);
      alert('Report submitted! AI agents are analyzing the data.');
    } catch (err) {
      console.error('Submit error:', err);
      const newReport = { id: Date.now(), symptoms: reportData.symptoms, hasVoice: !!reportData.voice, hasImage: !!reportData.image, notes: reportData.notes, timestamp: new Date().toLocaleString(), status: 'Queued (offline)' };
      setRecentReports(r => [newReport, ...r]);
      setReportData({ symptoms: [], voice: null, image: null, notes: '' }); setImagePreview(null);
      alert('Backend offline. Report saved locally.');
    }
    setSubmitting(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div><h1 className="text-xl font-bold">Sanket ASHA</h1><p className="text-sm text-indigo-100">{user.name} - {user.village}</p></div>
          <div className="flex items-center gap-2">
            <span className={`px-2 py-1 rounded text-xs ${apiStatus.connected ? 'bg-green-500' : 'bg-red-500'}`}>{apiStatus.message}</span>
            <button onClick={onLogout} className="p-2 hover:bg-white/20 rounded-lg"><LogOut className="w-5 h-5" /></button>
          </div>
        </div>
      </div>
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 flex gap-1">
          <button onClick={() => setView('report')} className={`px-4 py-3 font-medium ${view === 'report' ? 'text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-600'}`}>New Report</button>
          <button onClick={() => setView('history')} className={`px-4 py-3 font-medium ${view === 'history' ? 'text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-600'}`}>History</button>
        </div>
      </div>
      <div className="max-w-4xl mx-auto px-4 py-6">
        {view === 'report' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Symptoms</h2>
              <div className="grid grid-cols-2 gap-3">
                {symptomOptions.map(s => (<button key={s} onClick={() => toggleSymptom(s)} className={`p-3 rounded-lg text-left font-medium ${reportData.symptoms.includes(s) ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700'}`}>{s}</button>))}
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Voice Recording (Optional)</h2>
              <button onClick={startRecording} disabled={recording} className={`w-full py-4 rounded-lg font-medium flex items-center justify-center gap-2 ${recording ? 'bg-red-500 text-white' : reportData.voice ? 'bg-green-500 text-white' : 'bg-indigo-600 text-white'}`}>
                <Mic className="w-5 h-5" />{recording ? 'Recording...' : reportData.voice ? 'Voice Recorded ✓' : 'Start Recording'}
              </button>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Photo (Optional)</h2>
              <input type="file" ref={fileInputRef} onChange={handleImageUpload} accept="image/*" className="hidden" />
              {imagePreview ? (<div className="space-y-3"><img src={imagePreview} alt="Preview" className="w-full h-48 object-cover rounded-lg" /><button onClick={() => fileInputRef.current?.click()} className="w-full py-3 bg-gray-100 text-gray-700 rounded-lg">Change Photo</button></div>)
                : (<button onClick={() => fileInputRef.current?.click()} className="w-full py-4 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center gap-2 text-gray-600"><Camera className="w-5 h-5" />Take or Upload Photo</button>)}
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Additional Notes</h2>
              <textarea value={reportData.notes} onChange={(e) => setReportData(d => ({...d, notes: e.target.value}))} placeholder="Any additional information..." className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none" rows="4" />
            </div>
            <button onClick={submitReport} disabled={submitting || reportData.symptoms.length === 0} className="w-full py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold text-lg disabled:opacity-50 flex items-center justify-center gap-2">
              {submitting ? 'Processing...' : <><Send className="w-5 h-5" />Submit Report</>}
            </button>
          </div>
        )}
        {view === 'history' && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-900">Recent Reports</h2>
            {recentReports.length === 0 ? (<div className="bg-white rounded-xl shadow-sm p-12 text-center"><AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" /><p className="text-gray-600">No reports yet.</p></div>)
              : recentReports.map(r => (<div key={r.id} className="bg-white rounded-xl shadow-sm p-6"><div className="flex items-start justify-between mb-3"><div><p className="font-semibold text-gray-900">Report #{r.id}</p><p className="text-sm text-gray-500">{r.timestamp}</p></div><span className={`px-3 py-1 rounded-full text-sm font-medium ${r.status === 'Processed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>{r.status}</span></div><div className="flex flex-wrap gap-2 mb-3">{r.symptoms.map(s => (<span key={s} className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm">{s}</span>))}</div><div className="flex gap-4 text-sm text-gray-600">{r.hasVoice && <span>🎤 Voice</span>}{r.hasImage && <span>📷 Image</span>}</div></div>))}
          </div>
        )}
      </div>
    </div>
  );
};

// Agent Communications Component
const AgentCommunications = () => {
  const [comms, setComms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchComms = async () => {
      try {
        const data = await api.get('/api/v1/swarm/communications?limit=50');
        setComms(data.communications || []);
      } catch (err) {
        console.error('Failed to fetch communications:', err);
      }
      setLoading(false);
    };
    fetchComms();
    const interval = setInterval(fetchComms, 5000);
    return () => clearInterval(interval);
  }, []);

  const getTypeColor = (type) => {
    const colors = {
      'symptom_report': 'bg-blue-100 text-blue-800',
      'status_query': 'bg-yellow-100 text-yellow-800',
      'status_response': 'bg-green-100 text-green-800',
      'consensus_proposal': 'bg-purple-100 text-purple-800',
      'vote': 'bg-indigo-100 text-indigo-800',
      'quantum_escalation': 'bg-red-100 text-red-800',
      'quantum_trigger': 'bg-red-100 text-red-800',
      'quantum_result': 'bg-pink-100 text-pink-800',
      'workflow_trigger': 'bg-orange-100 text-orange-800',
      'belief_share': 'bg-cyan-100 text-cyan-800',
      'collective_decision': 'bg-emerald-100 text-emerald-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="text-center py-8">Loading communications...</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Agent Communications Log</h2>
        <span className="text-sm text-gray-500">{comms.length} messages</span>
      </div>
      <p className="text-sm text-gray-600">Real-time inter-agent communication showing how swarm intelligence emerges from simple message passing.</p>
      <div className="bg-white rounded-xl shadow-sm divide-y max-h-96 overflow-y-auto">
        {comms.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No communications yet. Submit symptom reports to see agent interactions.</div>
        ) : (
          comms.slice().reverse().map((msg, idx) => (
            <div key={idx} className="p-4 hover:bg-gray-50">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-semibold text-gray-900">{msg.from}</span>
                <span className="text-gray-400">→</span>
                <span className="font-semibold text-gray-900">{msg.to}</span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getTypeColor(msg.type)}`}>{msg.type.replace(/_/g, ' ')}</span>
              </div>
              <div className="text-sm text-gray-600 bg-gray-50 rounded p-2">
                {JSON.stringify(msg.content, null, 0).slice(0, 150)}
              </div>
              <div className="text-xs text-gray-400 mt-1">{new Date(msg.timestamp).toLocaleTimeString()}</div>
            </div>
          ))
        )}
      </div>
      <div className="bg-indigo-50 rounded-lg p-4">
        <h3 className="font-semibold text-indigo-900 mb-2">How Swarm Intelligence Works</h3>
        <ul className="text-sm text-indigo-800 space-y-1">
          <li>• Agents communicate via simple messages (no LLM)</li>
          <li>• Each agent updates beliefs based on local data + neighbor info</li>
          <li>• Consensus emerges from collective voting</li>
          <li>• Quantum analysis triggered only when consensus reached</li>
        </ul>
      </div>
    </div>
  );
};

const OfficialDashboard = ({ user, onLogout }) => {
  const [activeView, setActiveView] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [apiConnected, setApiConnected] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [swarmData, setSwarmData] = useState({});
  const [quantumInsights, setQuantumInsights] = useState({ outbreakProbability: 0, hiddenCorrelations: 0, resourceOptimization: 'Pending', affectedVillages: [] });
  const [dashboardStats, setDashboardStats] = useState({ active_villages: 0, total_reports: 0, high_risk_villages: 0, average_outbreak_belief: 0 });

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [health, agents, quantum, dashboard] = await Promise.all([
          api.get('/health'), api.get('/api/v1/swarm/agents'), api.get('/api/v1/quantum/insights'), api.get('/api/v1/analytics/dashboard')
        ]);
        setApiConnected(true);
        if (agents.agents) {
          setSwarmData(agents.agents);
          const alertsFromAgents = Object.entries(agents.agents).filter(([_, a]) => a.risk_level === 'high' || a.risk_level === 'critical').map(([id, a], i) => ({
            id: i + 1, severity: a.risk_level === 'critical' ? 'high' : 'medium', village: a.name, symptom: `${a.symptom_count} symptoms reported`, confidence: a.outbreak_belief, quantum: a.outbreak_belief > 0.7, status: 'pending'
          }));
          setAlerts(alertsFromAgents);
        }
        if (quantum) setQuantumInsights({ outbreakProbability: quantum.outbreak_probability || 0, hiddenCorrelations: quantum.hidden_correlations?.length || 0, resourceOptimization: 'Computed', affectedVillages: quantum.high_risk_villages || [] });
        if (dashboard) setDashboardStats(dashboard);
      } catch (err) {
        console.error('API Error:', err);
        setApiConnected(false);
        setSwarmData({ dharavi: { name: 'Dharavi', risk_level: 'high', outbreak_belief: 0.82, symptom_count: 8 }, kalyan: { name: 'Kalyan', risk_level: 'medium', outbreak_belief: 0.65, symptom_count: 5 }, thane: { name: 'Thane', risk_level: 'low', outbreak_belief: 0.42, symptom_count: 2 }, navi_mumbai: { name: 'Navi Mumbai', risk_level: 'normal', outbreak_belief: 0.15, symptom_count: 0 }});
        setAlerts([{ id: 1, severity: 'high', village: 'Dharavi', symptom: 'Fever cluster (8 cases)', confidence: 0.87, quantum: true, status: 'pending' }]);
      }
      setLoading(false);
    };
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const approveAlert = async (alertId) => {
    setAlerts(a => a.map(x => x.id === alertId ? {...x, status: 'approved'} : x));
    alert('Resources dispatched! Medical team notified.');
  };

  const triggerQuantumAnalysis = async () => {
    try {
      const result = await api.post('/api/v1/quantum/analyze', {});
      setQuantumInsights({ outbreakProbability: result.pattern_detection?.outbreak_probability || 0, hiddenCorrelations: result.pattern_detection?.hidden_correlations?.length || 0, resourceOptimization: 'Computed', affectedVillages: result.pattern_detection?.high_risk_villages || [] });
      alert('Quantum analysis complete!');
    } catch (err) { alert('Quantum analysis failed: ' + err.message); }
  };

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><div className="text-center"><Activity className="w-12 h-12 text-indigo-600 animate-spin mx-auto mb-4" /><p className="text-gray-600">Loading dashboard...</p></div></div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center"><Activity className="w-6 h-6 text-white" /></div>
            <div><h1 className="text-xl font-bold text-gray-900">Sanket Command Center</h1><p className="text-sm text-gray-600">{user.name} - {user.designation}</p></div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${apiConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>{apiConnected ? '🟢 Live' : '🔴 Offline'}</span>
            <button className="relative p-2 hover:bg-gray-100 rounded-lg"><Bell className="w-5 h-5 text-gray-600" />{alerts.filter(a => a.status === 'pending').length > 0 && <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>}</button>
            <button onClick={onLogout} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg flex items-center gap-2"><LogOut className="w-4 h-4" />Logout</button>
          </div>
        </div>
      </header>
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 flex gap-1">
          {['overview', 'alerts', 'swarm', 'comms', 'quantum', 'map'].map(v => (<button key={v} onClick={() => setActiveView(v)} className={`px-4 py-3 font-medium capitalize ${activeView === v ? 'text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-600'}`}>{v === 'comms' ? 'Agent Comms' : v}</button>))}
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 py-6">

        {activeView === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-indigo-600"><div className="flex items-center justify-between"><div><p className="text-sm text-gray-600">Active Villages</p><p className="text-3xl font-bold text-gray-900">{dashboardStats.active_villages || Object.keys(swarmData).length}</p></div><MapPin className="w-8 h-8 text-indigo-600" /></div></div>
              <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-red-600"><div className="flex items-center justify-between"><div><p className="text-sm text-gray-600">Active Alerts</p><p className="text-3xl font-bold text-gray-900">{alerts.filter(a => a.status === 'pending').length}</p></div><AlertCircle className="w-8 h-8 text-red-600" /></div></div>
              <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-purple-600"><div className="flex items-center justify-between"><div><p className="text-sm text-gray-600">Outbreak Risk</p><p className="text-3xl font-bold text-gray-900">{(quantumInsights.outbreakProbability * 100).toFixed(0)}%</p></div><Brain className="w-8 h-8 text-purple-600" /></div></div>
              <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-green-600"><div className="flex items-center justify-between"><div><p className="text-sm text-gray-600">Total Reports</p><p className="text-3xl font-bold text-gray-900">{dashboardStats.total_reports || Object.values(swarmData).reduce((s, v) => s + (v.symptom_count || 0), 0)}</p></div><Users className="w-8 h-8 text-green-600" /></div></div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Alerts - Action Required</h2>
              {alerts.filter(a => a.status === 'pending').length === 0 ? <p className="text-gray-500">No pending alerts</p> : alerts.filter(a => a.status === 'pending').map(alert => (
                <div key={alert.id} className={`p-4 rounded-lg border-l-4 mb-3 ${alert.severity === 'high' ? 'bg-red-50 border-red-600' : alert.severity === 'medium' ? 'bg-yellow-50 border-yellow-600' : 'bg-blue-50 border-blue-600'}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1"><div className="flex items-center gap-2 mb-2"><span className="font-semibold text-gray-900">{alert.village}</span>{alert.quantum && <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs font-medium">QUANTUM</span>}</div><p className="text-gray-700">{alert.symptom}</p><p className="text-sm text-gray-600 mt-1">Confidence: {(alert.confidence * 100).toFixed(0)}%</p></div>
                    <button onClick={() => approveAlert(alert.id)} className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700">Approve & Dispatch</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeView === 'alerts' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between"><h2 className="text-xl font-bold text-gray-900">All Alerts</h2><button className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm">Export Report</button></div>
            {alerts.map(alert => (
              <div key={alert.id} className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${alert.severity === 'high' ? 'bg-red-100 text-red-800' : alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'}`}>{alert.severity.toUpperCase()}</span>
                      {alert.quantum && <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">QUANTUM</span>}
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${alert.status === 'pending' ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}`}>{alert.status.toUpperCase()}</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{alert.village}</h3>
                    <p className="text-gray-700 mb-2">{alert.symptom}</p>
                    <p className="text-sm text-gray-600">Confidence: {(alert.confidence * 100).toFixed(0)}%</p>
                  </div>
                  {alert.status === 'pending' && <button onClick={() => approveAlert(alert.id)} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Approve</button>}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeView === 'swarm' && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-900">Village Swarm Network (Live from API)</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(swarmData).map(([id, village]) => (
                <div key={id} className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div><h3 className="text-lg font-semibold text-gray-900">{village.name}</h3><p className="text-sm text-gray-600">Agent ID: {id}</p></div>
                    <span className={`w-3 h-3 rounded-full ${village.risk_level !== 'normal' ? 'bg-green-500' : 'bg-gray-300'}`}></span>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between"><span className="text-sm text-gray-600">Risk Level</span><span className={`px-3 py-1 rounded-full text-xs font-medium ${village.risk_level === 'high' || village.risk_level === 'critical' ? 'bg-red-100 text-red-800' : village.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>{(village.risk_level || 'normal').toUpperCase()}</span></div>
                    <div className="flex items-center justify-between"><span className="text-sm text-gray-600">Outbreak Belief</span><span className="text-sm font-semibold text-gray-900">{((village.outbreak_belief || 0) * 100).toFixed(0)}%</span></div>
                    <div className="w-full bg-gray-200 rounded-full h-2"><div className="bg-gradient-to-r from-indigo-600 to-purple-600 h-2 rounded-full" style={{ width: `${(village.outbreak_belief || 0) * 100}%` }} /></div>
                    <div className="flex items-center justify-between pt-2 border-t border-gray-200"><span className="text-sm text-gray-600">Symptoms Reported</span><span className="text-lg font-bold text-gray-900">{village.symptom_count || 0}</span></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeView === 'comms' && (
          <AgentCommunications />
        )}

        {activeView === 'quantum' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3"><Brain className="w-10 h-10" /><div><h2 className="text-2xl font-bold">Quantum Intelligence Layer</h2><p className="text-purple-100">TensorFlow Quantum / Cirq Analysis</p></div></div>
                <button onClick={triggerQuantumAnalysis} className="px-4 py-2 bg-white text-purple-600 rounded-lg font-medium hover:bg-purple-50">Run Analysis</button>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-xl shadow-sm p-6"><h3 className="text-sm font-medium text-gray-600 mb-2">Outbreak Probability</h3><div className="flex items-end gap-2"><p className="text-4xl font-bold text-gray-900">{(quantumInsights.outbreakProbability * 100).toFixed(1)}%</p><p className="text-sm text-gray-500 mb-1">confidence</p></div><div className="mt-4 w-full bg-gray-200 rounded-full h-3"><div className="bg-gradient-to-r from-purple-600 to-indigo-600 h-3 rounded-full" style={{ width: `${quantumInsights.outbreakProbability * 100}%` }} /></div></div>
              <div className="bg-white rounded-xl shadow-sm p-6"><h3 className="text-sm font-medium text-gray-600 mb-2">Hidden Correlations</h3><div className="flex items-end gap-2"><p className="text-4xl font-bold text-gray-900">{quantumInsights.hiddenCorrelations}</p><p className="text-sm text-gray-500 mb-1">detected</p></div><p className="mt-4 text-sm text-gray-600">Non-obvious transmission pathways via quantum analysis</p></div>
              <div className="bg-white rounded-xl shadow-sm p-6"><h3 className="text-sm font-medium text-gray-600 mb-2">Resource Optimization</h3><div className="flex items-center gap-2 mb-2"><CheckCircle className="w-6 h-6 text-green-600" /><p className="text-xl font-bold text-gray-900">{quantumInsights.resourceOptimization}</p></div><p className="mt-4 text-sm text-gray-600">QAOA algorithm optimized distribution</p></div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Affected Villages & Recommendations</h3>
              <div className="space-y-3">
                {(quantumInsights.affectedVillages.length > 0 ? quantumInsights.affectedVillages : ['Dharavi', 'Kalyan', 'Thane']).map((village, idx) => (
                  <div key={village} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"><div><p className="font-semibold text-gray-900">{village}</p><p className="text-sm text-gray-600">Priority: {idx === 0 ? 'High' : idx === 1 ? 'Medium' : 'Low'}</p></div><div className="text-right"><p className="text-sm text-gray-600">ORS Packets: {80 - (idx * 20)}</p><p className="text-sm text-gray-600">Medical Staff: {5 - idx}</p></div></div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeView === 'map' && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Village Risk Map</h2>
            <div className="h-96 bg-gradient-to-br from-blue-100 to-green-100 rounded-lg flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 p-8">
                {Object.entries(swarmData).map(([id, village], idx) => {
                  const positions = [{ top: '25%', left: '33%' }, { top: '66%', left: '50%' }, { top: '50%', right: '25%' }, { top: '33%', right: '40%' }];
                  const pos = positions[idx % 4];
                  const riskColor = village.risk_level === 'high' || village.risk_level === 'critical' ? 'red' : village.risk_level === 'medium' ? 'yellow' : 'green';
                  return (
                    <div key={id} className="absolute" style={pos}>
                      <div className="relative">
                        <div className={`w-12 h-12 bg-${riskColor}-500 rounded-full opacity-50 animate-pulse`}></div>
                        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                          <div className={`w-6 h-6 bg-${riskColor}-600 rounded-full flex items-center justify-center text-white text-xs font-bold`}>{village.name?.[0]}</div>
                        </div>
                      </div>
                      <p className="text-xs font-semibold mt-2 text-center">{village.name}</p>
                      <p className={`text-xs text-${riskColor}-600 text-center`}>{(village.risk_level || 'Normal').charAt(0).toUpperCase() + (village.risk_level || 'normal').slice(1)} Risk</p>
                    </div>
                  );
                })}
              </div>
              <div className="text-center z-10"><Map className="w-16 h-16 text-gray-400 mx-auto mb-2" /><p className="text-gray-600">Interactive Map View</p><p className="text-sm text-gray-500">Real-time village risk visualization</p></div>
            </div>
            <div className="mt-4 flex items-center justify-center gap-6">
              <div className="flex items-center gap-2"><div className="w-4 h-4 bg-red-500 rounded-full"></div><span className="text-sm text-gray-600">High Risk</span></div>
              <div className="flex items-center gap-2"><div className="w-4 h-4 bg-yellow-500 rounded-full"></div><span className="text-sm text-gray-600">Medium Risk</span></div>
              <div className="flex items-center gap-2"><div className="w-4 h-4 bg-green-500 rounded-full"></div><span className="text-sm text-gray-600">Low Risk</span></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SanketApp;
