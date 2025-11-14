import { apiClient } from '../api-client';
import { 
  VideoTasksResponse, 
  VideoTask, 
  UrlPreviewResponse,
  GenerateVideoParams,
  GenerateVideoResponse,
  VoiceType
} from '../types/api';

// Query parameters for getting video tasks
export interface GetVideoTasksParams {
  page?: number;
  page_size?: number;
  status?: VideoTask['status'];
  input_type?: string;
  target_language?: string;
  voice_type?: string;
  sort_by?: 'created_at' | 'updated_at' | 'progress';
  sort_order?: 'asc' | 'desc';
}

/**
 * Get all video tasks with optional filtering and pagination
 * @param params Query parameters for filtering and pagination
 * @returns Promise with video tasks and pagination info
 */
export async function getTasks(params?: GetVideoTasksParams) {
  return apiClient.get<VideoTasksResponse>('/video/tasks', params);
}

/**
 * Get URL preview metadata (favicon and title)
 * @param url The URL to get preview for
 * @returns Promise with URL preview data
 */
export async function getUrlPreview(url: string) {
  return apiClient.get<UrlPreviewResponse>('/video/url-preview', { url });
}

/**
 * Generate a video from text, file, or URL
 * @param params Video generation parameters (text, file, url, language, voice_type)
 * @returns Promise with task_id
 */
export async function generateVideo(params: GenerateVideoParams) {
  const formData = new FormData();

  // Add text if provided
  if (params.text) {
    formData.append('text', params.text);
  }

  // Add file if provided
  if (params.file) {
    formData.append('file', params.file);
  }

  // Add URL if provided
  if (params.url) {
    formData.append('url', params.url);
  }

  // Add language (default to 'en')
  formData.append('language', params.language || 'en');

  // Add voice type (default to ACHERNAR)
  formData.append('voice_type', params.voice_type || VoiceType.ACHERNAR);

  return apiClient.postFormData<GenerateVideoResponse>('/video/generate', formData);
}
