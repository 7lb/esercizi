drop table if exists users;
drop table if exists days;

create table users (
    username text primary key,
    password text not null
);

create table days (
    id integer primary key autoincrement,
    date text not null,
    nsteps integer not null,
    username text not null,
    foreign key(username) references users(username)
);
