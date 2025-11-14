// API Response Types
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data: T;
  message: string;
}

// Video Task Types
export interface VideoTask {
  id: string;
  name: string;
  task_id: string;
  input_type: string;
  source_url: string | null;
  input_file_url: string | null;
  output_video_url: string | null;
  audio_url: string | null;
  target_language: string;
  voice_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  created_at: string;
  updated_at: string;
  error_message: string | null;
}

export interface Pagination {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface VideoTasksResponse {
  tasks: VideoTask[];
  pagination: Pagination;
}

// URL Preview Types
export interface UrlPreviewData {
  favicon_url: string;
  title: string;
}

export interface UrlPreviewResponse {
  favicon_url: string;
  title: string;
}

// API Error Types
export interface ApiError {
  status: 'error';
  message: string;
  code?: string;
  details?: any;
}

// Voice Type Enum
export enum VoiceType {
  ZEPHYR = 'Zephyr',
  PUCK = 'Puck',
  CHARON = 'Charon',
  KORE = 'Kore',
  FENRIR = 'Fenrir',
  LEDA = 'Leda',
  ORUS = 'Orus',
  AOEDE = 'Aoede',
  CALLIRRHOE = 'Callirrhoe',
  AUTONOE = 'Autonoe',
  ENCELADUS = 'Enceladus',
  IAPETUS = 'Iapetus',
  UMBRIEL = 'Umbriel',
  ALGIEBA = 'Algieba',
  DESPINA = 'Despina',
  ERINOME = 'Erinome',
  ALGENIB = 'Algenib',
  RASALGETHI = 'Rasalgethi',
  LAOMEDEIA = 'Laomedeia',
  ACHERNAR = 'Achernar',
  ALNILAM = 'Alnilam',
  SCHEDAR = 'Schedar',
  GACRUX = 'Gacrux',
  PULCHERRIMA = 'Pulcherrima',
  ACHIRD = 'Achird',
  ZUBENELGENUBI = 'Zubenelgenubi',
  VINDEMIATRIX = 'Vindemiatrix',
  SADACHBIA = 'Sadachbia',
  SADALTAGER = 'Sadaltager',
  SULAFAT = 'Sulafat',
}

// Video Generation Request Types
export interface GenerateVideoParams {
  text?: string;
  file?: File;
  url?: string;
  language?: string;
  voice_type?: VoiceType;
}

// Video Generation Response
export interface GenerateVideoData {
  task_id: string;
}

export type GenerateVideoResponse = GenerateVideoData;

// Subscription Plan Types
export interface PlanPeriod {
  period: 'monthly' | 'yearly';
  price: number;
  product_id: string;
  billing_cycle_months: number;
  billing_amount: number;
  billing_description: string;
}

export interface SubscriptionPlan {
  type: 'basic' | 'pro' | 'enterprise';
  name: string;
  monthly_credits: number;
  description: string;
  periods: PlanPeriod[];
}

export interface SubscriptionPlansData {
  plans: SubscriptionPlan[];
}

export type SubscriptionPlansResponse = SubscriptionPlansData;

// Subscription Payment Types
export enum SubscriptionType {
  BASIC = 'basic',
  PRO = 'pro',
  ENTERPRISE = 'enterprise',
}

export enum SubscriptionPeriod {
  MONTHLY = 'monthly',
  YEARLY = 'yearly',
}

export interface CreateSubscriptionPaymentParams {
  product_id: string;
  subscription_type: SubscriptionType;
  subscription_period: SubscriptionPeriod;
}

export interface CreateSubscriptionPaymentData {
  payment_url: string;
}

export type CreateSubscriptionPaymentResponse = CreateSubscriptionPaymentData;

// Credit Transaction Types
export enum TransactionType {
  MONTHLY_GRANT = 'monthly_grant',      // Monthly grant
  MONTHLY_RECLAIM = 'monthly_reclaim',  // Monthly credit reclaim (clear unused credits from previous month)
  TASK_CONSUME = 'task_consume',        // Task consumption
  REFUND = 'refund',                    // Refund
  ADMIN_ADJUST = 'admin_adjust',        // Admin adjustment
  PURCHASE = 'purchase',                // Purchase
  REDEEM = 'redeem',                    // Redeem code
}

export interface CreditTransaction {
  id: string;
  user_id: string;
  task_id: string | null;
  subscription_id: string | null;
  transaction_type: TransactionType;
  amount: number;
  balance_after: number;
  description: string;
  created_at: string;
}

export interface CreditTransactionsData {
  total: number;
  transactions: CreditTransaction[];
  current_balance: number;
}

export type CreditTransactionsResponse = CreditTransactionsData;

// Redeem Code Types
export interface RedeemCodeParams {
  code: string;
}

export interface RedeemCodeData {
  transaction_id: string;
  credit_amount: number;
  balance_after: number;
  code: string;
}

export type RedeemCodeResponse = RedeemCodeData;
