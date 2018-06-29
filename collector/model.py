#encoding = utf8

from peewee import *
from playhouse.postgres_ext import *
from scrapy.utils.project import get_project_settings
import datetime

class BaseExtModel(Model):
    class Meta:
        settings = get_project_settings()
        psql_conf = settings.getdict("POSTGRESQL_CONFIG")
        database = PostgresqlDatabase(
            psql_conf.get('db'),  # Required by Peewee.
            user = psql_conf.get('user'),
            password = psql_conf.get('passwd'),
            host='127.0.0.1',
            autorollback=True,
        )
        #database = psql_db

class Article(BaseExtModel):
    name = TextField(default="")
    title = TextField(default="")
    desc    = TextField(default="")
    fly = TextField(default="")
    rubric = TextField(default="")
    summary = TextField(default="")
    content = TextField(default="")
    imgs = ArrayField(field_class=TextField,null=True)
    section = TextField(default="")
    edition = DateField()
    origin = TextField(unique=True)
    ts = DateTimeField(default=datetime.datetime.now)
    tsv = TSVectorField()

    class Meta:
        indexes = (
            (('edition',), False),
            (('section',), False),
        )

class Edition(BaseExtModel):
    cover   = TextField()
    edition = DateField(unique=True)


if __name__ == '__main__':
    settings = get_project_settings()
    psql_conf = settings.getdict("POSTGRESQL_CONFIG")
    psql_db = PostgresqlDatabase(
        psql_conf.get('db'),  # Required by Peewee.
        user = psql_conf.get('user'),
        password = psql_conf.get('passwd'),
        host='127.0.0.1',
        autorollback=True,
    )
    psql_db.connect()
    psql_db.create_tables([Edition, Article])

    date = datetime.datetime.now()
    e = Edition(edition=date, cover='cover')
    e.save()

    content='hello world'
    a = Article(edition=date,name='aaaid',title='atitle',imgs=['a','b'],tsv=fn.to_tsvector(content))
    a.save()

