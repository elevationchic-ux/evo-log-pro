'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  MessageSquare, Send, Search, Users, Shield, Clock, 
  Sparkles, UserCheck, RefreshCw, CheckCheck, 
  MessageCircle, Building2, UserCircle2, ArrowRight,
  Video, VideoOff, Mic, MicOff, PhoneOff, Monitor,
  Plus, Hash, Radio, PhoneCall, Check, UserPlus,
  ChevronRight, Volume2, Maximize2, Minimize2, Paperclip, X
} from 'lucide-react';
import { useAuth } from '@/components/shared/AuthProvider';
import { chatCollabAPI } from '@/lib/api-client';
import { toast } from 'sonner';

interface ChatMessage {
  id: number;
  company_id: number | null;
  sender_id: number;
  recipient_id: number | null;
  room_id?: number | null;
  channel_type: string;
  content: string;
  sender_name: string;
  sender_role: string;
  is_read: boolean;
  created_at: string;
}

interface Colleague {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role_code: string;
  role_title: string;
  company_id: number | null;
  is_online: boolean;
}

interface MeetingRoom {
  id: number;
  room_uuid: string;
  name: string;
  topic: string;
  channel_type: string;
  is_private: boolean;
  active_call: boolean;
  created_by_id: number | null;
  created_by_name: string;
  created_at: string;
  members_count: number;
  members: Array<{
    id: number;
    username: string;
    full_name: string;
    role_title: string;
  }>;
}

export default function EnterpriseChatPage() {
  const { user } = useAuth();

  // Active view: 'thematic' | 'meeting' | 'direct'
  const [activeTab, setActiveTab] = useState<'thematic' | 'meeting' | 'direct'>('thematic');

  // Rooms & Direct states
  const [rooms, setRooms] = useState<MeetingRoom[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<MeetingRoom | null>(null);
  const [roomMessages, setRoomMessages] = useState<ChatMessage[]>([]);
  const [newRoomMessage, setNewRoomMessage] = useState('');
  const [isSendingRoom, setIsSendingRoom] = useState(false);

  // Direct 1-to-1 states
  const [colleagues, setColleagues] = useState<Colleague[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedColleague, setSelectedColleague] = useState<Colleague | null>(null);
  const [directMessages, setDirectMessages] = useState<ChatMessage[]>([]);
  const [newDirectMessage, setNewDirectMessage] = useState('');
  const [isSendingDirect, setIsSendingDirect] = useState(false);

  // Create Meeting Modal State
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [meetingName, setMeetingName] = useState('');
  const [meetingTopic, setMeetingTopic] = useState('');
  const [isMeetingPrivate, setIsMeetingPrivate] = useState(false);
  const [selectedInviteeIds, setSelectedInviteeIds] = useState<number[]>([]);
  const [isCreatingRoom, setIsCreatingRoom] = useState(false);

  // WebRTC Video Call State
  const [isInCall, setIsInCall] = useState(false);
  const [callRoomUuid, setCallRoomUuid] = useState<string | null>(null);
  const [callPeerName, setCallPeerName] = useState<string>('Salle de Réunion');
  const [isMicMuted, setIsMicMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [callDuration, setCallDuration] = useState(0);

  // Video Stream References
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const callTimerRef = useRef<NodeJS.Timeout | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat to bottom
  const scrollToBottom = () => {
    setTimeout(() => {
      if (chatScrollRef.current) {
        chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
      }
    }, 100);
  };

  // Fetch all rooms (thematic channels + user meetings)
  const fetchRooms = useCallback(async () => {
    try {
      const res = await chatCollabAPI.getRooms();
      if (Array.isArray(res.data)) {
        setRooms(res.data);
        // Default select first room if none selected
        if (!selectedRoom && res.data.length > 0 && activeTab !== 'direct') {
          setSelectedRoom(res.data[0]);
        }
      }
    } catch (err) {
      console.error('Erreur chargement des salons:', err);
    }
  }, [activeTab, selectedRoom]);

  // Fetch Directory (search by name or role)
  const fetchColleagues = useCallback(async (query = '') => {
    try {
      const res = await chatCollabAPI.getDirectory(query);
      if (Array.isArray(res.data)) {
        setColleagues(res.data);
        if (!selectedColleague && res.data.length > 0 && activeTab === 'direct') {
          setSelectedColleague(res.data[0]);
        }
      }
    } catch (err) {
      console.error('Erreur chargement annuaire:', err);
    }
  }, [activeTab, selectedColleague]);

  // Fetch messages for selected room
  const fetchRoomMessages = useCallback(async (roomUuid: string) => {
    try {
      const res = await chatCollabAPI.getRoomMessages(roomUuid);
      if (Array.isArray(res.data)) {
        setRoomMessages(res.data);
        scrollToBottom();
      }
    } catch (err) {
      console.error('Erreur messages salon:', err);
    }
  }, []);

  // Fetch direct messages for selected colleague
  const fetchDirectMessages = useCallback(async (colleagueId: number) => {
    try {
      const res = await chatCollabAPI.getDirectMessages(colleagueId);
      if (Array.isArray(res.data)) {
        setDirectMessages(res.data);
        scrollToBottom();
      }
    } catch (err) {
      console.error('Erreur messages directs:', err);
    }
  }, []);

  // Initial Data Load
  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      await Promise.all([fetchRooms(), fetchColleagues()]);
      setIsLoading(false);
    };
    init();
  }, [fetchRooms, fetchColleagues]);

  // Handle room selection change
  useEffect(() => {
    if (selectedRoom) {
      fetchRoomMessages(selectedRoom.room_uuid);
    }
  }, [selectedRoom, fetchRoomMessages]);

  // Handle colleague selection change
  useEffect(() => {
    if (selectedColleague) {
      fetchDirectMessages(selectedColleague.id);
    }
  }, [selectedColleague, fetchDirectMessages]);

  // Polling loop for new messages (every 3 seconds)
  useEffect(() => {
    const interval = setInterval(() => {
      if (activeTab === 'direct' && selectedColleague) {
        fetchDirectMessages(selectedColleague.id);
      } else if (selectedRoom) {
        fetchRoomMessages(selectedRoom.room_uuid);
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [activeTab, selectedColleague, selectedRoom, fetchDirectMessages, fetchRoomMessages]);

  // Send message to room
  const handleSendRoomMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRoomMessage.trim() || !selectedRoom) return;

    try {
      setIsSendingRoom(true);
      const res = await chatCollabAPI.sendRoomMessage(selectedRoom.room_uuid, newRoomMessage.trim());
      setRoomMessages((prev) => [...prev, res.data]);
      setNewRoomMessage('');
      scrollToBottom();
    } catch (err) {
      toast.error("Erreur lors de l'envoi du message.");
    } finally {
      setIsSendingRoom(false);
    }
  };

  // Send message to direct chat
  const handleSendDirectMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDirectMessage.trim() || !selectedColleague) return;

    try {
      setIsSendingDirect(true);
      const res = await chatCollabAPI.sendDirectMessage(selectedColleague.id, newDirectMessage.trim());
      setDirectMessages((prev) => [...prev, res.data]);
      setNewDirectMessage('');
      scrollToBottom();
    } catch (err) {
      toast.error("Erreur lors de l'envoi du message privé.");
    } finally {
      setIsSendingDirect(false);
    }
  };

  // Create new Meeting Room
  const handleCreateMeetingRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!meetingName.trim()) {
      toast.warning('Le nom du salon de meeting est requis.');
      return;
    }

    try {
      setIsCreatingRoom(true);
      const res = await chatCollabAPI.createRoom({
        name: meetingName.trim(),
        topic: meetingTopic.trim() || 'Réunion opérationnelle',
        is_private: isMeetingPrivate,
        participant_ids: selectedInviteeIds
      });

      toast.success(`Salon « ${res.data.name} » créé avec succès !`);
      setIsCreateModalOpen(false);
      setMeetingName('');
      setMeetingTopic('');
      setSelectedInviteeIds([]);
      await fetchRooms();
      setSelectedRoom(res.data);
      setActiveTab('meeting');
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Erreur lors de la création du salon.';
      toast.error(msg);
    } finally {
      setIsCreatingRoom(false);
    }
  };

  // =========================================================================
  // 🎥 WEBRTC VIDEO CALL ENGINE
  // =========================================================================

  const startVideoCall = async (targetRoomUuid: string, peerLabel: string) => {
    try {
      setCallRoomUuid(targetRoomUuid);
      setCallPeerName(peerLabel);
      setIsInCall(true);
      setCallDuration(0);

      // Start timer
      if (callTimerRef.current) clearInterval(callTimerRef.current);
      callTimerRef.current = setInterval(() => {
        setCallDuration((prev) => prev + 1);
      }, 1000);

      // Notify backend that call started
      await chatCollabAPI.sendWebRTCSignal({
        room_uuid: targetRoomUuid,
        signal_type: 'call-start',
        payload: { caller_name: user?.fullName || (user as any)?.username || 'Collaborateur' }
      }).catch(() => {});

      // Acquire User Media (Webcam & Mic)
      let stream: MediaStream | null = null;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true
        });
      } catch (mediaErr) {
        console.warn('Accès caméra/micro non accordé, mode simulation activé:', mediaErr);
        toast.info("Caméra matérielle non détectée ou non autorisée. Appel initialisé en mode audio/simulation.");
      }

      if (stream) {
        localStreamRef.current = stream;
        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }

        // Setup RTCPeerConnection
        const pc = new RTCPeerConnection({
          iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' }
          ]
        });
        peerConnectionRef.current = pc;

        // Add tracks
        stream.getTracks().forEach((track) => pc.addTrack(track, stream!));

        // Listen for remote tracks
        pc.ontrack = (event) => {
          if (remoteVideoRef.current && event.streams[0]) {
            remoteVideoRef.current.srcObject = event.streams[0];
          }
        };

        // Send local offer signal
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        await chatCollabAPI.sendWebRTCSignal({
          room_uuid: targetRoomUuid,
          signal_type: 'offer',
          payload: { sdp: offer.sdp, type: offer.type }
        }).catch(() => {});
      }

      toast.info(`Appel vidéo initialisé avec ${peerLabel}`);
    } catch (err) {
      console.error("Erreur lors de l'appel vidéo:", err);
      toast.error("Impossible d'initialiser l'appel vidéo.");
    }
  };

  const endVideoCall = async () => {
    if (callRoomUuid) {
      await chatCollabAPI.sendWebRTCSignal({
        room_uuid: callRoomUuid,
        signal_type: 'call-end',
        payload: {}
      }).catch(() => {});
    }

    // Stop all media tracks
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((track) => track.stop());
      localStreamRef.current = null;
    }

    // Close peer connection
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }

    if (callTimerRef.current) {
      clearInterval(callTimerRef.current);
      callTimerRef.current = null;
    }

    setIsInCall(false);
    setCallRoomUuid(null);
    setIsScreenSharing(false);
    toast.info('Appel vidéo terminé.');
  };

  // Toggle Microphone Mute
  const toggleMicrophone = () => {
    if (localStreamRef.current) {
      const audioTrack = localStreamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsMicMuted(!audioTrack.enabled);
      }
    } else {
      setIsMicMuted(!isMicMuted);
    }
  };

  // Toggle Camera Video
  const toggleCamera = () => {
    if (localStreamRef.current) {
      const videoTrack = localStreamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoOff(!videoTrack.enabled);
      }
    } else {
      setIsVideoOff(!isVideoOff);
    }
  };

  // Screen Sharing
  const toggleScreenShare = async () => {
    if (!isScreenSharing) {
      try {
        const displayStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        const screenTrack = displayStream.getVideoTracks()[0];

        if (peerConnectionRef.current) {
          const sender = peerConnectionRef.current.getSenders().find((s) => s.track?.kind === 'video');
          if (sender) {
            sender.replaceTrack(screenTrack);
          }
        }

        if (localVideoRef.current) {
          localVideoRef.current.srcObject = displayStream;
        }

        screenTrack.onended = () => {
          setIsScreenSharing(false);
          if (localStreamRef.current && localVideoRef.current) {
            localVideoRef.current.srcObject = localStreamRef.current;
          }
        };

        setIsScreenSharing(true);
        toast.success("Partage d'écran activé");
      } catch (err) {
        toast.error("Impossible de partager l'écran.");
      }
    } else {
      if (localStreamRef.current && localVideoRef.current) {
        localVideoRef.current.srcObject = localStreamRef.current;
      }
      setIsScreenSharing(false);
      toast.info("Partage d'écran désactivé");
    }
  };

  // Format call duration MM:SS
  const formatDuration = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  // Filtered rooms
  const thematicRooms = rooms.filter((r) => r.channel_type === 'thematic');
  const meetingRooms = rooms.filter((r) => r.channel_type !== 'thematic');

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 space-y-4">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/50 border border-slate-800 rounded-3xl p-5 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-slate-950 font-black shadow-lg shadow-cyan-500/20">
            <MessageSquare className="w-7 h-7 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-wider text-cyan-400 bg-cyan-500/15 px-3 py-0.5 rounded-full border border-cyan-500/30">
                K-CHAT COLLABORATIF & VISIOCONFÉRENCE
              </span>
              <span className="text-xs text-slate-400 font-mono">Port de Douala (PAD)</span>
            </div>
            <h1 className="text-2xl font-black text-white mt-1">
              Communication d&apos;Exploitation & Réunions Virtuelles
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-black flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all"
          >
            <UserPlus className="w-4 h-4" />
            <span>Nouveau Salon de Meeting</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Sidebar Channels + Active Conversation Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[750px]">
        {/* Left Sidebar (Channels, Meetings, Direct Colleagues) */}
        <div className="lg:col-span-4 bg-slate-900/90 border border-slate-800 rounded-3xl p-4 flex flex-col justify-between shadow-xl overflow-hidden">
          {/* Tabs */}
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-1 bg-slate-950/80 p-1 rounded-2xl border border-slate-800">
              <button
                onClick={() => { setActiveTab('thematic'); if (thematicRooms[0]) setSelectedRoom(thematicRooms[0]); }}
                className={`py-2 text-[11px] font-black rounded-xl transition-all ${
                  activeTab === 'thematic'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Salons Métiers
              </button>
              <button
                onClick={() => { setActiveTab('meeting'); if (meetingRooms[0]) setSelectedRoom(meetingRooms[0]); }}
                className={`py-2 text-[11px] font-black rounded-xl transition-all ${
                  activeTab === 'meeting'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Meetings ({meetingRooms.length})
              </button>
              <button
                onClick={() => { setActiveTab('direct'); if (colleagues[0]) setSelectedColleague(colleagues[0]); }}
                className={`py-2 text-[11px] font-black rounded-xl transition-all ${
                  activeTab === 'direct'
                    ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Direct 1-1 ({colleagues.length})
              </button>
            </div>

            {/* Subheader / Search */}
            {activeTab === 'direct' ? (
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Rechercher un collègue ou un rôle..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    fetchColleagues(e.target.value);
                  }}
                  className="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs focus:border-cyan-500 focus:outline-none"
                />
              </div>
            ) : (
              <div className="flex items-center justify-between text-[11px] text-slate-400 px-1 font-semibold">
                <span>{activeTab === 'thematic' ? 'Canaux Officiels Équipe' : 'Salons Privés / Multi-Employés'}</span>
                {activeTab === 'meeting' && (
                  <button 
                    onClick={() => setIsCreateModalOpen(true)}
                    className="text-emerald-400 hover:underline flex items-center gap-1 font-bold"
                  >
                    <Plus className="w-3 h-3" /> Créer
                  </button>
                )}
              </div>
            )}
          </div>

          {/* List Content */}
          <div className="flex-1 overflow-y-auto mt-3 space-y-1.5 pr-1">
            {/* Thematic Channels */}
            {activeTab === 'thematic' && thematicRooms.map((r) => (
              <button
                key={r.room_uuid}
                onClick={() => setSelectedRoom(r)}
                className={`w-full p-3 rounded-2xl text-left transition-all flex items-center justify-between border ${
                  selectedRoom?.room_uuid === r.room_uuid
                    ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-200 shadow-md'
                    : 'bg-slate-950/50 border-slate-800/80 text-slate-300 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="w-8 h-8 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center flex-shrink-0 font-mono font-bold">
                    <Hash className="w-4 h-4" />
                  </div>
                  <div className="truncate">
                    <div className="text-xs font-bold truncate text-white">{r.name}</div>
                    <div className="text-[10px] text-slate-400 truncate">{r.topic}</div>
                  </div>
                </div>
                {r.active_call && (
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping flex-shrink-0" title="Appel en cours" />
                )}
              </button>
            ))}

            {/* Custom Meeting Rooms */}
            {activeTab === 'meeting' && (
              <>
                {meetingRooms.map((r) => (
                  <button
                    key={r.room_uuid}
                    onClick={() => setSelectedRoom(r)}
                    className={`w-full p-3 rounded-2xl text-left transition-all flex items-center justify-between border ${
                      selectedRoom?.room_uuid === r.room_uuid
                        ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-200 shadow-md'
                        : 'bg-slate-950/50 border-slate-800/80 text-slate-300 hover:bg-slate-800/50'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0 font-bold">
                        <Users className="w-4 h-4" />
                      </div>
                      <div className="truncate">
                        <div className="text-xs font-bold truncate text-white">{r.name}</div>
                        <div className="text-[10px] text-slate-400 truncate">
                          {r.members_count} participants • {r.created_by_name}
                        </div>
                      </div>
                    </div>
                    {r.active_call && (
                      <span className="px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/40 text-[9px] font-black animate-pulse">
                        EN DIRECT
                      </span>
                    )}
                  </button>
                ))}

                {meetingRooms.length === 0 && (
                  <div className="p-6 text-center text-slate-500 text-xs space-y-3">
                    <Users className="w-8 h-8 mx-auto text-slate-600" />
                    <p>Aucun salon de réunion créé.</p>
                    <button
                      onClick={() => setIsCreateModalOpen(true)}
                      className="px-3 py-1.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs font-bold inline-flex items-center gap-1.5"
                    >
                      <Plus className="w-3.5 h-3.5" /> Créer un meeting
                    </button>
                  </div>
                )}
              </>
            )}

            {/* Direct 1-to-1 Colleagues */}
            {activeTab === 'direct' && colleagues.map((colleague) => (
              <button
                key={colleague.id}
                onClick={() => setSelectedColleague(colleague)}
                className={`w-full p-3 rounded-2xl text-left transition-all flex items-center justify-between border ${
                  selectedColleague?.id === colleague.id
                    ? 'bg-blue-500/15 border-blue-500/40 text-blue-200 shadow-md'
                    : 'bg-slate-950/50 border-slate-800/80 text-slate-300 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="relative">
                    <div className="w-9 h-9 rounded-xl bg-slate-800 flex items-center justify-center font-bold text-xs text-slate-200 border border-slate-700">
                      {colleague.full_name.slice(0, 2).toUpperCase()}
                    </div>
                    <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-slate-900" />
                  </div>
                  <div className="truncate">
                    <div className="text-xs font-bold text-white truncate">{colleague.full_name}</div>
                    <div className="text-[10px] text-slate-400 truncate">{colleague.role_title}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* User Quick Info */}
          <div className="pt-3 border-t border-slate-800/80 mt-2 flex items-center justify-between text-xs text-slate-400">
            <span className="truncate">Connecté : <b className="text-slate-200">{user?.fullName || (user as any)?.username || 'Utilisateur'}</b></span>
            <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded-full">En ligne</span>
          </div>
        </div>

        {/* Center / Right Content: Active Conversation Panel */}
        <div className="lg:col-span-8 bg-slate-900/90 border border-slate-800 rounded-3xl flex flex-col justify-between shadow-2xl overflow-hidden relative">
          {/* Header of Active Chat */}
          <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {activeTab === 'direct' && selectedColleague ? (
                <>
                  <div className="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-sm">
                    {selectedColleague.full_name.slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-white flex items-center gap-2">
                      {selectedColleague.full_name}
                      <span className="text-[10px] font-normal text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                        {selectedColleague.role_code}
                      </span>
                    </h2>
                    <p className="text-[11px] text-slate-400">{selectedColleague.role_title}</p>
                  </div>
                </>
              ) : selectedRoom ? (
                <>
                  <div className="w-10 h-10 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-sm">
                    {selectedRoom.channel_type === 'thematic' ? <Hash className="w-5 h-5" /> : <Users className="w-5 h-5" />}
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-white flex items-center gap-2">
                      {selectedRoom.name}
                      {selectedRoom.channel_type !== 'thematic' && (
                        <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                          {selectedRoom.members_count} participants
                        </span>
                      )}
                    </h2>
                    <p className="text-[11px] text-slate-400">{selectedRoom.topic || 'Canal de collaboration opérationnelle'}</p>
                  </div>
                </>
              ) : (
                <div className="text-xs text-slate-400">Sélectionnez une discussion</div>
              )}
            </div>

            {/* Action Buttons: Video Call Button */}
            <div className="flex items-center gap-2">
              {activeTab === 'direct' && selectedColleague ? (
                <button
                  onClick={() => startVideoCall(`direct-${user?.id}-${selectedColleague.id}`, selectedColleague.full_name)}
                  className="px-3.5 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-lg shadow-emerald-500/25 transition-all"
                >
                  <Video className="w-4 h-4" />
                  <span>Appel Vidéo 1-à-1</span>
                </button>
              ) : selectedRoom ? (
                <button
                  onClick={() => startVideoCall(selectedRoom.room_uuid, selectedRoom.name)}
                  className="px-3.5 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-lg shadow-cyan-500/25 transition-all"
                >
                  <Video className="w-4 h-4" />
                  <span>Rejoindre Réunion Vidéo</span>
                </button>
              ) : null}
            </div>
          </div>

          {/* Messages Feed */}
          <div 
            ref={chatScrollRef}
            className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-slate-950/40"
          >
            {activeTab === 'direct' ? (
              directMessages.map((m) => {
                const isMine = String(m.sender_id) === String(user?.id);
                return (
                  <div 
                    key={m.id} 
                    className={`flex flex-col ${isMine ? 'items-end' : 'items-start'}`}
                  >
                    <div className="flex items-center gap-2 mb-1 px-1">
                      <span className="text-[11px] font-bold text-slate-300">{m.sender_name}</span>
                      <span className="text-[10px] text-slate-500">{m.sender_role}</span>
                      <span className="text-[10px] text-slate-600">
                        {new Date(m.created_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div 
                      className={`max-w-lg p-3 rounded-2xl text-xs leading-relaxed ${
                        isMine 
                          ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-tr-none shadow-md' 
                          : 'bg-slate-800/90 text-slate-100 border border-slate-700/80 rounded-tl-none shadow'
                      }`}
                    >
                      {m.content}
                    </div>
                  </div>
                );
              })
            ) : (
              roomMessages.map((m) => {
                const isMine = String(m.sender_id) === String(user?.id);
                return (
                  <div 
                    key={m.id} 
                    className={`flex flex-col ${isMine ? 'items-end' : 'items-start'}`}
                  >
                    <div className="flex items-center gap-2 mb-1 px-1">
                      <span className="text-[11px] font-bold text-slate-300">{m.sender_name}</span>
                      <span className="text-[10px] text-cyan-400 font-mono bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/20">
                        {m.sender_role}
                      </span>
                      <span className="text-[10px] text-slate-600">
                        {new Date(m.created_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div 
                      className={`max-w-lg p-3.5 rounded-2xl text-xs leading-relaxed ${
                        isMine 
                          ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-tr-none shadow-md' 
                          : 'bg-slate-800/90 text-slate-100 border border-slate-700/80 rounded-tl-none shadow'
                      }`}
                    >
                      {m.content}
                    </div>
                  </div>
                );
              })
            )}

            {((activeTab === 'direct' && directMessages.length === 0) || (activeTab !== 'direct' && roomMessages.length === 0)) && (
              <div className="p-12 text-center text-slate-500 text-xs">
                Aucun message dans ce salon. Soyez le premier à engager la discussion !
              </div>
            )}
          </div>

          {/* Message Input Box */}
          <form 
            onSubmit={activeTab === 'direct' ? handleSendDirectMessage : handleSendRoomMessage}
            className="p-3 bg-slate-950 border-t border-slate-800 flex items-center gap-2"
          >
            <input
              type="text"
              placeholder={activeTab === 'direct' ? `Message direct pour ${selectedColleague?.full_name || 'le collègue'}...` : `Écrire dans ${selectedRoom?.name || 'le salon'}...`}
              value={activeTab === 'direct' ? newDirectMessage : newRoomMessage}
              onChange={(e) => activeTab === 'direct' ? setNewDirectMessage(e.target.value) : setNewRoomMessage(e.target.value)}
              className="flex-1 bg-slate-900 border border-slate-800 text-slate-100 rounded-xl px-4 py-2.5 text-xs focus:border-cyan-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={activeTab === 'direct' ? isSendingDirect : isSendingRoom}
              className="p-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl text-xs font-bold transition-all shadow-md flex items-center justify-center"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* MODAL : VISIOCONFÉRENCE / APPEL VIDÉO WEBRTC                              */}
      {/* ========================================================================= */}
      {isInCall && (
        <div className="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-emerald-500/50 rounded-3xl overflow-hidden shadow-2xl max-w-4xl w-full flex flex-col h-[600px] animate-in zoom-in-95">
            {/* Call Header */}
            <div className="p-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-red-500 animate-ping" />
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    Visioconférence en cours : {callPeerName}
                  </h3>
                  <span className="text-xs font-mono text-emerald-400">
                    Durée : {formatDuration(callDuration)} • WebRTC P2P Chiffré
                  </span>
                </div>
              </div>
              <button 
                onClick={endVideoCall}
                className="text-slate-400 hover:text-white p-1"
                title="Fermer la session"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Video Streams Container */}
            <div className="flex-1 bg-slate-950 p-4 grid grid-cols-1 md:grid-cols-2 gap-4 relative overflow-hidden">
              {/* Remote Video Stream / Active Speaker */}
              <div className="bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden relative flex items-center justify-center shadow-inner">
                <video 
                  ref={remoteVideoRef} 
                  autoPlay 
                  playsInline 
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center text-white font-black text-2xl shadow-xl shadow-cyan-500/20">
                    {callPeerName.slice(0, 2).toUpperCase()}
                  </div>
                  <span className="text-xs font-bold text-slate-300 mt-2 bg-slate-950/80 px-3 py-1 rounded-full border border-slate-800">
                    {callPeerName}
                  </span>
                </div>
                <div className="absolute bottom-3 left-3 bg-slate-950/80 px-2.5 py-1 rounded-lg border border-slate-800 text-[10px] text-slate-300 font-mono">
                  Flux Distant
                </div>
              </div>

              {/* Local Video Stream (Self Preview) */}
              <div className="bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden relative flex items-center justify-center shadow-inner">
                <video 
                  ref={localVideoRef} 
                  autoPlay 
                  playsInline 
                  muted 
                  className={`w-full h-full object-cover ${isVideoOff ? 'hidden' : ''}`}
                />
                {isVideoOff && (
                  <div className="flex flex-col items-center justify-center">
                    <div className="w-20 h-20 rounded-full bg-slate-800 flex items-center justify-center text-slate-300 font-black text-2xl border border-slate-700">
                      {(user?.fullName || (user as any)?.username || 'MO').slice(0, 2).toUpperCase()}
                    </div>
                    <span className="text-xs text-slate-400 mt-2 font-medium">Caméra désactivée</span>
                  </div>
                )}
                <div className="absolute bottom-3 left-3 bg-slate-950/80 px-2.5 py-1 rounded-lg border border-slate-800 text-[10px] text-slate-300 font-mono">
                  Vous ({user?.fullName || (user as any)?.username || 'Moi'})
                </div>
              </div>
            </div>

            {/* Call Controls Bar */}
            <div className="p-4 bg-slate-950 border-t border-slate-800 flex items-center justify-center gap-4">
              <button
                onClick={toggleMicrophone}
                className={`p-3.5 rounded-2xl border transition-all ${
                  isMicMuted 
                    ? 'bg-red-500/20 border-red-500/40 text-red-300' 
                    : 'bg-slate-800 border-slate-700 text-slate-200 hover:bg-slate-700'
                }`}
                title={isMicMuted ? 'Activer le micro' : 'Couper le micro'}
              >
                {isMicMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>

              <button
                onClick={toggleCamera}
                className={`p-3.5 rounded-2xl border transition-all ${
                  isVideoOff 
                    ? 'bg-red-500/20 border-red-500/40 text-red-300' 
                    : 'bg-slate-800 border-slate-700 text-slate-200 hover:bg-slate-700'
                }`}
                title={isVideoOff ? 'Activer la caméra' : 'Couper la caméra'}
              >
                {isVideoOff ? <VideoOff className="w-5 h-5" /> : <Video className="w-5 h-5" />}
              </button>

              <button
                onClick={toggleScreenShare}
                className={`p-3.5 rounded-2xl border transition-all ${
                  isScreenSharing 
                    ? 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300' 
                    : 'bg-slate-800 border-slate-700 text-slate-200 hover:bg-slate-700'
                }`}
                title="Partager l'écran"
              >
                <Monitor className="w-5 h-5" />
              </button>

              <button
                onClick={endVideoCall}
                className="px-6 py-3.5 bg-red-600 hover:bg-red-500 text-white font-bold rounded-2xl flex items-center gap-2 shadow-lg shadow-red-600/30 transition-all text-xs"
              >
                <PhoneOff className="w-5 h-5" />
                <span>Raccrocher</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL : CRÉER UN NOUVEAU SALON DE MEETING ENTRE COLLÈGUES                */}
      {/* ========================================================================= */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-emerald-500/40 rounded-3xl p-6 max-w-lg w-full shadow-2xl space-y-5 animate-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-emerald-400" />
                <h2 className="text-base font-bold text-slate-100">Nouveau Salon de Meeting</h2>
              </div>
              <button 
                onClick={() => setIsCreateModalOpen(false)}
                className="text-slate-400 hover:text-white text-xs font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateMeetingRoom} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Nom du Salon</label>
                <input
                  type="text"
                  required
                  placeholder="Ex: Briefing Quai STS - Rotation Nuit..."
                  value={meetingName}
                  onChange={(e) => setMeetingName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3.5 py-2 text-xs focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-1">Ordre du Jour / Sujet</label>
                <input
                  type="text"
                  placeholder="Ex: Synchronisation cadences manutention..."
                  value={meetingTopic}
                  onChange={(e) => setMeetingTopic(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3.5 py-2 text-xs focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase mb-2">
                  Inviter des Collaborateurs Spécifiques ({selectedInviteeIds.length} sélectionnés)
                </label>
                <div className="max-h-44 overflow-y-auto space-y-1.5 bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                  {colleagues.map((c) => {
                    const isSelected = selectedInviteeIds.includes(c.id);
                    return (
                      <button
                        type="button"
                        key={c.id}
                        onClick={() => {
                          if (isSelected) {
                            setSelectedInviteeIds(selectedInviteeIds.filter((id) => id !== c.id));
                          } else {
                            setSelectedInviteeIds([...selectedInviteeIds, c.id]);
                          }
                        }}
                        className={`w-full p-2 rounded-lg text-left text-xs flex items-center justify-between transition-all ${
                          isSelected 
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' 
                            : 'hover:bg-slate-800/60 text-slate-300'
                        }`}
                      >
                        <div className="truncate">
                          <span className="font-bold">{c.full_name}</span> • <span className="text-[10px] text-slate-400">{c.role_title}</span>
                        </div>
                        {isSelected && <Check className="w-4 h-4 text-emerald-400" />}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="private-check"
                  checked={isMeetingPrivate}
                  onChange={(e) => setIsMeetingPrivate(e.target.checked)}
                  className="rounded border-slate-700 text-emerald-500 focus:ring-emerald-500"
                />
                <label htmlFor="private-check" className="text-xs text-slate-300">
                  Salon privé (réservé exclusivement aux collègues invités)
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold transition-all"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={isCreatingRoom}
                  className="px-5 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-black shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-2"
                >
                  {isCreatingRoom ? 'Création...' : 'Ouvrir le Salon de Meeting'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
