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
    valor_mensal float not null,
    data_renovacao date not null,
    status varchar(20) not null default 'ativa',
    tipo_plano varchar(50),
    metodo_pagamento varchar(30) not null default 'cartao_credito',
    id_usuario int not null,
    id_categoria int not null,
    foreign key (id_usuario) references usuarios(id_usuario),
    foreign key (id_categoria) references categorias(id_categoria)
);
-- Para bancos já existentes, execute uma vez:
-- alter table assinaturas add column metodo_pagamento varchar(30) not null default 'cartao_credito';
