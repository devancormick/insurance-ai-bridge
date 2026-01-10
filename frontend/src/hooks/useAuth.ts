import { useSession, signOut } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export function useAuth(requireAuth: boolean = false) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (requireAuth && status === 'unauthenticated') {
      router.push('/auth/signin');
    }
  }, [status, requireAuth, router]);

  const logout = async () => {
    await signOut({ redirect: false });
    router.push('/auth/signin');
    router.refresh();
  };

  return {
    session,
    user: session?.user,
    isAuthenticated: status === 'authenticated',
    isLoading: status === 'loading',
    logout,
  };
}

