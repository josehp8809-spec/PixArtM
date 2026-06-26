import React from 'react';
import { MessageSquare, Users, Settings, Search, Send, MoreHorizontal, User } from 'lucide-react';

function App() {
  return (
    <div className="app-container">
      {/* 1. Sidebar / Inbox List */}
      <aside className="sidebar">
        <header style={{ padding: '20px', borderBottom: '1px solid var(--border-color)' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600' }}>Mensajes</h2>
          <div style={{ marginTop: '15px', position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-secondary)' }} />
            <input 
              type="text" 
              placeholder="Buscar chats..." 
              style={{ 
                width: '100%', 
                padding: '8px 8px 8px 35px', 
                borderRadius: '8px', 
                border: 'none', 
                backgroundColor: 'var(--surface-secondary)', 
                color: 'white' 
              }} 
            />
          </div>
        </header>
        
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {/* Ejemplo de Item de Chat */}
          {[1, 2, 3].map((i) => (
            <div key={i} style={{ 
              padding: '15px', 
              borderBottom: '1px solid var(--border-color)', 
              cursor: 'pointer',
              backgroundColor: i === 1 ? 'var(--surface-color)' : 'transparent'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: '500' }}>Contacto {i}</span>
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>14:20</span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                Hola, ¿cómo puedo ayudarte hoy?
              </p>
            </div>
          ))}
        </div>
      </aside>

      {/* 2. Main Chat Window */}
      <main className="chat-window">
        <header style={{ padding: '15px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: '600' }}>Contacto 1</h3>
            <span style={{ fontSize: '12px', color: '#34c759' }}>● En línea</span>
          </div>
          <MoreHorizontal size={20} color="var(--text-secondary)" />
        </header>

        <div style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {/* Burbujas de Mensaje */}
          <div style={{ alignSelf: 'flex-start', backgroundColor: 'var(--surface-secondary)', padding: '10px 15px', borderRadius: '15px 15px 15px 0px', maxWidth: '70%' }}>
            Hola, quería saber el precio de la suscripción.
          </div>
          <div style={{ alignSelf: 'flex-end', backgroundColor: 'var(--primary-color)', padding: '10px 15px', borderRadius: '15px 15px 0px 15px', maxWidth: '70%' }}>
            ¡Claro! Tenemos planes desde $15/mes.
          </div>
        </div>

        {/* Input Area */}
        <footer style={{ padding: '20px', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', backgroundColor: 'var(--surface-secondary)', padding: '10px', borderRadius: '20px' }}>
            <input 
              type="text" 
              placeholder="Escribe un mensaje..." 
              style={{ flex: 1, background: 'none', border: 'none', color: 'white', outline: 'none' }} 
            />
            <button style={{ background: 'none', border: 'none', color: 'var(--primary-color)', cursor: 'pointer' }}>
              <Send size={20} />
            </button>
          </div>
        </footer>
      </main>

      {/* 3. Details Panel */}
      <aside className="details-panel">
        <div style={{ padding: '40px 20px', textAlign: 'center' }}>
          <div style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: 'var(--surface-secondary)', margin: '0 auto 15px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <User size={40} color="var(--text-secondary)" />
          </div>
          <h3 style={{ fontSize: '18px' }}>Contacto 1</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>+52 55 1234 5678</p>
        </div>
        
        <div style={{ padding: '20px', borderTop: '1px solid var(--border-color)' }}>
          <h4 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '10px' }}>Etiquetas</h4>
          <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
            <span style={{ padding: '4px 10px', backgroundColor: '#5856d6', borderRadius: '12px', fontSize: '12px' }}>Cliente Nuevo</span>
            <span style={{ padding: '4px 10px', backgroundColor: '#af52de', borderRadius: '12px', fontSize: '12px' }}>Potencial</span>
          </div>
        </div>
      </aside>
    </div>
  );
}

export default App;
