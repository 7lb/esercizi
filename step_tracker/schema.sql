drop table if exists users
drop table if exists days

create table users (
    username text primary key,
    password text not null
);

create table days (
    id int primary key autoincrement,
    date date not null,
    nsteps int not null,
    username text not null,
    foreign key(username) refrences users(username)
);
