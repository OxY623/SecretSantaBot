/*
  # Secret Santa Bot Database Schema

  1. New Tables
    - `games`
      - `id` (uuid, primary key) - Unique game session identifier
      - `chat_id` (bigint) - Telegram chat/group ID where game was started
      - `status` (text) - Game status: 'registration', 'completed'
      - `created_at` (timestamptz) - When the game was created
      - `started_at` (timestamptz) - When the game was started/distributed
    
    - `participants`
      - `id` (uuid, primary key)
      - `game_id` (uuid, foreign key) - Reference to games table
      - `user_id` (bigint) - Telegram user ID
      - `username` (text) - Telegram username
      - `first_name` (text) - User's first name
      - `joined_at` (timestamptz) - When user joined the game
    
    - `assignments`
      - `id` (uuid, primary key)
      - `game_id` (uuid, foreign key) - Reference to games table
      - `giver_user_id` (bigint) - Telegram user ID of gift giver
      - `receiver_user_id` (bigint) - Telegram user ID of gift receiver
      - `created_at` (timestamptz) - When assignment was created

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated access (bot service role)

  3. Indexes
    - Index on game_id for faster lookups
    - Index on user_id for participant queries
*/

-- Create games table
CREATE TABLE IF NOT EXISTS games (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  chat_id bigint NOT NULL,
  status text NOT NULL DEFAULT 'registration',
  created_at timestamptz DEFAULT now(),
  started_at timestamptz
);

-- Create participants table
CREATE TABLE IF NOT EXISTS participants (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id uuid NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  user_id bigint NOT NULL,
  username text,
  first_name text NOT NULL,
  joined_at timestamptz DEFAULT now(),
  UNIQUE(game_id, user_id)
);

-- Create assignments table
CREATE TABLE IF NOT EXISTS assignments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id uuid NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  giver_user_id bigint NOT NULL,
  receiver_user_id bigint NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_games_chat_id ON games(chat_id);
CREATE INDEX IF NOT EXISTS idx_games_status ON games(status);
CREATE INDEX IF NOT EXISTS idx_participants_game_id ON participants(game_id);
CREATE INDEX IF NOT EXISTS idx_participants_user_id ON participants(user_id);
CREATE INDEX IF NOT EXISTS idx_assignments_game_id ON assignments(game_id);

-- Enable RLS
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
ALTER TABLE participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE assignments ENABLE ROW LEVEL SECURITY;

-- Create policies for service role access
CREATE POLICY "Service role can manage games"
  ON games FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role can manage participants"
  ON participants FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role can manage assignments"
  ON assignments FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);