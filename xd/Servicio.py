class Servicio(db.Model):
    __tablename__ = 'servicios'

    Id = db.Column(db.Integer, primary_key=True)
    Id_Empleado_Recibe = db.Column(db.Integer, db.ForeignKey('empleado.Id'))
    Id_Empleado_Lava = db.Column(db.Integer, db.ForeignKey('empleado.Id'))
    Id_Vehiculo = db.Column(db.Integer, db.ForeignKey('vehículos.Id'))  # Relación con la tabla 'vehículos'
    Id_TipoLavado = db.Column(db.Integer, db.ForeignKey('tipo_lavado.Id'))
    Fecha_Recibe = db.Column(db.DateTime, default=datetime.utcnow)
    Hora_Recibe = db.Column(db.Time)
    Hora_Entrega = db.Column(db.Time)
    Precio = db.Column(db.Numeric(10, 2))
    Estado = db.Column(db.String(50), default="En proceso")

    # Relaciones
    empleado_recibe = db.relationship('Empleado', foreign_keys=[Id_Empleado_Recibe])
    empleado_lava = db.relationship('Empleado', foreign_keys=[Id_Empleado_Lava])
    vehiculo = db.relationship('Vehiculo')  # No hace falta usar backref aquí, solo la relación directa
    tipo_lavado = db.relationship('TipoLavado')



