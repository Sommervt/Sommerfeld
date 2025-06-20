use notify::{RecommendedWatcher, RecursiveMode, Watcher, Event};
use serde::Deserialize;
use std::{
    fs::File,
    io::{self, BufRead, BufReader},
    path::Path,
    sync::{Arc, Mutex},
    sync::mpsc::channel,
    thread,
    time::Duration,
};

fn cargar_palabras(path: &str) -> Vec<String> {
    let file = File::open(path).expect("❌ No se pudo abrir el archivo palabras.json");
    serde_json::from_reader(file).expect("❌ Error al leer o deserializar el JSON")
}

fn main() -> notify::Result<()> {
    let path_json = "badwords.json";

    // Carga inicial de palabras prohibidas
    let palabras = Arc::new(Mutex::new(cargar_palabras(path_json)));

    // Canal para recibir eventos de cambios en archivos
    let (tx, rx) = channel();

    // Crear watcher para detectar cambios
    let mut watcher: RecommendedWatcher = Watcher::new(tx, Duration::from_secs(1))?;
    watcher.watch(Path::new(path_json), RecursiveMode::NonRecursive)?;

    // Clonar el Arc para el hilo que procesa stdin
    let palabras_stdin = Arc::clone(&palabras);

    // Hilo para procesar mensajes stdin
    let handle = thread::spawn(move || {
        let stdin = io::stdin();
        for linea in stdin.lock().lines() {
            let mensaje = linea.unwrap();
            let lista = palabras_stdin.lock().unwrap();
            let mensaje_lower = mensaje.to_lowercase();

            let bloqueado = lista.iter().any(|p| mensaje_lower.contains(&p.to_lowercase()));

            if bloqueado {
                println!("bloqueado");
            } else {
                println!("permitido");
            }
        }
    });

    // Hilo principal escucha cambios en el JSON
    loop {
        match rx.recv() {
            Ok(event) => {
                // Cuando el archivo cambia, recarga las palabras
                if let Event{paths, ..} = event {
                    if paths.iter().any(|p| p.ends_with(path_json)) {
                        match cargar_palabras(path_json) {
                            Ok(nuevas_palabras) => {
                                let mut lista = palabras.lock().unwrap();
                                *lista = nuevas_palabras;
                                eprintln!("🔄 Palabras prohibidas recargadas.");
                            }
                            Err(e) => eprintln!("❌ Error recargando JSON: {:?}", e),
                        }
                    }
                }
            }
            Err(e) => eprintln!("Watcher error: {:?}", e),
        }
    }

    // Nunca llega aquí, pero por si acaso:
    // handle.join().unwrap();

    // Ok(())
}
