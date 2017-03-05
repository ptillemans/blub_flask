drop table if exists log_entries;
create table log_entries (
  id integer primary key autoincrement,
  ts integer not null,
  temperature real not null,
  desired real not null,
  debounce integer not null,
  manual_time_left integer not null
);
