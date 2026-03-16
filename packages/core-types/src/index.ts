// ─── User & Auth ──────────────────────────────────────────────────────────────
export type UserRole = "super_admin" | "admin" | "affiliate";

export interface User {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  last_login: string | null;
}

// ─── Affiliate ────────────────────────────────────────────────────────────────
export type AffiliateStatus = "pending" | "approved" | "rejected" | "suspended";

export interface AffiliateProfile {
  id: string;
  user_id: string;
  status: AffiliateStatus;
  full_name: string;
  phone: string | null;
  bio: string | null;
  tiktok_url: string | null;
  instagram_url: string | null;
  twitter_url: string | null;
  payout_method: string | null;
  bank_name: string | null;
  bank_code: string | null;
  account_number: string | null;
  paystack_recipient_code: string | null;
  last_payout_at: string | null;
  terms_version_accepted: number;
  approved_at: string | null;
  created_at: string;
}

// ─── Store & Products ─────────────────────────────────────────────────────────
export interface Store {
  id: string;
  name: string;
  slug: string;
  website_url: string | null;
  active: boolean;
  created_at: string;
}

export type Currency = "KES" | "USD";

export interface Product {
  id: string;
  store_id: string;
  name: string;
  sku: string | null;
  price: number;
  currency: Currency;
  description: string | null;
  image_url: string | null;
  product_url: string | null;
  category: string | null;
  active: boolean;
  created_at: string;
}

// ─── Campaign ─────────────────────────────────────────────────────────────────
export type CommissionType = "percent" | "fixed";

export interface Campaign {
  id: string;
  name: string;
  product_id: string | null;
  store_id: string | null;
  commission_type: CommissionType;
  rate: number;
  min_sale_amount: number | null;
  cookie_days: number;
  active: boolean;
  expires_at: string | null;
  created_at: string;
}

// ─── Referral ─────────────────────────────────────────────────────────────────
export interface ReferralLink {
  id: string;
  affiliate_id: string;
  campaign_id: string;
  code: string;
  short_url: string;
  is_custom: boolean;
  created_at: string;
  // optional stats
  total_clicks?: number;
  total_conversions?: number;
  total_earned?: number;
}

// ─── Conversion ───────────────────────────────────────────────────────────────
export type ConversionStatus = "pending" | "approved" | "rejected" | "paid";
export type ConversionSource = "api" | "webhook" | "manual";

export interface Conversion {
  id: string;
  referral_link_id: string;
  store_id: string;
  external_order_id: string;
  sale_amount: number;
  commission_earned: number;
  status: ConversionStatus;
  conversion_source: ConversionSource;
  created_at: string;
  approved_at: string | null;
}

// ─── Balance & Payouts ────────────────────────────────────────────────────────
export interface AffiliateBalance {
  pending: number;
  approved: number;
  paid_out: number;
}

export type PayoutStatus = "pending" | "processing" | "paid" | "failed";

export interface PayoutRequest {
  id: string;
  affiliate_id: string;
  amount: number;
  status: PayoutStatus;
  paystack_transfer_code: string | null;
  failure_reason: string | null;
  requested_at: string;
  paid_at: string | null;
}

// ─── Pagination ───────────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// ─── Creative Assets ──────────────────────────────────────────────────────────
export type AssetType = "banner" | "video" | "image" | "text";

export interface CreativeAsset {
  id: number;
  campaign_id: number | null;
  asset_type: AssetType;
  title: string | null;
  url: string;
  size: string | null;
  embed_code: string | null;
  created_at: string;
}

// ─── Notification ─────────────────────────────────────────────────────────────
export interface Notification {
  id: string;
  title: string;
  message: string;
  read: boolean;
  created_at: string;
}
