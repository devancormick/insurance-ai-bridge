import NextAuth, { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: 'Username', type: 'text' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          return null;
        }

        try {
          const formData = new URLSearchParams();
          formData.append('username', credentials.username);
          formData.append('password', credentials.password);

          const response = await axios.post(
            `${API_URL}/api/v1/auth/login`,
            formData,
            {
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
              },
            }
          );

          if (response.data.access_token) {
            // Fetch user info
            const userResponse = await axios.get(
              `${API_URL}/api/v1/auth/me`,
              {
                headers: {
                  Authorization: `Bearer ${response.data.access_token}`,
                },
              }
            );

            return {
              id: userResponse.data.username,
              name: userResponse.data.full_name || userResponse.data.username,
              email: userResponse.data.email,
              accessToken: response.data.access_token,
            };
          }
          return null;
        } catch (error) {
          console.error('Authentication error:', error);
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = (user as any).accessToken;
      }
      return token;
    },
    async session({ session, token }) {
      if (token) {
        (session as any).accessToken = token.accessToken;
      }
      return session;
    },
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 60, // 30 minutes
  },
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };

