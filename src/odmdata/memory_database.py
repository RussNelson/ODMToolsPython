from odmdata import *
from odmdata.series import copy_series

class MemoryDatabase(object):

    # series_service is a SeriesService
    def __init__(self, series):        
        self.connection_string = "sqlite:///:memory:"
        self.session_factory = SessionFactory(self.connection_string, echo=False)
        Base.metadata.create_all(self.session_factory.engine)

        self.series = copy_series(series)
        self.session = self.session_factory.get_session()
        self.session.add(self.series)
        self.session.add_all(self.series.data_values)
        self.session.commit()

    def get_series(self):
        series = self.session.query(Series).one()
        return series

    def get_data_values(self):
        dvs = self.session.query(DataValue).all()
        return [dv.get_list_repr() for dv in dvs ]
  
    def delete_points(self, filter):
        raise NotImplementedError

    def add_points(self, filter):
        raise NotImplementedError

    def update_points(self, filter, values):
        raise NotImplementedError

    