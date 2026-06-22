import { Download } from 'lucide-react';
import './ImageCard.css';

interface ImageCardProps {
  imageUrl: string;
  prompt: string;
}

export default function ImageCard({ imageUrl, prompt }: ImageCardProps) {
  const backendUrl = "http://127.0.0.1:8000/"; // In production use .env
  // If imageUrl doesn't start with http, prepend backend URL
  const fullUrl = imageUrl.startsWith("http") ? imageUrl : backendUrl + imageUrl;

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = fullUrl;
    link.download = `AI_Canvas_${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="image-card animate-fade-in">
      <div className="image-wrapper">
        <img src={fullUrl} alt={prompt} loading="lazy" />
        <div className="image-overlay">
          <button className="download-btn" onClick={handleDownload} title="Download">
            <Download size={20} />
          </button>
        </div>
      </div>
      <div className="image-info">
        <p className="image-prompt" title={prompt}>{prompt}</p>
      </div>
    </div>
  );
}
