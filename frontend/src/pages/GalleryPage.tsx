import { useState, useEffect } from 'react';
import { getImages } from '../services/api';
import type { ImageRecord } from '../services/api';
import ImageCard from '../components/ImageCard';
import { Image as ImageIcon } from 'lucide-react';
import './GalleryPage.css';

export default function GalleryPage() {
  const [images, setImages] = useState<ImageRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const data = await getImages();
        setImages(data);
      } catch {
        setError('Failed to load gallery. Make sure backend is running.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchImages();
  }, []);

  return (
    <div className="gallery-page animate-fade-in">
      <div className="gallery-header">
        <h1 className="gallery-title">Your <span className="text-gradient">Gallery</span></h1>
        <p className="gallery-subtitle">A collection of your AI-generated masterpieces</p>
      </div>

      {isLoading ? (
        <div className="loading-state">
          <div className="spinner-large"></div>
        </div>
      ) : error ? (
        <div className="error-state glass-panel">
          <p className="error-text">{error}</p>
        </div>
      ) : images.length === 0 ? (
        <div className="empty-state glass-panel">
          <ImageIcon size={48} className="empty-icon" />
          <p>No images found. Go generate some magic!</p>
        </div>
      ) : (
        <div className="gallery-grid">
          {images.map((img) => (
            <ImageCard key={img.id} imageUrl={img.file_path} prompt={img.prompt} />
          ))}
        </div>
      )}
    </div>
  );
}
