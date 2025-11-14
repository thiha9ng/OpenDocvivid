import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import CredentialsProvider from "next-auth/providers/credentials"

const handler = NextAuth({
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID!,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
        }),
        CredentialsProvider({
            name: 'Email',
            credentials: {
                email: { label: "Email", type: "email" },
                password: { label: "Password", type: "password" }
            },
            async authorize(credentials) {
                if (!credentials?.email || !credentials?.password) {
                    return null
                }

                try {
                    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/email`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            email: credentials.email,
                            password: credentials.password
                        })
                    });

                    if (!response.ok) {
                        return null
                    }

                    const data = await response.json();

                    // Create user object based on backend response
                    const user = {
                        id: data.user_id || "unknown",
                        email: credentials.email,
                        name: data.name || credentials.email,
                        accessToken: data.access_token
                    }

                    return user
                } catch (error) {
                    console.error('Email login failed:', error);
                    return null
                }
            }
        })
    ],
    callbacks: {
        async jwt({ token, user }) {
            // Save information to token on first login
            if (user) {
                // Handle Google login and email login
                token.accessToken = (user as any).accessToken;
                token.email = user.email;
                token.name = user.name;
                token.userId = (user as any).id;
            }
            return token;
        },
        async session({ session, token }) {
            if (session.user) {
                (session.user as any).id = token.userId || token.sub as string;
                (session.user as any).accessToken = token.accessToken;
                session.user.email = token.email as string;
                session.user.name = token.name as string;
            }
            return session;
        },
        async signIn({ user, account, profile }) {
            // If email login, authorize already handled, return true directly
            if (account?.provider === 'credentials') {
                return true;
            }

            // Call backend API after Google login
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/sync-user`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: user.email,
                        google_id: profile?.sub,
                        name: user.name
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    // Add access token and user info to user object
                    (user as any).accessToken = data.access_token;
                    (user as any).id = data.user_id || user.id;
                    (user as any).email = data.email || user.email;
                    (user as any).name = data.name || user.name;
                    return true;
                }
                return false;
            } catch (error) {
                console.error('User data sync failed:', error);
                return false;
            }
        }
    },
    pages: {
        signIn: '/login'
    },
    session: {
        strategy: "jwt"
    },
    secret: process.env.NEXTAUTH_SECRET,
})

export { handler as GET, handler as POST }