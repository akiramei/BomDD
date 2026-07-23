--
-- PostgreSQL database dump
--

\restrict Z31CUUetpheGHHmnNgkuCTYpKPuXJgkoUe4but4WRjnY9XOrH4vBhypyOZhkv0N

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: dashboard_entries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_entries (
    id integer NOT NULL,
    dashboard_id integer,
    title text,
    total boolean DEFAULT false,
    type text,
    keys text,
    "interval" text,
    range_id integer,
    range_from text,
    range_to text,
    mobile_position text,
    desktop_position text
);


--
-- Name: dashboard_entries_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dashboard_entries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dashboard_entries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dashboard_entries_id_seq OWNED BY public.dashboard_entries.id;


--
-- Name: dashboard_ranges; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_ranges (
    id integer NOT NULL,
    name text,
    dashboard_id integer,
    editable boolean,
    "from" text,
    "to" text
);


--
-- Name: dashboard_ranges_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dashboard_ranges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dashboard_ranges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dashboard_ranges_id_seq OWNED BY public.dashboard_ranges.id;


--
-- Name: dashboard_tag_filters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_tag_filters (
    dashboard_entry_id integer,
    key text,
    string_value text,
    include boolean
);


--
-- Name: dashboards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboards (
    id integer NOT NULL,
    user_id integer,
    name text
);


--
-- Name: dashboards_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dashboards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dashboards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dashboards_id_seq OWNED BY public.dashboards.id;


--
-- Name: devices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.devices (
    id integer NOT NULL,
    token text,
    name text,
    user_id integer,
    created_at timestamp with time zone,
    type text,
    active_at timestamp with time zone
);


--
-- Name: devices_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.devices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: devices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.devices_id_seq OWNED BY public.devices.id;


--
-- Name: tag_definitions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tag_definitions (
    key text,
    user_id integer,
    color text
);


--
-- Name: time_span_tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.time_span_tags (
    time_span_id integer,
    key text,
    string_value text
);


--
-- Name: time_spans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.time_spans (
    id integer NOT NULL,
    start_utc timestamp with time zone,
    end_utc timestamp with time zone,
    start_user_time timestamp with time zone,
    end_user_time timestamp with time zone,
    offset_utc integer,
    user_id integer,
    note text
);


--
-- Name: time_spans_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.time_spans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: time_spans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.time_spans_id_seq OWNED BY public.time_spans.id;


--
-- Name: user_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_settings (
    user_id integer NOT NULL,
    theme text,
    date_locale text,
    first_day_of_the_week text,
    date_time_input_style text
);


--
-- Name: user_settings_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_settings_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_settings_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_settings_user_id_seq OWNED BY public.user_settings.user_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name text,
    pass bytea,
    admin boolean
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: dashboard_entries id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_entries ALTER COLUMN id SET DEFAULT nextval('public.dashboard_entries_id_seq'::regclass);


--
-- Name: dashboard_ranges id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_ranges ALTER COLUMN id SET DEFAULT nextval('public.dashboard_ranges_id_seq'::regclass);


--
-- Name: dashboards id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboards ALTER COLUMN id SET DEFAULT nextval('public.dashboards_id_seq'::regclass);


--
-- Name: devices id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices ALTER COLUMN id SET DEFAULT nextval('public.devices_id_seq'::regclass);


--
-- Name: time_spans id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_spans ALTER COLUMN id SET DEFAULT nextval('public.time_spans_id_seq'::regclass);


--
-- Name: user_settings user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_settings ALTER COLUMN user_id SET DEFAULT nextval('public.user_settings_user_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: dashboard_entries dashboard_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_entries
    ADD CONSTRAINT dashboard_entries_pkey PRIMARY KEY (id);


--
-- Name: dashboard_ranges dashboard_ranges_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_ranges
    ADD CONSTRAINT dashboard_ranges_pkey PRIMARY KEY (id);


--
-- Name: dashboards dashboards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboards
    ADD CONSTRAINT dashboards_pkey PRIMARY KEY (id);


--
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (id);


--
-- Name: devices devices_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_token_key UNIQUE (token);


--
-- Name: time_spans time_spans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_spans
    ADD CONSTRAINT time_spans_pkey PRIMARY KEY (id);


--
-- Name: user_settings user_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_settings
    ADD CONSTRAINT user_settings_pkey PRIMARY KEY (user_id);


--
-- Name: users users_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_name_key UNIQUE (name);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: uix_dashboard_entries_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uix_dashboard_entries_id ON public.dashboard_entries USING btree (id);


--
-- Name: uix_dashboard_ranges_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uix_dashboard_ranges_id ON public.dashboard_ranges USING btree (id);


--
-- Name: uix_dashboards_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uix_dashboards_id ON public.dashboards USING btree (id);


--
-- Name: uix_devices_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uix_devices_id ON public.devices USING btree (id);


--
-- Name: uix_time_spans_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uix_time_spans_id ON public.time_spans USING btree (id);


--
-- Name: uix_user_settings_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uix_user_settings_user_id ON public.user_settings USING btree (user_id);


--
-- Name: uix_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uix_users_id ON public.users USING btree (id);


--
-- Name: dashboard_entries dashboard_entries_dashboard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_entries
    ADD CONSTRAINT dashboard_entries_dashboard_id_fkey FOREIGN KEY (dashboard_id) REFERENCES public.dashboards(id) ON DELETE CASCADE;


--
-- Name: dashboard_ranges dashboard_ranges_dashboard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_ranges
    ADD CONSTRAINT dashboard_ranges_dashboard_id_fkey FOREIGN KEY (dashboard_id) REFERENCES public.dashboards(id) ON DELETE CASCADE;


--
-- Name: dashboard_tag_filters dashboard_tag_filters_dashboard_entry_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_tag_filters
    ADD CONSTRAINT dashboard_tag_filters_dashboard_entry_id_fkey FOREIGN KEY (dashboard_entry_id) REFERENCES public.dashboard_entries(id) ON DELETE CASCADE;


--
-- Name: dashboards dashboards_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboards
    ADD CONSTRAINT dashboards_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: devices devices_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: tag_definitions tag_definitions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tag_definitions
    ADD CONSTRAINT tag_definitions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: time_span_tags time_span_tags_time_span_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_span_tags
    ADD CONSTRAINT time_span_tags_time_span_id_fkey FOREIGN KEY (time_span_id) REFERENCES public.time_spans(id) ON DELETE CASCADE;


--
-- Name: time_spans time_spans_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_spans
    ADD CONSTRAINT time_spans_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict Z31CUUetpheGHHmnNgkuCTYpKPuXJgkoUe4but4WRjnY9XOrH4vBhypyOZhkv0N

