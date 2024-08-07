from os import path, environ
import pandas as pd
from eesrep.components.bus import GenericBus
import numpy as np
import pytest

from eesrep import Eesrep
from eesrep.components.converter import Cluster
from eesrep.components.dam import Dam
from eesrep.components.sink_source import FatalSink, Sink, Source
from eesrep.test_interface_solver import get_couple_from_key

solver_for_tests, interface_for_tests = get_couple_from_key()

@pytest.mark.Theory
@pytest.mark.Dam
@pytest.mark.H_001
def test_H_001_mass_summary():
    app_home = path.dirname(path.realpath(__file__))

    data_ts = pd.read_csv(path.join(app_home, "DataSeries", "H_001_dataseries.csv"), sep=";")

    model = Eesrep(solver=solver_for_tests, interface=interface_for_tests)

    null_source = Source("null_source", 0., 0., 1.)

    dam = Dam("dam", 
                1., 
                0.,
                1000000,
                1500000,
                0.,
                0.,
                1.,
                True,
                False,
                0.,
                0.,
                water_inflow=(data_ts[["Time", "Amont"]]).rename(columns={"Time":"time", "Amont":"value"}))

    fatal_sink = FatalSink("fatal_sink", (data_ts[["Time", "Load"]]).rename(columns={"Time":"time", "Load":"value"}))

    model.add_component(null_source)
    model.add_component(dam)
    model.add_component(fatal_sink)

    model.add_link(null_source.power_out, dam.power_in, 1., 0.)
    model.add_link(dam.power_out, fatal_sink.power_in, 1., 0.)

    model.define_time_range(3600., 1001, 1001, 1)

    model.solve()

    results = model.get_results(as_dataframe=True)
    theory = pd.read_csv(path.join(app_home, "ReferenceResults", "H_001_theory.csv"))

    assert np.max(results["dam_power_out"].to_numpy() - theory["production"].to_numpy()) < 1e-5
    assert np.max(results["dam_storage"].to_numpy() - theory["storage"].to_numpy()) < 1e-5




@pytest.mark.Theory
@pytest.mark.Dam
@pytest.mark.H_004
def test_H_004_variable_minimum_storage():
    app_home = path.dirname(path.realpath(__file__))

    data_ts = pd.read_csv(path.join(app_home, "DataSeries", "H_004_dataseries.csv"), sep=";")

    model = Eesrep(solver=solver_for_tests, interface=interface_for_tests)

    bus = GenericBus("bus")
    model.add_component(bus)

    unsupplied = Source("unsupplied", 0., 10000., 10.)
    spilled = Sink("spilled", 0., 10000., 5000.)
    fatal_sink = FatalSink("fatal_sink", (data_ts[["Time", "Load"]]).rename(columns={"Time":"time", "Load":"value"}))

    dam = Dam("dam", 
                1., 
                0.,
                1000000,
                500000,
                0.,
                0.,
                1.,
                False,
                False,
                -1.,
                0.,
                water_inflow = 
                    (data_ts[["Time", "Amont"]]).rename(columns={"Time":"time", "Amont":"value"}),
                variable_storage_min = 
                    (data_ts[["Time", "Stockage_Min"]]).rename(columns={"Time":"time", "Stockage_Min":"value"}))

    model.add_component(unsupplied)
    model.add_component(spilled)
    model.add_component(dam)
    model.add_component(fatal_sink)

    model.plug_to_bus(dam.power_out, bus.input, 1., 0.)

    model.plug_to_bus(unsupplied.power_out, bus.input, 1., 0.)

    model.plug_to_bus(fatal_sink.power_in, bus.output, 1., 0.)
    model.plug_to_bus(spilled.power_in, bus.output, 1., 0.)

    model.define_time_range(3600., 1, 1000, 1)

    model.solve()

    results = model.get_results(as_dataframe=True)
    
    #   Relaxed condition as significative figures is too low.
    assert min(np.array(results["dam_storage"]) - np.array((500000.*data_ts["Stockage_Min"]).iloc[1:-1])) >= -1e-5




@pytest.mark.Theory
@pytest.mark.Dam
@pytest.mark.H_005
def test_H_005_variable_maximum_storage():
    app_home = path.dirname(path.realpath(__file__))

    data_ts = pd.read_csv(path.join(app_home, "DataSeries", "H_005_dataseries.csv"), sep=";")

    model = Eesrep(solver=solver_for_tests, interface=interface_for_tests)

    bus = GenericBus("bus")
    model.add_component(bus)

    unsupplied = Source("unsupplied", 0., 10000., 10.)
    spilled = Sink("spilled", 0., 10000., 5000.)
    null_source = Source("null_source", 0., 0., 1.)

    dam = Dam("dam", 
                1., 
                0.,
                1000000,
                500000,
                0.,
                0.,
                1.,
                False,
                True,
                -1.,
                0.,
                water_inflow = 
                    (data_ts[["Time", "Amont"]]).rename(columns={"Time":"time", "Amont":"value"}),
                variable_storage_max = 
                    (data_ts[["Time", "Stockage_Max"]]).rename(columns={"Time":"time", "Stockage_Max":"value"}))

    fatal_sink = FatalSink("fatal_sink", (data_ts[["Time", "Load"]]).rename(columns={"Time":"time", "Load":"value"}))

    model.add_component(unsupplied)
    model.add_component(spilled)
    model.add_component(null_source)
    model.add_component(dam)
    model.add_component(fatal_sink)
    
    model.add_link(null_source.power_out, dam.power_in, 1., 0.)

    model.plug_to_bus(dam.power_out, bus.input, 1., 0.)

    model.plug_to_bus(unsupplied.power_out, bus.input, 1., 0.)

    model.plug_to_bus(fatal_sink.power_in, bus.output, 1., 0.)
    model.plug_to_bus(spilled.power_in, bus.output, 1., 0.)

    model.define_time_range(3600., 1000, 1000, 1)

    model.solve()

    results = model.get_results(as_dataframe=True)
    #   Relaxed condition as significative figures is too low.
    assert max(np.array(results["dam_storage"]) - np.array((500000.*data_ts["Stockage_Max"]).iloc[1:-1])) <= 1e-5

if __name__ == "__main__":
    test_H_004_variable_minimum_storage()
