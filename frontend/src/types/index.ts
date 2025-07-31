// Branded types for domain safety
export type UserId = string & { readonly brand: unique symbol };
export type DocumentId = string & { readonly brand: unique symbol };
export type WorkspaceId = string & { readonly brand: unique symbol };
export type CommentId = string & { readonly brand: unique symbol };
export type VersionId = string & { readonly brand: unique symbol };

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// User Management
export interface User {
  id: UserId;
  email: string;
  name: string;
  avatar?: string;
  role: UserRole;
  permissions: Permission[];
  preferences: UserPreferences;
  createdAt: string;
  updatedAt: string;
  lastLoginAt?: string;
  isActive: boolean;
}

export type UserRole = "admin" | "editor" | "viewer" | "guest";

export interface Permission {
  resource: string;
  actions: string[];
}

export interface UserPreferences {
  theme: "light" | "dark" | "system";
  language: string;
  timezone: string;
  notifications: NotificationSettings;
  accessibility: AccessibilitySettings;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  inApp: boolean;
  frequency: "immediate" | "daily" | "weekly";
}

export interface AccessibilitySettings {
  highContrast: boolean;
  reducedMotion: boolean;
  fontSize: "small" | "medium" | "large";
  screenReader: boolean;
}

// Document Management
export interface Document {
  id: DocumentId;
  title: string;
  content: DocumentContent;
  workspaceId: WorkspaceId;
  authorId: UserId;
  collaborators: UserId[];
  tags: string[];
  status: DocumentStatus;
  visibility: DocumentVisibility;
  version: number;
  createdAt: string;
  updatedAt: string;
  publishedAt?: string;
  metadata: DocumentMetadata;
}

export interface DocumentContent {
  blocks: DocumentBlock[];
  version: number;
  lastModified: string;
}

export interface DocumentBlock {
  id: string;
  type: BlockType;
  content: any;
  metadata?: Record<string, any>;
  children?: DocumentBlock[];
}

export type BlockType =
  | "paragraph"
  | "heading"
  | "list"
  | "code"
  | "image"
  | "table"
  | "quote"
  | "divider"
  | "embed"
  | "ai-assistant";

export type DocumentStatus = "draft" | "review" | "published" | "archived";
export type DocumentVisibility = "public" | "private" | "shared" | "restricted";

export interface DocumentMetadata {
  wordCount: number;
  readingTime: number;
  lastEditor: UserId;
  editHistory: EditHistory[];
  aiGenerated: boolean;
  aiConfidence?: number;
  citations: Citation[];
}

export interface EditHistory {
  version: number;
  editorId: UserId;
  timestamp: string;
  changes: Change[];
}

export interface Change {
  type: "insert" | "delete" | "update";
  blockId: string;
  content: any;
}

export interface Citation {
  id: string;
  source: string;
  title: string;
  url?: string;
  confidence: number;
  context: string;
}

// Workspace Management
export interface Workspace {
  id: WorkspaceId;
  name: string;
  description?: string;
  ownerId: UserId;
  members: WorkspaceMember[];
  settings: WorkspaceSettings;
  createdAt: string;
  updatedAt: string;
}

export interface WorkspaceMember {
  userId: UserId;
  role: WorkspaceRole;
  joinedAt: string;
  permissions: Permission[];
}

export type WorkspaceRole = "owner" | "admin" | "editor" | "viewer";

export interface WorkspaceSettings {
  allowGuestAccess: boolean;
  requireApproval: boolean;
  aiFeatures: boolean;
  collaboration: boolean;
  versioning: boolean;
}

// Search and Discovery
export interface SearchQuery {
  query: string;
  filters: SearchFilters;
  sort: SearchSort;
  pagination: PaginationParams;
}

export interface SearchFilters {
  workspaceId?: WorkspaceId;
  authorId?: UserId;
  tags?: string[];
  status?: DocumentStatus[];
  dateRange?: DateRange;
  contentType?: BlockType[];
}

export interface DateRange {
  start: string;
  end: string;
}

export interface SearchSort {
  field: "relevance" | "title" | "createdAt" | "updatedAt" | "popularity";
  direction: "asc" | "desc";
}

export interface PaginationParams {
  page: number;
  limit: number;
}

export interface SearchResult {
  documents: Document[];
  suggestions: string[];
  facets: SearchFacets;
  totalResults: number;
  queryTime: number;
}

export interface SearchFacets {
  authors: FacetItem[];
  tags: FacetItem[];
  workspaces: FacetItem[];
  status: FacetItem[];
}

export interface FacetItem {
  value: string;
  count: number;
  selected: boolean;
}

// AI Integration
export interface AIRequest {
  prompt: string;
  context: AIContext;
  options: AIOptions;
}

export interface AIContext {
  documentId?: DocumentId;
  workspaceId?: WorkspaceId;
  userHistory: string[];
  relatedDocuments: DocumentId[];
}

export interface AIOptions {
  model: AIModel;
  temperature: number;
  maxTokens: number;
  includeCitations: boolean;
  language: string;
}

export type AIModel =
  | "gpt-4"
  | "gpt-3.5-turbo"
  | "claude-3"
  | "claude-3-sonnet";

export interface AIResponse {
  content: string;
  confidence: number;
  citations: Citation[];
  suggestions: string[];
  metadata: AIMetadata;
}

export interface AIMetadata {
  model: AIModel;
  tokensUsed: number;
  processingTime: number;
  cost: number;
}

// Real-time Collaboration
export interface CollaborationSession {
  id: string;
  documentId: DocumentId;
  participants: CollaborationParticipant[];
  cursors: CursorPosition[];
  selections: TextSelection[];
  locks: DocumentLock[];
}

export interface CollaborationParticipant {
  userId: UserId;
  name: string;
  avatar?: string;
  color: string;
  isOnline: boolean;
  lastActivity: string;
}

export interface CursorPosition {
  userId: UserId;
  blockId: string;
  position: number;
  timestamp: string;
}

export interface TextSelection {
  userId: UserId;
  blockId: string;
  start: number;
  end: number;
  timestamp: string;
}

export interface DocumentLock {
  userId: UserId;
  blockId: string;
  timestamp: string;
}

// Analytics and Metrics
export interface AnalyticsEvent {
  eventType: string;
  userId?: UserId;
  documentId?: DocumentId;
  workspaceId?: WorkspaceId;
  metadata: Record<string, any>;
  timestamp: string;
  sessionId: string;
}

export interface UserAnalytics {
  userId: UserId;
  documentsCreated: number;
  documentsEdited: number;
  searchQueries: number;
  aiInteractions: number;
  collaborationTime: number;
  lastActivity: string;
}

export interface DocumentAnalytics {
  documentId: DocumentId;
  views: number;
  uniqueViews: number;
  edits: number;
  shares: number;
  timeSpent: number;
  popularSections: string[];
}

// Error Handling
export interface AppError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
  userId?: UserId;
  sessionId: string;
}

export type ErrorCode =
  | "AUTHENTICATION_FAILED"
  | "AUTHORIZATION_DENIED"
  | "RESOURCE_NOT_FOUND"
  | "VALIDATION_ERROR"
  | "RATE_LIMIT_EXCEEDED"
  | "AI_SERVICE_UNAVAILABLE"
  | "COLLABORATION_CONFLICT"
  | "NETWORK_ERROR"
  | "INTERNAL_SERVER_ERROR";

// UI State Management
export interface UIState {
  theme: "light" | "dark" | "system";
  sidebar: {
    isOpen: boolean;
    activeTab: string;
  };
  modals: {
    [key: string]: boolean;
  };
  notifications: Notification[];
  loading: {
    [key: string]: boolean;
  };
  errors: AppError[];
}

export interface Notification {
  id: string;
  type: "success" | "error" | "warning" | "info";
  title: string;
  message: string;
  action?: NotificationAction;
  timestamp: string;
  read: boolean;
}

export interface NotificationAction {
  label: string;
  onClick: () => void;
}

// Form Types
export interface FormField {
  name: string;
  label: string;
  type:
    | "text"
    | "email"
    | "password"
    | "textarea"
    | "select"
    | "checkbox"
    | "radio";
  required: boolean;
  validation?: ValidationRule[];
  options?: FormOption[];
  placeholder?: string;
  defaultValue?: any;
}

export interface ValidationRule {
  type: "required" | "email" | "minLength" | "maxLength" | "pattern" | "custom";
  value?: any;
  message: string;
}

export interface FormOption {
  value: string;
  label: string;
  disabled?: boolean;
}

// API Endpoints
export type ApiEndpoint =
  | "/api/auth/login"
  | "/api/auth/logout"
  | "/api/auth/register"
  | "/api/users"
  | "/api/documents"
  | "/api/workspaces"
  | "/api/search"
  | "/api/ai/generate"
  | "/api/ai/chat"
  | "/api/analytics"
  | "/api/collaboration";

// Utility Types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequireFields<T, K extends keyof T> = T & { [P in K]-?: T[P] };

export type PickByType<T, U> = {
  [K in keyof T]: T[K] extends U ? K : never;
}[keyof T];

export type ValueOf<T> = T[keyof T];
