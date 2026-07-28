@echo off
echo =======================================================
echo   Starting Aether-Nexus Industrial Copilot ^& Backends  
echo =======================================================
echo.
echo Booting Document Pipeline (port 8000), GraphRAG (port 8010), and Vite (port 5173)...
cd frontend
npm run dev
