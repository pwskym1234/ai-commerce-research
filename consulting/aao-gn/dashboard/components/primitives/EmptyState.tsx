import { Card } from "./Card";

export function EmptyState({
  title = "데이터가 없습니다",
  message,
}: {
  title?: string;
  message?: string;
}) {
  return (
    <Card className="text-center text-sm text-ink-500 dark:text-ink-400">
      <div className="font-medium text-ink-700 dark:text-ink-300">{title}</div>
      {message ? <div className="mt-1">{message}</div> : null}
    </Card>
  );
}
