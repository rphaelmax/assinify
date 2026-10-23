create database if not exists assinify;
use assinify;

create table if not exists usuarios (
    id_usuario int auto_increment primary key,
    nome varchar(100) not null,
    email varchar(120) not null unique,
    senha_hash varchar(255) not null,
    role varchar(20) not null default 'user',
    data_cadastro date default (current_date)
);

create table if not exists categorias (
    id_categoria int auto_increment primary key,
    nome_categoria varchar(100) not null,
    descricao varchar(255),
    id_usuario int not null,
    foreign key (id_usuario) references usuarios(id_usuario)
);

create table if not exists assinaturas (
    id_assinatura int auto_increment primary key,
    nome_servico varchar(100) not null,
    valor_mensal decimal(10,2) not null,
    data_renovacao date not null,
    status varchar(20) not null default 'ativa',
    tipo_plano varchar(50),
    metodo_pagamento varchar(30) not null default 'cartao_credito',
    periodicidade varchar(20) not null default 'mensal',
    id_usuario int not null,
    id_categoria int not null,
    foreign key (id_usuario) references usuarios(id_usuario),
    foreign key (id_categoria) references categorias(id_categoria)
);

create table if not exists historico_assinaturas (
    id int auto_increment primary key,
    id_assinatura int null,
    campo varchar(50) not null,
    valor_antigo text null,
    valor_novo text null,
    data_alteracao datetime not null default current_timestamp,
    id_usuario int null,
    foreign key (id_assinatura) references assinaturas(id_assinatura) on delete set null,
    foreign key (id_usuario) references usuarios(id_usuario) on delete set null
);

-- bancos já existentes:
-- alter table assinaturas add column metodo_pagamento varchar(30) not null default 'cartao_credito';
-- alter table assinaturas modify valor_mensal decimal(10,2) not null;
-- alter table assinaturas add column periodicidade varchar(20) not null default 'mensal';
