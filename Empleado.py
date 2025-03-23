from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Empleado(db.Model):
    __tablename__ = 'empleado'

    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50))
    Apellidos = db.Column(db.String(50))
    Fecha_Nacimiento = db.Column(db.Date)
    Estado = db.Column(db.String(50))

    # Relaciones con otros modelos
    servicios_recibe = db.relationship('Servicio', foreign_keys='Servicio.Id_Empleado_Recibe')
    servicios_lava = db.relationship('Servicio', foreign_keys='Servicio.Id_Empleado_Lava')
