from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, MetaData, create_engine

def connect(user, password, db, host='localhost', port=5432):
    '''Returns a connection and a metadata object'''
    # We connect with the help of the PostgreSQL URL
    # postgresql://postgres:root@localhost:5432/taipei_places
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    con = create_engine(url, client_encoding='utf8', echo=True)

    # We then bind the connection to MetaData()
    meta = MetaData(bind=con, reflect=True)

    return con, meta

def tables():
    con, meta = connect('postgres','root','taipei_places')
    
    #Tables based on schema
    person = Table('person', meta,
                   Column('uID', Integer, primary_key=True),
                   Column('password',String),
                   Column('name',String),
                   Column('gender',String),
                   Column('age',Integer)
                   )
    vendor = Table('vendor', meta,
                   Column('vID', String, primary_key=True),
                   Column('vname',String),
                   Column('address',String),
                   Column('district',String),
                   Column('latitude', Float),
                   Column('longitude', Float),
                   Column('rating', Float),
                   )
    review = Table('review', meta,
                   Column('rID', Integer, primary_key=True),
                   Column('author',String),
                   Column('description',String),
                   Column('rating',Float),
                   Column('vID',String, ForeignKey('vendor.vID'))
                   )
    category = Table('category', meta,
                   Column('cName', String, primary_key=True)
                   )
    like = Table('likes', meta,
                   Column('uID',Integer, ForeignKey('person.uID')),
                   Column('vID',String, ForeignKey('vendor.vID'))
                   )
    has = Table('has', meta,
                   Column('cName',String, ForeignKey('category.cName')),
                   Column('vID',String, ForeignKey('vendor.vID'))
                   )
    #Create above tables in database
    meta.create_all(con)
    return
