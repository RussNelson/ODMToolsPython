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

	def test_get_data_values_empty(self):
		new_series = copy_series(self.series)
		new_series.data_values = []
		memory_db = MemoryDatabase(new_series)
		dvs = memory_db.get_data_values()
		assert len(dvs) == 0

<<<<<<< HEAD
	def test_get_data_values(self):
		memory_db = MemoryDatabase(self.series)
		dvs = memory_db.get_data_values()
		assert len(dvs) != 0

		outside_dv = self.series.data_values[0]
		inside_dv = dvs[0]

		assert outside_dv.site_id == inside_dv[6]
		assert outside_dv.variable_id == inside_dv[7]

	def test_get_data_values_len(self):
		memory_db = MemoryDatabase(self.series)
		dvs = memory_db.get_data_values()
		assert len(dvs) == len(self.series.data_values)

	


	# def test_delete_points(self):
	# 	with pytest.raises(NotImplementedError):
	# 		self.memory_db.delete_points("filter")

	# def test_add_points(self):
	# 	with pytest.raises(NotImplementedError):
	# 		self.memory_db.add_points("filter")

	# def test_update_points(self):
	# 	with pytest.raises(NotImplementedError):
	# 		self.memory_db.update_points("filter", [1,2,3])
=======
	def test_get_data_values_is_empty(self):
		dvs = self.memory_db.get_data_values()
		assert len(dvs) == 0
>>>>>>> master
