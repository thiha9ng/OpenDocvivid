import { NextResponse } from 'next/server';

/**
 * Health check endpoint
 * For Docker container health check and load balancer probe
 */
export async function GET() {
  return NextResponse.json(
    {
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
    },
    { status: 200 }
  );
}

