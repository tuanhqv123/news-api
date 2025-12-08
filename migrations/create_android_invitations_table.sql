-- Create table for tracking Android app invitations
CREATE TABLE IF NOT EXISTS android_invitations (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    role_id INTEGER NOT NULL REFERENCES roles(id),
    channel_id INTEGER REFERENCES channels(id) ON DELETE SET NULL,
    invited_by VARCHAR(255) NOT NULL,
    invitation_code VARCHAR(255) NOT NULL UNIQUE,
    app_scheme VARCHAR(50) NOT NULL DEFAULT 'newsapp',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'expired')),
    device_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX idx_android_invitations_email ON android_invitations(email);
CREATE INDEX idx_android_invitations_status ON android_invitations(status);
CREATE INDEX idx_android_invitations_code ON android_invitations(invitation_code);
CREATE INDEX idx_android_invitations_expires ON android_invitations(expires_at);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_android_invitations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER android_invitations_updated_at
    BEFORE UPDATE ON android_invitations
    FOR EACH ROW
    EXECUTE FUNCTION update_android_invitations_updated_at();