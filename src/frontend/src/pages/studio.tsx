import React, { useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useQuery } from 'react-query';
import { modelsAPI, layersAPI, generationAPI } from '@/utils/api';
import { useClientTheme } from '@/contexts/ClientThemeContext';

export default function Studio() {
  const router = useRouter();
  const { clientId, clientName } = useClientTheme();
  const { id: modelId } = router.query;
  
  const [hairLayerId, setHairLayerId] = useState<number | null>(null);
  const [outfitLayerId, setOutfitLayerId] = useState<number | null>(null);
  const [sceneLayerId, setSceneLayerId] = useState<number | null>(null);
  const [prompt, setPrompt] = useState('');
  const [previewCollapsed, setPreviewCollapsed] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  
  // Fetch model data
  const { data: model } = useQuery(
    ['model', modelId],
    () => modelId ? modelsAPI.getById(Number(modelId)) : null,
    { enabled: !!modelId }
  );
  
  // Fetch layers
  const { data: hairLayers } = useQuery(
    'hairLayers',
    () => layersAPI.getAll('hair')
  );
  
  const { data: outfitLayers } = useQuery(
    'outfitLayers',
    () => layersAPI.getAll('outfit')
  );
  
  const { data: sceneLayers } = useQuery(
    'sceneLayers',
    () => layersAPI.getAll('scene')
  );
  
  // Fetch models for sidebar
  const { data: models } = useQuery(
    ['models', clientId],
    () => clientId ? modelsAPI.getAll(clientId) : null,
    { enabled: !!clientId }
  );
  
  const handleGenerate = async () => {
    try {
      const response = await generationAPI.generate({
        model_id: Number(modelId),
        hair_layer_id: hairLayerId,
        outfit_layer_id: outfitLayerId,
        scene_layer_id: sceneLayerId,
        prompt,
      });
      
      setGeneratedImage(response.data.image_path);
    } catch (error) {
      console.error('Error generating image:', error);
    }
  };
  
  const togglePreview = () => {
    setPreviewCollapsed(!previewCollapsed);
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Studio | Stunning Modeling Studio</title>
        <meta name="description" content="AI-powered modeling studio system" />
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
              className="px-3 py-2 text-gray-900 border-b-2 border-primary-500"
              onClick={() => router.push(`/studio`)}
            >
              Studio
            </button>
            <button 
              className="px-3 py-2 text-gray-700 hover:text-gray-900"
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
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Model Gallery Sidebar */}
          <div className="lg:w-1/4 bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold mb-4">MODEL GALLERY</h2>
            <div className="space-y-4">
              {models?.data.map((model: any) => (
                <div 
                  key={model.id}
                  className={`p-2 rounded cursor-pointer ${Number(modelId) === model.id ? 'bg-primary-100 border border-primary-300' : 'hover:bg-gray-100'}`}
                  onClick={() => router.push(`/studio?id=${model.id}`)}
                >
                  <div className="aspect-square bg-gray-200 mb-2 rounded"></div>
                  <p className="font-medium">{model.name}</p>
                </div>
              ))}
              <div 
                className="p-2 rounded cursor-pointer hover:bg-gray-100 flex items-center justify-center aspect-square"
                onClick={() => router.push(`/clients/${clientId}/models/new`)}
              >
                <span className="text-xl">+ New Model</span>
              </div>
            </div>
          </div>
          
          {/* Main Content */}
          <div className="lg:w-3/4 space-y-6">
            {/* Preview */}
            <div 
              className={`bg-white rounded-lg shadow overflow-hidden ${previewCollapsed ? 'collapsible-preview-collapsed' : 'collapsible-preview-expanded'}`}
              onClick={previewCollapsed ? togglePreview : undefined}
            >
              <div className="p-4 bg-gray-800 text-white flex justify-between items-center">
                <h3 className="font-medium">LIVE PREVIEW</h3>
                <button 
                  className="text-sm"
                  onClick={togglePreview}
                >
                  {previewCollapsed ? 'Expand' : 'Collapse'}
                </button>
              </div>
              <div className="p-4 flex items-center justify-center">
                {generatedImage ? (
                  <img 
                    src={generatedImage} 
                    alt="Generated model" 
                    className="max-w-full max-h-[60vh]"
                  />
                ) : (
                  <div className="aspect-square w-full max-w-md bg-gray-200 flex items-center justify-center">
                    <p className="text-gray-500">Preview will appear here</p>
                  </div>
                )}
              </div>
            </div>
            
            {/* Styling Controls */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4">STYLING CONTROLS</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="label">Hair:</label>
                  <select 
                    className="select"
                    value={hairLayerId || ''}
                    onChange={(e) => setHairLayerId(e.target.value ? Number(e.target.value) : null)}
                  >
                    <option value="">Select Hair Style</option>
                    {hairLayers?.data.map((layer: any) => (
                      <option key={layer.id} value={layer.id}>
                        {layer.name}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="label">Outfit:</label>
                  <select 
                    className="select"
                    value={outfitLayerId || ''}
                    onChange={(e) => setOutfitLayerId(e.target.value ? Number(e.target.value) : null)}
                  >
                    <option value="">Select Outfit</option>
                    {outfitLayers?.data.map((layer: any) => (
                      <option key={layer.id} value={layer.id}>
                        {layer.name}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="label">Scene:</label>
                  <select 
                    className="select"
                    value={sceneLayerId || ''}
                    onChange={(e) => setSceneLayerId(e.target.value ? Number(e.target.value) : null)}
                  >
                    <option value="">Select Background</option>
                    {sceneLayers?.data.map((layer: any) => (
                      <option key={layer.id} value={layer.id}>
                        {layer.name}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="label">Prompt:</label>
                  <input
                    type="text"
                    className="input"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Enter additional prompt details..."
                  />
                </div>
                
                <div className="flex space-x-4 pt-4">
                  <button 
                    className="btn btn-primary"
                    onClick={handleGenerate}
                  >
                    Generate
                  </button>
                  <button className="btn btn-secondary">
                    Save
                  </button>
                  <button className="btn btn-secondary">
                    Undo
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
