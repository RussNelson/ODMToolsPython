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

    def get_data_values(self):
        return []

    def getDataValuesforEdit(self):
        # query = "SELECT ValueID, SeriesID, DataValue, ValueAccuracy, LocalDateTime, UTCOffset, DateTimeUTC, QualifierCode, OffsetValue, OffsetTypeID, CensorCode, SampleID FROM DataValuesEdit AS d LEFT JOIN Qualifiers AS q ON (d.QualifierID = q.QualifierID) "
        query = "SELECT * from DataValuesEdit"
        self.cursor.execute(query)
        return [list(x) for x in  self.cursor.fetchall()]

    def getEditDataValuesforGraph(self):
        query ="SELECT DataValue, LocalDateTime, CensorCode, strftime('%m', LocalDateTime) as DateMonth, strftime('%Y', LocalDateTime) as DateYear FROM DataValuesEdit ORDER BY LocalDateTime"
        self.cursor.execute(query)
        return [list(x) for x in  self.cursor.fetchall()]# return a list of lists orig returns a list of cursors

    def getEditRowCount(self):
        query ="SELECT COUNT(ValueID) FROM DataValuesEdit "
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]


    def getEditColumns(self):
        sql = "SELECT * FROM DataValuesEdit WHERE 1=0"
        # sql= "SELECT ValueID, SeriesID, DataValue, ValueAccuracy, LocalDateTime, UTCOffset, DateTimeUTC, QualifierCode, OffsetValue, OffsetTypeID, CensorCode, SampleID FROM DataValuesEdit AS d LEFT JOIN Qualifiers AS q ON (d.QualifierID = q.QualifierID) WHERE 1=0"
        self.cursor.execute(sql)
        return [(x[0],i) for (i,x) in enumerate(self.cursor.description)]

    def getDataValuesforGraph(self, seriesID, strNoDataValue, strStartDate, strEndDate):
        series = self.series_service.get_series_by_id(seriesID)
        DataValues = [(dv.id, dv.data_value, dv.value_accuracy, dv.local_date_time, dv.utc_offset, dv.date_time_utc,
                dv.site_id, dv.variable_id, dv.offset_value, dv.offset_type_id, dv.censor_code,
                dv.qualifier_id, dv.method_id, dv.source_id, dv.sample_id, dv.derived_from_id,
                dv.quality_control_level_id) for dv in series.data_values]

        #clear any previous queries from table
        self.cursor.execute("DELETE FROM DataValues")

        #fill temporary table with values from requested series
        self.cursor.executemany("INSERT INTO DataValues VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", DataValues)
        self.conn.commit()

        #select values for plotting
        query ="SELECT DataValue, LocalDateTime, CensorCode, strftime('%m', LocalDateTime) as DateMonth, strftime('%Y', LocalDateTime) as DateYear FROM DataValues WHERE (DataValue <> "+ strNoDataValue + ") ORDER BY LocalDateTime"
        self.cursor.execute(query)

        return [list(x) for x in  self.cursor.fetchall()]# return a list of lists orig returns a list of cursors

    def getSeriesCatalog(self):
        sql = "SELECT * FROM SeriesCatalog"
        self.cursor.execute(sql)
        return [list(x) for x in self.cursor.fetchall()]


    def getSeriesColumns(self):
        sql = "SELECT * FROM SeriesCatalog WHERE 1=0"
        self.cursor.execute(sql)
        return (x[0] for (i,x) in enumerate(self.cursor.description))



    def resetDB(self, series_service):
        self.series_service = series_service

        self.conn = sqlite3.connect(":memory:", detect_types= sqlite3.PARSE_DECLTYPES)
        self.cursor = self.conn.cursor()
        self.initDB()

        self.DataValuesEdit= None
        self.SeriesCatalog = None

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def stopEdit(self):
        self.DataValuesEdit= None
        self.editLoaded= False
        self.cursor.execute("DROP TABLE DataValuesEdit")
        self.conn.commit()
        self.createEditTable()


    def initEditValues(self, seriesID):
        if not self.editLoaded:
            series = self.series_service.get_series_by_id(seriesID)
            self.DataValuesEdit = [(dv.id, dv.data_value, dv.value_accuracy, dv.local_date_time, dv.utc_offset, dv.date_time_utc,
                dv.site_id, dv.variable_id, dv.offset_value, dv.offset_type_id, dv.censor_code,
                dv.qualifier_id, dv.method_id, dv.source_id, dv.sample_id, dv.derived_from_id,
                dv.quality_control_level_id) for dv in series.data_values]

            self.cursor.executemany("INSERT INTO DataValuesEdit VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", self.DataValuesEdit)
            self.conn.commit()
            self.editLoaded = True



    def initSC(self):
        self.SeriesCatalog = [(s.id, s.site_id, s.site_code, s.site_name, s.variable_id, s.variable_code,
            s.variable_name, s.speciation, s.variable_units_id, s.variable_units_name, s.sample_medium,
            s.value_type, s.time_support, s.time_units_id, s.time_units_name, s.data_type, s.general_category,
            s.method_id, s.method_description, s.source_id, s.organization, s.source_description,
            s.citation, s.quality_control_level_id, s.quality_control_level_code, s.begin_date_time,
            s.end_date_time, s.begin_date_time_utc, s.end_date_time_utc, s.value_count) for s in self.series_service.get_all_series() ]
        self.cursor.executemany("INSERT INTO SeriesCatalog VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", self.SeriesCatalog)
        self.cursor.execute("ALTER TABLE SeriesCatalog ADD COLUMN isSelected INTEGER ")

        self.cursor.execute("UPDATE SeriesCatalog SET isSelected=0")
        self.conn.commit()

    def initDB(self):
        self.cursor.execute("""CREATE TABLE SeriesCatalog
                (SeriesID INTEGER NOT NULL,
                SiteID INTEGER,
                SiteCode VARCHAR(50),
                SiteName VARCHAR(255),
                VariableID INTEGER,
                VariableCode VARCHAR(50),
                VariableName VARCHAR(255),
                Speciation VARCHAR(255),
                VariableUnitsID INTEGER,
                VariableUnitsName VARCHAR(255),
                SampleMedium VARCHAR(255),
                ValueType VARCHAR(255),
                TimeSupport FLOAT,
                TimeUnitsID INTEGER,
                TimeUnitsName VARCHAR(255),
                DataType VARCHAR(255),
                GeneralCategory VARCHAR(255),
                MethodID INTEGER,
                MethodDescriptions VARCHAR(255),
                SourceID INTEGER,
                Organization VARCHAR(255),
                SourceDescription VARCHAR(255),
                Citation VARCHAR(255),
                QualityControlLevelID INTEGER,
                QualityControlLevelCode VARCHAR(50),
                BeginDateTime TIMESTAMP,
                EndDateTime TIMESTAMP,
                BeginDateTimeUTC TIMESTAMP,
                EndDateTimeUTC TIMESTAMP,
                ValueCount INTEGER,

                PRIMARY KEY (SeriesID))

               """)



        self.cursor.execute("""CREATE TABLE DataValues
                (ValueID INTEGER NOT NULL,
                DataValue FLOAT NOT NULL,
                ValueAccuracy FLOAT,
                LocalDateTime TIMESTAMP NOT NULL,
                UTCOffset FLOAT NOT NULL,
                DateTimeUTC TIMESTAMP NOT NULL,
                SiteID INTEGER NOT NULL,
                VariableID INTEGER NOT NULL,
                OffsetValue FLOAT,
                OffsetTypeID INTEGER,
                CensorCode VARCHAR(50) NOT NULL,
                QualifierID INTEGER,
                MethodID INTEGER NOT NULL,
                SourceID INTEGER NOT NULL,
                SampleID INTEGER,
                DerivedFromID INTEGER,
                QualityControlLevelID INTEGER NOT NULL,

                PRIMARY KEY (ValueID),
                UNIQUE (DataValue, LocalDateTime, SiteID, VariableID, MethodID, SourceID, QualityControlLevelID))
               """)


        self.createEditTable()

    def createEditTable(self):
        self.cursor.execute("""CREATE TABLE DataValuesEdit
                (ValueID INTEGER NOT NULL,
                DataValue FLOAT NOT NULL,
                ValueAccuracy FLOAT,
                LocalDateTime TIMESTAMP NOT NULL,
                UTCOffset FLOAT NOT NULL,
                DateTimeUTC TIMESTAMP NOT NULL,
                SiteID INTEGER NOT NULL,
                VariableID INTEGER NOT NULL,
                OffsetValue FLOAT,
                OffsetTypeID INTEGER,
                CensorCode VARCHAR(50) NOT NULL,
                QualifierID INTEGER,
                MethodID INTEGER NOT NULL,
                SourceID INTEGER NOT NULL,
                SampleID INTEGER,
                DerivedFromID INTEGER,
                QualityControlLevelID INTEGER NOT NULL,

                PRIMARY KEY (ValueID),
                UNIQUE (DataValue, LocalDateTime, SiteID, VariableID, MethodID, SourceID, QualityControlLevelID))
               """)
