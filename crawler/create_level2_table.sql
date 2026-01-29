
-- Create Data Features Table for Level 2 (Preprocessing)
-- Determines Input Features for Level 4 (AutoML)

create table if not exists model_features (
    date date primary key,
    
    -- Calendar
    year int,
    month int,
    day int,
    day_of_week int,
    is_weekend int,
    is_holiday int,
    
    -- Weather
    avg_temp float,
    precip_total float,
    
    -- Target (Label)
    total_traffic int,
    
    -- Lag Features (Context)
    lag_1d float,
    lag_7d float,
    lag_364d float,
    rolling_7d_avg float,
    
    -- Metadata
    version_id text,
    
    created_at timestamp default now()
);

-- Note: In Supabase SQL Editor, just Run this.
