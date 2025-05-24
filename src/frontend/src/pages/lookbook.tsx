import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useQuery } from 'react-query';
import { historyAPI } from '@/utils/api';
import { useClientTheme } from '@/contexts/ClientThemeContext';

export default function Lookbook() {
  const router = useRouter();
  const { clientId, clientName } = useClientTheme();
  const [selectedModelId, setSelectedModelId] = useState<number | null>(null);
  
  // Fetch history entries
  const { data: histories, isLoading, error } = useQuery(
    ['histories', selectedModelId],
    () => historyAPI.getAll(selectedModelId || undefined)
  );
  
  const handleRestore = (historyId: number) => {
    // Navigate to studio with the history ID
    router.push(`/studio?history=${historyId}`);
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Lookbook | Stunning Modeling Studio</title>
        <meta name="description" content="Browse your model history" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <header className="bg-white shadow">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900 mr-4">STUNNING</h1>
            <span className="text-gray-600">Client: {clientName || 'Select a client'}</span>
          </div>
          <button 
            className="btn btn-secondary"
            onClick={() => router.push('/settings')}
          >
            Settings
          </button>
        </div>
      </header>
      
      <nav className="bg-white border-b">
        <div className="container mx-auto px-4">
          <div className="flex space-x-4">
            <button 
              className="px-3 py-2 text-gray-700 hover:text-gray-900"
              onClick={() => router.push(`/clients/${clientId}/models`)}
            >
              Models
            </button>
            <button 
              className="px-3 py-2 text-gray-700 hover:text-gray-900"
              onClick={() => router.push(`/studio`)}
            >
              Studio
            </button>
            <button 
              className="px-3 py-2 text-gray-900 border-b-2 border-primary-500"
              onClick={() => router.push(`/lookbook`)}
            >
              Lookbook
            </button>
            <button 
              className="px-3 py-2 text-gray-700 hover:text-gray-900"
              onClick={() => router.push(`/templates`)}
            >
              Templates
            </button>
            <button 
              className="px-3 py-2 text-gray-700 hover:text-gray-900"
              onClick={() => router.push(`/export`)}
            >
              Export/Share
            </button>
          </div>
        </div>
      </nav>
      
      <main className="container mx-auto px-4 py-6">
        <div className="bg-white rounded-lg shadow p-4 mb-6 flex justify-between items-center">
          <h2 className="text-xl font-semibold">LOOKBOOK: All History</h2>
          <select 
            className="select max-w-xs"
            value={selectedModelId || ''}
            onChange={(e) => setSelectedModelId(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">Filter by Model</option>
            {/* Model options would be populated here */}
          </select>
        </div>
        
        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
          </div>
        ) : error ? (
          <div className="text-center py-12 text-red-500">
            Error loading history. Please try again.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {histories?.data.map((history: any) => (
              <div key={history.id} className="card">
                <div className="flex flex-col items-center">
                  <div className="w-full aspect-square bg-gray-200 mb-4 rounded overflow-hidden">
                    {history.image_path && (
                      <img 
                        src={history.image_path} 
                        alt="Generated model" 
                        className="w-full h-full object-cover"
                      />
                    )}
                  </div>
                  <h3 className="font-medium mb-1">Model {history.model_id}</h3>
                  <p className="text-sm text-gray-500 mb-1">
                    {history.prompt ? `Prompt: ${history.prompt.substring(0, 30)}...` : 'No prompt'}
                  </p>
                  <p className="text-sm text-gray-500 mb-4">
                    {new Date(history.created_at).toLocaleDateString()}
                  </p>
                  <button 
                    className="btn btn-primary w-full"
                    onClick={() => handleRestore(history.id)}
                  >
                    Restore
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
