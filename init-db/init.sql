create table furniture (
	id serial primary key,
	name text not null,
	price numeric(10,2) not null,
	category text not null
);

create table orders (
	id serial primary key,
	email text not null,
	total_price numeric(12,2) not null,
	date date not null
);

create table order_items (
	order_id int references orders(id),
	furniture_id int references furniture(id),
	quantity int not null,
	primary key (furniture_id, order_id)
);

insert into furniture(name, price, category)
values
	('chair_1', 49.99, 'chairs'),
	('chair_2', 75.55, 'chairs'),
	('chair_3', 63.99, 'chairs'),
	('table_1', 99.99, 'tables'),
	('table_2', 129.99, 'tables'),
	('armchair_1', 59.99, 'armchairs'),
	('armchair_2', 65.50, 'armchairs'),
	('armchair_3', 68.99, 'armchairs'),
	('coffeetable_1', 78.99, 'coffeetables'),
	('coffeetable_2', 85.45, 'coffeetables'),
	('coffeetable_3', 89.99, 'coffeetables'),
	('sofa_1', 249.99, 'sofas'),
	('sofa_2', 315.50, 'sofas'),
	('sofa_3', 215.55, 'sofas');