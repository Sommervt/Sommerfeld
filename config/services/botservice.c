#include <windows.h>
#include <winsvc.h>
#include <stdio.h>
#include <shlwapi.h>

SERVICE_STATUS serviceStatus = {0};
SERVICE_STATUS_HANDLE hStatus = 0;
PROCESS_INFORMATION pi = {0};
HANDLE hStopEvent = NULL;

int archivo(const char *ruta) {
    DWORD attr = GetFileAttributesA(ruta);
    return (attr != INVALID_FILE_ATTRIBUTES && !(attr & FILE_ATTRIBUTE_DIRECTORY));
}

void ObtenerDirectorioDelBot(char *buffer, DWORD size) {
    GetModuleFileNameA(NULL, buffer, size);
    PathRemoveFileSpecA(buffer); 
    PathRemoveFileSpecA(buffer); 
    PathRemoveFileSpecA(buffer); 
}

void EjecutarSommerfeld() {
    char ruta_base[MAX_PATH];
    ObtenerDirectorioDelBot(ruta_base, MAX_PATH);

    char ruta_py[MAX_PATH];
    char ruta_exe[MAX_PATH];
    char comando[MAX_PATH * 2];

    sprintf(ruta_py, "%s\\sommerfeld.py", ruta_base);
    sprintf(ruta_exe, "%s\\sommerfeld.exe", ruta_base);

    STARTUPINFOA si = {0};
    si.cb = sizeof(si);

    if (archivo(ruta_py)) {
        sprintf(comando, "python \"%s\"", ruta_py);
    } else if (archivo(ruta_exe)) {
        sprintf(comando, "\"%s\"", ruta_exe);
    } else {
        MessageBoxA(NULL, "No se encontró sommerfeld.py ni sommerfeld.exe", "Error", MB_OK | MB_ICONERROR);
        return;
    }

    if (!CreateProcessA(NULL, comando, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
        MessageBoxA(NULL, "Error al ejecutar el bot", "Sommerfeld Service", MB_OK | MB_ICONERROR);
        return;
    }
}

void WINAPI ServiceCtrlHandler(DWORD controlCode) {
    if (controlCode == SERVICE_CONTROL_STOP) {
        serviceStatus.dwCurrentState = SERVICE_STOP_PENDING;
        SetServiceStatus(hStatus, &serviceStatus);
        SetEvent(hStopEvent);
    }
}

void WINAPI ServiceMain(DWORD argc, LPTSTR *argv) {
    hStatus = RegisterServiceCtrlHandler("SommerfeldBotService", ServiceCtrlHandler);

    serviceStatus.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
    serviceStatus.dwCurrentState = SERVICE_START_PENDING;
    serviceStatus.dwControlsAccepted = SERVICE_ACCEPT_STOP;
    SetServiceStatus(hStatus, &serviceStatus);

    hStopEvent = CreateEvent(NULL, TRUE, FALSE, NULL);

    EjecutarSommerfeld();

    serviceStatus.dwCurrentState = SERVICE_RUNNING;
    SetServiceStatus(hStatus, &serviceStatus);

    WaitForSingleObject(hStopEvent, INFINITE);

    serviceStatus.dwCurrentState = SERVICE_STOPPED;
    SetServiceStatus(hStatus, &serviceStatus);
}

void AutoRegistrarServicio() {
    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CREATE_SERVICE);
    if (!hSCManager) return;

    SC_HANDLE hService = OpenServiceA(hSCManager, "SommerfeldBotService", SERVICE_QUERY_STATUS);
    if (hService) {
        CloseServiceHandle(hService);
        CloseServiceHandle(hSCManager);
        return;
    }

    char ruta[MAX_PATH];
    GetModuleFileNameA(NULL, ruta, MAX_PATH);

    hService = CreateServiceA(
        hSCManager,
        "SommerfeldBotService",
        "Sommerfeld Assistant",
        SERVICE_ALL_ACCESS,
        SERVICE_WIN32_OWN_PROCESS,
        SERVICE_AUTO_START,
        SERVICE_ERROR_NORMAL,
        ruta,
        NULL, NULL, NULL, NULL, NULL
    );

    if (hService) {
        MessageBoxA(NULL, "Sommerfeld se registró como servicio y se iniciará con Windows.", "Registro exitoso", MB_OK | MB_ICONINFORMATION);
        CloseServiceHandle(hService);
    }

    CloseServiceHandle(hSCManager);
}

int main() {
    AutoRegistrarServicio();

    SERVICE_TABLE_ENTRY serviceTable[] = {
        { "SommerfeldBotService", ServiceMain },
        { NULL, NULL }
    };

    StartServiceCtrlDispatcher(serviceTable);
    return 0;
}

//meow