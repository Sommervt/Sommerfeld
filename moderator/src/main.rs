use std::{
    fs::File,
    io::{self, BufRead},
    process,
};

fn cargar_palabras(path: &str) -> Vec<String> {
    let file = File::open(path).unwrap_or_else(|_| {
        eprintln!("❌ No se pudo abrir el archivo '{}'.", path);
        process::exit(1);
    });

    serde_json::from_reader(file).unwrap_or_else(|e| {
        eprintln!("❌ Error al leer el archivo JSON: {:?}", e);
        process::exit(1);
    })
}

fn main() {
    let path_json = "badwords/badwords.json";
    let palabras = cargar_palabras(path_json);

    let stdin = io::stdin();
    let mut line = String::new();

    match stdin.read_line(&mut line) {
        Ok(_) => {
            let mensaje = line.trim().to_lowercase();
            let bloqueado = palabras.iter().any(|p| mensaje.contains(&p.to_lowercase()));

            if bloqueado {
                println!("bloqueado");
            } else {
                println!("permitido");
            }
        }
        Err(e) => {
            eprintln!("❌ Error leyendo stdin: {:?}", e);
            process::exit(1);
        }
    }
}