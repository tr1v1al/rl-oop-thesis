# Project Repository Structure

Bachelor's thesis: Object-Oriented Development of Graduality Management Software Using Level-Based Representations. Test Implementation.

This repository contains the source code and documentation for the `rlistic` software library, available at [https://github.com/tr1vial/rl-oop-thesis](https://github.com/tr1vial/rl-oop-thesis). Below is an overview of its structure:

- `docs`: Documentation for the `rlistic` library, generated using `sphinx`, a popular documentation generator in the Python community. Available in `html` and `pdf` formats.
- `examples`: Example scripts demonstrating the use of the `rlistic` library, including:
  - `good_students_proxy`, `good_students_rlprogram`, and `possible_groups`: Examples showing how to use `proxy` and `rlprogram` to solve the "good students" grouping problem with a crisp program.
  - `heavy_calc_input` and `heavy_calc_script`: Examples highlighting the `rlprogram` module.
  - `static_input`, `static_output`, and `static_usage`: Examples demonstrating the `static` module.
  - `runtime_usage`: Example showcasing the `runtime` module.
  - `proxy_usage`: Example illustrating the `proxy` module.
- `rlistic`: The main package containing the `rlistic` software library, with the following modules:
  - `common`: Common utilities.
  - `rlprogram`: Program rlifier.
  - `static`: Static class rlifier.
  - `runtime`: Runtime class rlifier.
  - `proxy`: Proxy rlifier.
- `tests`: Individual test modules for the `rlistic` library, implemented using `unittest`, including:
  - `test_common`
  - `test_rlprogram`
  - `test_static`
  - `test_runtime`
  - `test_proxy`