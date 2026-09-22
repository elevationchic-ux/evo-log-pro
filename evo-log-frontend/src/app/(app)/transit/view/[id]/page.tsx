import { redirect } from 'next/navigation';

export default function ViewPage({ params }: { params: { id: string } }) {
  redirect(`/transit/view?id=${params.id}`);
}
