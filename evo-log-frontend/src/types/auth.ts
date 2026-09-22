export interface AuthUser {
  id: string
  email: string
  role: string
}
// API Service for Auth Module

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

export interface MFAVerification {
  code: string;
  method: 'sms' | 'email' | 'authenticator';
}

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    username: string;
    email: string;
    role: string;
  };
  mfaRequired: boolean;
}

