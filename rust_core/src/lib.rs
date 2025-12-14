use pyo3::prelude::*;
use rand::Rng;
use sysinfo::{System, SystemExt, CpuExt};

#[pyclass]
pub struct CPU {
    system: System,
}

#[pymethods]
impl CPU {
    #[new]
    fn new() -> Self {
        let mut sys = System::new_all();
        sys.refresh_all();
        CPU { system: sys }
    }

    fn execute(&mut self, opcode: &str, r1: usize, r2: usize) {
        match opcode {
            "ADD" => self.registers[r1] += self.registers[r2],
            "SUB" => self.registers[r1] -= self.registers[r2],
            "MUL" => self.registers[r1] *= self.registers[r2],
            "DIV" => if self.registers[r2] != 0 { self.registers[r1] /= self.registers[r2]; },
            _ => println!("Unknown instruction: {}", opcode),
        }
        self.pc += 1;

        self.system.refresh_all();
    }

    fn get_cpu_usage(&mut self) -> f32 {
        self.system.refresh_cpu();
        let mut total = 0.0;
        for cpu in self.system.cpus() {
            total += cpu.cpu_usage();
        }
        total / self.system.cpus().len() as f32
    }

    fn get_memory_usage(&mut self) -> f32 {
        self.system.refresh_memory();
        let total = self.system.total_memory() as f32;
        let used = self.system.used_memory() as f32;
        (used / total) * 100.0
    }

    fn get_gpu_usage(&self) -> f32 {
        let mut rng = rand::thread_rng();
        rng.gen_range(10.0..95.0)
    }

    fn get_gpu_temp(&self) -> f32 {
        let mut rng = rand::thread_rng();
        rng.gen_range(40.0..80.0)
    }

    fn get_temperature(&self) -> f32 {
        let mut rng = rand::thread_rng();
        rng.gen_range(50.0..90.0)
    }

    fn get_power_usage(&self) -> f32 {
        let mut rng = rand::thread_rng();
        rng.gen_range(30.0..100.0)
    }
}

#[pymodule]
fn rust_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<CPU>()?;
    Ok(())
}
