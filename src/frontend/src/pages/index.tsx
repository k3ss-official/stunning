import React from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useQuery } from 'react-query';
import { clientsAPI } from '@/utils/api';

export default function Home() {
  const router = useRouter();
  const { data: clients, isLoading, error } = useQuery('clients', clientsAPI.getAll);

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Stunning Modeling Studio</title>
        <meta name="description" content="AI-powered modeling studio system" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">STUNNING</h1>
          <button 
            className="btn btn-primary"
            onClick={() => router.push('/clients/new')}
          >
            + NEW
          </button>
        </div>

        <div className="mb-6">
          <input
            type="text"
            placeholder="Search clients..."
            className="input"
          />
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
          </div>
        ) : error ? (
          <div className="text-center py-12 text-red-500">
            Error loading clients. Please try again.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {clients?.data.map((client: any) => (
              <div 
                key={client.id} 
                className="card hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => router.push(`/clients/${client.id}`)}
              >
                <div className="flex flex-col items-center">
                  <div className="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center mb-4">
                    <span className="text-2xl font-bold text-gray-500">
                      {client.name.charAt(0)}
                    </span>
                  </div>
                  <h2 className="text-xl font-semibold mb-1">{client.name}</h2>
                  <p className="text-gray-500">
                    {client.models?.length || 0} Models
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
