import { notFound } from "next/navigation";
import { loadBrandData } from "@/lib/data";
import { isValidSlug, isValidTimestamp } from "@/lib/paths";
import { BrandReportBody } from "@/components/report/BrandReportBody";

export const dynamic = "force-dynamic";

export default async function BrandSnapshotPage({
  params,
}: {
  params: { brand: string; timestamp: string };
}) {
  if (!isValidSlug(params.brand) || !isValidTimestamp(params.timestamp)) notFound();
  const data = await loadBrandData(params.brand, params.timestamp);
  if (!data) notFound();

  return <BrandReportBody brand={params.brand} data={data} />;
}
