import Providers from "@/components/Providers";

export default function ReaderLayout({ children }: { children: React.ReactNode }) {
  return <Providers>{children}</Providers>;
}