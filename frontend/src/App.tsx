import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import AppRoutes from './routes/AppRoutes';
import { Toaster } from 'react-hot-toast';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'rgba(17, 24, 39, 0.9)',
              color: '#f3f4f6',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              backdropFilter: 'blur(8px)',
              borderRadius: '12px',
              fontFamily: 'var(--font-sans)',
            },
            success: {
              iconTheme: {
                primary: 'var(--color-success)',
                secondary: '#ffffff',
              },
            },
            error: {
              iconTheme: {
                primary: 'var(--color-danger)',
                secondary: '#ffffff',
              },
            },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
