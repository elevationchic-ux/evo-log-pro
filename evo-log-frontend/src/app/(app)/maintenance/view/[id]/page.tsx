import { redirect } from 'next/navigation';

export default function ViewPage({ params }: { params: { id: string } }) {
  redirect(`/maintenance/view?id=${params.id}`);
}
