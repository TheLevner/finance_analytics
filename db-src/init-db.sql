-- Таблица активов 
create table if not exists assets (
	id serial primary key,
	ticker varchar(10) not null unique,
	company_name varchar(100),
	sector varchar(50),
	created_at timestamp with time zone default current_timestamp
);

-- Таблица котировок
create table if not exists quotes (
	asset_id INT NOT NULL REFERENCES assets(id) ON DELETE cascade,
	date date not null,
	open numeric(12,4) not null,
	high numeric(12,4) not null,
	low numeric(12,4) not null,
	close numeric(12,4) not null,
	volume bigint not null,
	
	-- защита от дублей по дате и индексу 
	CONSTRAINT pk_asset_date PRIMARY KEY (asset_id, date)
);
-- для быстрой обработки по 1 ключу, толкьо date
CREATE INDEX IF NOT EXISTS idx_quotes_date ON quotes(date);