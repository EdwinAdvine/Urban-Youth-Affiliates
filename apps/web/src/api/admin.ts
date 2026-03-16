import api from "./client";
import type {
  AffiliateProfile,
  Campaign,
  Conversion,
  CreativeAsset,
  PaginatedResponse,
  PayoutRequest,
  Product,
  Store,
} from "@yua/core-types";

// ─── Stores ───────────────────────────────────────────────────────────────────
export const adminApi = {
  // Stores
  listStores: (params?: { page?: number; page_size?: number }) =>
    api.get<PaginatedResponse<Store>>("/admin/stores", { params }),
  createStore: (data: Partial<Store>) => api.post<Store>("/admin/stores", data),
  updateStore: (id: string, data: Partial<Store>) =>
    api.patch<Store>(`/admin/stores/${id}`, data),
  deleteStore: (id: string) => api.delete(`/admin/stores/${id}`),

  // Products
  listProducts: (params?: { page?: number; store_id?: string; category?: string; search?: string }) =>
    api.get<PaginatedResponse<Product>>("/admin/products", { params }),
  createProduct: (data: Partial<Product>) => api.post<Product>("/admin/products", data),
  updateProduct: (id: string, data: Partial<Product>) =>
    api.patch<Product>(`/admin/products/${id}`, data),
  deleteProduct: (id: string) => api.delete(`/admin/products/${id}`),

  // Campaigns
  listCampaigns: (params?: { page?: number; active?: boolean }) =>
    api.get<PaginatedResponse<Campaign>>("/admin/campaigns", { params }),
  createCampaign: (data: Partial<Campaign>) => api.post<Campaign>("/admin/campaigns", data),
  updateCampaign: (id: string, data: Partial<Campaign>) =>
    api.patch<Campaign>(`/admin/campaigns/${id}`, data),
  deleteCampaign: (id: string) => api.delete(`/admin/campaigns/${id}`),

  // Affiliates
  listAffiliates: (params?: { page?: number; status?: string; search?: string }) =>
    api.get<PaginatedResponse<AffiliateProfile>>("/admin/affiliates", { params }),
  affiliateAction: (id: string, action: "approve" | "reject" | "suspend", notes?: string) =>
    api.post(`/admin/affiliates/${id}/action`, { action, notes }),

  // Conversions
  listConversions: (params?: { page?: number; status?: string; affiliate_id?: string }) =>
    api.get<PaginatedResponse<Conversion>>("/admin/conversions", { params }),
  conversionAction: (id: string, action: "approve" | "reject", notes?: string) =>
    api.post(`/admin/conversions/${id}/action`, { action, notes }),

  // Payouts
  listPayouts: (params?: { page?: number; status?: string }) =>
    api.get<PaginatedResponse<PayoutRequest>>("/admin/payouts", { params }),
  approvePayout: (id: string) => api.post(`/admin/payouts/${id}/approve`),

  // Analytics
  getAnalytics: (params?: { from?: string; to?: string }) =>
    api.get<{
      total_affiliates: number;
      pending_approvals: number;
      total_clicks: number;
      total_conversions: number;
      conversion_rate: number;
      total_revenue: number;
      total_commissions: number;
      pending_payouts: number;
      top_affiliates: Array<{ affiliate_id: string; full_name: string; earned: number; conversions: number }>;
      top_products: Array<{ product_id: string; name: string; conversions: number; revenue: number }>;
    }>("/admin/analytics", { params }),

  // Settings
  getSettings: () => api.get<Record<string, string>>("/admin/settings"),
  updateSettings: (data: Record<string, string>) => api.patch("/admin/settings", data),

  // Creative assets
  listAssets: (params?: { campaign_id?: number; asset_type?: string }) =>
    api.get<CreativeAsset[]>("/admin/creative-assets", { params }),
  createAsset: (data: Partial<CreativeAsset>) =>
    api.post<CreativeAsset>("/admin/creative-assets", data),
  updateAsset: (id: number, data: Partial<CreativeAsset>) =>
    api.patch<CreativeAsset>(`/admin/creative-assets/${id}`, data),
  deleteAsset: (id: number) => api.delete(`/admin/creative-assets/${id}`),
};
