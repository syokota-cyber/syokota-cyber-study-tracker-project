// 認証API Service for StudyTracker
// JWT認証関連のAPI呼び出しを行うサービスクラス

// 認証関連の型定義
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  message: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

// API設定
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://learninggarden.studio/api/v1'
  : 'http://localhost:8000/api/v1';

// 認証API Serviceクラス
export class AuthService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // トークンをローカルストレージに保存
  private saveToken(token: string): void {
    localStorage.setItem('auth_token', token);
  }

  // ローカルストレージからトークンを取得
  private getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  // ローカルストレージからトークンを削除
  private removeToken(): void {
    localStorage.removeItem('auth_token');
  }

  // テスト用ログイン（開発環境用）
  async testLogin(): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/test-login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: AuthResponse = await response.json();
      this.saveToken(data.access_token);
      return data;
    } catch (error) {
      console.error('テストログインエラー:', error);
      throw error;
    }
  }

  // ユーザーログイン
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const formData = new FormData();
      formData.append('username', credentials.email); // OAuth2PasswordBearerの仕様
      formData.append('password', credentials.password);

      const response = await fetch(`${this.baseUrl}/auth/login`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: AuthResponse = await response.json();
      this.saveToken(data.access_token);
      return data;
    } catch (error) {
      console.error('ログインエラー:', error);
      throw error;
    }
  }

  // ユーザー登録
  async register(userData: RegisterData): Promise<User> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('登録エラー:', error);
      throw error;
    }
  }

  // 現在のユーザー情報取得
  async getCurrentUser(): Promise<User> {
    try {
      const token = this.getToken();
      if (!token) {
        throw new Error('認証トークンがありません');
      }

      const response = await fetch(`${this.baseUrl}/auth/users/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('ユーザー情報取得エラー:', error);
      throw error;
    }
  }

  // ログアウト
  logout(): void {
    this.removeToken();
  }

  // 認証状態チェック
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  // 認証ヘッダーを取得（他のAPI呼び出しで使用）
  getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    if (!token) {
      return {};
    }
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }
}

// デフォルトインスタンスのエクスポート
export const authService = new AuthService();
