import { env } from './env';

export async function fetchHealth() {
  const response = await fetch(`${env.NEXT_PUBLIC_API_URL}/api/v1/health`);
  if (!response.ok) {
    throw new Error('Failed to fetch backend health state');
  }
  return response.json();
}
