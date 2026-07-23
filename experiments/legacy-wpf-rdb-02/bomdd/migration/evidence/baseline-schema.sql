-- Traggo v0.8.3 PostgreSQL schema reconstructed from the frozen model files.
-- Dependency order is explicit because model.All() lists TagDefinition before User.

CREATE TABLE users (
    id serial PRIMARY KEY,
    name text UNIQUE,
    pass bytea,
    admin boolean
);
CREATE UNIQUE INDEX uix_users_id ON users(id);

CREATE TABLE tag_definitions (
    key text,
    user_id integer REFERENCES users(id) ON DELETE CASCADE,
    color text
);

CREATE TABLE devices (
    id serial PRIMARY KEY,
    token text UNIQUE,
    name text,
    user_id integer REFERENCES users(id) ON DELETE CASCADE,
    created_at timestamp with time zone,
    type text,
    active_at timestamp with time zone
);
CREATE UNIQUE INDEX uix_devices_id ON devices(id);

CREATE TABLE time_spans (
    id serial PRIMARY KEY,
    start_utc timestamp with time zone,
    end_utc timestamp with time zone,
    start_user_time timestamp with time zone,
    end_user_time timestamp with time zone,
    offset_utc integer,
    user_id integer REFERENCES users(id) ON DELETE CASCADE,
    note text
);
CREATE UNIQUE INDEX uix_time_spans_id ON time_spans(id);

CREATE TABLE time_span_tags (
    time_span_id integer REFERENCES time_spans(id) ON DELETE CASCADE,
    key text,
    string_value text
);

CREATE TABLE user_settings (
    user_id serial PRIMARY KEY,
    theme text,
    date_locale text,
    first_day_of_the_week text,
    date_time_input_style text
);
CREATE UNIQUE INDEX uix_user_settings_user_id ON user_settings(user_id);

CREATE TABLE dashboards (
    id serial PRIMARY KEY,
    user_id integer REFERENCES users(id) ON DELETE CASCADE,
    name text
);
CREATE UNIQUE INDEX uix_dashboards_id ON dashboards(id);

CREATE TABLE dashboard_entries (
    id serial PRIMARY KEY,
    dashboard_id integer REFERENCES dashboards(id) ON DELETE CASCADE,
    title text,
    total boolean DEFAULT false,
    type text,
    keys text,
    interval text,
    range_id integer,
    range_from text,
    range_to text,
    mobile_position text,
    desktop_position text
);
CREATE UNIQUE INDEX uix_dashboard_entries_id ON dashboard_entries(id);

CREATE TABLE dashboard_tag_filters (
    dashboard_entry_id integer REFERENCES dashboard_entries(id) ON DELETE CASCADE,
    key text,
    string_value text,
    include boolean
);

CREATE TABLE dashboard_ranges (
    id serial PRIMARY KEY,
    name text,
    dashboard_id integer REFERENCES dashboards(id) ON DELETE CASCADE,
    editable boolean,
    "from" text,
    "to" text
);
CREATE UNIQUE INDEX uix_dashboard_ranges_id ON dashboard_ranges(id);

