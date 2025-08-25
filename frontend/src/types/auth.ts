export interface User {
  id: string;
  username: string;
  email: string;
  fullName: string;
  role: 'admin' | 'user' | 'analyst';
  permissions: string[];
  oracleConnections: OracleConnection[];
}

export interface OracleConnection {
  id: string;
  name: string;
  host: string;
  port: number;
  serviceName: string;
  username: string;
  isActive: boolean;
  lastConnected?: Date;
  status: 'connected' | 'disconnected' | 'error';
}

export interface LoginCredentials {
  username: string;
  password: string;
  rememberMe?: boolean;
}

export interface OracleConnectionForm {
  name: string;
  host: string;
  port: number;
  serviceName: string;
  username: string;
  password: string;
  testConnection?: boolean;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  addOracleConnection: (connection: OracleConnectionForm) => Promise<void>;
  removeOracleConnection: (connectionId: string) => Promise<void>;
  testOracleConnection: (connection: OracleConnectionForm) => Promise<boolean>;
  setActiveConnection: (connectionId: string) => Promise<void>;
}
