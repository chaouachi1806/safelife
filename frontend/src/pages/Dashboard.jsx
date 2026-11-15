import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api/axios';
import { getCurrentUser, logoutUser } from '../api/authService';
import { Activity, LogOut, AlertTriangle, CheckCircle, HeartPulse, Thermometer, Radio } from 'lucide-react';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [patientId, setPatientId] = useState('1');
  const [alertes, setAlertes] = useState([]);
  const [loadingAlertes, setLoadingAlertes] = useState(false);

  // Formulaire pour simuler l'envoi des données vitale
  const [bpm, setBpm] = useState(80);
  const [spo2, setSpo2] = useState(98);
  const [temp, setTemp] = useState(37.0);
  const [piezo, setPiezo] = useState(1.2);
  const [gsr, setGsr] = useState(0.5);
  const [acc, setAcc] = useState(0.1);
  const [message, setMessage] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    // 1. Récupérer l'utilisateur connecté
    getCurrentUser()
      .then((data) => setUser(data))
      .catch(() => {
        logoutUser();
        navigate('/login');
      });

    // 2. Charger les alertes
    fetchAlertes();
  }, [patientId]);

  const fetchAlertes = async () => {
    setLoadingAlertes(true);
    try {
      const res = await API.get(`/alertes/patient/${patientId}/actives`);
      setAlertes(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingAlertes(false);
    }
  };

  const handleSendDonnees = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const payload = {
        patient_id: parseInt(patientId),
        bpm: parseFloat(bpm),
        spo2: parseFloat(spo2),
        temperature: parseFloat(temp),
        piezo: parseFloat(piezo),
        gsr: parseFloat(gsr),
        acceleration: parseFloat(acc)
      };

      const res = await API.post('/donnees/', payload);

      // Calcul direct mta' al-risque fi al-Frontend
      const bpmNum = parseFloat(bpm);
      const spo2Num = parseFloat(spo2);
      const tempNum = parseFloat(temp);

      const isCrise = bpmNum > 100 || bpmNum < 50 || spo2Num < 92 || tempNum > 38.5 || res.data?.prediction_crise;

      setMessage(`Données envoyées avec succès! Risque calculé: ${isCrise ? '⚠️ CRISE DÉTECTÉE' : '✅ Normal'}`);
      
      fetchAlertes(); // Rafraîchir les alertes fil bloc al-yemna
    } catch (err) {
      console.error(err);
      setMessage('Erreur lors de l’envoi des données.');
    }
  };

  const handleResoudre = async (alerteId) => {
    try {
      await API.put(`/alertes/${alerteId}/resoudre`);
      fetchAlertes();
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = () => {
    logoutUser();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6">
      {/* Header */}
      <header className="flex justify-between items-center border-b border-slate-800 pb-4 mb-8">
        <div className="flex items-center gap-3">
          <Activity className="w-8 h-8 text-red-500 animate-pulse" />
          <h1 className="text-2xl font-bold">SafeLife <span className="text-sm font-normal text-slate-400">| Dashboard</span></h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-300">Bienvenue, <strong className="text-white">{user?.email || 'Utilisateur'}</strong></span>
          <button onClick={handleLogout} className="bg-slate-800 hover:bg-slate-700 text-slate-300 p-2 rounded-lg flex items-center gap-2 border border-slate-700">
            <LogOut className="w-4 h-4" /> Déconnexion
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Module 1: Envoi / Simulation des Capteurs */}
        <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl shadow-lg">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-red-400">
            <HeartPulse className="w-5 h-5" /> Ingestion des Données Capteurs
          </h2>
          {message && <div className="p-3 mb-4 rounded bg-slate-700 text-sm font-medium border border-slate-600">{message}</div>}
          <form onSubmit={handleSendDonnees} className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-400">ID Patient</label>
              <input type="number" value={patientId} onChange={(e) => setPatientId(e.target.value)} className="w-full bg-slate-900 border border-slate-700 p-2 rounded mt-1" />
            </div>
            <div>
              <label className="text-xs text-slate-400">BPM (Pouls)</label>
              <input type="number" value={bpm} onChange={(e) => setBpm(e.target.value)} className="w-full bg-slate-900 border border-slate-700 p-2 rounded mt-1" />
            </div>
            <div>
              <label className="text-xs text-slate-400">SpO2 (%)</label>
              <input type="number" value={spo2} onChange={(e) => setSpo2(e.target.value)} className="w-full bg-slate-900 border border-slate-700 p-2 rounded mt-1" />
            </div>
            <div>
              <label className="text-xs text-slate-400">Température (°C)</label>
              <input type="number" step="0.1" value={temp} onChange={(e) => setTemp(e.target.value)} className="w-full bg-slate-900 border border-slate-700 p-2 rounded mt-1" />
            </div>
            <div>
              <label className="text-xs text-slate-400">Piezo</label>
              <input type="number" step="0.1" value={piezo} onChange={(e) => setPiezo(e.target.value)} className="w-full bg-slate-900 border border-slate-700 p-2 rounded mt-1" />
            </div>
            <div>
              <label className="text-xs text-slate-400">GSR / Accélération</label>
              <input type="number" step="0.1" value={gsr} onChange={(e) => setGsr(e.target.value)} className="w-full bg-slate-900 border border-slate-700 p-2 rounded mt-1" />
            </div>
            <button type="submit" className="col-span-2 bg-red-600 hover:bg-red-700 p-2.5 rounded-lg font-medium mt-2 transition">
              Envoyer & Prédire (IA)
            </button>
          </form>
        </div>

        {/* Module 2: Alertes Actives */}
        <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl shadow-lg">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-yellow-400">
            <AlertTriangle className="w-5 h-5" /> Alertes Actives en Direct
          </h2>
          {loadingAlertes ? (
            <p className="text-slate-400 text-sm">Chargement des alertes...</p>
          ) : alertes.length === 0 ? (
            <div className="text-center py-8 text-slate-500">Aucune alerte active pour le patient #{patientId}</div>
          ) : (
            <div className="space-y-3">
              {alertes.map((al) => (
                <div key={al.id} className="bg-slate-900 border border-red-500/30 p-4 rounded-lg flex items-center justify-between">
                  <div>
                    <span className="text-xs text-red-400 font-semibold uppercase">{al.niveau_urgence}</span>
                    <p className="text-sm text-slate-200 mt-1">{al.description}</p>
                    <span className="text-xs text-slate-500">{new Date(al.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <button onClick={() => handleResoudre(al.id)} className="bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-400 border border-emerald-500/30 text-xs px-3 py-2 rounded-lg flex items-center gap-1 transition">
                    <CheckCircle className="w-4 h-4" /> Résoudre
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}