import pytest

from odmdata import MemoryDatabase
from odmservices import SeriesService
from odmtests import test_util
from odmdata import copy_series


class TestMemoryDB:
	def setup(self):
		self.connection_string = "sqlite:///:memory:"
		self.series_service = SeriesService(connection_string=self.connection_string, debug=False)
		self.session = self.series_service._session_factory.get_session()
		engine = self.series_service._session_factory.engine
		test_util.build_db(engine)
		self.series = test_util.add_series(self.session)

	def test_build_memory_db(self):
		memory_db = MemoryDatabase(self.series)

		assert self.series.site_code == memory_db.get_series().site_code
		assert self.series.variable_code == memory_db.get_series().variable_code
		assert self.series.method_description == memory_db.get_series().method_description
		assert self.series.source_description == memory_db.get_series().source_description
		assert self.series.quality_control_level_code == memory_db.get_series().quality_control_level_code


	def test_get_data_values_is_empty(self):
		dvs = self.memory_db.get_data_values()
		assert len(dvs) == 0

