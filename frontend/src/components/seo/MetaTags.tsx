interface MetaTagsProps {
  title: string;
  description: string;
}

export function MetaTags({ title, description }: MetaTagsProps) {
  return (
    <>
      <meta name="description" content={description} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
    </>
  );
}