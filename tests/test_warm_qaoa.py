"""Regression tests for the LP-seeded bounded-register QAOA variant."""
from __future__ import annotations

import itertools
import unittest
from unittest.mock import patch

import numpy as np
from qiskit.quantum_info import Statevector

from optimization.decoder import evaluate_quantum_solution
from optimization.milp import MILPSolver
from quantum.ising import convert_qubo_to_ising
from quantum.qaoa_solver import QAOAConfig, QAOASolver, encode_register_probabilities, normalize_ising
from quantum.qubo import _binary_weights
from tests.test_qaoa_solver import tiny_qubo


class WarmQAOAEncodingTests(unittest.TestCase):
    def test_every_integer_register_value_has_a_deterministic_encoding(self):
        for upper_bound in range(1, 65):
            pairs = tuple(enumerate(_binary_weights(upper_bound)))
            for expected in range(upper_bound + 1):
                marginals = encode_register_probabilities(float(expected), pairs)
                self.assertTrue(all(value in (0.0, 1.0) for value in marginals.values()))
                self.assertEqual(sum(marginals[index] * weight for index, weight in pairs), expected)

    def test_fractional_register_interpolation_preserves_expected_value(self):
        for upper_bound in range(1, 33):
            pairs = tuple(enumerate(_binary_weights(upper_bound)))
            for quarter in range(upper_bound * 4 + 1):
                expected = quarter / 4
                marginals = encode_register_probabilities(expected, pairs)
                measured_mean = sum(marginals[index] * weight for index, weight in pairs)
                self.assertAlmostEqual(measured_mean, expected, places=12)
                self.assertTrue(all(0 <= value <= 1 for value in marginals.values()))

    def test_lp_solution_is_a_continuous_feasible_seed_with_recorded_objective(self):
        qubo = tiny_qubo()
        seed, metadata = QAOASolver(QAOAConfig(warm_start=True))._compute_warm_start_thetas(qubo)
        self.assertEqual(metadata["seed_source"], "lp_relaxation")
        self.assertEqual(metadata["seed_feasibility"], "feasible_continuous_relaxation")
        self.assertIsInstance(metadata["seed_objective"], float)
        self.assertGreaterEqual(metadata["seed_preprocessing_seconds"], 0)
        self.assertEqual(seed.shape, (qubo.variable_count,))
        self.assertTrue(np.all(np.isfinite(seed)))

    def test_relaxation_mixer_preserves_the_prepared_state_before_cost_phase(self):
        qubo = tiny_qubo()
        solver = QAOASolver(QAOAConfig(warm_start=True, p=1))
        thetas, _ = solver._compute_warm_start_thetas(qubo)
        ising = convert_qubo_to_ising(qubo)
        initial = Statevector.from_instruction(
            solver.build_circuit(ising, np.array([0.0, 0.0]), thetas=thetas)
        )
        mixed = Statevector.from_instruction(
            solver.build_circuit(ising, np.array([0.0, 0.371]), thetas=thetas)
        )
        self.assertTrue(initial.equiv(mixed))

    def test_lp_failure_falls_back_to_validated_greedy_not_milp_optimum(self):
        qubo = tiny_qubo()
        with patch("optimization.milp.MILPSolver.solve_relaxation", side_effect=RuntimeError("LP unavailable")):
            result = QAOASolver(QAOAConfig(warm_start=True, shots=32, max_iterations=2)).solve(qubo)
        info = result.optimizer_information
        self.assertEqual(info["seed_source"], "greedy_fallback")
        self.assertEqual(info["seed_feasibility"], "feasible_integer")
        self.assertIn("LP relaxation unavailable", info["seed_fallback_reason"])
        self.assertEqual(sum(result.counts.values()), 32)

    def test_feasible_shot_rate_uses_independent_operational_validator(self):
        qubo = tiny_qubo()
        result = QAOASolver(QAOAConfig(warm_start=True, shots=64, max_iterations=3)).solve(qubo)
        valid = 0
        for bitstring, count in result.counts.items():
            if evaluate_quantum_solution(qubo, bitstring).feasibility:
                valid += count
        info = result.optimizer_information
        self.assertEqual(info["feasible_shots"], valid)
        self.assertEqual(info["measured_shots"], 64)
        self.assertAlmostEqual(info["feasible_shot_rate"], valid / 64)

    def test_cost_normalization_preserves_all_assignment_energies(self):
        qubo = tiny_qubo()
        original = convert_qubo_to_ising(qubo)
        normalized, scale = normalize_ising(original)
        for bits in itertools.product((0, 1), repeat=qubo.variable_count):
            self.assertAlmostEqual(normalized.energy(bits) * scale, qubo.energy(bits), places=8)

    def test_xy_option_is_not_exposed_as_a_feasibility_preserving_mixer(self):
        with self.assertRaises(TypeError):
            QAOAConfig(mixer="xy")


if __name__ == "__main__":
    unittest.main()
