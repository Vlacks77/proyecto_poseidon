-- public.inv_suministro definition

-- Drop table

-- DROP TABLE public.inv_suministro;

CREATE TABLE public.inv_suministro (
	id int4 NOT NULL,
	proveedor varchar NULL,
	transportadora varchar NULL,
	fec_cre timestamp NULL,
	fec_mod timestamp NULL,
	usu_cre varchar(50) NULL,
	usu_mod varchar(50) NULL,
	api_estado varchar(20) NULL,
	api_transaccion varchar(20) NULL,
	CONSTRAINT inv_suministro_pk PRIMARY KEY (id)
);


-- public.productos definition

-- Drop table

-- DROP TABLE public.productos;

CREATE TABLE public.productos (
	id_producto int4 NOT NULL,
	descripcion varchar NOT NULL,
	marca varchar NULL,
	fec_cre timestamp NULL,
	fec_mod timestamp NULL,
	usu_cre varchar(50) NULL,
	usu_mod varchar(50) NULL,
	api_estado varchar(20) NULL,
	api_transaccion varchar(20) NULL,
	precio numeric(6, 3) NULL,
	medida varchar(10) NOT NULL,
	precio_sf numeric(6, 3) NULL,
	CONSTRAINT productos_pk PRIMARY KEY (id_producto)
);


-- public.vta_cliente definition

-- Drop table

-- DROP TABLE public.vta_cliente;

CREATE TABLE public.vta_cliente (
	id int4 NOT NULL,
	razon_social varchar NOT NULL,
	celular int4 NULL,
	nit int4 NULL,
	fec_cre timestamp NULL,
	fec_mod timestamp NULL,
	usu_cre varchar(50) NULL,
	usu_mod varchar(50) NULL,
	api_estado varchar(20) NULL,
	api_transaccion varchar(20) NULL,
	CONSTRAINT vta_cliente_pk PRIMARY KEY (id)
);


-- public.inv_detalle_suministro definition

-- Drop table

-- DROP TABLE public.inv_detalle_suministro;

CREATE TABLE public.inv_detalle_suministro (
	id int4 NOT NULL,
	fecha date NOT NULL,
	unidades int4 NULL,
	kilos int4 NULL,
	emisor varchar NOT NULL,
	id_producto int4 NOT NULL,
	fec_cre timestamp NULL,
	fec_mod timestamp NULL,
	usu_cre varchar(50) NULL,
	usu_mod varchar(50) NULL,
	api_estado varchar(20) NULL,
	api_transaccion varchar(20) NULL,
	id_suministro int4 NOT NULL,
	CONSTRAINT inv_detalle_suministro_pk PRIMARY KEY (id),
	CONSTRAINT inv_detalle_suministro_inv_suministro_fk FOREIGN KEY (id) REFERENCES public.inv_suministro(id),
	CONSTRAINT inv_detalle_suministro_productos_fk FOREIGN KEY (id_producto) REFERENCES public.productos(id_producto)
);


-- public.inv_stock definition

-- Drop table

-- DROP TABLE public.inv_stock;

CREATE TABLE public.inv_stock (
	id_producto int4 NOT NULL,
	unidades int4 NOT NULL,
	kilos int4 NOT NULL,
	id_stock int4 NOT NULL,
	fec_cre timestamp NULL,
	fec_mod timestamp NULL,
	usu_cre varchar(50) NULL,
	usu_mod varchar(50) NULL,
	api_estado varchar(20) NULL,
	api_transaccion varchar(20) NULL,
	CONSTRAINT inv_stock_pk PRIMARY KEY (id_stock),
	CONSTRAINT inv_stock_productos_fk FOREIGN KEY (id_producto) REFERENCES public.productos(id_producto)
);


-- public.vta_ventas definition

-- Drop table

-- DROP TABLE public.vta_ventas;

CREATE TABLE public.vta_ventas (
	id_venta int4 NOT NULL,
	id_producto varchar NOT NULL,
	fecha date NOT NULL,
	id_cliente int4 NOT NULL,
	fec_cre timestamp NULL,
	fec_mod timestamp NULL,
	usu_cre varchar(50) NULL,
	usu_mod varchar(50) NULL,
	api_estado varchar(20) NULL,
	api_transaccion varchar(20) NULL,
	rebaja numeric(6, 3) NULL,
	tipo varchar(2) NULL,
	efectivo numeric(6, 3) NULL,
	cambio numeric(6, 3) NULL,
	CONSTRAINT vta_ventas_pk PRIMARY KEY (id_venta),
	CONSTRAINT vta_ventas_vta_cliente_fk FOREIGN KEY (id_cliente) REFERENCES public.vta_cliente(id)
);


-- public.inv_historial_stock definition

-- Drop table

-- DROP TABLE public.inv_historial_stock;

CREATE TABLE public.inv_historial_stock (
	id_inv_historial_stock int4 NOT NULL,
	id_stock int4 NOT NULL,
	id_inv_suministro int4 NULL,
	id_venta int4 NULL,
	fec_cre timestamp NULL,
	fec_mod timestamp NULL,
	usu_cre varchar(50) NULL,
	usu_mod varchar(50) NULL,
	api_estado varchar(20) NULL,
	api_transaccion varchar(20) NULL,
	tipo varchar NULL,
	CONSTRAINT inv_historial_stock_pk PRIMARY KEY (id_inv_historial_stock),
	CONSTRAINT inv_historial_stock_inv_stock_fk FOREIGN KEY (id_stock) REFERENCES public.inv_stock(id_stock),
	CONSTRAINT inv_historial_stock_inv_suministro_fk FOREIGN KEY (id_inv_suministro) REFERENCES public.inv_suministro(id),
	CONSTRAINT inv_historial_stock_vta_ventas_fk FOREIGN KEY (id_venta) REFERENCES public.vta_ventas(id_venta)
);


-- public.vta_facturas definition

-- Drop table

-- DROP TABLE public.vta_facturas;

CREATE TABLE public.vta_facturas (
	id_factura int4 NOT NULL,
	id_cliente int4 NOT NULL,
	nit int4 NULL,
	id_venta int4 NULL,
	fec_cre timestamp NULL,
	fec_mod timestamp NULL,
	usu_cre varchar(50) NULL,
	usu_mod varchar(50) NULL,
	api_estado varchar(20) NULL,
	api_transaccion varchar(20) NULL,
	CONSTRAINT vta_facturas_pk PRIMARY KEY (id_factura),
	CONSTRAINT vta_facturas_vta_cliente_fk FOREIGN KEY (id_cliente) REFERENCES public.vta_cliente(id),
	CONSTRAINT vta_facturas_vta_ventas_fk FOREIGN KEY (id_venta) REFERENCES public.vta_ventas(id_venta)
);