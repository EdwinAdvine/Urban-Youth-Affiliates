import api from "./client";
import type {
  AffiliateBalance,
  AffiliateProfile,
  Conversion,
  CreativeAsset,
  Notification,
  PaginatedResponse,
  PayoutRequest,
  Product,
  ReferralLink,
} from "@yua/core-types";

export const affiliateApi = {
  // Dashboard
  getDashboard: () =>
    api.get<{
      profile: AffiliateProfile;
      balance: AffiliateBalance;
      total_clicks: number;
      total_conversions: number;
      conversion_rate: number;
      recent_conversions: Conversion[];
    }>("/affiliate/dashboard"),

  // Profile
  getProfile: () => api.get<AffiliateProfile>("/affiliate/profile"),
  updateProfile: (data: Partial<AffiliateProfile>) =>
    api.patch<AffiliateProfile>("/affiliate/profile", data),
  listBanks: (country = "kenya") =>
    api.get<{ banks: Array<{ id: number; name: string; code: string; slug: string }> }>(
      "/affiliate/banks",
      { params: { country } }
    ),

  updateBankDetails: (data: {
    bank_name: string;
    bank_code: string;
    account_number: string;
    payout_method?: string;
  }) => api.patch<AffiliateProfile>("/affiliate/profile/bank-details", data),

  // Links
  generateLink: (data: { campaign_id: string }) =>
    api.post<ReferralLink>("/affiliate/links", data),
  listLinks: (params?: { page?: number; page_size?: number }) =>
    api.get<PaginatedResponse<ReferralLink>>("/affiliate/links", { params }),

  // Earnings / Conversions
  getBalance: () => api.get<AffiliateBalance>("/affiliate/earnings/balance"),
  listConversions: (params?: {
    page?: number;
    status?: string;
    from?: string;
    to?: string;
  }) => api.get<PaginatedResponse<Conversion>>("/affiliate/earnings/conversions", { params }),

  // Payouts
  requestPayout: (data: { amount: number }) =>
    api.post<PayoutRequest>("/affiliate/payouts", data),
  listPayouts: (params?: { page?: number }) =>
    api.get<PaginatedResponse<PayoutRequest>>("/affiliate/payouts", { params }),

  // Marketplace
  listProducts: (params?: {
    page?: number;
    page_size?: number;
    store_id?: string;
    category?: string;
    search?: string;
  }) =>
    api.get<
      PaginatedResponse<
        Product & { campaign_id: string; commission_type: string; commission_rate: number }
      >
    >("/affiliate/marketplace", { params }),

  // Creative assets (per campaign)
  listCampaignAssets: (campaign_id: number) =>
    api.get<CreativeAsset[]>("/affiliate/creative-assets", { params: { campaign_id } }),

  // Stats — daily series (for charts)
  getStatsDaily: (days = 30) =>
    api.get<{
      days: number;
      series: Array<{ date: string; clicks: number; conversions: number }>;
    }>("/affiliate/stats/daily", { params: { days } }),

  // Stats — period totals (date-range)
  getStats: (params?: { from?: string; to?: string }) =>
    api.get<{
      period: { from: string | null; to: string | null };
      summary: {
        total_links: number;
        total_clicks: number;
        total_conversions: number;
        approved_conversions: number;
        conversion_rate: number;
        total_earned: number;
      };
      balance: { pending: number; approved: number; paid_out: number };
      top_links: Array<{
        id: number;
        code: string;
        short_url: string;
        clicks: number;
        conversions: number;
        earned: number;
      }>;
    }>("/affiliate/stats", { params }),

  // Notifications
  listNotifications: () => api.get<Notification[]>("/affiliate/notifications"),
  markNotificationRead: (id: string) => api.patch(`/affiliate/notifications/${id}/read`),
  markAllNotificationsRead: () => api.post("/affiliate/notifications/read-all"),

  // Public profile (no auth needed, but available here for convenience)
  getPublicProfile: (affiliateId: string | number) =>
    api.get<{
      id: number;
      full_name: string;
      bio: string | null;
      tiktok_url: string | null;
      instagram_url: string | null;
      twitter_url: string | null;
      member_since: string | null;
      stats: {
        total_links: number;
        total_clicks: number;
        total_conversions: number;
        conversion_rate: number;
      };
    }>(`/public/affiliates/${affiliateId}`),
};
