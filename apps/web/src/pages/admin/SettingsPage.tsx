import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { adminApi } from "@/api/admin";

const SETTING_LABELS: Record<string, { label: string; hint: string; type: "text" | "number" | "boolean" }> = {
  default_commission_rate: {
    label: "Default Commission Rate",
    hint: "Decimal fraction, e.g. 0.10 = 10%",
    type: "number",
  },
  min_payout_threshold: {
    label: "Minimum Payout Threshold (KES)",
    hint: "Minimum amount affiliates must earn before requesting a payout",
    type: "number",
  },
  cookie_days: {
    label: "Referral Cookie Duration (days)",
    hint: "How long the referral cookie stays valid after a click",
    type: "number",
  },
  require_affiliate_approval: {
    label: "Require Affiliate Approval",
    hint: "When enabled, new affiliates start as pending until approved by an admin",
    type: "boolean",
  },
  terms_version: {
    label: "Terms Version",
    hint: "Current terms and conditions version number",
    type: "number",
  },
};

export default function AdminSettingsPage() {
  const queryClient = useQueryClient();
  const { data: settings, isLoading } = useQuery({
    queryKey: ["admin-settings"],
    queryFn: () => adminApi.getSettings().then((r) => r.data),
  });

  const [form, setForm] = useState<Record<string, string>>({});
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (settings) {
      setForm(settings);
      setDirty(false);
    }
  }, [settings]);

  const { mutate: saveSettings, isPending } = useMutation({
    mutationFn: (data: Record<string, string>) => adminApi.updateSettings(data),
    onSuccess: () => {
      toast.success("Settings saved");
      queryClient.invalidateQueries({ queryKey: ["admin-settings"] });
      setDirty(false);
    },
    onError: () => toast.error("Failed to save settings"),
  });

  const handleChange = (key: string, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setDirty(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    saveSettings(form);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-40">
        <div className="w-8 h-8 border-4 border-yu-gold-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const knownKeys = Object.keys(SETTING_LABELS);
  const unknownKeys = Object.keys(form).filter((k) => !knownKeys.includes(k));

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold">Platform Settings</h1>
        <p className="text-gray-500 text-sm mt-1">
          These settings take effect immediately after saving.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="card space-y-5">
          {knownKeys.map((key) => {
            const meta = SETTING_LABELS[key];
            const value = form[key] ?? "";

            return (
              <div key={key}>
                <label className="label">{meta.label}</label>
                {meta.type === "boolean" ? (
                  <div className="flex items-center gap-3 mt-1">
                    <button
                      type="button"
                      onClick={() =>
                        handleChange(key, value === "true" ? "false" : "true")
                      }
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        value === "true" ? "bg-yu-gold-500" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                          value === "true" ? "translate-x-6" : "translate-x-1"
                        }`}
                      />
                    </button>
                    <span className="text-sm text-gray-700">
                      {value === "true" ? "Enabled" : "Disabled"}
                    </span>
                  </div>
                ) : (
                  <input
                    type={meta.type === "number" ? "text" : "text"}
                    value={value}
                    onChange={(e) => handleChange(key, e.target.value)}
                    className="input mt-1"
                    inputMode={meta.type === "number" ? "decimal" : "text"}
                  />
                )}
                <p className="text-xs text-gray-400 mt-1">{meta.hint}</p>
              </div>
            );
          })}

          {unknownKeys.length > 0 && (
            <>
              <hr />
              <p className="text-xs text-gray-400 uppercase tracking-wide font-semibold">
                Other settings
              </p>
              {unknownKeys.map((key) => (
                <div key={key}>
                  <label className="label">{key}</label>
                  <input
                    type="text"
                    value={form[key] ?? ""}
                    onChange={(e) => handleChange(key, e.target.value)}
                    className="input mt-1"
                  />
                </div>
              ))}
            </>
          )}
        </div>

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={!dirty || isPending}
            className="btn-primary disabled:opacity-50"
          >
            {isPending ? "Saving…" : "Save Settings"}
          </button>
          {dirty && (
            <span className="text-sm text-amber-600">Unsaved changes</span>
          )}
        </div>
      </form>
    </div>
  );
}
