#include <windows.h>
#include <winsvc.h>
#include <shlwapi.h>
#include <strsafe.h>
#include <stdio.h>

SERVICE_STATUS serviceStatus = {0};
SERVICE_STATUS_HANDLE hStatus = 0;
HANDLE hStopEvent = NULL;

// Utilidad: ¿Existe el archivo?
int archivo(const char *ruta) {
    DWORD attr = GetFileAttributesA(ruta);
    return (attr != INVALID_FILE_ATTRIBUTES && !(attr & FILE_ATTRIBUTE_DIRECTORY));
}

// Log al Event Viewer
void LogError(const char *msg) {
    HANDLE hEventLog = RegisterEventSourceA(NULL, "SommerfeldBotService");
    if (hEventLog) {
        const char *msgs[] = { msg };
        ReportEventA(hEventLog, EVENTLOG_ERROR_TYPE, 0, 0, NULL, 1, 0, msgs, NULL);
        DeregisterEventSource(hEventLog);
    }
}

// Obtener directorio base del ejecutable, subiendo `niveles`
void ObtenerDirectorioDelBot(char *buffer, DWORD size, int niveles) {
    if (!GetModuleFileNameA(NULL, buffer, size)) return;
    for (int i = 0; i < niveles; ++i) {
        PathRemoveFileSpecA(buffer);
    }
}

// Ejecutar sommerfeld.py o sommerfeld.exe
void EjecutarSommerfeld() {
    char ruta_base[MAX_PATH];
    ObtenerDirectorioDelBot(ruta_base, MAX_PATH, 3);

    char ruta_py[MAX_PATH], ruta_exe[MAX_PATH], comando[MAX_PATH * 2];
    STARTUPINFOA si = {0};
    PROCESS_INFORMATION pi = {0};
    si.cb = sizeof(si);

    StringCchPrintfA(ruta_py, MAX_PATH, "%s\\sommerfeld.py", ruta_base);
    StringCchPrintfA(ruta_exe, MAX_PATH, "%s\\sommerfeld.exe", ruta_base);

    if (archivo(ruta_py)) {
        StringCchPrintfA(comando, MAX_PATH * 2, "python \"%s\"", ruta_py);
    } else if (archivo(ruta_exe)) {
        StringCchPrintfA(comando, MAX_PATH * 2, "\"%s\"", ruta_exe);
    } else {
        LogError("No se encontró sommerfeld.py ni sommerfeld.exe");
        return;
    }

    if (!CreateProcessA(NULL, comando, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
        LogError("Error al ejecutar el bot (CreateProcessA falló)");
        return;
    }

    // Cerrar los handles del proceso hijo
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
}

// Manejador de control del servicio
void WINAPI ServiceCtrlHandler(DWORD controlCode) {
    switch (controlCode) {
        case SERVICE_CONTROL_STOP:
            serviceStatus.dwCurrentState = SERVICE_STOP_PENDING;
            SetServiceStatus(hStatus, &serviceStatus);
            SetEvent(hStopEvent);
            break;
        case SERVICE_CONTROL_SHUTDOWN:
            // Ignorar shutdown para evitar que Windows detenga el servicio
            break;
        default:
            break;
    }
}

// Lógica principal del servicio
void WINAPI ServiceMain(DWORD argc, LPTSTR *argv) {
    hStatus = RegisterServiceCtrlHandlerA("SommerfeldBotService", ServiceCtrlHandler);
    if (!hStatus) {
        LogError("Fallo al registrar Service Control Handler.");
        return;
    }

    serviceStatus.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
    serviceStatus.dwCurrentState = SERVICE_START_PENDING;
    serviceStatus.dwControlsAccepted = SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN;
    SetServiceStatus(hStatus, &serviceStatus);

    hStopEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
    if (!hStopEvent) {
        LogError("Fallo al crear el evento de parada.");
        return;
    }

    EjecutarSommerfeld();

    serviceStatus.dwCurrentState = SERVICE_RUNNING;
    SetServiceStatus(hStatus, &serviceStatus);

    WaitForSingleObject(hStopEvent, INFINITE);

    serviceStatus.dwCurrentState = SERVICE_STOPPED;
    SetServiceStatus(hStatus, &serviceStatus);

    CloseHandle(hStopEvent);
}

// Registrar el servicio si no existe
void AutoRegistrarServicio() {
    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CREATE_SERVICE);
    if (!hSCManager) {
        LogError("No se pudo abrir el Service Control Manager.");
        return;
    }

    SC_HANDLE hService = OpenServiceA(hSCManager, "SommerfeldBotService", SERVICE_QUERY_STATUS);
    if (hService) {
        // Ya existe, no registrar de nuevo
        CloseServiceHandle(hService);
        CloseServiceHandle(hSCManager);
        return;
    }

    char ruta[MAX_PATH];
    if (!GetModuleFileNameA(NULL, ruta, MAX_PATH)) {
        LogError("No se pudo obtener la ruta del ejecutable.");
        CloseServiceHandle(hSCManager);
        return;
    }

    hService = CreateServiceA(
        hSCManager,
        "SommerfeldBotService",
        "Sommerfeld Assistant",
        SERVICE_START | SERVICE_STOP | SERVICE_QUERY_STATUS,
        SERVICE_WIN32_OWN_PROCESS,
        SERVICE_AUTO_START,
        SERVICE_ERROR_NORMAL,
        ruta,
        NULL, NULL, NULL, NULL, NULL
    );

    if (!hService) {
        DWORD error = GetLastError();
        char msg[256];
        StringCchPrintfA(msg, 256, "Error al registrar el servicio. Código: %lu", error);
        LogError(msg);
    } else {
        // Registro exitoso, sin MessageBox
        CloseServiceHandle(hService);
    }

    CloseServiceHandle(hSCManager);
}

int main() {
    AutoRegistrarServicio();

    SERVICE_TABLE_ENTRYA serviceTable[] = {
        { "SommerfeldBotService", ServiceMain },
        { NULL, NULL }
    };

    if (!StartServiceCtrlDispatcherA(serviceTable)) {
        LogError("StartServiceCtrlDispatcherA falló. Probablemente se está ejecutando fuera del contexto de servicios.");
    }

    return 0;
}