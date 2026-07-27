import { useState } from 'react'; 
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { WorkspaceProvider } from './contexts/WorkspaceContext';
import { DocumentProvider } from './contexts/DocumentContext';
import { ChatProvider } from './contexts/ChatContext'; 
import { useWorkspace } from './hooks/useWorkspace';
import ProtectedRoute from './routes/ProtectedRoute';
import GuestRoute from './routes/GuestRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Card from './components/Card';
import Sidebar from './components/Sidebar';
import { DocumentManager } from './components/Documentmanager.tsx';
import { ChatInterface } from './components/ChatInterface'; 
/**
 * Dashboard component displaying the main application view.
 * Integrates Workspace Switcher Sidebar and displays active workspace details.
 */
function Dashboard() {
  const { activeWorkspace, isLoading } = useWorkspace();
  const [activeTab, setActiveTab] = useState<'documents' | 'chat'>('documents');

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f5f7fb' }}>
      {/* Sidebar Component */}
      <Sidebar />

      {/* Main Workspace content */}
      <main style={{ flex: 1, padding: '40px' }} aria-labelledby="workspace-detail-title">
        {isLoading && !activeWorkspace ? (
          <p>Loading workspace details...</p>
        ) : activeWorkspace ? (
          <Card>
            <header>
              <h1 id="workspace-detail-title">{activeWorkspace.name}</h1>
              {activeWorkspace.description && (
                <p style={{ color: '#555', fontStyle: 'italic', margin: '8px 0 16px 0' }}>
                  {activeWorkspace.description}
                </p>
              )}
            </header>

            <section style={{ fontSize: '0.85em', color: '#666', marginBottom: '20px' }}>
              <p>Workspace ID: <code>{activeWorkspace.id}</code></p>
              <p>Created: {new Date(activeWorkspace.created_at).toLocaleString()}</p>
            </section>
            
            {/* Simple tab navigator */}
            <div style={{ display: 'flex', gap: '20px', borderBottom: '1px solid #eee', marginBottom: '20px' }}>
              <button 
                onClick={() => setActiveTab('documents')}
                style={{
                  padding: '10px 16px',
                  background: 'none',
                  border: 'none',
                  borderBottom: activeTab === 'documents' ? '2px solid #0066cc' : '2px solid transparent',
                  fontWeight: activeTab === 'documents' ? 'bold' : 'normal',
                  color: activeTab === 'documents' ? '#0066cc' : '#555',
                  cursor: 'pointer',
                  fontSize: '0.95em',
                  outline: 'none'
                }}
              >
                📁 Files
              </button>
              <button 
                onClick={() => setActiveTab('chat')}
                style={{
                  padding: '10px 16px',
                  background: 'none',
                  border: 'none',
                  borderBottom: activeTab === 'chat' ? '2px solid #0066cc' : '2px solid transparent',
                  fontWeight: activeTab === 'chat' ? 'bold' : 'normal',
                  color: activeTab === 'chat' ? '#0066cc' : '#555',
                  cursor: 'pointer',
                  fontSize: '0.95em',
                  outline: 'none'
                }}
              >
                💬 AI Chat
              </button>
            </div>

            <section>
              {activeTab === 'documents' ? (
                <DocumentManager />
              ) : (
                <ChatInterface />
              )}
            </section>
          </Card>
        ) : (
          <Card>
            <h1>No Workspace Selected</h1>
            <p>Please select a workspace from the sidebar or create a new one to begin studying.</p>
          </Card>
        )}
      </main>
    </div>
  );
}


export function App() {
  return (
    <AuthProvider>
      <WorkspaceProvider>
        <DocumentProvider>
          <ChatProvider> {/* <-- Mount Provider Here */}
            <BrowserRouter>
              <Routes>
                {/* Guest-only Routes */}
                <Route element={<GuestRoute />}>
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/forgot-password" element={<ForgotPassword />} />
                  <Route path="/reset-password" element={<ResetPassword />} />
                </Route>

                {/* Protected Routes */}
                <Route element={<ProtectedRoute />}>
                  <Route path="/" element={<Dashboard />} />
                </Route>

                {/* Fallback Redirection */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </BrowserRouter>
          </ChatProvider>
        </DocumentProvider>
      </WorkspaceProvider>
    </AuthProvider>
  );
}


export default App;
