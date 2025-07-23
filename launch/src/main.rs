use windows_service::{
    service::{ServiceAccess, ServiceState},
    service_manager::{ServiceManager, ServiceManagerAccess},
};
use std::{error::Error, thread, time::Duration, path::Path, process::exit};

fn main() -> Result<(), Box<dyn Error>> {
    // Verifica si botservice.exe existe en la ruta esperada
    let exe_path = Path::new("../config/services/botservice.exe");
    if !exe_path.exists() {
        eprintln!("[ERROR] No se encontró botservice.exe en {:?}", exe_path);
        exit(2);
    }

    let manager_access = ServiceManagerAccess::CONNECT;
    let service_manager = ServiceManager::local_computer(None::<&str>, manager_access)?;

    match service_manager.open_service("SommerfeldBotService", ServiceAccess::QUERY_STATUS | ServiceAccess::START) {
        Ok(service) => {
            let status = service.query_status()?;
            if status.current_state != ServiceState::Running {
                println!("[INFO] Servicio encontrado pero no está corriendo. Iniciando...");
                service.start::<&std::ffi::OsStr>(&[])?;
                // Espera a que el servicio realmente arranque
                for _ in 0..10 {
                    let status = service.query_status()?;
                    if status.current_state == ServiceState::Running {
                        println!("[INFO] Servicio iniciado correctamente.");
                        break;
                    }
                    thread::sleep(Duration::from_millis(500));
                }
            } else {
                println!("[INFO] Servicio ya está corriendo.");
            }
        }
        Err(_) => {
            eprintln!("[WARN] Servicio no encontrado. Regístralo con botservice.exe una vez.");
            exit(1);
        }
    }

    Ok(())
}