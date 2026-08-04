export interface UserRef {
  id: number;
  email: string;
  role: string;
}

export interface HealthState {
  status: string;
  service: string;
  version: string;
}
