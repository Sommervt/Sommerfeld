use windows_service::{
    service::{ServiceAccess, ServiceState},
    service_manager::{ServiceManager, ServiceManagerAccess},
};
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let manager_access = ServiceManagerAccess::CONNECT;
    let service_manager = ServiceManager::local_computer(None::<&str>, manager_access)?;

    match service_manager.open_service("SommerfeldBotService", ServiceAccess::QUERY_STATUS | ServiceAccess::START) {
        Ok(service) => {
            let status = service.query_status()?;
            if status.current_state != ServiceState::Running {
                println!("[INFO] Iniciando servicio...");
                service.start::<&std::ffi::OsStr>(&[])?; // <- corrección aquí
                println!("[INFO] Servicio iniciado.");
            } else {
                println!("[INFO] Servicio ya está corriendo.");
            }
        }
        Err(_) => {
            println!("[WARN] Servicio no encontrado. Regístralo con botservice.exe una vez.");
        }
    }

    Ok(())
}