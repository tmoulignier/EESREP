
from os import environ
import pytest

import eesrep
from eesrep.eesrep_exceptions import BusTypeException, ParametersException
from eesrep.test_interface_solver import get_couple_from_key

solver_for_tests, interface_for_tests = get_couple_from_key()

@pytest.mark.Unit
@pytest.mark.bus
def test_wrong_bus_type():
    """
        Tests if the cluster starts the right amount of machines
    """
    model = eesrep.Eesrep(solver=solver_for_tests, interface=interface_for_tests)
    
    try:
        model.create_bus("wrong_bus", {})
        assert False, "Bus name does not exist"
    except BusTypeException:
        assert True
        
@pytest.mark.Unit
@pytest.mark.bus
def test_wrong_bus_name():
    """
        Tests if the cluster starts the right amount of machines
    """
    model = eesrep.Eesrep(solver=solver_for_tests, interface=interface_for_tests)
    
    try:
        model.create_bus("bus", {})
        assert False, "Bus name does not exist"
    except ParametersException:
        assert True

@pytest.mark.Unit
@pytest.mark.bus
def test_wrong_bus_argument_type():
    """
        Tests if the cluster starts the right amount of machines
    """
    model = eesrep.Eesrep(solver=solver_for_tests, interface=interface_for_tests)
    
    try:
        model.create_bus("bus", {"name":2})
        assert False, "Bus name does not exist"
    except ParametersException:
        assert True
        

@pytest.mark.Unit
@pytest.mark.bus
def test_bus_dict():
    """
        Tests if the cluster starts the right amount of machines
    """
    model = eesrep.Eesrep(solver=solver_for_tests, interface=interface_for_tests)
    
    model.create_bus("bus", {"name":"the_bus"})

    assert isinstance(model._Eesrep__buses["the_bus"], dict)
    assert list(model._Eesrep__buses["the_bus"].keys()) == ["name", "component_type", "inputs", "outputs"]