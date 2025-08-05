export interface StudyRecord {
  id: number
  title: string
  content: string
  category: string
  difficulty: number
  study_time: number
  created_at: string
  updated_at: string
}

export interface StudyRecordCreate {
  title: string
  content: string
  category: string
  difficulty: number
  study_time: number
}

export interface StudyRecordUpdate {
  title?: string
  content?: string
  category?: string
  difficulty?: number
  study_time?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: {
    page: number
    limit: number
    total_items: number
    total_pages: number
  }
} 