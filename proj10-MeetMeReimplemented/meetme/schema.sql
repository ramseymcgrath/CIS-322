drop table if exists user;
create table user (
  user_id text,
  email text,
);

drop table if exists friends;
create table friends (
  user_id integer,
  friend_id integer,
  friend_status text
);

drop table if exists meetings;
create table meetings (
  meeting_id text,
  user_id integer not null,
  title text,
  meeting_start text,
  meeting_end text,
  meeting_url text
);

drop table if exists meeting_members;
create table meeting_members (
  meeting_id text,
  host_id integer not null,
  attendee_id integer not null
);
