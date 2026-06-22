import { useState } from 'react';
import { Sparkles, Image as ImageIcon } from 'lucide-react';
import Button from '../components/Button';
import Input from '../components/Input';
import ImageCard from '../components/ImageCard';
import { generateImage } from '../services/api';
import type { ImageRecord } from '../services/api';
import './GeneratorPage.css';

export default function GeneratorPage() {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<ImageRecord | null>(null);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsLoading(true);
    setError('');
    
    try {
      const data = await generateImage(prompt);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate image. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="generator-page animate-fade-in">
      <div className="hero-section text-center">
        <h1 className="hero-title">
          Bring your <span className="text-gradient">imagination</span> to life
        </h1>
        <p className="hero-subtitle">
          Enter a prompt below and let our advanced AI generate stunning visuals in seconds.
        </p>
      </div>

      <div className="generator-container">
        <form className="generator-form glass-panel" onSubmit={handleGenerate}>
          <div className="input-group">
            <Input 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="A futuristic city with flying cars at sunset, cyberpunk style..."
              disabled={isLoading}
              error={error}
            />
            <Button type="submit" isLoading={isLoading} disabled={!prompt.trim()}>
              <Sparkles size={20} />
              Generate
            </Button>
          </div>
        </form>

        <div className="result-container">
          {isLoading && (
            <div className="loading-state glass-panel animate-fade-in">
              <div className="spinner-large"></div>
              <p>AI is painting your imagination...</p>
            </div>
          )}

          {!isLoading && result && (
            <div className="success-state animate-fade-in">
              <ImageCard imageUrl={result.file_path} prompt={result.prompt} />
            </div>
          )}

          {!isLoading && !result && !error && (
            <div className="empty-state glass-panel">
              <ImageIcon size={48} className="empty-icon" />
              <p>Your generated image will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
