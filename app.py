from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

# Crear una instancia de SQLAlchemy
db = SQLAlchemy()

# Crear la aplicación Flask
app = Flask(__name__)
app.config.from_object('config.Config')  # Configuración externa (como la cadena de conexión a la base de datos)
db.init_app(app)  # Inicializa la extensión de SQLAlchemy con la app de Flask

# Definir los modelos de base de datos

class Empleado(db.Model):
    __tablename__ = 'empleado'
    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50))
    Apellidos = db.Column(db.String(50))
    Fecha_Nacimiento = db.Column(db.Date)
    Estado = db.Column(db.String(50))

    # Relaciones
    servicios_recibe = db.relationship('Servicio', foreign_keys='Servicio.Id_Empleado_Recibe')
    servicios_lava = db.relationship('Servicio', foreign_keys='Servicio.Id_Empleado_Lava')
    turnos = db.relationship('TurnoEmpleado', backref='empleado')


class Vehiculo(db.Model):
    __tablename__ = 'vehículos'

    Id = db.Column(db.Integer, primary_key=True)
    Placa = db.Column(db.String(50), unique=True, nullable=False)
    Marca = db.Column(db.String(50))
    Modelo = db.Column(db.String(50))
    Color = db.Column(db.String(50))
    Tipo_Vehículo = db.Column(db.String(50))
    Descripcion = db.Column(db.String(50))  # 👈 Asegúrate de tener esta línea
    Estado = db.Column(db.String(50), default="Activo")

    # Relación con servicios
    servicios = db.relationship('Servicio', backref='vehiculo')

class ChecklistIngreso(db.Model):
    __tablename__ = 'checklist_ingreso'
    Id = db.Column(db.Integer, primary_key=True)
    Id_Servicio = db.Column(db.Integer, db.ForeignKey('servicios.Id'))
    Observaciones = db.Column(db.Text)
    EstadoVehiculo = db.Column(db.String(100))

    servicio = db.relationship('Servicio', backref='checklist')

class InsumoPorServicio(db.Model):
    __tablename__ = 'insumos_por_servicio'
    Id = db.Column(db.Integer, primary_key=True)
    Id_Servicio = db.Column(db.Integer, db.ForeignKey('servicios.Id'))
    Id_Insumo = db.Column(db.Integer, db.ForeignKey('insumos.Id'))
    Cantidad_Utilizada = db.Column(db.Integer)

    servicio = db.relationship('Servicio', backref='insumos_usados')
    insumo = db.relationship('Insumo')

class TipoLavado(db.Model):
    __tablename__ = 'tipo_lavado'
    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50))
    Precio = db.Column(db.Numeric(10, 2))
    Id_Insumo = db.Column(db.Integer, db.ForeignKey('insumos.Id'))
    Estado = db.Column(db.String(50))

    servicios = db.relationship('Servicio', backref='tipo_lavado')


class Servicio(db.Model):
    __tablename__ = 'servicios'
    Id = db.Column(db.Integer, primary_key=True)
    Id_Empleado_Recibe = db.Column(db.Integer, db.ForeignKey('empleado.Id'))
    Id_Empleado_Lava = db.Column(db.Integer, db.ForeignKey('empleado.Id'))
    Id_Tipovehículo = db.Column(db.Integer, db.ForeignKey('vehículos.Id'))
    Id_TipoLavado = db.Column(db.Integer, db.ForeignKey('tipo_lavado.Id'))
    Hora_Recibe = db.Column(db.Time)
    Hora_Entrega = db.Column(db.Time)
    Precio = db.Column(db.Numeric(10, 2))
    Placa = db.Column(db.String(50))
    Fecha = db.Column(db.Date)
    Estado = db.Column(db.String(50), default='En proceso')  # Esto ya lo manejas visualmente


    # Relaciones explícitas con alias
    empleado_recibe = db.relationship('Empleado', foreign_keys=[Id_Empleado_Recibe], backref='recibe_servicios')
    empleado_lava = db.relationship('Empleado', foreign_keys=[Id_Empleado_Lava], backref='lava_servicios')
    # vehiculo y tipo_lavado están definidos con backref


class Insumo(db.Model):
    __tablename__ = 'insumos'
    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50))
    Precio_Unitario = db.Column(db.Numeric(10, 2))
    Id_TipoInsumo = db.Column(db.Integer, db.ForeignKey('tipo_insumo.Id'))
    Estado = db.Column(db.String(50))

    tipo_insumo = db.relationship('TipoInsumo', backref='insumos')


class TipoInsumo(db.Model):
    __tablename__ = 'tipo_insumo'
    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50))
    Descripcion = db.Column(db.Integer)  # Es un int en tu SQL (¿quieres cambiarlo a texto?)
    Estado = db.Column(db.Integer)


class Inventario(db.Model):
    __tablename__ = 'inventario'
    Id = db.Column(db.Integer, primary_key=True)
    Id_insumo = db.Column(db.Integer, db.ForeignKey('insumos.Id'))
    Stock = db.Column(db.Integer)
    Estado = db.Column(db.Integer)  # En tu SQL es int, aunque suena a texto

    insumo = db.relationship('Insumo', backref='inventario')


class Jornada(db.Model):
    __tablename__ = 'jornada'
    Id = db.Column(db.Integer, primary_key=True)
    Hora_Inicio = db.Column(db.Time)
    Hora_Final = db.Column(db.Time)
    Estado = db.Column(db.String(50))

    turnos = db.relationship('TurnoEmpleado', backref='jornada')


class TurnoEmpleado(db.Model):
    __tablename__ = 'turno_empleado'
    Id = db.Column(db.Integer, primary_key=True)
    Id_Empleado = db.Column(db.Integer, db.ForeignKey('empleado.Id'))
    Día = db.Column(db.String(50))
    Id_Jornada = db.Column(db.Integer, db.ForeignKey('jornada.Id'))

@app.route('/registro_insumo', methods=['GET', 'POST'])
def registro_insumo():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        tipo = request.form['tipo']
        estado = request.form['estado']

        nuevo = Insumo(Nombre=nombre, Precio_Unitario=precio, Id_TipoInsumo=tipo, Estado=estado)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('registro_insumo.html')

@app.route('/inventario')
def inventario():
    inventario = Inventario.query.all()
    return render_template('inventario.html', inventario=inventario)

@app.route('/registro_inventario', methods=['GET', 'POST'])
def registro_inventario():
    if request.method == 'POST':
        insumo_id = request.form['insumo']
        stock = request.form['stock']
        estado = request.form['estado']

        item = Inventario(Id_insumo=insumo_id, Stock=stock, Estado=estado)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('registro_inventario.html')




# Rutas para manejar la aplicación

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro_vehiculo', methods=['GET', 'POST'])
def registro_vehiculo():
    if request.method == 'POST':
        placa = request.form['placa']
        marca = request.form['marca']
        modelo = request.form['modelo']
        color = request.form['color']
        tipo_vehiculo = request.form['tipo_vehiculo']
        descripcion = request.form['descripcion']
        estado = request.form['estado']

        vehiculo = Vehiculo(
            Placa=placa,
            Marca=marca,
            Modelo=modelo,
            Color=color,
            Tipo_Vehículo=tipo_vehiculo,
            Descripcion=descripcion,
            Estado=estado
        )

        db.session.add(vehiculo)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('registro_vehiculo.html')


@app.route('/servicios')
def servicios():
    servicios = Servicio.query.all()
    return render_template('servicios.html', servicios=servicios)
@app.route('/insumos')
def insumos():
    insumos = Insumo.query.all()
    return render_template('insumos.html', insumos=insumos)

@app.route('/registrar_servicio', methods=['GET', 'POST'])
def registrar_servicio():
    if request.method == 'POST':
        # Recoger datos del formulario
        placa = request.form['placa']
        empleado_recibe = int(request.form['empleado_recibe'])
        empleado_lava = int(request.form['empleado_lava'])
        tipo_lavado = int(request.form['tipo_lavado'])
        observaciones = request.form['observaciones']

        # Obtener vehículo
        vehiculo = Vehiculo.query.filter_by(Placa=placa).first()
        if not vehiculo:
            return "❌ Vehículo no encontrado", 404

        # Obtener tipo de lavado y su precio
        tipo = TipoLavado.query.get(tipo_lavado)
        precio = tipo.Precio

        # Crear nuevo servicio
        servicio = Servicio(
            Id_Empleado_Recibe=empleado_recibe,
            Id_Empleado_Lava=empleado_lava,
            Id_Tipovehículo=vehiculo.Id,
            Id_TipoLavado=tipo_lavado,
            Hora_Recibe=datetime.now().time(),
            Fecha=datetime.now().date(),
            Precio=precio,
            Placa=placa
        )

        db.session.add(servicio)
        db.session.commit()

        # Registrar checklist de ingreso
        checklist = ChecklistIngreso(
            Id_Servicio=servicio.Id,
            Observaciones=observaciones,
            EstadoVehiculo="Normal"
        )

        db.session.add(checklist)
        db.session.commit()

        return redirect(url_for('servicios'))

    # Mostrar formulario (GET)
    empleados = Empleado.query.all()
    tipos_lavado = TipoLavado.query.all()
    return render_template('registro_servicio.html', empleados=empleados, tipos_lavado=tipos_lavado)

@app.route('/ver_inventario')
def ver_inventario():
    inventario = Inventario.query.all()
    return render_template('inventario.html', inventario=inventario)

@app.route('/registro_inventario', methods=['GET', 'POST'])
def registrar_inventario():
    if request.method == 'POST':
        insumo_id = request.form['insumo']
        stock = request.form['stock']
        estado = request.form['estado']

        nuevo = Inventario(Id_insumo=insumo_id, Stock=stock, Estado=estado)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('ver_inventario'))

    insumos = Insumo.query.all()  # Para desplegar en select
    return render_template('registro_inventario.html', insumos=insumos)

def verificar_conexion():
    try:
        # Ejecutar una consulta simple
        db.session.execute(text('SELECT 1'))
        print("✅ Conexión a la base de datos exitosa.")
    except OperationalError as e:
        print("❌ Error al conectar a la base de datos:", e)


if __name__ == '__main__':
    with app.app_context():
        verificar_conexion()  # 👈 Ahora sí funcionará correctamente
    app.run(debug=True)



