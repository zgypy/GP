-- 建表语句-- 集群主机信息（也可以考虑建两张表）
create table computepool(
    pool_name text default '' PRIMARY KEY UNIQUE,
    gi_homepath text default '',
    ora_homepath text default '',
    gi_name text default '',
    ora_name text default '',
    node_ip text,
    rootpasswd text,
    create_user text default 'admin',
    gi_version text default '',
    create_time timestamp(0) default now(),
    last_event_time timestamp(0) default now()
);

CREATE TABLE cpool_host(
    pool_name text,
    host_id SERIAL primary key,
    host_name text,
    vip text,
    scan_ip text,
    m_ip text,
    root_passwd text
);


create table dbpool(
    pool_name text,
    dbpool_id SERIAL primary key,
    dbpool_name text,
    live_host text,
    dblevel int default 0,
    min_v int default 1,
    max_v int default -1,
    create_time timestamp(0) default now(),
    last_event_time timestamp(0) default now()
);


create table db(
    db_id serial primary key,
    pool_name text,
    db_name text,
    instance_name text,
    sga_size text ,
    cpu_core text,
    pga_size text ,
    create_time timestamp(0) default now()
);



create table modle(
    compool_name text,
    modle_id serial,
    sga text,
    pga text,
    cpu text,
    ccsid text,
    cn_ccsid text,
    data_disk_g text,
    log_disk_g text,
    redo_size text,
    archive text,
    dispose text,
    rac_type text,
    hosts text,
    db_v text,
    monitor_u text,
    create_time timestamp(0) default now()
);


