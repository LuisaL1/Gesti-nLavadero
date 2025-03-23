class TipoLavado(db.Model):
    __tablename__ = 'tipo_lavado'

    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50))
    Precio = db.Column(db.Numeric(10, 2))  # Cambié Decimal por Numeric
    Id_Insumo = db.Column(db.Integer, db.ForeignKey('insumos.Id'))
    Estado = db.Column(db.String(50))

    # Relación con el modelo Servicio
    servicios = db.relationship('Servicio', backref='tipo_lavado')

