import axios, { AxiosInstance } from 'axios';
import type { WarpRequest, WarpResponse, HealthResponse, BaselineResponse } from '../types';

class EchoZeroAPI {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async health(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  async baseline(): Promise<BaselineResponse> {
    const response = await this.client.get<BaselineResponse>('/baseline');
    return response.data;
  }

  async warp(request: WarpRequest): Promise<WarpResponse> {
    const response = await this.client.post<WarpResponse>('/warp', request);
    return response.data;
  }

  async warpDemo(request: WarpRequest): Promise<WarpResponse> {
    const response = await this.client.post<WarpResponse>('/warp/demo', request);
    return response.data;
  }
}

export const api = new EchoZeroAPI();
export default api;
