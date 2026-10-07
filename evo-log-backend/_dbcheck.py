import sqlite3
c = sqlite3.connect("kamlog_erp.db")
q = lambda s: c.execute(s).fetchone()[0]
print("permissions:", q("select count(*) from permissions"))
print("roles:", q("select count(*) from roles"))
print("role_permissions:", q("select count(*) from role_permissions"))
print("RESPONSABLE_COMMERCIAL:", q("select count(*) from roles where name='RESPONSABLE_COMMERCIAL'"))
print("b2b perms:", q("select count(*) from permissions where code like 'b2b.%'"))
print("aerien perms:", q("select count(*) from permissions where code like 'aerien.%'"))
print("tresorerie perms:", q("select count(*) from permissions where code like 'tresorerie.%'"))
print("comptabilite perms:", q("select count(*) from permissions where code like 'comptabilite.%'"))
print("port perms:", q("select count(*) from permissions where code like 'port.%'"))
print("CHEF_PARC links:", q("select count(*) from role_permissions rp join roles r on r.id=rp.role_id where r.name='CHEF_PARC'"))
print("wildcard rows:", q("select count(*) from permissions where code like '%.*.%'"))
