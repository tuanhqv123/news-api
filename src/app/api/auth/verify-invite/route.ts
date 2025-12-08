import { createClient } from '@/utils/supabase/server'
import { NextRequest, NextResponse } from 'next/server'

/**
 * API endpoint to verify invitation token
 * Called by Android app before showing password setup dialog
 */
export async function POST(request: NextRequest) {
  try {
    const { token_hash } = await request.json()

    if (!token_hash) {
      return NextResponse.json(
        {
          success: false,
          error: 'Token hash is required',
          error_code: 'MISSING_TOKEN'
        },
        { status: 400 }
      )
    }

    const supabase = createClient()

    // Verify the invitation token
    const { data, error } = await supabase.auth.verifyOtp({
      type: 'invite',
      token_hash,
    })

    if (error) {
      console.error('Invite verification error:', error)
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid or expired invitation',
          error_code: 'INVALID_INVITE'
        },
        { status: 400 }
      )
    }

    // Get user details
    if (data.user) {
      return NextResponse.json({
        success: true,
        data: {
          user_id: data.user.id,
          email: data.user.email,
          user_metadata: data.user.user_metadata
        },
        message: 'Invitation verified successfully'
      })
    }

    return NextResponse.json(
      {
        success: false,
        error: 'Failed to retrieve user information',
        error_code: 'USER_RETRIEVAL_FAILED'
      },
      { status: 500 }
    )

  } catch (error) {
    console.error('Verify invite API error:', error)
    return NextResponse.json(
      {
        success: false,
        error: 'Internal server error',
        error_code: 'INTERNAL_ERROR'
      },
      { status: 500 }
    )
  }
}