-- Table: public.db_csl_broker_input

-- DROP TABLE IF EXISTS public.db_csl_broker_input;

CREATE TABLE IF NOT EXISTS public.db_csl_broker_input
(
    date_time timestamp without time zone,
    "Ua_POI" real,
    "Ub_POI" real,
    "Uc_POI" real,
    "F_POI" real,
    "P_POI" real,
    "Q_POI" real,
    "Ia_POI" real,
    "Ib_POI" real,
    "Ic_POI" real,
    "In_POI" real,
    "U12_POI" real,
    "U23_POI" real,
    "U31_POI" real,
    "U1_POI" real,
    "U2_POI" real,
    "U3_POI" real,
    "Uab_CT1" integer,
    "Ubc_POI" integer,
    "Uca_POI" integer,
    "Ia_CT1" integer,
    "Ib_CT1" integer,
    "Ic_CT1" integer,
    "P_CT1" integer,
    "Q_CT1" integer,
    "P_REF_CT1" bigint,
    "Q_REF_CT1" integer,
    "Uab_CT2" integer,
    "Ubc_CT2" integer,
    "Uca_CT2" integer,
    "Ia_CT2" integer,
    "Ib_CT2" integer,
    "Ic_CT2" integer,
    "P_CT2" integer,
    "Q_CT2" integer,
    "P_REF_CT2" bigint,
    "Q_REF_CT2" integer
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.db_csl_broker_input
    OWNER to postgres;