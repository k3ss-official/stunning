import React, { createContext, useContext, useState, ReactNode } from 'react';

// Define theme types
type ThemeColors = {
  primary: string;
  secondary: string;
  accent: string;
};

// Define client theme context type
interface ClientThemeContextType {
  clientTheme: ThemeColors;
  setClientTheme: (theme: ThemeColors) => void;
  clientId: number | null;
  setClientId: (id: number | null) => void;
  clientName: string | null;
  setClientName: (name: string | null) => void;
}

// Create context with default values
const ClientThemeContext = createContext<ClientThemeContextType>({
  clientTheme: {
    primary: '#0ea5e9', // Default primary color
    secondary: '#64748b', // Default secondary color
    accent: '#3b82f6', // Default accent color
  },
  setClientTheme: () => {},
  clientId: null,
  setClientId: () => {},
  clientName: null,
  setClientName: () => {},
});

// Provider component
export const ClientThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [clientTheme, setClientTheme] = useState<ThemeColors>({
    primary: '#0ea5e9',
    secondary: '#64748b',
    accent: '#3b82f6',
  });
  
  const [clientId, setClientId] = useState<number | null>(null);
  const [clientName, setClientName] = useState<string | null>(null);

  // Apply theme to CSS variables
  React.useEffect(() => {
    document.documentElement.style.setProperty('--client-primary', clientTheme.primary);
    document.documentElement.style.setProperty('--client-secondary', clientTheme.secondary);
    document.documentElement.style.setProperty('--client-accent', clientTheme.accent);
  }, [clientTheme]);

  return (
    <ClientThemeContext.Provider 
      value={{ 
        clientTheme, 
        setClientTheme, 
        clientId, 
        setClientId, 
        clientName, 
        setClientName 
      }}
    >
      {children}
    </ClientThemeContext.Provider>
  );
};

// Custom hook for using the client theme context
export const useClientTheme = () => useContext(ClientThemeContext);
