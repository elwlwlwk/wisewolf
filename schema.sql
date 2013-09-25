drop table if exists members;
create table members(
	email text primary key not null,
	pass text not null,
	name text not null unique
);
