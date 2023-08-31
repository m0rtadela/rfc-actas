import firebase_admin
from firebase_admin import credentials, firestore, storage
from io import BytesIO


credentials = credentials.ApplicationDefault()
app = firebase_admin.initialize_app(credentials)

db = firestore.client()

def get_user(user_id):
    return db.collection(u'users').document( user_id ).get()

def get_users():
    return db.collection(u'users').get()

def user_put( user_data ):
    user_ref = db.collection(u'users').document( user_data.username )
    user_ref.set( {u'password': user_data.password} )

def constancia_add( constancia ):
    db.collection(u'constancias').add( {
        u'rfc': constancia.rfc,
        u'curp': constancia.curp,
        # u'name': constancia.name,
        # u'first_last_name': constancia.first_last_name,
        # u'second_last_name': constancia.second_last_name,
        u'tipo': constancia.tipo,
        u'owner': constancia.owner_id[0],
        u'date': constancia.date,
        u'state': constancia.state
    } )

def constancias_add( constancias ):
    print("Subiendo constancias a Firestore")
    batch = db.batch()
    for constancia in constancias:
        constancia_ref = db.collection(u'constancias').document()
        batch.set( constancia_ref, {
            u'rfc': constancia.rfc,
            u'curp': constancia.curp,
            # u'name': constancia.name,
            # u'first_last_name': constancia.first_last_name,
            # u'second_last_name': constancia.second_last_name,
            u'tipo': constancia.tipo,
            u'owner': constancia.owner_id[0],
            u'date': constancia.date,
            u'state': constancia.state
        } )
        print(constancia_ref)
    batch.commit()
    print("Constancias subidas a Firestore")

def get_constancias( user_id ):
    return db.collection(u'constancias')\
        .where(u'owner', u'==', user_id).get()

def get_constancia_pending( user_id ):
    return db.collection(u'constancias')\
        .where(u'owner', u'==', user_id)\
        .where(u'state', u'==', u'PENDING').get()

def get_all_constancias_pending():
    return db.collection(u'constancias')\
        .where(u'state', u'==', u'PENDING').get()

def update_constancia_status( constancia_id, status, file="" ):
    constancia_ref = db.collection(u'constancias').document( constancia_id )
    constancia_ref.update( {u'state': status, 'file_url': file} )

def upload_file( file_path, file_name, user_id ):
    f_name = f"{user_id}/{file_name}.pdf"
    bucket = storage.bucket("rfc-actas.appspot.com", app)
    blob = bucket.blob( f_name )
    blob.upload_from_filename( file_path, content_type='application/pdf' )
    return f_name

def download_file( file_path ):
    bucket = storage.bucket("rfc-actas.appspot.com", app)
    blob = bucket.blob( file_path )
    file = BytesIO()
    blob.download_to_file( file )
    return ( file, file_path.split('/')[-1] )

def get_certificate():
    bucket = storage.bucket("rfc-actas.appspot.com", app)
    blob = bucket.blob( "certificados/certificado.cer" )
    file = BytesIO()
    blob.download_to_file( file )
    return file

def get_key():
    bucket = storage.bucket("rfc-actas.appspot.com", app)
    blob = bucket.blob( "certificados/llave.key" )
    file = BytesIO()
    blob.download_to_file( file )
    return file