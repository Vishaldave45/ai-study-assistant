import { useState } from 'react';
import { useWorkspace } from '../hooks/useWorkspace';
import { useAuth } from '../hooks/useAuth';
import { WorkspaceModal } from './WorkspaceModal.tsx';
import type { WorkspaceSummary } from '../types/workspace.ts';

export function Sidebar() {
  const { workspaces, activeWorkspace, selectWorkspace } = useWorkspace();
  const { logout, user } = useAuth();

  // Modal control states
  const [modalType, setModalType] = useState<'create' | 'edit' | 'delete' | null>(null);
  const [selectedWs, setSelectedWs] = useState<WorkspaceSummary | null>(null);

  const openModal = (type: 'create' | 'edit' | 'delete', ws?: WorkspaceSummary) => {
    setModalType(type);
    setSelectedWs(ws || null);
  };

  const closeModal = () => {
    setModalType(null);
    setSelectedWs(null);
  };

  return (
    <aside 
      style={{ 
        width: '260px', 
        borderRight: '1px solid #ccc', 
        padding: '20px', 
        background: '#fff', 
        display: 'flex', 
        flexDirection: 'column' 
      }} 
      aria-label="Sidebar navigation"
    >
      <div>
        <h3>Hello, {user?.full_name}</h3>
        <p style={{ fontSize: '0.85em', color: '#666', marginBottom: '20px' }}>
          {user?.email}
        </p>
      </div>

      <nav aria-labelledby="workspaces-heading" style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h4 id="workspaces-heading" style={{ margin: 0 }}>Workspaces</h4>
          <button 
            onClick={() => openModal('create')} 
            aria-label="Create new workspace"
            style={{ 
              padding: '2px 8px', 
              fontSize: '0.9em', 
              cursor: 'pointer' 
            }}
          >
            + Add
          </button>
        </div>

        {workspaces.length === 0 ? (
          <p style={{ fontSize: '0.9em', color: '#888', fontStyle: 'italic' }}>
            No workspaces found.
          </p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0, margin: '10px 0' }}>
            {workspaces.map((ws) => {
              const isActive = activeWorkspace?.id === ws.id;
              return (
                <li
                  key={ws.id}
                  onClick={() => selectWorkspace(ws.id)}
                  style={{
                    padding: '8px 12px',
                    margin: '4px 0',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    background: isActive ? '#e0f0ff' : 'transparent',
                    fontWeight: isActive ? 'bold' : 'normal',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    border: isActive ? '1px solid #b8daff' : '1px solid transparent',
                  }}
                >
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginRight: '10px' }}>
                    {ws.name}
                  </span>
                  
                  {/* Action buttons */}
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openModal('edit', ws);
                      }}
                      aria-label={`Rename ${ws.name}`}
                      style={{ 
                        padding: '2px 5px', 
                        fontSize: '0.8em', 
                        cursor: 'pointer' 
                      }}
                    >
                      ✏️
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openModal('delete', ws);
                      }}
                      aria-label={`Delete ${ws.name}`}
                      style={{ 
                        padding: '2px 5px', 
                        fontSize: '0.8em', 
                        cursor: 'pointer' 
                      }}
                    >
                      🗑️
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </nav>

      <footer style={{ marginTop: 'auto', paddingTop: '20px', borderTop: '1px solid #eee' }}>
        <button 
          onClick={logout} 
          style={{ 
            width: '100%', 
            padding: '8px', 
            background: '#ffebeb', 
            border: '1px solid #ffd1d1', 
            borderRadius: '4px', 
            cursor: 'pointer', 
            color: '#c00' 
          }}
        >
          Log Out
        </button>
      </footer>

      {/* Render the modals */}
      {modalType && (
        <WorkspaceModal
          type={modalType}
          workspace={selectedWs}
          onClose={closeModal}
        />
      )}
    </aside>
  );
}
export default Sidebar;
