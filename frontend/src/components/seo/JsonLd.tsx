import { constructSoftwareApplicationJsonLd } from "@/lib/seo";

export function JsonLd() {
  const schemaData = constructSoftwareApplicationJsonLd();

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }}
    />
  );
}