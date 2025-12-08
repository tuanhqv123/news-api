import { createClient } from '@/utils/supabase/server'
import { NextRequest, NextResponse } from 'next/server'

/**
 * API endpoint to set password for invited user
 * Called by Android app after user enters password
 */
export async function POST(request: NextRequest) {
  try {
    const { password, token_hash, user_id } = await request.json()

    if (!password || !token_hash || !user_id) {
      return NextResponse.json(
        {
          success: false,
          error: 'Password, token hash, and user ID are required',
          error_code: 'MISSING_REQUIRED_FIELDS'
        },
        { status: 400 }
      )
    }

    // Password validation
    if (password.length < 6) {
      return NextResponse.json(
        {
          success: false,
          error: 'Password must be at least 6 characters long',
          error_code: 'PASSWORD_TOO_SHORT'
        },
        { status: 400 }
      )
    }

    const supabase = createClient()

    // First verify the token again for security
    const { error: verifyError } = await supabase.auth.verifyOtp({
      type: 'invite',
      token_hash,
    })

    if (verifyError) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid or expired invitation token',
          error_code: 'INVALID_TOKEN'
        },
        { status: 400 }
      )
    }

    // Update user password using admin method
    const { error: updateError } = await supabase.auth.admin.updateUserById(
      user_id,
      { password }
    )

    if (updateError) {
      console.error('Password update error:', updateError)
      return NextResponse.json(
        {
          success: false,
          error: 'Failed to update password',
          error_code: 'PASSWORD_UPDATE_FAILED'
        },
        { status: 500 }
      )
    }

    return NextResponse.json({
      success: true,
      message: 'Password set successfully. You can now login with your email and password.'
    })

  } catch (error) {
    console.error('Setup password API error:', error)
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