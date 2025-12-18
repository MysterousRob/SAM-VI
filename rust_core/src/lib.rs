use pyo3::prelude::*;
use sysinfo::{System, Components, Disks};
//use nvml_wrapper::Nvml;
//use nvml_wrapper::enum_wrappers::device::TemperatureSensor

#[pyclass]
pub struct CPU {
    system: System,
    components: Components,
    disks: Disks, 
}

#[pymethods]
impl CPU {
    #[new]
    fn new() -> Self {
        let mut sys = System::new_all();
        sys.refresh_all();
        
        let components = Components::new_with_refreshed_list();
        let disks = Disks::new_with_refreshed_list();
        
        CPU { 
            system: sys,
            components,
            disks,
        }
    }

    fn refresh(&mut self) {
        self.system.refresh_all();
        self.components.refresh();
        self.disks.refresh(); 
    }

    fn get_cpu_usage(&mut self) -> f32 {
        self.system.refresh_cpu_usage(); 
        let cpus = self.system.cpus();
        if cpus.is_empty() { return 0.0; }
        cpus.iter().map(|cpu| cpu.cpu_usage()).sum::<f32>() / cpus.len() as f32
    }

    fn get_memory_usage(&mut self) -> f32 {
        self.system.refresh_memory();
        let total = self.system.total_memory() as f32;
        let used = self.system.used_memory() as f32;
        if total == 0.0 { return 0.0; }
        (used / total) * 100.0
    }

    fn get_temperature(&mut self) -> f32 {
        self.components.refresh();
        
        self.components
            .iter()
            .find(|c| {
                let label = c.label().to_uppercase();
                label.contains("CPU") || label.contains("PACKAGE")
            })
            .map(|c| c.temperature()) 
            .unwrap_or(45.0) 
    }

    fn get_disk_usage(&mut self) -> f32 {
        self.disks.refresh(); 
        let disk = self.disks.iter().next(); 
        if let Some(d) = disk {
            let total = d.total_space() as f32;
            let available = d.available_space() as f32;
            if total == 0.0 { return 0.0; }
            return ((total - available) / total) * 100.0;
        }
        0.0
    }
}

#[pymodule]
fn rust_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CPU>()?;
    Ok(())
}