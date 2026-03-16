import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { affiliateApi } from "@/api/affiliate";

export function useNotifications() {
  const queryClient = useQueryClient();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => affiliateApi.listNotifications().then((r) => r.data),
    refetchInterval: 30_000, // poll every 30s
  });

  const unreadCount = notifications.filter((n) => !n.read).length;

  const { mutate: markRead } = useMutation({
    mutationFn: (id: string) => affiliateApi.markNotificationRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const { mutate: markAllRead } = useMutation({
    mutationFn: () => affiliateApi.markAllNotificationsRead(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  return { notifications, unreadCount, isLoading, markRead, markAllRead };
}
