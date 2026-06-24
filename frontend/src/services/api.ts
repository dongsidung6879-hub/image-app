import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export interface ImageRecord {
  id: number;
  prompt: string;
  file_path: string;
  created_at: string;
}

export const generateImage = async (prompt: string): Promise<ImageRecord> => {
  const response = await api.post('/generate-image', { prompt });
  return response.data;
};

export const getImages = async (skip = 0, limit = 50): Promise<ImageRecord[]> => {
  const response = await api.get(`/images?skip=${skip}&limit=${limit}`);
  return response.data;
};
