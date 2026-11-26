import { redirect } from 'next/navigation';

export default function ViewPage({ params }: { params: { id: string } }) {
  redirect(`/acconage/view?id=${params.id}`);
}
