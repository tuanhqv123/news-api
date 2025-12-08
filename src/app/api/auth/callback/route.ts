import { NextRequest, NextResponse } from 'next/server'

/**
 * Auth callback endpoint for deep links
 * Redirects to app or shows instructions
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const token_hash = searchParams.get('token_hash')
  const type = searchParams.get('type')

  // If this is an invite callback, redirect to app with the token
  if (type === 'invite' && token_hash) {
    // Create deep link for Android app
    const deepLink = `newsapp://auth/invite?token_hash=${token_hash}`

    // For mobile, we want to redirect directly to the app
    // For desktop/web, we can show a message
    const userAgent = request.headers.get('user-agent') || ''

    if (userAgent.includes('Android') || userAgent.includes('iPhone') || userAgent.includes('iPad')) {
      // Mobile device - try to open the app
      return NextResponse.redirect(deepLink)
    } else {
      // Desktop - show instructions
      return NextResponse.json({
        message: 'Please open this link on your mobile device to continue setup',
        deep_link: deepLink
      })
    }
  }

  // Handle other callback types if needed
  return NextResponse.json({
    error: 'Invalid callback parameters'
  }, { status: 400 })
}