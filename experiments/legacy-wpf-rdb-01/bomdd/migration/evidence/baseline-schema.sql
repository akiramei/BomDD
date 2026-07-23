CREATE TABLE IF NOT EXISTS "tag_definitions" ("key" varchar(255),"user_id" int REFERENCES users(id) ON DELETE CASCADE,"color" varchar(255) );
CREATE TABLE IF NOT EXISTS "users" ("id" integer primary key autoincrement,"name" varchar(255) UNIQUE,"pass" blob,"admin" bool );
CREATE UNIQUE INDEX uix_users_id ON "users"("id") ;
CREATE TABLE IF NOT EXISTS "devices" ("id" integer primary key autoincrement,"token" varchar(255) UNIQUE,"name" varchar(255),"user_id" int REFERENCES users(id) ON DELETE CASCADE,"created_at" datetime,"type" varchar(255),"active_at" datetime );
CREATE UNIQUE INDEX uix_devices_id ON "devices"("id") ;
CREATE TABLE IF NOT EXISTS "time_spans" ("id" integer primary key autoincrement,"start_utc" datetime,"end_utc" datetime,"start_user_time" datetime,"end_user_time" datetime,"offset_utc" integer,"user_id" int REFERENCES users(id) ON DELETE CASCADE,"note" varchar(255) );
CREATE UNIQUE INDEX uix_time_spans_id ON "time_spans"("id") ;
CREATE TABLE IF NOT EXISTS "time_span_tags" ("time_span_id" int REFERENCES time_spans(id) ON DELETE CASCADE,"key" varchar(255),"string_value" varchar(255) );
CREATE TABLE IF NOT EXISTS "user_settings" ("user_id" integer primary key autoincrement,"theme" varchar(255),"date_locale" varchar(255),"first_day_of_the_week" varchar(255),"date_time_input_style" varchar(255) );
CREATE UNIQUE INDEX uix_user_settings_user_id ON "user_settings"(user_id) ;
CREATE TABLE IF NOT EXISTS "dashboards" ("id" integer primary key autoincrement,"user_id" int REFERENCES users(id) ON DELETE CASCADE,"name" varchar(255) );
CREATE UNIQUE INDEX uix_dashboards_id ON "dashboards"("id") ;
CREATE TABLE IF NOT EXISTS "dashboard_entries" ("id" integer primary key autoincrement,"dashboard_id" int REFERENCES dashboards(id) ON DELETE CASCADE,"title" varchar(255),"total" bool DEFAULT false,"type" varchar(255),"keys" varchar(255),"interval" varchar(255),"range_id" integer,"range_from" varchar(255),"range_to" varchar(255),"mobile_position" varchar(255),"desktop_position" varchar(255) );
CREATE UNIQUE INDEX uix_dashboard_entries_id ON "dashboard_entries"("id") ;
CREATE TABLE IF NOT EXISTS "dashboard_tag_filters" ("dashboard_entry_id" int REFERENCES dashboard_entries(id) ON DELETE CASCADE,"key" varchar(255),"string_value" varchar(255),"include" bool );
CREATE TABLE IF NOT EXISTS "dashboard_ranges" ("id" integer primary key autoincrement,"name" varchar(255),"dashboard_id" int REFERENCES dashboards(id) ON DELETE CASCADE,"editable" bool,"from" varchar(255),"to" varchar(255) );
CREATE UNIQUE INDEX uix_dashboard_ranges_id ON "dashboard_ranges"("id") ;

