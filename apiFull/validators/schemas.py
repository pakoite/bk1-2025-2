from marshmallow import Schema, fields, validate, validates, ValidationError

class UserSchema(Schema):
    """Schema para validar registro de usuarios"""
    id = fields.Int(dump_only=True)
    
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=50, error='Username debe tener entre 3 y 50 caracteres'),
            validate.Regexp(
                r'^[a-zA-Z0-9_]+$',
                error='Username solo puede contener letras, números y guión bajo'
            )
        ]
    )
    
    email = fields.Email(
        required=True,
        error_messages={'invalid': 'Email inválido'}
    )
    
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, error='Password debe tener mínimo 8 caracteres')
    )
    
    role = fields.Str(
        validate=validate.OneOf(['user', 'admin', 'premium']),
        dump_only=True
    )
    
    created_at = fields.DateTime(dump_only=True)
    
    @validates('username')
    def validate_username(self, value):
        """Validar username no sea palabra reservada"""
        forbidden = ['admin', 'root', 'superuser', 'system']
        if value.lower() in forbidden:
            raise ValidationError('Este username no está permitido')

class UserLoginSchema(Schema):
    """Schema para validar login"""
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class EstablecimientoSchema(Schema):
    """Schema para validar establecimientos"""
    id = fields.Int(dump_only=True)
    
    clee = fields.Str(
        required=True,
        validate=validate.Length(max=255)
    )
    
    nom_estab = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255, error='Nombre requerido')
    )
    
    raz_social = fields.Str(validate=validate.Length(max=255))
    codigo_act = fields.Str(validate=validate.Length(max=255))
    nombre_act = fields.Str(validate=validate.Length(max=255))
    per_ocu = fields.Int(validate=validate.Range(min=0))
    
    tipo_vial = fields.Str(validate=validate.Length(max=255))
    nom_vial = fields.Str(validate=validate.Length(max=255))
    
    tipo_v_e_1 = fields.Str(validate=validate.Length(max=255))
    nom_v_e_1 = fields.Str(validate=validate.Length(max=255))
    tipo_v_e_2 = fields.Str(validate=validate.Length(max=255))
    nom_v_e_2 = fields.Str(validate=validate.Length(max=255))
    tipo_v_e_3 = fields.Str(validate=validate.Length(max=255))
    nom_v_e_3 = fields.Str(validate=validate.Length(max=255))
    
    numero_ext = fields.Str(validate=validate.Length(max=50))
    letra_ext = fields.Str(validate=validate.Length(max=10))
    edificio = fields.Str(validate=validate.Length(max=255))
    edificio_e = fields.Str(validate=validate.Length(max=255))
    numero_int = fields.Str(validate=validate.Length(max=50))
    letra_int = fields.Str(validate=validate.Length(max=10))
    
    tipo_asent = fields.Str(validate=validate.Length(max=255))
    nomb_asent = fields.Str(validate=validate.Length(max=255))
    
    tipoCenCom = fields.Str(validate=validate.Length(max=255))
    nom_CenCom = fields.Str(validate=validate.Length(max=255))
    num_local = fields.Str(validate=validate.Length(max=50))
    
    cod_postal = fields.Str(
        validate=validate.Regexp(r'^\d{5}$', error='Código postal debe tener 5 dígitos')
    )
    
    cve_ent = fields.Str(validate=validate.Length(max=50))
    entidad = fields.Str(validate=validate.Length(max=255))
    cve_mun = fields.Str(validate=validate.Length(max=50))
    municipio = fields.Str(validate=validate.Length(max=255))
    cve_loc = fields.Str(validate=validate.Length(max=50))
    localidad = fields.Str(validate=validate.Length(max=255))
    ageb = fields.Str(validate=validate.Length(max=50))
    manzana = fields.Str(validate=validate.Length(max=50))
    
    telefono = fields.Str(
        validate=validate.Regexp(
            r'^\d{10}$',
            error='Teléfono debe tener 10 dígitos'
        ),
        allow_none=True
    )
    
    correoelec = fields.Email(allow_none=True)
    www = fields.Url(allow_none=True)
    
    tipoUniEco = fields.Str(validate=validate.Length(max=255))
    
    latitud = fields.Float(
        validate=validate.Range(min=-90, max=90, error='Latitud debe estar entre -90 y 90')
    )
    
    longitud = fields.Float(
        validate=validate.Range(min=-180, max=180, error='Longitud debe estar entre -180 y 180')
    )
    
    fecha_alta = fields.DateTime(format='%Y-%m-%d', allow_none=True)

class EstablecimientoUpdateSchema(EstablecimientoSchema):
    """Schema para actualizar establecimientos (todos los campos opcionales)"""
    clee = fields.Str(validate=validate.Length(max=255), required=False)
    nom_estab = fields.Str(validate=validate.Length(max=255), required=False)

class PaginationSchema(Schema):
    """Schema para parámetros de paginación"""
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=20)