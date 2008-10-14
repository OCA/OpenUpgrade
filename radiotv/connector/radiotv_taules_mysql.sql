CREATE TABLE zik_radiotv_channel (
  id int(11) unsigned NOT NULL,
  name varchar(200) NOT NULL,
  description text,
  changed tinyint(1) NOT NULL,
  PRIMARY KEY  (`id`)
) DEFAULT CHARSET=utf8;


CREATE TABLE zik_radiotv_program (
  id int(11) unsigned NOT NULL,
  name character varying(200) NOT NULL,
  introduction text NOT NULL,
  state character varying(16) NOT NULL,
  team text,
  category_id integer,
  email character varying(100),
  description text,
  changed tinyint(1) NOT NULL,
  production_year integer,
  classification character varying(16) NOT NULL,
  broadcast_language character varying(50),
  original_language character varying(50),
  production_type character varying(16) NOT NULL,
  editor character varying(100),
  production_country_id integer,
  approx_duration integer
  PRIMARY KEY  (`id`)
) DEFAULT CHARSET=utf8;


CREATE TABLE zik_radiotv_channel_program_rel (
  program_id integer NOT NULL,
  channel_id integer NOT NULL
) DEFAULT CHARSET=utf8;


CREATE TABLE zik_radiotv_category (
  id int(11) unsigned NOT NULL,
  name character varying(200) NOT NULL,
  description text,
  changed tinyint(1) NOT NULL,
  PRIMARY KEY  (`id`)
) DEFAULT CHARSET=utf8;


CREATE TABLE zik_radiotv_broadcast (
  id int(11) unsigned NOT NULL,
  description text,
  program_id integer NOT NULL,
  channel_id integer NOT NULL,
  dt_end timestamp NOT NULL,
  dt_start timestamp NOT NULL,
  url text,
  changed tinyint(1) NOT NULL,
  PRIMARY KEY  (`id`)
) DEFAULT CHARSET=utf8;


CREATE TABLE zik_radiotv_podcast (
  id int(11) unsigned NOT NULL,
  name character varying(200) NOT NULL,
  file_name character varying(200) NOT NULL,
  broadcast_id integer NOT NULL,
  description text,
  author varchar(255),
  block tinyint(1),
  category varchar(255),
  duration varchar(10),
  explicit tinyint(1),
  keywords varchar(255),
  subtitle varchar(255),
  pub_date timestamp NOT NULL,
  changed tinyint(1) NOT NULL,
  PRIMARY KEY  (`id`)
) DEFAULT CHARSET=utf8;
