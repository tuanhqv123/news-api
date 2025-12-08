# Android Invitation Setup Guide

This guide explains how to set up Android user invitations with deep linking and password setup.

## Overview

The Android invitation flow consists of these steps:

1. Admin sends invitation via API
2. User receives email with deep link
3. User clicks link → opens Android app
4. App verifies invitation
5. User sets password in the app
6. User can now log in normally

## API Endpoints Created

### 1. Send Android Invitation

```http
POST /api/v1/auth/android/invite
```

**Request Body:**
```json
{
    "email": "user@example.com",
    "role_id": 3,
    "channel_id": 1,  // Optional
    "invited_by": "admin_name",
    "app_scheme": "newsapp"  // Optional, defaults to "newsapp"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "user_id": "uuid-here",
        "email": "user@example.com",
        "role": "author",
        "deep_link_scheme": "newsapp",
        "message": "Invitation sent to Android app"
    },
    "message": "Android user invitation sent successfully"
}
```

### 2. Verify Invitation (in Android App)

```http
POST /api/v1/auth/android/verify-invite
```

**Request Body:**
```json
{
    "token_hash": "hash-from-email-link",
    "email": "user@example.com"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "user_id": "uuid-here",
        "email": "user@example.com",
        "role": "author",
        "role_id": 3,
        "channel_id": 1,
        "invited_by": "admin_name",
        "can_set_password": true,
        "message": "Invitation verified - ready to set password"
    },
    "message": "Invitation verified successfully"
}
```

### 3. Set Password (in Android App)

```http
POST /api/v1/auth/android/setup-password
```

**Request Body:**
```json
{
    "token_hash": "hash-from-email-link",
    "email": "user@example.com",
    "password": "newSecurePassword123!",
    "device_info": {  // Optional
        "device_id": "unique-device-id",
        "device_model": "Samsung Galaxy S21",
        "os_version": "Android 12"
    }
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "user_id": "uuid-here",
        "email": "user@example.com",
        "access_token": "jwt-token-here",
        "refresh_token": "refresh-token-here",
        "message": "Password set and logged in successfully"
    },
    "message": "Password setup successful"
}
```

### 4. Check Invitation Status

```http
GET /api/v1/auth/android/check-invitation/{email}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "has_pending_invitation": true,
        "expires_at": "2024-01-15T10:30:00Z",
        "is_expired": false,
        "app_scheme": "newsapp"
    },
    "message": "Pending invitation found"
}
```

## Supabase Email Template Configuration

### Step 1: Go to Supabase Dashboard

1. Navigate to your Supabase project
2. Go to Authentication → Email Templates
3. Select the "Invite user" template

### Step 2: Update the Template Content

Replace the default content with:

```html
<h2>You're Invited to Join Our News App!</h2>
<p>You have been invited to join our news platform as an author.</p>
<p>To get started, please install our Android app and click the button below:</p>

<p style="margin: 20px 0;">
    <a href="{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=invite&redirect_to=newsapp://auth/invite?token={{ .TokenHash }}&email={{ .Email }}"
       style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
        Open App & Set Password
    </a>
</p>

<p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
<p><a href="{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=invite&redirect_to=newsapp://auth/invite?token={{ .TokenHash }}&email={{ .Email }}">{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=invite&redirect_to=newsapp://auth/invite?token={{ .TokenHash }}&email={{ .Email }}</a></p>

<p>Or open this link directly in your Android app:</p>
<p><code>newsapp://auth/invite?token={{ .TokenHash }}&email={{ .Email }}</code></p>

<p>This invitation will expire in 7 days.</p>

<p>Best regards,<br>The News Team</p>
```

### Step 3: Update URL Configuration

1. Go to Authentication → URL Configuration
2. Add your app's URL scheme to "Redirect URLs" and "Additional Redirect URLs"
3. Add: `newsapp://auth/invite`
4. Also add: `https://your-api-domain.com/auth/confirm`

## Android App Implementation

### 1. Configure Android Manifest

Add to `AndroidManifest.xml` inside your MainActivity:

```xml
<activity android:name=".MainActivity">
    <!-- Existing intent filters -->

    <!-- Deep link handler for invitations -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="newsapp"
              android:host="auth"
              android:pathPrefix="/invite" />
    </intent-filter>
</activity>
```

### 2. Handle Deep Links in MainActivity

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Handle deep link when app opens
        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent?) {
        intent?.data?.let { uri ->
            when {
                uri.scheme == "newsapp" && uri.host == "auth" && uri.path?.startsWith("/invite") == true -> {
                    val token = uri.getQueryParameter("token")
                    val email = uri.getQueryParameter("email")

                    if (token != null && email != null) {
                        // Show password setup dialog
                        showPasswordSetupDialog(token, email)
                    }
                }
            }
        }
    }

    private fun showPasswordSetupDialog(token: String, email: String) {
        // Create dialog for password setup
        val dialog = PasswordSetupDialog.newInstance(token, email)
        dialog.show(supportFragmentManager, "password_setup")
    }
}
```

### 3. Create Password Setup Dialog

```kotlin
class PasswordSetupDialog : DialogFragment() {

    private lateinit var binding: DialogPasswordSetupBinding
    private lateinit var token: String
    private lateinit var email: String

    companion object {
        fun newInstance(token: String, email: String): PasswordSetupDialog {
            return PasswordSetupDialog().apply {
                arguments = Bundle().apply {
                    putString("token", token)
                    putString("email", email)
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        token = requireArguments().getString("token")!!
        email = requireArguments().getString("email")!!
    }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        binding = DialogPasswordSetupBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.btnSetupPassword.setOnClickListener {
            val password = binding.etPassword.text.toString()
            val confirmPassword = binding.etConfirmPassword.text.toString()

            if (password.length < 8) {
                Toast.makeText(requireContext(), "Password must be at least 8 characters", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (password != confirmPassword) {
                Toast.makeText(requireContext(), "Passwords don't match", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            setupPassword(password)
        }

        binding.btnCancel.setOnClickListener {
            dismiss()
        }
    }

    private fun setupPassword(password: String) {
        // Show loading
        binding.progressBar.visibility = View.VISIBLE
        binding.btnSetupPassword.isEnabled = false

        val deviceInfo = mapOf(
            "device_id" Settings.Secure.getString(requireContext().contentResolver, Settings.Secure.ANDROID_ID),
            "device_model" to Build.MODEL,
            "os_version" to Build.VERSION.RELEASE
        )

        val request = PasswordSetupRequest(
            token_hash = token,
            email = email,
            password = password,
            device_info = deviceInfo
        )

        RetrofitClient.apiService.setupAndroidPassword(request)
            .enqueue(object : Callback<StandardResponse> {
                override fun onResponse(call: Call<StandardResponse>, response: Response<StandardResponse>) {
                    binding.progressBar.visibility = View.GONE
                    binding.btnSetupPassword.isEnabled = true

                    if (response.isSuccessful) {
                        val data = response.body()?.data
                        val accessToken = data?.get("access_token")?.toString()
                        val refreshToken = data?.get("refresh_token")?.toString()

                        // Save tokens
                        if (accessToken != null && refreshToken != null) {
                            SessionManager.saveTokens(accessToken, refreshToken)
                        }

                        Toast.makeText(requireContext(), "Password set successfully!", Toast.LENGTH_LONG).show()

                        // Navigate to main app
                        startActivity(Intent(requireContext(), HomeActivity::class.java))
                        requireActivity().finish()

                        dismiss()
                    } else {
                        Toast.makeText(requireContext(), "Failed to set password", Toast.LENGTH_LONG).show()
                    }
                }

                override fun onFailure(call: Call<StandardResponse>, t: Throwable) {
                    binding.progressBar.visibility = View.GONE
                    binding.btnSetupPassword.isEnabled = true
                    Toast.makeText(requireContext(), "Network error: ${t.message}", Toast.LENGTH_LONG).show()
                }
            })
    }
}
```

### 4. API Service Setup

```kotlin
interface ApiService {

    @POST("/api/v1/auth/android/verify-invite")
    suspend fun verifyInvitation(@Body request: InvitationVerifyRequest): Response<StandardResponse>

    @POST("/api/v1/auth/android/setup-password")
    fun setupAndroidPassword(@Body request: PasswordSetupRequest): Call<StandardResponse>

    @GET("/api/v1/auth/android/check-invitation/{email}")
    suspend fun checkInvitationStatus(@Path("email") email: String): Response<StandardResponse>
}

data class InvitationVerifyRequest(
    val token_hash: String,
    val email: String
)

data class PasswordSetupRequest(
    val token_hash: String,
    val email: String,
    val password: String,
    val device_info: Map<String, String>? = null
)
```

## Database Migration

Run the migration to create the android_invitations table:

```bash
psql -h your-db-host -U your-db-user -d your-db-name -f migrations/create_android_invitations_table.sql
```

## Testing the Flow

1. Send an invitation using the API
2. Check the email contains the deep link
3. Click the link on Android device
4. App should open and show password dialog
5. Enter and confirm password
6. User should be logged in automatically

## Security Considerations

- Invitation tokens expire after 7 days
- Tokens can only be used once
- Email verification is required
- Passwords must meet minimum requirements
- All API calls should use HTTPS

## Troubleshooting

### Common Issues

1. **Deep link doesn't open app**
   - Check AndroidManifest.xml intent filter
   - Ensure URL scheme matches exactly
   - Clear app cache and retry

2. **Token verification fails**
   - Check if invitation has expired
   - Verify token_hash is correctly extracted
   - Check email matches invitation

3. **Password setup fails**
   - Ensure password meets requirements
   - Check network connectivity
   - Verify API endpoint is accessible

### Debug Tips

- Use adb to test deep links:
  ```bash
  adb shell am start -W -a android.intent.action.VIEW -d "newsapp://auth/invite?token=abc&email=test@example.com" com.your.package
  ```

- Check logs for deep link handling
- Verify API responses in Postman first