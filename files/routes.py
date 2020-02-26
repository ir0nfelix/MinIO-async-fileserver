from files import views


routes = (
    dict(
        method='GET',
        path='/',
        handler=views.index,
        name='index',
    ),
    dict(
        method='POST',
        path='/upload/',
        handler=views.upload,
        name='upload',
    ),
)
