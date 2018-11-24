import os
import unittest

import numpy as np

from openmdao.api import Problem, ExplicitComponent, IndepVarComp, ExecComp, ScipyOptimizeDriver
from openmdao.devtools.xdsm_writer import write_xdsm
from openmdao.test_suite.components.sellar import SellarNoDerivatives

FILENAME = 'XDSM'


class TestXDSMViewer(unittest.TestCase):

    def setUp(self):
        try:
            from pyxdsm.XDSM import XDSM
        except ImportError:
            raise unittest.SkipTest("pyXDSM is not installed")

    def test_sellar(self):
        """Makes XDSM for the Sellar problem"""

        prob = Problem()
        prob.model = SellarNoDerivatives()

        prob.setup(check=False)
        prob.final_setup()

        # no output checking, just make sure no exceptions raised
        write_xdsm(prob, filename=FILENAME)

    def test_sphere(self):
        """
        Makes an XDSM of the Sphere test case. It also adds a design variable, constraint and
        objective.
        """
        class Rosenbrock(ExplicitComponent):

            def __init__(self, problem):
                super(Rosenbrock, self).__init__()
                self.problem = problem
                self.counter = 0

            def setup(self):
                self.add_input('x', np.array([1.5, 1.5]))
                self.add_output('f', 0.0)
                self.declare_partials('f', 'x', method='fd', form='central', step=1e-4)

            def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
                x = inputs['x']
                outputs['f'] = sum(x**2)

        x0 = np.array([1.2, 1.5])

        prob = Problem()
        indeps = prob.model.add_subsystem('indeps', IndepVarComp(problem=prob), promotes=['*'])
        indeps.add_output('x', list(x0))

        prob.model.add_subsystem('sphere', Rosenbrock(problem=prob), promotes=['*'])
        prob.model.add_subsystem('con', ExecComp('c=sum(x)', x=np.ones(2)), promotes=['*'])
        prob.driver = ScipyOptimizeDriver()
        prob.model.add_design_var('x')
        prob.model.add_objective('f')
        prob.model.add_constraint('c', lower=1.0)

        prob.setup(check=False)
        prob.final_setup()

        # no output checking, just make sure no exceptions raised
        write_xdsm(prob, filename=FILENAME)

    def tearDown(self):
        """Comment out this method, if you want to inspect the output files."""
        for ext in ('aux', 'log', 'pdf', 'tex', 'tikz'):
            filename = '.'.join([FILENAME, ext])
            if os.path.exists(filename):
                os.remove(filename)


if __name__ == "__main__":
    unittest.main()