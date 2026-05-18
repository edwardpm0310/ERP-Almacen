from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ================== MODELOS ==================

class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ruc = db.Column(db.String(11), unique=True, nullable=False)
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)

    def __repr__(self):
        return f'<Proveedor {self.nombre}>'


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True)


class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    precio_compra = db.Column(db.Float, default=0.0)
    precio_venta = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'))


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(8), unique=True, nullable=False)
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)


# (Mantengo los demás modelos igual por ahora)
class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, default=0.0)

    proveedor = db.relationship('Proveedor', backref='compras')
    detalles = db.relationship('DetalleCompra', backref='compra', cascade="all, delete-orphan")


class DetalleCompra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey('compra.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

    producto = db.relationship('Producto', backref='detalles_compra')


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, default=0.0)

    cliente = db.relationship('Cliente', backref='ventas')
    detalles = db.relationship('DetalleVenta', backref='venta', cascade="all, delete-orphan")


class DetalleVenta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

    producto = db.relationship('Producto', backref='detalles_venta')