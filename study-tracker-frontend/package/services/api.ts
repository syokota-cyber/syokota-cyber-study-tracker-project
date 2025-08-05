// API Service for StudyTracker
// FastAPIとの通信を行うサービスクラス

// 学習記録の型定義
export interface StudyRecord {
  id: number;
  title: string;
  category: string;
  difficulty: number;
  study_time: number;
  content: string;
  created_at: string;
  updated_at: string;
}

// 学習記録作成用の型定義
export interface StudyRecordCreate {
  title: string;
  category: string;
  difficulty: number;
  study_time: number;
  content: string;
}

// 学習記録更新用の型定義
export interface StudyRecordUpdate {
  title?: string;
  category?: string;
  difficulty?: number;
  study_time?: number;
  content?: string;
}

// 統計情報の型定義
export interface StudyStats {
  total_records: number;
  total_study_time: number;
  average_difficulty: number;
  categories: { [key: string]: number };
  difficulties: { [key: string]: number };
}

// API設定
const API_BASE_URL = 'http://localhost:8000/api/v1';

// API Serviceクラス
export class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // 学習記録一覧取得
  async getStudyRecords(page: number = 1, limit: number = 10): Promise<{
    records: StudyRecord[];
    total: number;
    page: number;
    limit: number;
  }> {
    try {
      const response = await fetch(
        `${this.baseUrl}/study-records/paginated?page=${page}&limit=${limit}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return {
        records: data.items,
        total: data.pagination.total_items,
        page: data.pagination.page,
        limit: data.pagination.limit
      };
    } catch (error) {
      console.error('学習記録取得エラー:', error);
      throw error;
    }
  }

  // 学習記録詳細取得
  async getStudyRecord(id: number): Promise<StudyRecord> {
    try {
      const response = await fetch(`${this.baseUrl}/study-records/${id}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('学習記録詳細取得エラー:', error);
      throw error;
    }
  }

  // 学習記録作成
  async createStudyRecord(record: StudyRecordCreate): Promise<StudyRecord> {
    try {
      const response = await fetch(`${this.baseUrl}/study-records`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(record),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('学習記録作成エラー:', error);
      throw error;
    }
  }

  // 学習記録更新
  async updateStudyRecord(id: number, record: StudyRecordUpdate): Promise<StudyRecord> {
    try {
      const response = await fetch(`${this.baseUrl}/study-records/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(record),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('学習記録更新エラー:', error);
      throw error;
    }
  }

  // 学習記録削除
  async deleteStudyRecord(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/study-records/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('学習記録削除エラー:', error);
      throw error;
    }
  }

  // 統計情報取得
  async getStudyStats(): Promise<StudyStats> {
    try {
      const response = await fetch(`${this.baseUrl}/study-records/stats/summary`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('統計情報取得エラー:', error);
      throw error;
    }
  }

  // カテゴリ別統計取得
  async getCategoryStats(): Promise<{ [key: string]: number }> {
    try {
      const response = await fetch(`${this.baseUrl}/study-records/stats/category`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('カテゴリ統計取得エラー:', error);
      throw error;
    }
  }

  // 難易度別統計取得
  async getDifficultyStats(): Promise<{ [key: string]: number }> {
    try {
      const response = await fetch(`${this.baseUrl}/study-records/stats/difficulty`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('難易度統計取得エラー:', error);
      throw error;
    }
  }
}

// デフォルトインスタンスのエクスポート
export const apiService = new ApiService(); 