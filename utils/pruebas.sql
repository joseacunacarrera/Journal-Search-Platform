use mydb;

DELETE FROM history WHERE id > 0;
DELETE FROM groups WHERE id > 0;
DELETE FROM jobs WHERE id > 0;

select * from jobs;
select * from groups;
