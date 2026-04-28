import { notFound } from "next/navigation";
import { loadBrandData } from "@/lib/data";
import { isValidSlug } from "@/lib/paths";
import { BrandReportBody } from "@/components/report/BrandReportBody";

export const dynamic = "force-dynamic";

export default async function BrandPage({
  params,
}: {
  params: { brand: string };
}) {
  if (!isValidSlug(params.brand)) notFound();
  const data = await loadBrandData(params.brand);
  if (!data) notFound();

  return <BrandReportBody brand={params.brand} data={data} />;
}
