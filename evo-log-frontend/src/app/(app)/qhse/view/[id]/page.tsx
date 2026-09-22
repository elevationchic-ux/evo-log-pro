import { redirect } from 'next/navigation';

export default function ViewPage({ params }: { params: { id: string } }) {
  redirect(`/qhse/view?id=${params.id}`);
}
