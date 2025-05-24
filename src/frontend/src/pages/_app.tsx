import React from 'react';
import { AppProps } from 'next/app';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ClientThemeProvider } from '@/contexts/ClientThemeContext';
import '@/styles/globals.css';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <ClientThemeProvider>
        <Component {...pageProps} />
      </ClientThemeProvider>
    </QueryClientProvider>
  );
}

export default MyApp;
