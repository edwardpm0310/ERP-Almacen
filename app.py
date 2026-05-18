from flask import Flask, render_template, redirect, url_for, request, flash
from config import Config
from models import db, Proveedor, Producto, Compra, DetalleCompra, Cliente, Venta, DetalleVenta
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# ===================== CRUD PROVEEDORES =====================
@app.route('/proveedores')
def proveedores():
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    return render_template('proveedores/index.html', proveedores=proveedores)

@app.route('/proveedores/crear', methods=['GET', 'POST'])
def crear_proveedor():
    if request.method == 'POST':
        nuevo = Proveedor(
            nombre=request.form['nombre'],
            ruc=request.form['ruc'],
            telefono=request.form.get('telefono'),
            email=request.form.get('email'),
            direccion=request.form.get('direccion')
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Proveedor creado correctamente', 'success')
        return redirect(url_for('proveedores'))
    return render_template('proveedores/crear.html')

@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    if request.method == 'POST':
        proveedor.nombre = request.form['nombre']
        proveedor.ruc = request.form['ruc']
        proveedor.telefono = request.form.get('telefono')
        proveedor.email = request.form.get('email')
        proveedor.direccion = request.form.get('direccion')
        db.session.commit()
        flash('Proveedor actualizado', 'success')
        return redirect(url_for('proveedores'))
    return render_template('proveedores/editar.html', proveedor=proveedor)

@app.route('/proveedores/eliminar/<int:id>')
def eliminar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    db.session.delete(proveedor)
    db.session.commit()
    flash('Proveedor eliminado', 'danger')
    return redirect(url_for('proveedores'))

# ===================== CRUD PRODUCTOS =====================
@app.route('/productos')
def productos():
    productos = Producto.query.order_by(Producto.nombre).all()
    return render_template('productos/index.html', productos=productos)

@app.route('/productos/crear', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        nuevo = Producto(
            codigo=request.form['codigo'],
            nombre=request.form['nombre'],
            descripcion=request.form.get('descripcion'),
            precio_compra=float(request.form.get('precio_compra', 0)),
            precio_venta=float(request.form.get('precio_venta', 0)),
            stock=int(request.form.get('stock', 0)),
            stock_minimo=int(request.form.get('stock_minimo', 5)),
            proveedor_id=int(request.form['proveedor_id']) if request.form.get('proveedor_id') else None
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Producto creado correctamente', 'success')
        return redirect(url_for('productos'))
    
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    return render_template('productos/crear.html', proveedores=proveedores)
@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        producto.codigo = request.form['codigo']
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form.get('descripcion')
        producto.precio_compra = float(request.form.get('precio_compra', 0))
        producto.precio_venta = float(request.form.get('precio_venta', 0))
        producto.stock = int(request.form.get('stock', 0))
        producto.stock_minimo = int(request.form.get('stock_minimo', 5))
        producto.proveedor_id = int(request.form['proveedor_id']) if request.form.get('proveedor_id') else None
        
        db.session.commit()
        flash('Producto actualizado correctamente', 'success')
        return redirect(url_for('productos'))
    
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    return render_template('productos/editar.html', producto=producto, proveedores=proveedores)


@app.route('/productos/eliminar/<int:id>')
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente', 'danger')
    return redirect(url_for('productos'))
@app.route('/productos/ajuste/<int:id>', methods=['GET', 'POST'])

# ===================== AJUSTE DE STOCK =====================
@app.route('/productos/ajuste/<int:id>', methods=['GET', 'POST'])
def ajuste_stock(id):
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'POST':
        cantidad = int(request.form['cantidad'])
        tipo = request.form['tipo']   # entrada o salida
        motivo = request.form.get('motivo', 'Ajuste manual')
        
        if tipo == 'entrada':
            producto.stock += cantidad
            flash(f'Se agregaron {cantidad} unidades de {producto.nombre}', 'success')
        else:  # salida
            if producto.stock >= cantidad:
                producto.stock -= cantidad
                flash(f'Se restaron {cantidad} unidades de {producto.nombre}', 'success')
            else:
                flash('Stock insuficiente para realizar la salida', 'danger')
                return redirect(url_for('ajuste_stock', id=id))
        
        db.session.commit()
        return redirect(url_for('productos'))
    
    return render_template('productos/ajuste.html', producto=producto)
# =======================================================

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    total_productos = Producto.query.count()
    stock_bajo = Producto.query.filter(Producto.stock <= Producto.stock_minimo).count()
    valor_inventario = db.session.query(db.func.sum(Producto.stock * Producto.precio_compra)).scalar() or 0
    total_proveedores = Proveedor.query.count()
    productos_bajos = Producto.query.filter(Producto.stock <= Producto.stock_minimo).limit(6).all()

    return render_template('dashboard.html', 
                           total_productos=total_productos,
                           stock_bajo=stock_bajo,
                           valor_inventario=valor_inventario,
                           total_proveedores=total_proveedores,
                           productos_bajos=productos_bajos)

# ===================== CRUD COMPRAS =====================

@app.route('/compras')
def compras():
    # Filtros básicos
    proveedor_id = request.args.get('proveedor_id')
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')

    query = Compra.query.order_by(Compra.fecha.desc())

    if proveedor_id:
        query = query.filter(Compra.proveedor_id == proveedor_id)
    # Se pueden agregar más filtros de fecha después

    compras = query.all()
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()

    return render_template('compras/index.html', 
                         compras=compras, 
                         proveedores=proveedores)

@app.route('/compras/crear', methods=['GET', 'POST'])
def crear_compra():
    if request.method == 'POST':
        proveedor_id = request.form.get('proveedor_id')
        
        if not proveedor_id:
            flash('Debe seleccionar un proveedor', 'danger')
            return redirect(url_for('crear_compra'))
        
        nueva_compra = Compra(proveedor_id=proveedor_id, total=0.0)
        db.session.add(nueva_compra)
        db.session.commit()
        
        flash('Compra creada. Ahora puedes agregar productos.', 'success')
        return redirect(url_for('compras'))  # Por ahora redirige al listado
    
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    return render_template('compras/crear.html', proveedores=proveedores)

# ===================== DETALLE DE COMPRA =====================

@app.route('/compras/<int:compra_id>/agregar', methods=['GET', 'POST'])
def agregar_detalle_compra(compra_id):
    compra = Compra.query.get_or_404(compra_id)
    
    if request.method == 'POST':
        producto_id = request.form['producto_id']
        cantidad = int(request.form['cantidad'])
        precio_unitario = float(request.form['precio_unitario'])
        
        # Crear detalle
        detalle = DetalleCompra(
            compra_id=compra_id,
            producto_id=producto_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )
        db.session.add(detalle)
        
        # Actualizar stock automáticamente
        producto = Producto.query.get(producto_id)
        producto.stock += cantidad
        
        # Actualizar total de la compra
        compra.total += cantidad * precio_unitario
        
        db.session.commit()
        flash('Producto agregado a la compra y stock actualizado', 'success')
        return redirect(url_for('compras'))
    
    productos = Producto.query.order_by(Producto.nombre).all()
    return render_template('compras/agregar.html', compra=compra, productos=productos)
    
@app.route('/compras/<int:compra_id>/detalle')
def detalle_compra(compra_id):
    compra = Compra.query.get_or_404(compra_id)
    return render_template('compras/detalle.html', compra=compra)

# ===================== VENTAS =====================

@app.route('/ventas')
def ventas():
    search = request.args.get('search', '').strip()
    query = Venta.query.order_by(Venta.fecha.desc())

    if search:
        query = query.join(Cliente).filter(
            Cliente.nombre.ilike(f'%{search}%') |
            Venta.id.cast(db.String).ilike(f'%{search}%')
        )
    
    ventas = query.all()
    return render_template('ventas/index.html', ventas=ventas, search=search)

@app.route('/ventas/crear', methods=['GET', 'POST'])
def crear_venta():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        
        nueva_venta = Venta(
            cliente_id=cliente_id,
            total=0.0
        )
        db.session.add(nueva_venta)
        db.session.commit()
        
        flash('Venta creada. Ahora agrega productos.', 'success')
        return redirect(url_for('agregar_detalle_venta', venta_id=nueva_venta.id))
    
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    return render_template('ventas/crear.html', clientes=clientes)

@app.route('/ventas/<int:venta_id>/agregar', methods=['GET', 'POST'])
def agregar_detalle_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    
    if request.method == 'POST':
        try:
            producto_id = int(request.form['producto_id'])
            cantidad = int(request.form['cantidad'])
            precio_unitario = float(request.form['precio_unitario'])
        except ValueError:
            flash('Por favor ingrese datos válidos', 'danger')
            return redirect(url_for('agregar_detalle_venta', venta_id=venta_id))

        producto = Producto.query.get_or_404(producto_id)

        # Validación de stock
        if producto.stock < cantidad:
            flash(f'Stock insuficiente. Solo hay {producto.stock} unidades de {producto.nombre}', 'danger')
            return redirect(url_for('agregar_detalle_venta', venta_id=venta_id))

        # Crear detalle de venta
        detalle = DetalleVenta(
            venta_id=venta_id,
            producto_id=producto_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )
        db.session.add(detalle)

        # Descontar stock
        producto.stock -= cantidad

        # Actualizar total de la venta
        venta.total += cantidad * precio_unitario

        db.session.commit()
        flash(f'Se agregaron {cantidad} unidades de {producto.nombre}', 'success')
        return redirect(url_for('agregar_detalle_venta', venta_id=venta_id))

    # GET request
    productos = Producto.query.order_by(Producto.nombre).all()
    return render_template('ventas/agregar.html', venta=venta, productos=productos)

@app.route('/ventas/<int:venta_id>/detalle')
def detalle_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    return render_template('ventas/detalle.html', venta=venta)

@app.route('/ventas/<int:venta_id>/anular')
def anular_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    
    # Devolver el stock de cada producto vendido
    for detalle in venta.detalles:
        producto = detalle.producto
        producto.stock += detalle.cantidad  # Se devuelve el stock
    
    # Opcional: Marcar como anulada en vez de borrar (mejor práctica)
    # venta.estado = 'Anulada'   # Si quieres agregar un campo estado después
    
    db.session.delete(venta)   # Borramos la venta y sus detalles
    db.session.commit()
    
    flash(f'Venta #{venta_id} anulada correctamente. Stock devuelto.', 'danger')
    return redirect(url_for('ventas'))
    
# ===================== CRUD CLIENTES =====================

@app.route('/clientes')
def clientes():
    search = request.args.get('search', '').strip()
    query = Cliente.query

    if search:
        query = query.filter(
            (Cliente.nombre.ilike(f'%{search}%')) |
            (Cliente.dni.ilike(f'%{search}%')) |
            (Cliente.telefono.ilike(f'%{search}%'))
        )
    
    clientes = query.order_by(Cliente.nombre).all()
    return render_template('clientes/index.html', clientes=clientes, search=search)

@app.route('/clientes/crear', methods=['GET', 'POST'])
def crear_cliente():
    if request.method == 'POST':
        dni = request.form['dni'].strip()
        if Cliente.query.filter_by(dni=dni).first():
            flash('Ya existe un cliente con ese DNI', 'danger')
            return redirect(url_for('crear_cliente'))
        
        nuevo = Cliente(
            nombre=request.form['nombre'].strip(),
            dni=dni,
            telefono=request.form.get('telefono', '').strip(),
            email=request.form.get('email', '').strip(),
            direccion=request.form.get('direccion', '').strip()
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Cliente creado correctamente', 'success')
        return redirect(url_for('clientes'))
    return render_template('clientes/crear.html')

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nombre = request.form['nombre'].strip()
        cliente.telefono = request.form.get('telefono', '').strip()
        cliente.email = request.form.get('email', '').strip()
        cliente.direccion = request.form.get('direccion', '').strip()
        db.session.commit()
        flash('Cliente actualizado correctamente', 'success')
        return redirect(url_for('clientes'))
    return render_template('clientes/editar.html', cliente=cliente)

@app.route('/clientes/eliminar/<int:id>')
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado correctamente', 'danger')
    return redirect(url_for('clientes'))

# =======================================================   

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)