import { useState } from "react";
import { Bell, X } from "lucide-react";
import { useNotifications } from "@/hooks/useNotifications";

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const { notifications, unreadCount, markRead, markAllRead } = useNotifications();

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
        aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ""}`}
      >
        <Bell size={20} className="text-gray-600" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-20" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border z-30 max-h-96 flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b">
              <h3 className="font-semibold text-sm">Notifications</h3>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <button
                    onClick={() => markAllRead()}
                    className="text-xs text-yu-gold-600 hover:underline"
                  >
                    Mark all read
                  </button>
                )}
                <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-gray-600">
                  <X size={16} />
                </button>
              </div>
            </div>

            <div className="overflow-y-auto flex-1">
              {notifications.length === 0 ? (
                <p className="text-center text-gray-400 text-sm py-8">No notifications</p>
              ) : (
                notifications.map((n) => (
                  <div
                    key={n.id}
                    onClick={() => !n.read && markRead(String(n.id))}
                    className={`px-4 py-3 border-b last:border-0 cursor-pointer hover:bg-gray-50 transition-colors ${
                      !n.read ? "bg-amber-50" : ""
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {!n.read && (
                        <span className="mt-1.5 w-2 h-2 bg-yu-gold-500 rounded-full shrink-0" />
                      )}
                      <div className={!n.read ? "" : "pl-4"}>
                        <p className="text-sm font-medium text-gray-800">{n.title}</p>
                        <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{n.message}</p>
                        <p className="text-[11px] text-gray-400 mt-1">
                          {new Date(n.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
