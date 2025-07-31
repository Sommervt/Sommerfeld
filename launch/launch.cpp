#include <windows.h>
#include <shellapi.h>
#include <shlwapi.h>

#pragma comment(lib, "shlwapi.lib")

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int) {
    wchar_t exePath[MAX_PATH];
    wchar_t exeDir[MAX_PATH];
    wchar_t targetPath[MAX_PATH];

    if (!GetModuleFileNameW(NULL, exePath, MAX_PATH)) {
        MessageBoxW(NULL, L"No se pudo obtener la ruta del ejecutable.", L"Error", MB_ICONERROR);
        return 1;
    }

    wcscpy_s(exeDir, exePath);
    PathRemoveFileSpecW(exeDir);

    if (!PathCombineW(targetPath, exeDir, L"sommerfeld.exe")) {
        MessageBoxW(NULL, L"No se pudo construir la ruta a sommerfeld.exe.", L"Error", MB_ICONERROR);
        return 1;
    }

    SHELLEXECUTEINFOW sei = { sizeof(sei) };
    sei.fMask = SEE_MASK_NOASYNC;
    sei.lpVerb = L"runas";
    sei.lpFile = targetPath;
    sei.nShow = SW_SHOWNORMAL;

    if (!ShellExecuteExW(&sei)) {
        MessageBoxW(NULL, L"No se pudo iniciar sommerfeld.exe con privilegios elevados.", L"Error", MB_ICONERROR);
        return 1;
    }

    return 0;
}