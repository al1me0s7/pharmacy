--
-- PostgreSQL database dump
--

\restrict TLsVIjMe1DtOUXnIeO7adz8mQ5wuZLXChbMNN3XmyqKmTg46lQNjzyR2Pcg5gDX

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: admins; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admins (
    admin_id integer NOT NULL,
    login character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL
);


ALTER TABLE public.admins OWNER TO postgres;

--
-- Name: admins_admin_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.admins_admin_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admins_admin_id_seq OWNER TO postgres;

--
-- Name: admins_admin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.admins_admin_id_seq OWNED BY public.admins.admin_id;


--
-- Name: bookings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bookings (
    booking_id integer NOT NULL,
    user_id integer,
    medicine_id integer,
    pharmacy_id integer,
    booking_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    pickup_deadline timestamp without time zone,
    status character varying(50) DEFAULT 'Активне'::character varying,
    pdf_booking_path character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status_last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    items text
);


ALTER TABLE public.bookings OWNER TO postgres;

--
-- Name: bookings_booking_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bookings_booking_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bookings_booking_id_seq OWNER TO postgres;

--
-- Name: bookings_booking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bookings_booking_id_seq OWNED BY public.bookings.booking_id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    category_id integer NOT NULL,
    category_name character varying(100) NOT NULL,
    description text,
    is_visible boolean DEFAULT true
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_category_id_seq OWNER TO postgres;

--
-- Name: categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_category_id_seq OWNED BY public.categories.category_id;


--
-- Name: cities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cities (
    city_id integer NOT NULL,
    city_name character varying(50) NOT NULL,
    region character varying(50),
    postal_code_prefix character varying(10)
);


ALTER TABLE public.cities OWNER TO postgres;

--
-- Name: cities_city_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cities_city_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cities_city_id_seq OWNER TO postgres;

--
-- Name: cities_city_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cities_city_id_seq OWNED BY public.cities.city_id;


--
-- Name: inventory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory (
    medicine_id integer NOT NULL,
    pharmacy_id integer NOT NULL,
    quantity integer DEFAULT 0 NOT NULL,
    selling_price numeric(10,2),
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    inventory_id integer NOT NULL
);


ALTER TABLE public.inventory OWNER TO postgres;

--
-- Name: inventory_inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_inventory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_inventory_id_seq OWNER TO postgres;

--
-- Name: inventory_inventory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_inventory_id_seq OWNED BY public.inventory.inventory_id;


--
-- Name: manufacturers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.manufacturers (
    manufacturer_id integer NOT NULL,
    manufacturer_name character varying(100) NOT NULL,
    country character varying(50),
    city character varying(50),
    address text,
    contact_email character varying(100),
    contact_phone character varying(50),
    license_number character varying(50),
    founded_year integer
);


ALTER TABLE public.manufacturers OWNER TO postgres;

--
-- Name: manufacturers_manufacturer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.manufacturers_manufacturer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.manufacturers_manufacturer_id_seq OWNER TO postgres;

--
-- Name: manufacturers_manufacturer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.manufacturers_manufacturer_id_seq OWNED BY public.manufacturers.manufacturer_id;


--
-- Name: medicines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medicines (
    medicine_id integer NOT NULL,
    manufacturer_id integer,
    category_id integer,
    name character varying(100) NOT NULL,
    description text,
    active_substance character varying(100),
    dosage_form character varying(50),
    dosage_value character varying(50),
    price numeric(10,2) NOT NULL,
    quantity_in_stock integer DEFAULT 0,
    expiration_date date,
    prescription_required boolean DEFAULT false,
    contraindications text,
    storage_conditions text,
    date_added timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    image character varying(255),
    composition text,
    usage_instructions text,
    CONSTRAINT check_price_positive CHECK ((price > (0)::numeric))
);


ALTER TABLE public.medicines OWNER TO postgres;

--
-- Name: medicines_medicine_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.medicines_medicine_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.medicines_medicine_id_seq OWNER TO postgres;

--
-- Name: medicines_medicine_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.medicines_medicine_id_seq OWNED BY public.medicines.medicine_id;


--
-- Name: order_medicine; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_medicine (
    order_id integer NOT NULL,
    medicine_id integer NOT NULL,
    quantity integer NOT NULL,
    price_at_purchase numeric(10,2) NOT NULL,
    subtotal numeric(10,2)
);


ALTER TABLE public.order_medicine OWNER TO postgres;

--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    user_id integer,
    order_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    delivery_address text,
    delivery_method character varying(50),
    delivery_status character varying(50) DEFAULT 'Очікується'::character varying,
    total_sum numeric(10,2) NOT NULL,
    comment text,
    pdf_receipt_path character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    pharmacy_id integer,
    status_last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    payment_method character varying(50) DEFAULT 'cash_on_delivery'::character varying,
    city_name character varying(100)
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: orders_order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_order_id_seq OWNER TO postgres;

--
-- Name: orders_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_order_id_seq OWNED BY public.orders.order_id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    payment_id integer NOT NULL,
    order_id integer,
    payment_method character varying(50),
    payment_status character varying(50),
    amount numeric(10,2) NOT NULL,
    transaction_code character varying(100),
    payment_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- Name: payments_payment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payments_payment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payments_payment_id_seq OWNER TO postgres;

--
-- Name: payments_payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payments_payment_id_seq OWNED BY public.payments.payment_id;


--
-- Name: pharmacies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pharmacies (
    pharmacy_id integer NOT NULL,
    city_id integer,
    pharmacy_name character varying(100) NOT NULL,
    address character varying(200) NOT NULL,
    working_hours character varying(100),
    contact_phone character varying(20),
    email character varying(100),
    has_delivery boolean DEFAULT false,
    rating numeric(3,2),
    date_added timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.pharmacies OWNER TO postgres;

--
-- Name: pharmacies_pharmacy_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pharmacies_pharmacy_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pharmacies_pharmacy_id_seq OWNER TO postgres;

--
-- Name: pharmacies_pharmacy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pharmacies_pharmacy_id_seq OWNED BY public.pharmacies.pharmacy_id;


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reviews (
    review_id integer NOT NULL,
    medicine_id integer,
    user_id integer,
    rating integer,
    comment text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reviews_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE public.reviews OWNER TO postgres;

--
-- Name: reviews_review_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reviews_review_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reviews_review_id_seq OWNER TO postgres;

--
-- Name: reviews_review_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reviews_review_id_seq OWNED BY public.reviews.review_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    full_name character varying(100),
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    phone_number character varying(20),
    address text,
    city character varying(50),
    postal_code character varying(20),
    registration_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    role character varying(20) DEFAULT 'user'::character varying,
    is_active boolean DEFAULT true
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: view_pharmacy_stats; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.view_pharmacy_stats AS
 SELECT p.pharmacy_name,
    sum(i.quantity) AS total_quantity,
    sum(((i.quantity)::numeric * m.price)) AS total_value,
    count(i.medicine_id) AS unique_medicines_count
   FROM ((public.pharmacies p
     JOIN public.inventory i ON ((p.pharmacy_id = i.pharmacy_id)))
     JOIN public.medicines m ON ((i.medicine_id = m.medicine_id)))
  GROUP BY p.pharmacy_name;


ALTER VIEW public.view_pharmacy_stats OWNER TO postgres;

--
-- Name: admins admin_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admins ALTER COLUMN admin_id SET DEFAULT nextval('public.admins_admin_id_seq'::regclass);


--
-- Name: bookings booking_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings ALTER COLUMN booking_id SET DEFAULT nextval('public.bookings_booking_id_seq'::regclass);


--
-- Name: categories category_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN category_id SET DEFAULT nextval('public.categories_category_id_seq'::regclass);


--
-- Name: cities city_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities ALTER COLUMN city_id SET DEFAULT nextval('public.cities_city_id_seq'::regclass);


--
-- Name: inventory inventory_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory ALTER COLUMN inventory_id SET DEFAULT nextval('public.inventory_inventory_id_seq'::regclass);


--
-- Name: manufacturers manufacturer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manufacturers ALTER COLUMN manufacturer_id SET DEFAULT nextval('public.manufacturers_manufacturer_id_seq'::regclass);


--
-- Name: medicines medicine_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicines ALTER COLUMN medicine_id SET DEFAULT nextval('public.medicines_medicine_id_seq'::regclass);


--
-- Name: orders order_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN order_id SET DEFAULT nextval('public.orders_order_id_seq'::regclass);


--
-- Name: payments payment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN payment_id SET DEFAULT nextval('public.payments_payment_id_seq'::regclass);


--
-- Name: pharmacies pharmacy_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pharmacies ALTER COLUMN pharmacy_id SET DEFAULT nextval('public.pharmacies_pharmacy_id_seq'::regclass);


--
-- Name: reviews review_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews ALTER COLUMN review_id SET DEFAULT nextval('public.reviews_review_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: admins; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.admins (admin_id, login, password_hash) FROM stdin;
1	admin	scrypt:32768:8:1$oYvgON4ObWcKCj9d$d0c5ce079e2d7705d5be38f49935feceb1608afe7150e8e4e8d9e078611ff46dfe7047c9471b3f3f58389f9bc1001ef80330ff655c0da38238116fe0c485f900
\.


--
-- Data for Name: bookings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bookings (booking_id, user_id, medicine_id, pharmacy_id, booking_date, pickup_deadline, status, pdf_booking_path, created_at, status_last_updated, items) FROM stdin;
7	3	3	7	2025-12-03 22:22:31.394109	2025-12-10 22:22:31.32631	collected	\N	2025-12-03 22:22:31.394109	2025-12-12 23:55:16.051345	\N
10	3	3	6	2025-12-11 23:00:38.74327	2025-12-12 23:00:38.696626	collected	\N	2025-12-11 23:00:38.74327	2025-12-12 23:59:06.718468	\N
9	3	3	3	2025-12-06 21:49:38.108918	2025-12-07 21:49:38.064217	collected	\N	2025-12-06 21:49:38.108918	2025-12-13 00:49:47.348292	\N
8	3	3	7	2025-12-06 21:13:28.913101	2025-12-13 21:13:28.867929	collected	\N	2025-12-06 21:13:28.913101	2025-12-12 23:55:16.051345	\N
6	3	3	2	2025-12-03 22:10:59.630454	2025-12-10 22:10:59.56029	collected	\N	2025-12-03 22:10:59.630454	2025-12-12 23:55:16.051345	\N
5	2	3	3	2025-12-01 20:29:49.138354	2025-12-08 20:29:49.071083	collected	\N	2025-12-01 20:29:49.138354	2025-12-16 15:40:27.171545	\N
4	1	3	5	2025-12-01 19:53:39.527329	2025-12-08 19:53:39.476744	collected	\N	2025-12-01 19:53:39.527329	2025-12-16 15:40:31.367656	\N
12	3	3	6	2025-12-18 16:15:57.395341	2025-12-19 16:15:57.317819	expired	\N	2025-12-18 16:15:57.395341	2025-12-18 20:56:24.761244	\N
3	1	3	5	2025-12-01 19:29:04.993656	2025-12-02 19:29:04.948815	received	\N	2025-12-01 19:29:04.993656	2025-12-12 23:55:16.051345	\N
13	3	3	4	2025-12-24 00:24:14.223361	2025-12-25 00:24:14.156136	collected	\N	2025-12-24 00:24:14.223361	2025-12-24 00:25:03.727228	\N
16	3	\N	1	2025-12-27 09:05:20.266092	2025-12-28 09:05:20.084396	cancelled	\N	2025-12-27 09:05:20.266092	2025-12-27 22:33:06.936747	[{"medicine_id": 2, "name": "Ібупрофен", "quantity": 1, "unit_price": 200.0, "pharmacy_id": 1}, {"medicine_id": 5, "name": "Аспірин Кардіо", "quantity": 1, "unit_price": 89.0, "pharmacy_id": 1}]
15	3	5	1	2025-12-27 08:51:49.52615	2025-12-28 08:51:49.39913	collected	\N	2025-12-27 08:51:49.52615	2025-12-27 22:33:17.037326	\N
14	3	2	1	2025-12-27 08:51:49.460985	2025-12-28 08:51:49.39913	collected	\N	2025-12-27 08:51:49.460985	2025-12-27 22:33:20.125281	\N
18	1	\N	1	2025-12-28 00:54:23.599355	2025-12-29 00:54:23.430522	pending	\N	2025-12-28 00:54:23.599355	2025-12-28 00:54:23.599355	[{"medicine_id": 2, "name": "Ібупрофен", "quantity": 1, "unit_price": 200.0, "pharmacy_id": 1}, {"medicine_id": 3, "name": "Амоксицилін", "quantity": 1, "unit_price": 98.0, "pharmacy_id": 1}]
19	1	\N	1	2025-12-28 01:05:45.324496	2025-12-29 01:05:45.275261	pending	\N	2025-12-28 01:05:45.324496	2025-12-28 01:05:45.324496	[{"medicine_id": 2, "name": "Ібупрофен", "quantity": 1, "unit_price": 200.0, "pharmacy_id": 1}, {"medicine_id": 3, "name": "Амоксицилін", "quantity": 1, "unit_price": 98.0, "pharmacy_id": 1}]
20	1	\N	1	2025-12-28 01:29:40.555362	2025-12-29 01:29:40.51049	pending	\N	2025-12-28 01:29:40.555362	2025-12-28 01:29:40.555362	[{"medicine_id": 2, "name": "Ібупрофен", "quantity": 1, "unit_price": 200.0, "pharmacy_id": 1}, {"medicine_id": 5, "name": "Аспірин Кардіо", "quantity": 1, "unit_price": 89.0, "pharmacy_id": 1}]
21	1	\N	1	2025-12-28 10:24:20.342851	2025-12-29 10:24:20.267649	pending	\N	2025-12-28 10:24:20.342851	2025-12-28 10:24:20.342851	[{"medicine_id": 5, "name": "Аспірин Кардіо", "quantity": 1, "unit_price": 89.0, "pharmacy_id": 1}, {"medicine_id": 6, "name": "Вітамін С", "quantity": 1, "unit_price": 45.0, "pharmacy_id": 1}]
22	1	\N	1	2025-12-28 10:30:25.055783	2025-12-29 10:30:24.847544	pending	\N	2025-12-28 10:30:25.055783	2025-12-28 10:30:25.055783	[{"medicine_id": 3, "name": "Амоксицилін", "quantity": 1, "unit_price": 80.0, "pharmacy_id": 1}, {"medicine_id": 4, "name": "Колдрекс", "quantity": 1, "unit_price": 123.0, "pharmacy_id": 1}]
23	1	3	1	2025-12-28 13:25:57.577644	2025-12-29 13:25:57.525302	Активне	\N	2025-12-28 13:25:57.577644	2025-12-28 13:25:57.577644	\N
24	1	\N	1	2025-12-28 13:36:48.018385	2025-12-29 13:36:47.93143	pending	\N	2025-12-28 13:36:48.018385	2025-12-28 13:36:48.018385	[{"medicine_id": 3, "name": "Амоксицилін", "quantity": 1, "unit_price": 80.0, "pharmacy_id": 1}]
25	1	\N	1	2025-12-28 14:17:13.958294	2025-12-29 14:17:13.859032	pending	\N	2025-12-28 14:17:13.958294	2025-12-28 14:17:13.958294	[{"medicine_id": 3, "name": "Амоксицилін", "quantity": 1, "unit_price": 80.0, "pharmacy_id": 1}]
26	1	\N	1	2025-12-28 14:20:20.241429	2025-12-29 14:20:20.109702	pending	\N	2025-12-28 14:20:20.241429	2025-12-28 14:20:20.241429	[{"medicine_id": 3, "name": "Амоксицилін", "quantity": 1, "unit_price": 80.0, "pharmacy_id": 1}, {"medicine_id": 7, "name": "Анальгін", "quantity": 1, "unit_price": 215.0, "pharmacy_id": 1}]
27	3	\N	1	2025-12-28 19:43:04.53643	2025-12-29 19:43:04.328842	pending	\N	2025-12-28 19:43:04.53643	2025-12-28 19:43:04.53643	[{"medicine_id": 2, "name": "Ібупрофен", "quantity": 2, "unit_price": 180.0, "pharmacy_id": 1}, {"medicine_id": 3, "name": "Амоксицилін", "quantity": 1, "unit_price": 80.0, "pharmacy_id": 1}]
28	1	\N	1	2026-01-01 01:48:51.663694	2026-01-02 01:48:51.465845	pending	\N	2026-01-01 01:48:51.663694	2026-01-01 01:48:51.663694	[{"medicine_id": 2, "name": "Ібупрофен", "quantity": 1, "unit_price": 58.0, "pharmacy_id": 1}]
29	1	\N	1	2026-01-01 20:17:03.340336	2026-01-02 20:17:03.253705	pending	\N	2026-01-01 20:17:03.340336	2026-01-01 20:17:03.340336	[{"medicine_id": 3, "name": "Амоксицилін", "quantity": 1, "unit_price": 80.0, "pharmacy_id": 1}]
17	1	3	1	2025-12-28 00:52:36.88046	2025-12-29 00:52:36.725221	collected	\N	2025-12-28 00:52:36.88046	2025-12-28 00:52:36.88046	\N
11	1	3	2	2025-12-17 22:52:19.691919	2025-12-18 22:52:19.649225	collected	\N	2025-12-17 22:52:19.691919	2025-12-17 22:52:19.691919	\N
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (category_id, category_name, description, is_visible) FROM stdin;
1	Анальгетики	Знеболюючі препарати	t
2	Антибіотики	Препарати для лікування бактеріальних інфекцій	t
3	Вітаміни	Дієтичні добавки та вітамінні комплекси	t
4	Протизастудні	Ліки від застуди та грипу	t
5	Серцево-судинні	Препарати для серця та тиску	t
6	Для нормалізації тиску	\N	t
\.


--
-- Data for Name: cities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cities (city_id, city_name, region, postal_code_prefix) FROM stdin;
1	Київ	Київська обл.	01
2	Харків	Харківська обл.	61
3	Львів	Львівська обл.	79
4	Дніпро	Дніпропетровська обл.	49
5	Одеса	Одеська обл.	65
\.


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventory (medicine_id, pharmacy_id, quantity, selling_price, last_updated, inventory_id) FROM stdin;
3	1	0	80.00	2026-01-01 01:10:17.237675	13
3	2	20	95.00	2025-11-21 19:39:40.751226	14
3	6	15	68.00	2025-11-21 19:39:40.751226	15
7	10	44	35.00	2025-11-21 19:39:40.751226	11
5	5	25	95.00	2025-11-21 19:39:40.751226	4
5	7	40	90.00	2025-11-21 19:39:40.751226	5
6	8	70	50.00	2025-11-21 19:39:40.751226	6
6	9	60	48.00	2025-11-21 19:39:40.751226	7
2	4	70	55.00	2025-11-21 19:39:40.751226	1
2	1	39	58.00	2025-11-21 19:39:40.751226	12
4	3	50	130.00	2025-11-21 19:39:40.751226	2
4	4	30	125.00	2025-11-21 19:39:40.751226	3
1	1	50	126.00	2025-11-21 19:39:40.751226	8
1	2	60	100.00	2025-11-21 19:39:40.751226	9
1	3	29	36.00	2025-11-21 19:39:40.751226	10
\.


--
-- Data for Name: manufacturers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.manufacturers (manufacturer_id, manufacturer_name, country, city, address, contact_email, contact_phone, license_number, founded_year) FROM stdin;
1	Дарниця	Україна	Київ	вул. Бориспільська 13	info@darnitsa.ua	+380442898700	UA-001	1930
3	Артеріум	Україна	Київ	вул. Васильківська 34	info@arterium.ua	+380443333333	UA-003	2005
4	Teva	Ізраїль	Єрусалим	Herzog St 12	info@teva.com	+97225600000	INT-551	1901
5	Bayer	Німеччина	Леверкузен	Bayer Str. 1	info@bayer.com	+492140000	INT-122	1863
7	Галичина-Фарм	Україна	Львів	\N	\N	\N	\N	\N
2	Фармацевтична компанія "Здоров’я"	Україна	Харків	вул. Шевченка 22	info@health.ua	+380577777777	UA-002	1936
6	Здоров'я	Україна	Харків	вул. Миру 46	info@zdorovye.ua	+380501112233	LIC-9999	1995
\.


--
-- Data for Name: medicines; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.medicines (medicine_id, manufacturer_id, category_id, name, description, active_substance, dosage_form, dosage_value, price, quantity_in_stock, expiration_date, prescription_required, contraindications, storage_conditions, date_added, image, composition, usage_instructions) FROM stdin;
7	1	1	Анальгін	Знеболювальний засіб	Метамізол	Ампули 10 шт	500 мг	230.00	245	2026-08-01	f		До 25°C	2025-11-21 19:32:20.915198	/static/medicines/med_1765228975_.jpg		
5	5	5	Аспірин Кардіо	Для серця	Ацетилсаліцилова кислота	Таблетки 50 шт	100 мг	89.00	93	2026-04-02	t	Алергія	Зберігати сухим	2025-11-21 19:32:20.915198	/static/medicines/med_1765580146_.jpg		
6	3	3	Вітамін С	Імунітет	Аскорбінова кислота	Таблетки 30 шт	500 мг	45.00	296	2027-02-01	f	Гастрит	При кімнатній температурі	2025-11-21 19:32:20.915198	/static/medicines/med_1765580854_.jpg		
2	1	1	Ібупрофен	Протизапальний засіб	Ібупрофен	Таблетки 20 шт	200 мг	200.00	135	2027-01-10	f	Виразка	При кімнатній температурі	2025-11-21 19:32:20.915198	/static/medicines/med_1765580868_.jpg		
4	4	4	Колдрекс	Від застуди	Парацетамол, Фенілефрин	Порошок 10 шт	5 г	125.00	116	2025-11-11	f	Гіпертонія	До 25°C	2025-11-21 19:32:20.915198	/static/medicines/med_1765580883_.jpg		
8	5	1	Нурофен	Знеболювальний	Ібупрофен	Таблетки 12 шт	200 мг	135.00	122	2026-12-01	f		Сухе місце	2025-11-21 19:32:20.915198	/static/medicines/med_1765580898_.jpg		
3	2	2	Амоксицилін	антибіотик	Амоксицилін	Капсули 10 шт	500 мг	98.00	79	2025-09-21	t	Алергія на пеніцилін	Зберігати сухим	2025-11-21 19:32:20.915198	/static/medicines/med_1765229629_.jpeg		
1	1	1	Парацетамол	Жарознижувальний засіб	Парацетамол	Таблетки 10 шт	500 мг	126.00	197	2026-05-01	f	Індивідуальна непереносимість	Зберігати при 25°C	2025-11-21 19:32:20.915198	/static/medicines/med_1765580912_.jpg		
10	1	3	Вітамін D3	Для кісток	Холекальциферол	Краплі	10 мл	140.00	108	2027-01-01	f		У темному місці	2025-11-21 19:32:20.915198	/static/medicines/med_1765580328_3_1.jpg		
9	4	4	Терафлю	Проти застуди	Парацетамол	Порошок 10 шт	10 г	150.00	87	2025-12-15	f		Зберігати сухим	2025-11-21 19:32:20.915198	/static/medicines/med_1765580923_.jpg		
29	5	6	Занідіп	ййй	Лерканідипін	Таблетки 90 шт	10мг	300.00	11	2035-12-20	f	ййй	ййй	2025-12-29 14:19:33.833393	/static/medicines/med_1767295923_.jpg	фармадіпін 10мг	йййй
28	5	6	Тритаце	ййй	Раміприл	Таблетки 28 шт	5мг	200.00	10	2034-12-20	f	йййй	ййй	2025-12-29 14:17:07.995366	/static/medicines/med_1767296005_.jpg	Раміприл 	ййй
\.


--
-- Data for Name: order_medicine; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_medicine (order_id, medicine_id, quantity, price_at_purchase, subtotal) FROM stdin;
1	7	1	30.00	30.00
6	6	1	45.00	45.00
7	8	1	120.00	120.00
8	2	1	55.00	55.00
8	7	1	30.00	30.00
9	6	1	45.00	45.00
9	7	1	30.00	30.00
10	1	1	35.00	35.00
10	8	1	120.00	120.00
11	7	1	30.00	30.00
11	8	1	120.00	120.00
12	7	1	30.00	30.00
13	7	3	30.00	90.00
14	6	2	45.00	90.00
14	7	3	30.00	90.00
15	7	1	30.00	30.00
16	2	2	55.00	110.00
16	7	2	30.00	60.00
17	10	1	140.00	140.00
18	1	1	126.00	126.00
19	9	1	150.00	150.00
20	2	1	200.00	200.00
21	7	1	230.00	230.00
22	7	1	230.00	230.00
23	1	1	36.00	36.00
24	4	1	125.00	125.00
25	8	1	135.00	135.00
26	4	1	125.00	125.00
27	7	1	35.00	35.00
28	10	1	140.00	140.00
29	8	1	135.00	135.00
30	1	1	126.00	126.00
31	8	1	135.00	135.00
32	4	1	125.00	125.00
34	6	1	45.00	45.00
43	2	1	180.00	180.00
44	2	1	200.00	200.00
45	2	1	200.00	200.00
46	2	1	200.00	200.00
47	2	1	200.00	200.00
48	8	1	135.00	135.00
49	8	2	135.00	270.00
50	8	1	135.00	135.00
51	2	1	180.00	180.00
51	6	1	85.00	85.00
52	2	1	58.00	58.00
56	9	1	150.00	150.00
57	7	1	230.00	230.00
63	1	1	126.00	126.00
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (order_id, user_id, order_date, delivery_address, delivery_method, delivery_status, total_sum, comment, pdf_receipt_path, created_at, pharmacy_id, status_last_updated, payment_method, city_name) FROM stdin;
26	3	2025-12-16 15:38:51.988015	Нова пошта — №: 5	post	delivered	125.00		\N	2025-12-16 15:38:51.988015	\N	2025-12-16 15:43:48.933478	cash_on_delivery	\N
22	3	2025-12-12 20:35:12.732856	вул. Хнурешна, буд. 48	home	delivered	230.00	Аптека: Аптека низьких цін (ID:10)	\N	2025-12-12 20:35:12.732856	\N	2025-12-12 23:55:15.959912	cash_on_delivery	\N
57	1	2026-01-01 19:32:54.226075	Нова Пошта — 1	nova_poshta	Очікується	230.00		\N	2026-01-01 19:32:54.226075	\N	2026-01-01 19:32:54.226075	cash_on_delivery	\N
1	1	2025-11-21 21:10:49.075945	вул. Сонячна, 12, кв. 45	\N	delivered	30.00	\N	\N	2025-11-28 22:15:45.689028	\N	2025-12-13 00:47:30.367633	cash_on_delivery	\N
6	1	2025-11-28 21:39:58.190897	nova — відділення/номер: 12	post	delivered	45.00	02090	\N	2025-11-28 22:15:45.689028	\N	2025-12-13 00:47:35.462979	cash_on_delivery	\N
7	1	2025-12-01 19:28:15.929901	nova — відділення: None	post	delivered	120.00		\N	2025-12-01 19:28:15.929901	\N	2025-12-13 00:47:40.466641	cash_on_delivery	\N
8	1	2025-12-01 19:56:33.787747	ukr — №: 13	post	delivered	85.00	02090	\N	2025-12-01 19:56:33.787747	\N	2025-12-13 00:47:44.896656	cash_on_delivery	\N
9	1	2025-12-01 20:05:19.167435	вул. Сонячна, 12, кв. 45	home	delivered	75.00		\N	2025-12-01 20:05:19.167435	\N	2025-12-13 00:47:49.653668	cash_on_delivery	\N
10	2	2025-12-01 20:25:26.425876	вул. Зелена, буд. 12	home	delivered	155.00		\N	2025-12-01 20:25:26.425876	\N	2025-12-13 00:47:55.197167	cash_on_delivery	\N
11	3	2025-12-03 19:01:15.847395	nova — №: 90	post	delivered	270.00		\N	2025-12-03 19:01:15.847395	\N	2025-12-13 00:48:00.169114	cash_on_delivery	\N
12	3	2025-12-03 20:52:35.169496	Аптека Мед-Сервіс	self_pickup	delivered	90.00		\N	2025-12-03 20:52:35.169496	\N	2025-12-13 00:48:04.861575	cash_on_delivery	\N
13	3	2025-12-03 21:48:24.428262	Аптека Мед-Сервіс	self_pickup	delivered	90.00		\N	2025-12-03 21:48:24.428262	\N	2025-12-13 00:48:09.779489	cash_on_delivery	\N
14	3	2025-12-03 22:24:17.884825	ukr — №: 3	post	delivered	180.00		\N	2025-12-03 22:24:17.884825	\N	2025-12-13 00:48:14.652973	cash_on_delivery	\N
15	3	2025-12-04 22:22:38.002015	nova — №: 5	post	delivered	30.00		\N	2025-12-04 22:22:38.002015	\N	2025-12-13 00:48:19.328358	cash_on_delivery	\N
16	3	2025-12-06 21:21:05.773769	вул. Хнурешна, буд. 48	home	delivered	170.00		\N	2025-12-06 21:21:05.773769	\N	2025-12-13 00:48:24.666132	cash_on_delivery	\N
17	3	2025-12-08 23:50:12.461474	ukr — №: 9	post	delivered	140.00		\N	2025-12-08 23:50:12.461474	\N	2025-12-13 00:48:32.334728	cash_on_delivery	\N
18	3	2025-12-11 23:03:17.212274	Аптека Мед-Сервіс	self_pickup	delivered	126.00		\N	2025-12-11 23:03:17.212274	\N	2025-12-13 00:48:36.944792	cash_on_delivery	\N
19	3	2025-12-12 19:47:59.058296	вул. Хнурешна, буд. 48	home	delivered	150.00		\N	2025-12-12 19:47:59.058296	\N	2025-12-13 00:48:41.543358	cash_on_delivery	\N
20	3	2025-12-12 20:19:48.633057	вул. Хнурешна, буд. 48	home	delivered	200.00		\N	2025-12-12 20:19:48.633057	\N	2025-12-13 00:48:47.826672	cash_on_delivery	\N
21	3	2025-12-12 20:27:44.382534	вул. Хнурешна, буд. 48	home	delivered	230.00		\N	2025-12-12 20:27:44.382534	\N	2025-12-13 00:48:51.887611	cash_on_delivery	\N
34	3	2025-12-24 00:28:13.292921	вул. Хнурешна, буд. 48	home	delivered	45.00		\N	2025-12-24 00:28:13.292921	\N	2025-12-24 01:04:57.397744	cash_on_delivery	\N
25	3	2025-12-13 00:31:25.979638	Укрпошта — №: 1	post	delivered	135.00		\N	2025-12-13 00:31:25.979638	\N	2025-12-24 01:04:50.036495	cash_on_delivery	\N
23	3	2025-12-12 23:54:11.284724	вул. Хнурешна, буд. 48	home	delivered	36.00	Аптека ID:3	\N	2025-12-12 23:54:11.284724	3	2025-12-13 00:10:44.598308	cash_on_delivery	\N
24	3	2025-12-13 00:21:28.913324	Нова пошта — №: 8	post	delivered	125.00		\N	2025-12-13 00:21:28.913324	\N	2025-12-13 00:49:17.326984	cash_on_delivery	\N
29	1	2025-12-17 23:27:20.610084	Нова пошта — №: 9	post	delivered	135.00		\N	2025-12-17 23:27:20.610084	\N	2025-12-17 23:41:56.001048	card_online	\N
28	1	2025-12-17 23:00:01.802729	Нова пошта — №: 55	post	delivered	140.00		\N	2025-12-17 23:00:01.802729	\N	2025-12-17 23:41:51.96988	card_online	\N
30	1	2025-12-17 23:38:44.811478	Укрпошта — №: 1	post	delivered	126.00		\N	2025-12-17 23:38:44.811478	\N	2025-12-17 23:38:44.811478	card_online	\N
31	3	2025-12-18 16:12:23.679612	Нова Пошта — №: 8	post	delivered	135.00		\N	2025-12-18 16:12:23.679612	\N	2025-12-18 16:12:23.679612	card_online	\N
27	3	2025-12-17 22:15:29.059924	вул. Хнурешна, буд. 48	home	delivered	35.00	Аптека ID:10	\N	2025-12-17 22:15:29.059924	10	2025-12-18 21:09:07.433767	cash_on_delivery	\N
49	1	2025-12-28 14:26:04.311771	Нова Пошта — 4	nova_poshta	cancelled	270.00		\N	2025-12-28 14:26:04.311771	\N	2025-12-28 19:44:27.661476	card_online	\N
32	3	2025-12-23 23:23:07.842234	Нова Пошта — №: 55	post	delivered	125.00		\N	2025-12-23 23:23:07.842234	\N	2025-12-23 23:23:07.842234	card_online	\N
43	3	2025-12-27 18:03:39.923653	вул. Хнурешна, буд. 48	home	delivered	180.00	Аптека: Аптека №1 (ID:1)	\N	2025-12-27 18:03:39.923653	1	2025-12-27 18:03:39.923653	card_online	\N
48	1	2025-12-28 10:55:28.608215	Нова Пошта — 6	nova_poshta	delivered	135.00		\N	2025-12-28 10:55:28.608215	\N	2025-12-29 01:54:18.168768	card_online	\N
44	1	2025-12-27 23:01:30.53645	вул. Сонячна, 12, кв. 45	home	delivered	200.00		\N	2025-12-27 23:01:30.53645	\N	2025-12-27 23:01:30.53645	card_online	\N
45	1	2025-12-27 23:36:03.856323	Нова Пошта — 23	nova_poshta	delivered	200.00		\N	2025-12-27 23:36:03.856323	\N	2025-12-27 23:36:03.856323	card_online	\N
46	1	2025-12-28 00:07:20.326827	Нова Пошта — 6	nova_poshta	delivered	200.00		\N	2025-12-28 00:07:20.326827	\N	2025-12-28 00:07:20.326827	card_online	\N
51	3	2025-12-29 14:10:54.225506	Аптека №1	self_pickup	Очікується	265.00	Самовивіз з аптеки Аптека №1	\N	2025-12-29 14:10:54.225506	\N	2025-12-29 14:10:54.225506	cash_on_delivery	\N
50	3	2025-12-29 12:39:06.680391	Нова Пошта — 4	nova_poshta	delivered	135.00		\N	2025-12-29 12:39:06.680391	\N	2025-12-29 12:41:33.674329	card_online	\N
47	1	2025-12-28 10:47:10.277235	Нова Пошта — 45	nova_poshta	delivered	200.00		\N	2025-12-28 10:47:10.277235	\N	2025-12-28 10:47:10.277235	card_online	\N
52	1	2026-01-01 01:38:49.218543	Аптека №1	self_pickup	Очікується	58.00	Самовивіз з аптеки Аптека №1	\N	2026-01-01 01:38:49.218543	\N	2026-01-01 01:38:49.218543	cash_on_delivery	\N
56	1	2026-01-01 02:06:34.367322	Нова Пошта — 89	nova_poshta	Очікується	150.00		\N	2026-01-01 02:06:34.367322	\N	2026-01-01 02:06:34.367322	cash_on_delivery	\N
63	1	2026-01-01 20:58:13.140317	Укрпошта — 67	ukrposhta	confirmed	126.00	!!	\N	2026-01-01 20:58:13.140317	\N	2026-01-01 20:58:13.140317	card_online	Львів
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (payment_id, order_id, payment_method, payment_status, amount, transaction_code, payment_date) FROM stdin;
\.


--
-- Data for Name: pharmacies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pharmacies (pharmacy_id, city_id, pharmacy_name, address, working_hours, contact_phone, email, has_delivery, rating, date_added) FROM stdin;
1	1	Аптека №1	вул. Хрещатик 10	08:00-22:00	+380441112233	kyiv1@pharmacy.ua	t	4.60	2025-11-21 19:30:35.445045
2	1	Аптека Мед-Сервіс	пр. Бажана 3	08:00-23:00	+380441234567	ms_kyiv@pharmacy.ua	t	4.70	2025-11-21 19:30:35.445045
3	1	Подорожник	вул. Лесі Українки 15	09:00-21:00	+380447778899	pod_kyiv@pharmacy.ua	f	4.40	2025-11-21 19:30:35.445045
5	1	Аптека низьких цін	вул. Залізнична 5	08:00-20:00	+380442221111	anc_kyiv@pharmacy.ua	f	4.20	2025-11-21 19:30:35.445045
6	2	Аптека №5	пр. Науки 12	08:00-22:00	+380577778899	kh1@pharmacy.ua	t	4.60	2025-11-21 19:30:46.345752
7	2	Аптека Мед-Сервіс	вул. Пушкінська 50	08:00-23:00	+380577771122	kh2@pharmacy.ua	t	4.70	2025-11-21 19:30:46.345752
8	2	Подорожник	вул. Сумська 23	09:00-20:00	+380577775533	kh3@pharmacy.ua	f	4.30	2025-11-21 19:30:46.345752
9	2	Аптека D.S	вул. Героїв Праці 9	08:00-22:00	+380577774455	kh4@pharmacy.ua	t	4.60	2025-11-21 19:30:46.345752
4	1	Аптека D.S	вул. Сагайдачного 20	08:00-22:00	+380449998877	ds_kyiv@pharmacy.ua	t	4.80	2025-11-21 19:30:35.445045
10	2	Аптека низьких цін	вул. Молочна 8	08:00-20:00	+380577779988	kh5@pharmacy.ua	t	4.10	2025-11-21 19:30:46.345752
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reviews (review_id, medicine_id, user_id, rating, comment, created_at) FROM stdin;
1	3	3	4	допомагає	2025-12-11 23:11:34.640947
2	6	3	3	приємна ціна	2025-12-11 23:47:38.696913
3	10	3	4	добре	2025-12-24 01:00:04.846491
4	3	1	5	добре	2025-12-27 23:39:37.493507
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, full_name, email, password_hash, phone_number, address, city, postal_code, registration_date, role, is_active) FROM stdin;
1	Петро	petro@gmail.com	scrypt:32768:8:1$nMqO0ZpG8wecQaZU$2635b03bddfd64325e49e9c83fb6477af575c69f172d6b360d205f19f8d0c179da1feeb10ec13fbe68cd2f0e58383cf2dce265c0259896f8635bca409d37edcf	+380501234567	вул. Сонячна, 12, кв. 45	Львів	79000	2025-11-21 19:56:32.811264	user	t
2	Марія	maria@gmail.com	scrypt:32768:8:1$izIOCUCbpVPLiYxQ$190690f1e9c848c55496025ee4c4837f0a8f635c96caa359c61cc06d4d84f4b5c9cb377ef5d22b26f9941f0b32e39b2b71523b03281d7c06d75bc8d0767b434c	+380501234534	вул. Зелена, буд. 12	Київ	01001	2025-12-01 20:24:49.583989	user	t
3	Сідоров Іван Петренко	ivan@gmail.com	scrypt:32768:8:1$Sp8wl0INvVy32FIN$6cee8e20cb8fe9ff3d8d4485276861da9d600b7d1f607c741902923438131e5bf147e36ba56af862031b3ce4db15b69f4771f0bf0d63b0e946d5c5ab47b5ef70	+380782736453	вул. Хнурешна, буд. 48	Харків	61001	2025-12-03 17:12:52.784334	user	t
6	Мілана Олегівна	milana@gmail.com	scrypt:32768:8:1$6EqfjpsZbivtLZZT$d055e12cf167d671941cf0af54a2f756eedbecb2ca5a61b05fe813437745da11bcec1a53af980d8b09d690428def619b9381a1aef4d2ac0fd91dedbb6b947631	+380972354725		Одеса	\N	2025-12-29 13:41:36.14446	user	t
7	Користувач	user@example.com	scrypt:32768:8:1$2z2YQx9jeZwQDNnH$478fd9df8450d83d5f25a9e0b346f0d5fae3c0b69b7143d87794a8daa67501ee2a3506f8f80c8d72ffb235f1d1dc34e5a384c4fd67d865f0a4a7dd02f2d1a1b7	+0501234567	ХНУРЕ	Харків	\N	2026-01-01 23:37:46.36567	user	t
\.


--
-- Name: admins_admin_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.admins_admin_id_seq', 1, true);


--
-- Name: bookings_booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bookings_booking_id_seq', 29, true);


--
-- Name: categories_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_category_id_seq', 6, true);


--
-- Name: cities_city_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cities_city_id_seq', 5, true);


--
-- Name: inventory_inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_inventory_id_seq', 27, true);


--
-- Name: manufacturers_manufacturer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.manufacturers_manufacturer_id_seq', 7, true);


--
-- Name: medicines_medicine_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.medicines_medicine_id_seq', 29, true);


--
-- Name: orders_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_order_id_seq', 63, true);


--
-- Name: payments_payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_payment_id_seq', 1, false);


--
-- Name: pharmacies_pharmacy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pharmacies_pharmacy_id_seq', 10, true);


--
-- Name: reviews_review_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reviews_review_id_seq', 4, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 7, true);


--
-- Name: admins admins_login_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_login_key UNIQUE (login);


--
-- Name: admins admins_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (admin_id);


--
-- Name: bookings bookings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (booking_id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- Name: cities cities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_pkey PRIMARY KEY (city_id);


--
-- Name: inventory inventory_medicine_pharmacy_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_medicine_pharmacy_unique UNIQUE (medicine_id, pharmacy_id);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (inventory_id);


--
-- Name: manufacturers manufacturers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manufacturers
    ADD CONSTRAINT manufacturers_pkey PRIMARY KEY (manufacturer_id);


--
-- Name: medicines medicines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicines
    ADD CONSTRAINT medicines_pkey PRIMARY KEY (medicine_id);


--
-- Name: order_medicine order_medicine_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_medicine
    ADD CONSTRAINT order_medicine_pkey PRIMARY KEY (order_id, medicine_id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- Name: payments payments_order_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_order_id_key UNIQUE (order_id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (payment_id);


--
-- Name: pharmacies pharmacies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pharmacies
    ADD CONSTRAINT pharmacies_pkey PRIMARY KEY (pharmacy_id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (review_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: bookings bookings_medicine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_medicine_id_fkey FOREIGN KEY (medicine_id) REFERENCES public.medicines(medicine_id) ON DELETE CASCADE;


--
-- Name: bookings bookings_pharmacy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pharmacy_id_fkey FOREIGN KEY (pharmacy_id) REFERENCES public.pharmacies(pharmacy_id) ON DELETE CASCADE;


--
-- Name: bookings bookings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: inventory inventory_medicine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_medicine_id_fkey FOREIGN KEY (medicine_id) REFERENCES public.medicines(medicine_id) ON DELETE CASCADE;


--
-- Name: inventory inventory_pharmacy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pharmacy_id_fkey FOREIGN KEY (pharmacy_id) REFERENCES public.pharmacies(pharmacy_id) ON DELETE CASCADE;


--
-- Name: medicines medicines_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicines
    ADD CONSTRAINT medicines_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE SET NULL;


--
-- Name: medicines medicines_manufacturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicines
    ADD CONSTRAINT medicines_manufacturer_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES public.manufacturers(manufacturer_id) ON DELETE CASCADE;


--
-- Name: order_medicine order_medicine_medicine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_medicine
    ADD CONSTRAINT order_medicine_medicine_id_fkey FOREIGN KEY (medicine_id) REFERENCES public.medicines(medicine_id) ON DELETE CASCADE;


--
-- Name: order_medicine order_medicine_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_medicine
    ADD CONSTRAINT order_medicine_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE CASCADE;


--
-- Name: orders orders_pharmacy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pharmacy_id_fkey FOREIGN KEY (pharmacy_id) REFERENCES public.pharmacies(pharmacy_id);


--
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: payments payments_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE CASCADE;


--
-- Name: pharmacies pharmacies_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pharmacies
    ADD CONSTRAINT pharmacies_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(city_id) ON DELETE SET NULL;


--
-- Name: reviews reviews_medicine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_medicine_id_fkey FOREIGN KEY (medicine_id) REFERENCES public.medicines(medicine_id) ON DELETE CASCADE;


--
-- Name: reviews reviews_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict TLsVIjMe1DtOUXnIeO7adz8mQ5wuZLXChbMNN3XmyqKmTg46lQNjzyR2Pcg5gDX

