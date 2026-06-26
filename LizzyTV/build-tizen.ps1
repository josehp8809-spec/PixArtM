# Script de Empaquetado para Samsung Tizen TV (.wgt)
# Ejecutado de forma automática al compilar para Tizen.

$projectName = "lizzytv"
$distPath = "dist"
$configSource = "tizen-config.xml"
$configDest = "$distPath\config.xml"
$zipFile = "$projectName.zip"
$wgtFile = "$projectName.wgt"

Write-Host "Iniciando empaquetado para Tizen OS..." -ForegroundColor Cyan

# 1. Copiar el archivo config.xml al build dist
if (Test-Path $configSource) {
    Copy-Item -Path $configSource -Destination $configDest -Force
    Write-Host "config.xml copiado a la carpeta dist/." -ForegroundColor Green
} else {
    Write-Error "No se encontró el archivo $configSource en la raíz del proyecto."
    exit 1
}

# 2. Eliminar empaquetados anteriores si existen
if (Test-Path $wgtFile) {
    Remove-Item -Path $wgtFile -Force
    Write-Host "Archivo .wgt anterior eliminado." -ForegroundColor Yellow
}
if (Test-Path $zipFile) {
    Remove-Item -Path $zipFile -Force
}

# 3. Comprimir la carpeta dist en formato zip
Write-Host "Comprimiendo la carpeta dist/..." -ForegroundColor Cyan
# Usar .NET ZipFile para evitar problemas con directorios vacíos o Compress-Archive si está disponible
try {
    # Cambiar al directorio dist para que los archivos queden en la raíz del ZIP
    $previousDir = Get-Location
    Set-Location $distPath
    
    # Comprimir archivos de la raíz de dist/
    Compress-Archive -Path * -DestinationPath "..\$zipFile" -Force
    
    Set-Location $previousDir
    Write-Host "Compresión exitosa." -ForegroundColor Green
} catch {
    Write-Error "Fallo la compresión: $_"
    exit 1
}

# 4. Renombrar el archivo zip a .wgt
if (Test-Path $zipFile) {
    Rename-Item -Path $zipFile -NewName $wgtFile -Force
    Write-Host "Widget Tizen generado con éxito: $wgtFile" -ForegroundColor Green
} else {
    Write-Error "No se pudo generar el archivo ZIP intermedio."
    exit 1
}

# 5. Limpiar el config.xml copiado de dist/ para no interferir con otros builds
if (Test-Path $configDest) {
    Remove-Item -Path $configDest -Force
    Write-Host "Limpieza de dist/ completada." -ForegroundColor Gray
}

Write-Host "Empaquetado Tizen finalizado. Listo para instalar en Samsung TV." -ForegroundColor Green
